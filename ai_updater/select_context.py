"""
File to mess around with having AI choose what context to use.
Idea is to provide the AI with the git diff file and the directory structure of the project
and have it choose the most relevant directories to use as context to reduce tokens/unnecessary context.
"""

import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from prompts.gathercontext_prompt import GATHER_CONTEXT_P1

class ContextDirs(BaseModel):
    """Model for storing the directories that should be included as context."""
    context_dirs: list[str]

def main():
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    zsh_diff_output = os.getenv("ZSH_DIFF_OUTPUT")
    if not zsh_diff_output:
        raise ValueError("ZSH_DIFF_OUTPUT environment variable not set")
    tree_output = os.getenv("TREE_OUTPUT")
    if not tree_output:
        raise ValueError("TREE_OUTPUT environment variable not set")
    prompt = GATHER_CONTEXT_P1.format(tree_structure=tree_output, zsh_diff_output=zsh_diff_output)
    response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=ContextDirs
            )
        )
    print(response.text)

if __name__ == "__main__":
    main()
