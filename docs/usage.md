# Usage Guide

This guide focuses on how to use PromptKeep in everyday scenarios. For detailed technical information about commands and parameters, see the [Reference](reference.md) page.

## Getting Started

### Setting Up Your Vault

Before you can use PromptKeep, you need to create a prompt vault to store your prompts:

```bash
promptkeep init
```

This creates a vault in your home directory at `~/PromptVault`. You'll see a success message with next steps:

```
───────────────── Success ──────────────────
✅ Prompt vault created successfully at:
/Users/youruser/PromptVault

Next steps:
1. Add your prompts to the 'Prompts' directory
2. Use 'promptkeep add' to create new prompts
...
─────────────────────────────────────────────
```

If you want to keep your vault somewhere else, specify the path:

```bash
promptkeep init ~/Documents/MyPrompts
```

### Creating Your First Prompt

Now that you have a vault, let's add your first prompt:

1. Run the add command:
   ```bash
   promptkeep add
   ```

2. You'll be prompted for information:
   ```
   Enter a title for your prompt: Email Response Template
   Enter a description (optional): Professional response for client emails
   Enter tags separated by commas (optional): email, professional, client
   ```

3. Your default text editor will open. Add the prompt content below the YAML front matter:
   ```
   ---
   title: "Code Review Prompt"
   description: "Detailed code review analysis for pull requests"
   tags: ["coding", "review", "ai"]
   ---

   # Code Review Analysis

   Please review the following code and provide a comprehensive analysis:

   ```[LANGUAGE]
   [PASTE CODE HERE]
   ```

   Focus on these aspects:
   1. Code quality and best practices
   2. Potential bugs and edge cases
   3. Performance considerations
   4. Security vulnerabilities
   5. Readability and maintainability

   For each issue found:
   - Explain why it's problematic
   - Provide a suggested improvement
   - Include code examples where appropriate

   End with a summary of the main strengths and areas for improvement.
   ```

4. Save and close the editor. Your prompt is now saved in your vault!

## Working with Your Prompts

### Finding and Using Prompts

When you need to use a prompt:

1. Run the pick command:
   ```bash
   promptkeep pick
   ```

2. A fuzzy finder will appear showing all your prompts.

3. Start typing to search for a specific prompt. For example, type "email" to find your email templates.

4. Use arrow keys to navigate and press Enter to select a prompt.

5. The prompt is now copied to your clipboard! Paste it anywhere you need it.

### Organizing with Tags

Tags make it easier to organize and find your prompts:

1. When creating a prompt, add tags:
   ```bash
   promptkeep add --title "Meeting Notes" --tag meeting --tag notes
   ```

2. When searching for prompts, filter by tag:
   ```bash
   promptkeep pick --tag meeting
   ```

This will only show prompts with the "meeting" tag.

## Common Workflows

### Creating Effective AI Coding Assistants

1. Create specialized coding prompts for different scenarios:
   ```bash
   promptkeep add --title "Debugging Helper" --tag coding --tag debugging
   promptkeep add --title "Refactoring Guide" --tag coding --tag refactoring
   ```

2. When you encounter a coding challenge, find the right prompt:
   ```bash
   promptkeep pick --tag coding
   ```

3. Fill in the details with your specific code and context, then send to your AI assistant.

### Building a Knowledge Management System

1. Store prompts designed to help organize and retrieve information:
   ```bash
   promptkeep add --title "Concept Explainer" --tag learning --tag explanation
   promptkeep add --title "Research Summarizer" --tag research --tag summary
   ```

2. When studying a new topic or processing research papers:
   ```bash
   promptkeep pick --tag research
   ```

3. Combine with your source material and send to an AI assistant to generate organized notes or summaries.

### Creating Persona-Based AI Interactions

1. Define different AI personas for different types of feedback:
   ```bash
   promptkeep add --title "Technical Expert Persona" --tag persona --tag technical
   promptkeep add --title "Writing Coach Persona" --tag persona --tag writing
   ```

2. When you need specialized feedback, select the appropriate persona:
   ```bash
   promptkeep pick --tag persona
   ```

3. Start your AI conversation with the persona prompt, then continue with your specific questions or content.

## Maintaining Your Prompt Library

### Organizing Your Prompts

Use tags consistently to create an organized system. Consider a tagging structure like:

- Content type: `email`, `code`, `documentation`
- Audience: `client`, `team`, `public`
- Project: `projectA`, `projectB`
- Purpose: `template`, `reference`, `guide`

## Editing Prompts

To edit an existing prompt, use the `edit` command:

```bash
promptkeep edit
```

This will open a fuzzy finder to select the prompt you want to edit. You can filter prompts by tags using the `--tag` or `-t` option:

```bash
promptkeep edit --tag python --tag ai  # Edit prompts tagged with both "python" and "ai"
promptkeep edit -t coding             # Edit prompts tagged with "coding"
```

Once you select a prompt, it will open in your default text editor. Make your changes and save the file to update the prompt.

## Troubleshooting

### "Vault not found"

If you see this error, your prompt vault can't be located. Try:

1. Specify the vault path explicitly:
   ```bash
   promptkeep pick --vault ~/path/to/your/vault
   ```

2. Or set the environment variable:
   ```bash
   export PROMPTKEEP_VAULT=~/path/to/your/vault
   promptkeep pick
   ```

### "Editor exited with non-zero code"

This means there was a problem with your text editor:

1. Check that your EDITOR environment variable is set correctly:
   ```bash
   echo $EDITOR
   ```

2. Try setting it explicitly:
   ```bash
   export EDITOR=nano  # or vim, code, etc.
   ```

## Tips and Tricks

- **Template Placeholders**: Use consistent placeholder text like `[Client Name]` in your prompts to quickly identify what needs to be replaced.

- **Keyboard Navigation**: In the fuzzy finder, use Ctrl+P/Ctrl+N (or up/down arrows) to navigate without using the mouse.

- **Quick Filtering**: Add a dedicated tag like `favorite` or `frequent` to prompts you use often, then use `promptkeep pick --tag favorite` for quick access.

- **Multi-tag Filtering**: Combine tags to narrow down your search: `promptkeep pick --tag email --tag client`. 