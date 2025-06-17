import os
from google import genai
from google.genai import types
from pydantic import BaseModel

from prompts.diffparser_prompt import DIFF_PARSER_PROMPT
from prompts.funcgenerator_prompt import FUNCTION_GENERATOR_P1, FUNCTION_GENERATOR_P2

class NewFuncs(BaseModel):
    files_to_update: list[str]
    implementation_details: list[str]

class GeneratedFiles(BaseModel):
    file_paths: list[str]
    file_contents: list[str]

def write_to_file(filepath: str, content: str) -> None:
    print(f"Writing to: {filepath}")
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Successfully wrote to: {filepath}")

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def gather_context(current_dir: str, context: dict) -> None:
    project_root_dir = os.path.dirname(current_dir)
    sdk_dir = os.path.join(project_root_dir, "src/viam")

    for (root, dirs, files) in os.walk(sdk_dir, topdown=True):
        if root == sdk_dir: #get rid of directories not needed for context
            dirs.remove("gen")
            dirs.remove("proto")
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')

        current_directory_relative = os.path.relpath(root, sdk_dir) #this is a mess u should prob redo sometime
        current_category = None
        if current_directory_relative == ".":
            current_category = "root"
        else:
            current_category = current_directory_relative.split(os.sep)[0]

        # Write directory information to context
        context[current_category] += f"Directory: {os.path.relpath(root, project_root_dir)}\n"
        context[current_category] += f"Subdirectories: {dirs}\n"
        context[current_category] += f"Files: {files}\n"

        for file in files:
            file_path = os.path.join(root, file)
            sdk_file_path = os.path.relpath(file_path, project_root_dir)
            file_content = read_file_content(file_path)

            # Update context dictionary
            context[current_category] += f"File: {sdk_file_path}\n"
            context[current_category] += f"Content: {file_content}\n"
            context[current_category] += "--------------------------------\n"


def get_diff_analysis(client: genai.Client, current_dir: str, diff_output: str) -> types.GenerateContentResponse:
    context = {
        "root" : "",
        "components" : "",
        "resource" : "",
        "robot" : "",
        "rpc" : "",
        "services" : "",
        "module" : "",
        "media" : "",
        "app" : "",
    }

    gather_context(current_dir, context)

    prompt = DIFF_PARSER_PROMPT.format(root_context=context["root"], components_context=context["components"],
                                       resource_context=context["resource"], robot_context=context["robot"],
                                       rpc_context=context["rpc"], services_context=context["services"],
                                       module_context=context["module"], media_context=context["media"],
                                       app_context=context["app"], zsh_diff_output=diff_output)

    tokens = client.models.count_tokens(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt
    )
    print(f"Input tokens from first prompt: {tokens}")

    return client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=NewFuncs
        )
    )

def generate_implementations(client: genai.Client, current_dir: str, diff_analysis: types.GenerateContentResponse):
    project_root_dir = os.path.dirname(current_dir)

    parsed_response: NewFuncs = diff_analysis.parsed

    # Start with the first part of the prompt
    prompt = FUNCTION_GENERATOR_P1.format(implementation_details=parsed_response.implementation_details)

    # Add existing files to the prompt
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

    tokens = client.models.count_tokens(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt
    )
    print(f"Input tokens from second prompt: {tokens}")

    response2 = client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=GeneratedFiles
        )
    )

    # Write the responses to files
    parsed_response2: GeneratedFiles = response2.parsed
    if(len(parsed_response2.file_paths) == len(parsed_response2.file_contents)):
        for index, file_path in enumerate(parsed_response2.file_paths):
            # Write to test output in ai_updater directory
            write_to_file(os.path.join(current_dir, "test_output" + str(index) + ".txt"), parsed_response2.file_contents[index])

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
    # Get the absolute path of the current and parent directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Initialize Gemini API Client
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    # Get diff output from environment
    zsh_diff_output = os.getenv("ZSH_DIFF_OUTPUT")
    if not zsh_diff_output:
        raise ValueError("ZSH_DIFF_OUTPUT environment variable not set")

    # Write initial diff to file (only for debugging)
    testdiff_path = os.path.join(current_dir, "testDiff.txt")
    write_to_file(testdiff_path, zsh_diff_output)

    # Get diff analysis
    diff_analysis = get_diff_analysis(client, current_dir, zsh_diff_output)
    diffparsertest_path = os.path.join(current_dir, "diffparsertest.txt")
    write_to_file(diffparsertest_path, diff_analysis.text)

    # Generate implementations
    generate_implementations(client, current_dir, diff_analysis)
    #implementations = generate_implementations(client, current_dir, diff_analysis)
    #funcgeneratortest_path = os.path.join(current_dir, "funcgeneratortest.txt")
    #write_to_file(funcgeneratortest_path, implementations.text)

if __name__ == "__main__":
    main()
