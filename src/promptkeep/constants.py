"""Constants used throughout PromptKeep.

This module centralizes magic strings and configuration values
to improve maintainability and reduce duplication.
"""

# Directory names
PROMPTS_DIR_NAME = "Prompts"

# Default paths
DEFAULT_VAULT_PATH = "~/PromptVault"

# File patterns
YAML_DELIMITER = "---"
PROMPT_FILE_EXTENSION = ".md"

# Environment variables
ENV_VAULT_PATH = "PROMPTKEEP_VAULT"
ENV_EDITOR = "EDITOR"
DEFAULT_EDITOR = "vim"

# Filename constraints
MAX_FILENAME_LENGTH = 100

# FZF preview script - extracts title, tags and content from prompt files
# The {} placeholder is substituted by fzf with the currently highlighted file
FZF_PREVIEW_SCRIPT = """awk '
    BEGIN { in_yaml=0; printed_header=0 }
    /^---$/ { in_yaml = !in_yaml; next }
    in_yaml {
        if ($1 == "title:") title = substr($0, 8)
        if ($1 == "tags:") { tags=1; next }
        if (tags && $1 == "-") tag_list = tag_list ", " substr($0, 3)
    }
    !in_yaml && !printed_header {
        gsub(/"/, "", title)
        sub(/, /, "", tag_list)
        print "Title: " title
        if (tag_list) print "Tags:  " tag_list
        print "----------------------------------------"
        printed_header=1
        next
    }
    !in_yaml { print }
' {}'"""
