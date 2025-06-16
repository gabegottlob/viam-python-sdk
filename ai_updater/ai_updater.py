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
    file_paths: list[str]  # List of file paths
    file_contents: list[str]  # List of corresponding file contents

def write_to_file(filepath: str, content: str) -> None:
    print(f"Writing to: {filepath}")
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Successfully wrote to: {filepath}")

def get_diff_analysis(client: genai.Client, diff_output: str) -> types.GenerateContentResponse:
    prompt = DIFF_PARSER_PROMPT.format(zsh_diff_output=diff_output)

    tokens = client.models.count_tokens(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt
    )
    print(f"Input tokens from first prompt: {tokens}")

    return client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction='''
            You are an expert in analyzing protobuf definitions and determining required implementations in a Viam robotics SDK.
            Your task is to assist developers in automating SDK updates. Be precise, meticulous, and follow all instructions exactly.
            ''',
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=NewFuncs
        )
    )

def generate_implementations(client: genai.Client, current_dir: str, diff_analysis: types.GenerateContentResponse):
    project_root_dir = os.path.dirname(current_dir) #this is hardcoded and prob should be made better

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

    #write_to_file(os.path.join(current_dir, "prompt2test.txt"), prompt)

    response2 = client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=GeneratedFiles
        )
    )

    parsed_response2: GeneratedFiles = response2.parsed
    if(len(parsed_response2.file_paths) == len(parsed_response2.file_contents)):
        for index, file_path in enumerate(parsed_response2.file_paths):
            write_to_file(os.path.join(current_dir, "test_output" + str(index) + ".txt"), parsed_response2.file_contents[index])
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

    # Write initial diff to file
    testdiff_path = os.path.join(current_dir, "testDiff.txt")
    write_to_file(testdiff_path, zsh_diff_output)

    # Get diff analysis
    diff_analysis = get_diff_analysis(client, zsh_diff_output)
    diffparsertest_path = os.path.join(current_dir, "diffparsertest.txt")
    write_to_file(diffparsertest_path, diff_analysis.text)

    # Generate implementations
    generate_implementations(client, current_dir, diff_analysis)
    #implementations = generate_implementations(client, current_dir, diff_analysis)
    #funcgeneratortest_path = os.path.join(current_dir, "funcgeneratortest.txt")
    #write_to_file(funcgeneratortest_path, implementations.text)

if __name__ == "__main__":
    main()
