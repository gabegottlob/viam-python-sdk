#This zsh script is used to get the diff of the last automatic proto update
#!/usr/bin/env zsh
ZSH_DIFF_OUTPUT=$(git diff workflow/update-proto~1 workflow/update-proto -- ../src/viam/gen/component)
export ZSH_DIFF_OUTPUT
echo Diff output saved and exported to ZSH_DIFF_OUTPUT variable.
