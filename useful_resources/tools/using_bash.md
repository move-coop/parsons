# Using Bash

Bash is the program that runs in the Mac Terminal App. Here are some common
commands you may want to know. There are also many other resources and "cheat
sheets" available online.

## Basic Usage

| Command | Description                                                                | Example                                                                                      |
| ------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `pwd`   | Print the path to where you are                                            | `pwd`                                                                                        |
| `ls`    | List the files in the current folder                                       | `ls`                                                                                         |
| `cd`    | Change to a different folder. Without a path it changes to the home folder | `cd` or `cd subfolder/`                                                                      |
| `cat`   | Print the contents of a file                                               | `cat some_file.txt`                                                                          |
| `touch` | Create a file                                                              | `touch new_file.txt`                                                                         |
| `mkdir` | Create a new folder                                                        | `mkdir new_folder/`                                                                          |
| `mv`    | Move a file. Can also be used to rename a file                             | `mv old_folder/file.txt new_folder/file.txt` or `mv folder/file.txt folder/file_renamed.txt` |
| `cp`    | Copy a file                                                                | `cp folder/original.txt folder2/copied_file.txt`                                             |
| `rm`    | Delete a file. **Note:** this cannot be undone.                            | `rm file_to_delete.txt`                                                                      |
| `clear` | Clear the terminal window. You can still scroll up to view previous output | `clear`                                                                                      |

## Advanced Usage

| Command | Description                                     | Example                                                                            |
| ------- | ----------------------------------------------- | ---------------------------------------------------------------------------------- |
| `man`   | Display the manual pages for a command.         | `man ls`                                                                           |
| `wc`    | Count the characters, words or lines in a file. | `wc -m count_characters.txt` or `wc -w count_words.txt` or `wc -l count_lines.txt` |

## Additional Resources

- [Mac Terminal Cheat Sheet](https://gist.github.com/poopsplat/7195274)
- [Bash Cheat Sheet](https://github.com/LeCoupa/awesome-cheatsheets/blob/master/languages/bash.sh)
