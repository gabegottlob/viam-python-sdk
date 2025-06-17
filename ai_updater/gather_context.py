"""
File to mess around with context gathering
"""

import os
from google import genai
from google.genai import types

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def main():
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

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_dir = os.path.dirname(current_dir)
    sdk_dir = os.path.join(project_root_dir, "src/viam")

    # Create a debug file
    debug_file_path = os.path.join(current_dir, "debug_context.txt")
    for (root, dirs, files) in os.walk(sdk_dir, topdown=True):
        if root == sdk_dir: #get rid of directories not needed for context
            dirs.remove("gen")
            dirs.remove("proto")
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')

        current_directory_relative = os.path.relpath(root, sdk_dir)
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


    string = ""

    with open(debug_file_path, 'w', encoding='utf-8') as debug_file:
        for category, content in context.items():
            string += content
            debug_file.write(content)

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    tokens = client.models.count_tokens(
        model="gemini-2.5-flash-preview-05-20",
        contents=string
    )
    print(f"Input tokens from context: {tokens}")

if __name__ == "__main__":
    main()
