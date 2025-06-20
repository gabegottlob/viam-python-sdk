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
THE FILES YOU ARE EDITING WILL BE REINSERTED INTO THE CODEBASE AND MUST MAINTAIN THEIR EXACT ORIGINAL FUNCTIONALITY.
THIS IS VERY IMPORTANT.

CRITICAL FORMATTING INSTRUCTIONS:
1. MAINTAIN PROPER CODE FORMATTING with appropriate indentation and newlines.
2. DO NOT OUTPUT CODE AS A SINGLE LINE - preserve all line breaks.
3. DO NOT ESCAPE NEWLINES in your output - use actual newlines, not the string "\n".
4. ENSURE PROPER INDENTATION is preserved exactly as in the original files.
5. MAINTAIN CONSISTENT LINE ENDINGS throughout each file.

For each file, provide that files filepath (so it can be reinserted into the existing codebase), as well as the newly generated contents.

Your output should:
- Follow the same patterns and conventions as the examples and original files
- Maintain all existing functionality while adding new methods
- Include all necessary imports in the relevant file

ADDITIONAL TASK:
Based on the changes you made, the testing suite in the SDK will also need to be updated. I will
provide you with the entirety of the current tests folder, both for context and so you can analyze what modifications need to
be made. The discretion for what needs to be added is up to you, but follow the existing patterns and conventions.
Here is the current testing suite:
{testing_suite}

Task Review:
For each testing file that needs to be modified, regenerate the complete file contents including your edits.
WHEN REGENERATING THE FILES, ONLY ADD NEWLY CREATED METHODS OR  EDITS AS IS ABSOLUTELY NECESSARY.
DO NOT MODIFY THE EXISTING FILES IN ANY UNNECESSARY WAYS.
THE FILES YOU ARE EDITING WILL BE REINSERTED INTO THE CODEBASE AND MUST MAINTAIN THEIR EXACT ORIGINAL FUNCTIONALITY.
THIS IS VERY IMPORTANT.

For each modified testing file, provide that files filepath (so it can be reinserted into the existing codebase), as well as the newly generated contents.
If no changes are needed, you do not need to return anything for this task.

ENSURE that each file_contents entry contains properly formatted code with actual newlines, not escaped newlines.
'''
