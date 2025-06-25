import os
from google import genai
from google.genai import types
from pydantic import BaseModel
import argparse
import subprocess

from prompts.diffparser_prompt import DIFF_PARSER_P1
from prompts.funcgenerator_prompt import FUNCTION_GENERATOR_P1, FUNCTION_GENERATOR_P2
from prompts.getrelevantcontext_prompt import GET_RELEVANT_CONTEXT_P1

class ContextFiles(BaseModel):
    """Model for storing the files that should be included as context."""
    file_paths: list[str]
    explanation: list[str]

class RequiredChanges(BaseModel):
    """Model for storing analysis of code needed based on diff."""
    files_to_update: list[str]
    implementation_details: list[str]

class GeneratedFiles(BaseModel):
    """Model for storing AI-generated file content."""
    file_paths: list[str]
    file_contents: list[str]

class AIUpdater:
    """Class for updating SDK code based on proto changes using AI."""

    def __init__(self, args, api_key=""):
        """Initialize the AIUpdater.

        Args:
            args: Command line arguments
            api_key (str): Google API key. If None, will use GOOGLE_API_KEY env var
        """
        self.args = args

        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        if args.test:
            self.sdk_root_dir = args.test
        else:
            self.sdk_root_dir = os.path.dirname(self.current_dir)


        # Initialize the Gemini client
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set and no API key provided")
        self.client = genai.Client(api_key=api_key)

    def write_to_file(self, filepath: str, content: str) -> None:
        """Write content to a file at the specified path.

        Args:
            filepath: Path to the file to write
            content: Content to write to the file
        """
        print(f"Writing to: {filepath}")
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Successfully wrote to: {filepath} \n")

    def read_file_content(self, file_path) -> str:
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

    def get_relevant_context(self, git_diff_output: str) -> types.GenerateContentResponse:
        """Get relevant context files for analysis.

        Args:
            git_diff_output (str): Git diff output

        Returns:
            GenerateContentResponse: LLM response containing relevant files
        """
        sdk_tree_output = subprocess.check_output(["tree", os.path.join("src", "viam")], text=True, cwd=self.sdk_root_dir)
        tests_tree_output = subprocess.check_output(["tree", "tests"], text=True, cwd=self.sdk_root_dir)

        prompt = GET_RELEVANT_CONTEXT_P1.format(
            sdk_tree_structure=sdk_tree_output,
            tests_tree_structure=tests_tree_output,
            git_diff_output=git_diff_output
        )
        tokens = self.client.models.count_tokens(model="gemini-2.5-pro", contents=prompt)
        print(f"Input tokens from getrelevantdirs_prompt: {tokens}\n")

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=ContextFiles,
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
                system_instruction="""You are the first stage in an AI pipeline for updating SDK code.
                Your role is to act as an intelligent context selector. Given a git diff and SDK directory structures,
                identify and output only the most relevant implementation and test files that are directly impacted or
                provide crucial analogous examples. Be thorough but concise; the goal is to provide sufficient,
                focused context."""
            )
        )
        return response

    def gather_context_files(self, relevant_files: list[str]) -> str:
        """Gather context from specific files in the project.

        Args:
            relevant_files (list[str]): List of file paths to gather context from

        Returns:
            str: Concatenated content of all relevant files
        """
        context_str = ""
        for file in relevant_files:
            file_path = os.path.join(self.sdk_root_dir, file)
            file_content = self.read_file_content(file_path)
            file_info = f"File: {file}\nContent: \n{file_content}\n--------------------------------\n"
            context_str += file_info
        return context_str

    def get_diff_analysis(self, git_diff_output: str, relevant_files: list[str]) -> types.GenerateContentResponse:
        """Analyze git diff using LLM to identify required code changes.

        Args:
            git_diff_output: Git diff output as string
            relevant_files: List of relevant file paths for context

        Returns:
            GenerateContentResponse: LLM response containing analysis of needed changes
        """
        # Gather code context from the project
        relevant_context = self.gather_context_files(relevant_files=relevant_files)
        if self.args.debug:
            debug_file_path = os.path.join(self.current_dir, "relevant_context.txt")
            self.write_to_file(debug_file_path, relevant_context)

        # Format the prompt with gathered context
        prompt = DIFF_PARSER_P1.format(selected_context_files=relevant_context, git_diff_output=git_diff_output)

        # Count tokens for logging
        tokens = self.client.models.count_tokens(model="gemini-2.5-pro", contents=prompt)
        print(f"Input tokens from diffparser_prompt: {tokens}\n")

        # Generate content if AI is enabled, otherwise return empty response
        return self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=RequiredChanges,
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
                system_instruction="""You are the second stage in an AI pipeline for updating SDK code.
                Your role is to act as a highly precise code change analyst. Given a git diff and selected relevant code context,
                your task is to accurately identify *only* the necessary code modifications and generate extremely detailed,
                unambiguous implementation instructions for the next AI stage. Focus solely on the required changes;
                do not invent or suggest extraneous modifications. Assume the next stage has no context of the existing codebase
                and will simply be following your instructions."""
            )
        )

    def generate_implementations(self, diff_analysis: types.GenerateContentResponse):
        """Generate implementation code based on diff analysis.

        Args:
            diff_analysis: LLM response from diff analysis
        """
        # Parse the response from diff analysis
        parsed_response: RequiredChanges = diff_analysis.parsed

        # Start with the first part of the prompt
        prompt = FUNCTION_GENERATOR_P1.format(implementation_details=parsed_response.implementation_details)

        # Add existing files content to the prompt
        existing_files_text = "\n=== EXISTING FILES ===\n"
        for file_path in parsed_response.files_to_update:
            try:
                with open(os.path.join(self.sdk_root_dir, file_path), 'r') as f:
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
        tokens = self.client.models.count_tokens(model="gemini-2.5-flash-lite-preview-06-17", contents=prompt)
        print(f"Input tokens from funcgenerator_prompt: {tokens} \n")

        # Generate and write files if AI is enabled
        if not self.args.noai:
            response2 = self.client.models.generate_content(
                model="gemini-2.5-flash-lite-preview-06-17",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema=GeneratedFiles,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    system_instruction='''You are the third stage in an AI pipeline designed to update the Viam robotics SDK. Your role is to act as an expert Python developer.
                    You will receive specific implementation details from a previous AI stage and the full content of existing SDK files.
                    Your task is to regenerate the *complete* content of these files, integrating only the necessary new methods or edits as instructed.
                    It is CRITICAL that you preserve the exact original functionality, as well as ALL formatting, including newlines, indentation,
                    and whitespace, to ensure the code is perfectly readable and functional.
                    Your output for each file must be the complete, valid, and perfectly formatted Python code (as well as the filepath of the file)'''
                )
                )

            # Write the generated content to files
            parsed_response2: GeneratedFiles = response2.parsed
            if self.args.debug:
                self.write_to_file(os.path.join(self.current_dir, "generatedfilestest.txt"), response2.text)
            if(len(parsed_response2.file_paths) != len(parsed_response2.file_contents)):
                print("ERROR: AI OUTPUT A DIFFERENT NUMBER OF FILENAMES THAN GENERATED FILE CONTENTS")
                return

            for index, file_path in enumerate(parsed_response2.file_paths):
                # Output AI generated files
                original_file_dir = os.path.dirname(os.path.join(self.sdk_root_dir, file_path))
                original_filename = os.path.basename(file_path)
                filename_without_ext, file_ext = os.path.splitext(original_filename)
                if self.args.test:
                    ai_filename = f"{filename_without_ext}{file_ext}"
                    dir_structure = os.path.relpath(original_file_dir, self.sdk_root_dir)
                    ai_generated_dir = os.path.join(os.path.dirname(self.sdk_root_dir), "ai_generated", dir_structure)
                    os.makedirs(ai_generated_dir, exist_ok=True)
                    ai_file_path = os.path.join(ai_generated_dir, ai_filename)
                else:
                    ai_filename = f"{filename_without_ext}ai{file_ext}"
                    ai_file_path = os.path.join(original_file_dir, ai_filename)
                self.write_to_file(ai_file_path, parsed_response2.file_contents[index])

    def run(self):
        """Main execution method for the AI updater."""
        # Get diff and output (and write to file for debugging)
        # Note: the way I am currently doing git diff excludes the _pb2.py files because from what I can tell they are not useful as LLM context
        git_diff_dir = os.path.join(self.sdk_root_dir, "src", "viam", "gen")
        if self.args.test:
            scenario_dir = os.path.dirname(self.sdk_root_dir)
            # Check if specific proto diff file was specified for testing reasons
            if os.path.exists(os.path.join(scenario_dir, "proto_diff.txt")):
                with open(os.path.join(scenario_dir, "proto_diff.txt"), "r") as f:
                    git_diff_output = f.read()
            else:
                git_diff_output = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD", "--", git_diff_dir, ":!*_pb2.py"],
                                                        text=True,
                                                        cwd=self.sdk_root_dir)
        else:
            git_diff_output = subprocess.check_output(["git", "diff", "workflow/update-proto~1", "workflow/update-proto", "--", git_diff_dir, ":!*_pb2.py"],
                                                  text=True,
                                                  cwd=self.sdk_root_dir)
        if self.args.debug:
            testdiff_path = os.path.join(self.current_dir, "gitdifftest.txt")
            self.write_to_file(testdiff_path, git_diff_output)

        # Get relevant context files from LLM
        relevant_context = self.get_relevant_context(git_diff_output)
        if self.args.debug:
            self.write_to_file(os.path.join(self.current_dir, "relevantcontextfilestest.txt"), str(relevant_context.text))

        # Get diff analysis from LLM
        diff_analysis = self.get_diff_analysis(git_diff_output, relevant_context.parsed.file_paths)

        if self.args.debug:
            diffparsertest_path = os.path.join(self.current_dir, "diffanalysistest.txt")
            self.write_to_file(diffparsertest_path, diff_analysis.text)

        # Generate implementations based on analysis
        self.generate_implementations(diff_analysis)


def main():
    """Main entry point for the AI updater script."""
    parser = argparse.ArgumentParser(description="Viam SDK AI Updater")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode to print various helpful files")
    parser.add_argument("--noai", action="store_true", help="Disable AI (for testing)")
    parser.add_argument("--test", type=str, help="Enable when running tests. Supply path to root directory of desired test repo")
    args = parser.parse_args()

    # Create and run the updater
    updater = AIUpdater(args=args)
    updater.run()


if __name__ == "__main__":
    main()
