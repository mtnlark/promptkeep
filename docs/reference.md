# Command Reference

This page provides the command-line help text for PromptKeep.

## `promptkeep`

```text
Usage: python -m promptkeep.cli [OPTIONS] COMMAND [ARGS]...                                                
                                                                                                            
 PromptKeep - A CLI tool for managing and accessing your AI prompts                                         
                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                  │
│ --show-completion             Show completion for the current shell, to copy it or customize the         │
│                               installation.                                                              │
│ --help                        Show this message and exit.                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────╮
│ init   Initialize a new prompt vault.                                                                    │
│ add    Add a new prompt to your vault.                                                                   │
│ pick   Select a prompt and copy its content to clipboard.                                                │
│ edit   Edit an existing prompt in your vault.                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## `promptkeep init`

```text
Usage: python -m promptkeep.cli init [OPTIONS] [VAULT_PATH]                                                
                                                                                                            
 Initialize a new prompt vault.                                                                             
 This command creates a directory structure for storing prompts: - Creates the main vault directory -       
 Creates a 'Prompts' subdirectory - Adds an example prompt template                                         
 If the directory already exists, it will be overwritten.                                                   
 Args:     vault_path: Path where the vault should be created (defaults to ~/PromptVault)                   
                                                                                                            
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮
│   vault_path      [VAULT_PATH]  Path where your prompt vault will be created [default: ~/PromptVault]    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## `promptkeep add`

```text
Usage: python -m promptkeep.cli add [OPTIONS]                                                              
                                                                                                            
 Add a new prompt to your vault.                                                                            
 This command: 1. Creates a new markdown file with YAML front matter 2. Opens your default editor to write  
 the prompt content 3. Saves the file with a unique name based on title and timestamp                       
 Tags can be provided either as multiple --tag options or as a comma-separated list when prompted. These    
 tags make it easier to find and filter prompts later using the 'pick' and 'edit' commands.                 
 Usage:     1. Provide a title, description, and tags for your prompt     2. Your default text editor will  
 open to write the prompt content     3. Save and exit the editor to create the prompt file                 
 Examples:     promptkeep add --title "API Documentation" --tag coding --tag docs     promptkeep add        
 --title "Email Template" --description "Professional response" --vault /path/to/vault     promptkeep add   
 # Interactive prompts for all fields                                                                       
 Args:     title: The title of the prompt     description: Optional description of the prompt     tags:     
 Optional list of tags for categorizing the prompt     vault_path: Optional path to the prompt vault        
 Raises:     typer.Exit: If no vault exists or if user cancels the operation                                
                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --title        -t      TEXT  Title of the prompt [default: None] [required]                           │
│    --description  -d      TEXT  Description of the prompt                                                │
│    --tag                  TEXT  Tags for the prompt (can be specified multiple times)                    │
│    --vault        -v      TEXT  Path to the prompt vault (defaults to ~/PromptVault or PROMPTKEEP_VAULT  │
│                                 env var)                                                                 │
│                                 [default: None]                                                          │
│    --help                       Show this message and exit.                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## `promptkeep pick`

```text
Usage: python -m promptkeep.cli pick [OPTIONS]                                                             
                                                                                                            
 Select a prompt and copy its content to clipboard.                                                         
 This command provides an interactive selection interface that: 1. Lists all available prompts in the vault 
 2. Shows a preview of each prompt including:    - Title from YAML front matter    - Tags from YAML front   
 matter    - Full prompt content 3. Uses fzf for fuzzy finding and selection 4. Copies the selected         
 prompt's content to clipboard                                                                              
 You can filter prompts by tags using the --tag option. When multiple tags are specified, only prompts      
 containing ALL specified tags will be shown.                                                               
 Usage:     1. Run the command to see all prompts for selection     2. Use fuzzy search to filter prompts   
 by title or content     3. Use arrow keys to navigate and press Enter to select     4. The prompt content  
 will be automatically copied to your clipboard     5. Paste the content into any application (e.g.,        
 ChatGPT, email, document)                                                                                  
 Examples:     promptkeep pick                             # Select from all prompts     promptkeep pick    
 --tag job-search            # Select from prompts with tag "job-search"     promptkeep pick --tag coding   
 --tag python   # Select prompts with both "coding" and "python" tags     promptkeep pick --vault           
 /path/to/vault      # Specify custom vault location                                                        
 Args:     vault_path: Optional path to the prompt vault     tags: Optional list of tags to filter prompts  
 by      Raises:     typer.Exit: If no prompts are found, if selection is cancelled,                or if   
 fzf is not installed                                                                                       
                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --vault  -v      TEXT  Path to the prompt vault (defaults to ~/PromptVault or PROMPTKEEP_VAULT env var)  │
│                        [default: None]                                                                   │
│ --tag    -t      TEXT  Filter prompts by tag (can be specified multiple times) [default: None]           │
│ --help                 Show this message and exit.                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## `promptkeep edit`

```text
Usage: python -m promptkeep.cli edit [OPTIONS]                                                             
                                                                                                            
 Edit an existing prompt in your vault.                                                                     
 This command provides an interactive selection interface that: 1. Lists all available prompts in the vault 
 2. Shows a preview of each prompt including:    - Title from YAML front matter    - Tags from YAML front   
 matter    - Full prompt content 3. Uses fzf for fuzzy finding and selection 4. Opens the selected prompt   
 in your editor                                                                                             
 You can filter prompts by tags using the --tag option to quickly find the prompt you want to edit. When    
 multiple tags are specified, only prompts containing ALL specified tags will be shown.                     
 Usage:     1. Run the command to see all prompts for selection     2. Use fuzzy search to filter prompts   
 by title or content     3. Use arrow keys to navigate and press Enter to select     4. Edit the prompt in  
 your default text editor     5. Save and exit the editor to update the prompt                              
 Examples:     promptkeep edit                             # Edit any prompt     promptkeep edit --tag      
 job-search            # Edit prompts with tag "job-search"     promptkeep edit --tag python --tag ml       
 # Edit prompts with both "python" and "ml" tags     promptkeep edit --vault /path/to/vault      # Specify  
 custom vault location                                                                                      
 Args:     vault_path: Optional path to the prompt vault     tags: Optional list of tags to filter prompts  
 by      Raises:     typer.Exit: If no prompts are found, if selection is cancelled,                or if   
 fzf is not installed                                                                                       
                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --vault  -v      TEXT  Path to the prompt vault (defaults to ~/PromptVault or PROMPTKEEP_VAULT env var)  │
│                        [default: None]                                                                   │
│ --tag    -t      TEXT  Filter prompts by tag (can be specified multiple times) [default: None]           │
│ --help                 Show this message and exit.                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

