import os
from google import genai
from google.genai import types
from pydantic import BaseModel
import sys

from prompts.diffparser_prompt import DIFF_PARSER_P1
from prompts.funcgenerator_prompt import FUNCTION_GENERATOR_P1, FUNCTION_GENERATOR_P2
from prompts.getrelevantcontext_prompt import GET_RELEVANT_CONTEXT_P1

# Configuration flags
DEBUG = False
AI_ENABLED = False

class ContextDirs(BaseModel):
    """Model for storing the directories that should be included as context."""
    context_dirs: list[str]

class ContextFiles(BaseModel):
    """Model for storing the files that should be included as context."""
    context_files: list[str]

class RequiredChanges(BaseModel):
    """Model for storing analysis of code needed based on diff."""
    files_to_update: list[str]
    implementation_details: list[str]

class GeneratedFiles(BaseModel):
    """Model for storing AI-generated file content."""
    file_paths: list[str]
    file_contents: list[str]

def write_to_file(filepath: str, content: str) -> None:
    """Write content to a file at the specified path.

    Args:
        filepath: Path to the file to write
        content: Content to write to the file
    """
    print(f"Writing to: {filepath}")
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Successfully wrote to: {filepath} \n")

def read_file_content(file_path) -> str:
    """Read and return the content of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        str: Content of the file or error message if reading fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_relevant_context(client: genai.Client, zsh_diff_output: str, tree_output: str) -> types.GenerateContentResponse:
    prompt = GET_RELEVANT_CONTEXT_P1.format(tree_structure=tree_output, zsh_diff_output=zsh_diff_output)
    tokens = client.models.count_tokens(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt
    )
    print(f"Input tokens from getrelevantdirs_prompt: {tokens}\n")
    response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=ContextFiles
            )
        )
    return response

def gather_context_dirs(project_root_dir_abs: str, context_dir_rel: str, relevant_dirs: list[str], include_subdirs: bool = False) -> str:
    """Scrape directories and gather code context for LLM processing.

    Args:
        project_root_dir_abs: Absolute path to the project root
        context_dir_rel: Relative path to the context directory from project root
        relevant_dirs: List of directory paths (relative to project root) to include
        include_subdirs: Whether to include subdirectories of relevant_dirs

    Returns:
        str: Combined context from all relevant directories
    """
    context_str = ""
    context_dir_abs = os.path.join(project_root_dir_abs, context_dir_rel)

    # Convert relevant_dirs to absolute paths for easier comparison
    abs_relevant_dirs = [os.path.join(project_root_dir_abs, d) for d in relevant_dirs]

    # Walk through the directory structure
    for root, dirs, files in os.walk(context_dir_abs, topdown=True):
        # Skip __pycache__ directories
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")

        # Check if current directory is in our relevant directories
        is_relevant = root in abs_relevant_dirs or root == context_dir_abs

        # If not including subdirectories, prune dirs list to control traversal
        if not include_subdirs and not is_relevant:
            # Keep only directories that are direct paths to relevant directories
            dirs_to_keep = []
            for d in dirs:
                dir_path = os.path.join(root, d)
                # Check if this directory or any of its subdirectories are in our relevant list
                if dir_path in abs_relevant_dirs or any(rd.startswith(dir_path + os.sep) for rd in abs_relevant_dirs):
                    dirs_to_keep.append(d)
            dirs[:] = dirs_to_keep

        # If this directory is relevant, process it
        if is_relevant:
            # Add directory information
            dir_info = f"Directory: {os.path.relpath(root, project_root_dir_abs)}\n"
            dir_info += f"Subdirectories: {dirs}\n"
            dir_info += f"Files: {files}\n"
            context_str += dir_info

            # Process files in this directory
            for file in files:
                file_path = os.path.join(root, file)
                sdk_file_path = os.path.relpath(file_path, project_root_dir_abs)
                file_content = read_file_content(file_path)

                file_info = f"File: {sdk_file_path}\nContent: \n{file_content}\n--------------------------------\n"
                context_str += file_info

    return context_str

def gather_context_files(project_root_dir_abs: str, relevant_files: list[str]) -> str:
    """Gather context from specific files in the project."""
    context_str = ""
    for file in relevant_files:
        file_path = os.path.join(project_root_dir_abs, file)
        file_content = read_file_content(file_path)
        file_info = f"File: {file}\nContent: \n{file_content}\n--------------------------------\n"
        context_str += file_info
    return context_str


def get_diff_analysis(client: genai.Client, current_dir: str, diff_output: str, relevant_files: list[str]) -> types.GenerateContentResponse:
    """Analyze git diff using LLM to identify required code changes.

    Args:
        client: Gemini API client
        current_dir: Current directory path
        diff_output: Git diff output as string

    Returns:
        GenerateContentResponse: LLM response containing analysis of needed changes
    """
    # Gather code context from the project
    relevant_context = gather_context_files(project_root_dir_abs=os.path.dirname(current_dir), relevant_files=relevant_files)
    if DEBUG:
        debug_file_path = os.path.join(os.getcwd(), "relevant_context.txt")
        write_to_file(debug_file_path, relevant_context)

    # Format the prompt with gathered context
    prompt = DIFF_PARSER_P1.format(selected_context_files=relevant_context, zsh_diff_output=diff_output)

    # Count tokens for logging
    tokens = client.models.count_tokens(
    model="gemini-2.5-flash-preview-05-20",
        contents=prompt
    )
    print(f"Input tokens from diffparser_prompt: {tokens}\n")

    # Generate content if AI is enabled, otherwise return empty response
    if AI_ENABLED:
        return client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=RequiredChanges
            )
        )
    else:
        return client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents="Empty prompt because AI is disabled",
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=RequiredChanges
            )
        )


def generate_implementations(client: genai.Client, current_dir: str, diff_analysis: types.GenerateContentResponse):
    """Generate implementation code based on diff analysis.

    Args:
        client: Gemini API client
        current_dir: Current directory path
        diff_analysis: LLM response from diff analysis
    """
    project_root_dir = os.path.dirname(current_dir)

    # Parse the response from diff analysis
    parsed_response: RequiredChanges = diff_analysis.parsed

    # Start with the first part of the prompt
    prompt = FUNCTION_GENERATOR_P1.format(implementation_details=parsed_response.implementation_details)

    # Add existing files content to the prompt
    existing_files_text = "\n=== EXISTING FILES ===\n"
    for file_path in parsed_response.files_to_update:
        try:
            with open(os.path.join(project_root_dir, file_path), 'r') as f:
                file_content = f.read()
                existing_files_text += f"\n=== {file_path} ===\n{file_content}\n"
        except FileNotFoundError:
            print(f"Warning: File {file_path} not found. Skipping this file.")
            existing_files_text += f"\n=== {file_path} ===\n# File not found. Please ensure this file exists before proceeding.\n"
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            existing_files_text += f"\n=== {file_path} ===\n# Error reading file: {str(e)}\n"
    prompt += existing_files_text

    # Gather testing suite context
    testing_suite = gather_context_dirs(project_root_dir_abs=os.path.dirname(current_dir), context_dir_rel="tests", relevant_dirs=["tests/mocks"], include_subdirs=False)
    if DEBUG:
        debug_file_path = os.path.join(os.getcwd(), "testing_suite_context.txt")
        write_to_file(debug_file_path, testing_suite)

    # Add the second part of the prompt
    prompt += FUNCTION_GENERATOR_P2

    # Count tokens for logging
    tokens = client.models.count_tokens(
    model="gemini-2.5-flash-preview-05-20",
        contents=prompt
    )
    print(f"Input tokens from funcgenerator_prompt: {tokens} \n")

    # Generate and write files if AI is enabled
    if AI_ENABLED:
        response2 = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=GeneratedFiles
            )
        )

        # Write the generated content to files
        parsed_response2: GeneratedFiles = response2.parsed
        if(len(parsed_response2.file_paths) == len(parsed_response2.file_contents)):
            for index, file_path in enumerate(parsed_response2.file_paths):
                # Create AI version of the file in the same directory
                original_file_dir = os.path.dirname(os.path.join(project_root_dir, file_path))
                original_filename = os.path.basename(file_path)
                filename_without_ext, file_ext = os.path.splitext(original_filename)
                ai_filename = f"{filename_without_ext}ai{file_ext}"
                ai_file_path = os.path.join(original_file_dir, ai_filename)
                write_to_file(ai_file_path, parsed_response2.file_contents[index])
        else:
            print("ERROR: AI OUTPUT INCORRECT")


def main():
    """Main entry point for the AI updater script."""
    global DEBUG, AI_ENABLED
    # Parse command line arguments
    DEBUG = "--debug" in sys.argv
    AI_ENABLED = "--noai" not in sys.argv

    # Get the absolute path of the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Initialize Gemini API Client
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    # Get diff and tree output from environment (and write to file for debugging)
    zsh_diff_output = os.getenv("ZSH_DIFF_OUTPUT")
    if not zsh_diff_output:
        raise ValueError("ZSH_DIFF_OUTPUT environment variable not set")
    if DEBUG:
        testdiff_path = os.path.join(current_dir, "gitdifftest.txt")
        write_to_file(testdiff_path, zsh_diff_output)
    tree_output = os.getenv("TREE_OUTPUT")
    if not tree_output:
        raise ValueError("TREE_OUTPUT environment variable not set")
    if DEBUG:
        testtree_path = os.path.join(current_dir, "treeoutputtest.txt")
        write_to_file(testtree_path, tree_output)

    # Get relevant context files from LLM
    relevant_files: list[str] = get_relevant_context(client, zsh_diff_output, tree_output).parsed.context_files
    if DEBUG:
        write_to_file(os.path.join(current_dir, "relevantcontextfilestest.txt"), str(relevant_files))

    # Get diff analysis from LLM
    diff_analysis = get_diff_analysis(client, current_dir, zsh_diff_output, relevant_files)

    if DEBUG:
        diffparsertest_path = os.path.join(current_dir, "diffanalysistest.txt")
        write_to_file(diffparsertest_path, diff_analysis.text)

    # Generate implementations based on analysis
    generate_implementations(client, current_dir, diff_analysis)
    #implementations = generate_implementations(client, current_dir, diff_analysis)
    #funcgeneratortest_path = os.path.join(current_dir, "funcgeneratortest.txt")
    #write_to_file(funcgeneratortest_path, implementations.text)

if __name__ == "__main__":
    main()
