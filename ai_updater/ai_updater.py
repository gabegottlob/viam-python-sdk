import os
from google import genai
from google.genai import types
from pydantic import BaseModel
import sys

from prompts.diffparser_prompt import DIFF_PARSER_P1
from prompts.funcgenerator_prompt import FUNCTION_GENERATOR_P1, FUNCTION_GENERATOR_P2
from prompts.getrelevantdirs_prompt import GET_RELEVANT_DIRS_P1

# Configuration flags
DEBUG = False
AI_ENABLED = False

class ContextDirs(BaseModel):
    """Model for storing the directories that should be included as context."""
    context_dirs: list[str]

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

def get_relevant_dirs(client: genai.Client, zsh_diff_output: str, tree_output: str) -> types.GenerateContentResponse:
    prompt = GET_RELEVANT_DIRS_P1.format(tree_structure=tree_output, zsh_diff_output=zsh_diff_output)
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
                response_schema=ContextDirs
            )
        )
    return response

def gather_context(project_root_dir_abs: str, context_dir_rel: str, context: dict, relevant_dirs: list[str]) -> None:
    """Scrape the provided directory and gather code context for LLM processing.

    Walks through the directory structure, ignoring specified directories,
    and collects file contents organized by category.

    Args:
        project_root_dir_abs: Absolute path to the project root
        context_dir_rel: Relative path to the context directory from project root
        context: Dictionary to store gathered context by category
        relevant_dirs: List of directory names to include
    """
    context_dir_abs = os.path.join(project_root_dir_abs, context_dir_rel)
    debug_lines = []
    for (root, dirs, files) in os.walk(context_dir_abs, topdown=True):
        # Remove directories to ignore
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")

        for dir in dirs:
            if dir not in relevant_dirs:
                dirs.remove(dir)

        # Determine the category based on directory structure
        current_directory_relative = os.path.relpath(root, context_dir_abs)
        current_category = None
        if current_directory_relative == ".":
            current_category = "root"
        else:
            current_category = current_directory_relative.split(os.sep)[0]

        # Add directory information to context
        dir_info = f"Directory: {os.path.relpath(root, project_root_dir_abs)}\n"
        dir_info += f"Relevant subdirectories: {dirs}\n"
        dir_info += f"Files: {files}\n"
        context[current_category] += dir_info
        debug_lines.append(f"=== Category: {current_category} ===\n" + dir_info)

        # Process each file in the directory
        for file in files:
            file_path = os.path.join(root, file)
            sdk_file_path = os.path.relpath(file_path, project_root_dir_abs)
            file_content = read_file_content(file_path)

            file_info = f"File: {sdk_file_path}\nContent: \n{file_content}\n--------------------------------\n"
            context[current_category] += file_info
            debug_lines.append(file_info)

    # Write debug output if enabled
    if DEBUG:
        debug_file_path = os.path.join(os.getcwd(), "gathercontexttest.txt")
        write_to_file(debug_file_path, "\n".join(debug_lines))


def get_diff_analysis(client: genai.Client, current_dir: str, diff_output: str, relevant_dirs: list[str]) -> types.GenerateContentResponse:
    """Analyze git diff using LLM to identify required code changes.

    Args:
        client: Gemini API client
        current_dir: Current directory path
        diff_output: Git diff output as string

    Returns:
        GenerateContentResponse: LLM response containing analysis of needed changes
    """
    # Initialize context dictionary with empty categories
    context = {
        "root" : "",
        "components" : "",
        "proto" : "",
        "gen" : "",
        "resource" : "",
        "robot" : "",
        "rpc" : "",
        "services" : "",
        "module" : "",
        "media" : "",
        "app" : "",
    }

    # Gather code context from the project
    gather_context(project_root_dir_abs=os.path.dirname(current_dir), context_dir_rel="src/viam", context=context, relevant_dirs=relevant_dirs)

    # Format the prompt with gathered context
    prompt = DIFF_PARSER_P1.format(root_context=context["root"], components_context=context["components"],
                                       proto_context=context["proto"], gen_context=context["gen"],
                                       resource_context=context["resource"], robot_context=context["robot"],
                                       rpc_context=context["rpc"], services_context=context["services"],
                                       module_context=context["module"], media_context=context["media"],
                                       app_context=context["app"], zsh_diff_output=diff_output)

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

    # Get relevant directories from LLM
    relevant_dirs: list[str] = get_relevant_dirs(client, zsh_diff_output, tree_output).parsed.context_dirs

    # Get diff analysis from LLM
    diff_analysis = get_diff_analysis(client, current_dir, zsh_diff_output, relevant_dirs)

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
