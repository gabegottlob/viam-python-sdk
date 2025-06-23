"""Prompt for generating function implementations."""

FUNCTION_GENERATOR_P1 = '''
You are an expert Python developer implementing components for the Viam robotics SDK. You need to implement the following new functionality:

{implementation_details}

I will now give you the existing files from the codebase that you need to add your new methods or edits to:
'''

FUNCTION_GENERATOR_P2 = '''
Task Review:
For each file that needs to be modified, regenerate the complete file contents including your edits.
WHEN REGENERATING THE FILES, ONLY ADD NEWLY CREATED METHODS OR NECESSARY EDITS AS INSTRUCTED.
DO NOT MODIFY THE EXISTING FILES IN ANY UNNECESSARY WAYS.
THE FILES YOU ARE EDITING WILL BE REINSERTED INTO THE CODEBASE AND MUST MAINTAIN THEIR EXACT ORIGINAL FUNCTIONALITY AND FORMATTING.
THIS IS VERY IMPORTANT.

For each file, provide that files filepath (so it can be reinserted into the existing codebase), as well as the newly generated contents.

Your output should:
- Follow the same patterns and conventions as the examples and original files
- Maintain all existing functionality while adding new changes

Task Review:
For each file that needs to be modified, regenerate the complete file contents including your edits.
WHEN REGENERATING THE FILES, ONLY ADD NEWLY CREATED METHODS OR EDITS AS IS ABSOLUTELY NECESSARY.
DO NOT MODIFY THE EXISTING FILES IN ANY UNNECESSARY WAYS.
THE FILES YOU ARE EDITING WILL BE REINSERTED INTO THE CODEBASE AND MUST MAINTAIN THEIR EXACT ORIGINAL FUNCTIONALITY AND FORMATTING.
THIS IS VERY IMPORTANT.
'''
