you are (or were) given a long command, which should be saved into a file for reuse or future inspection. By default, save the current command, UNLESS explicitly requested otherwise (for example, `previous command` or `previous task`)

# Guidelines for Saving Commands
- Save the command into a file named `task-<what-to-do>.md` in the `context/tasks/auto-save/` directory.
- Break the command into bullet points for clarity.
- Be concise and clear in the description.
- If the command is referencing other files or directories, save their original paths in the file
  - If the paths are given as relative paths, save them as they are, DO NOT convert them to absolute paths.
  - DO NOT expand them into contents, UNLESS explicitly requested.
- The command does not include this file, so DO NOT save this file in the command.