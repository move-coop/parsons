# Using Git

## What is Git?

Git is a tool for versioning and version control. In other words, you can track
changes over time for files in a project. Git works by saving snapshots of your
project after changes are "committed".

**Note:** Not to be confused with GitHub which is a vendor for hosting code.

## Basic Usage

To check that you have git install type `git --version` into your terminal. To
run git commands, the command must be preceded by `git`. See the
examples below.

| Command    | Description                                                                                                                                              | Example                                               |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `init`     | Initialize git in the current folder.                                                                                                                    | `git init`                                            |
| `clone`    | Copy the code from a remote host and initialize git.                                                                                                     | `git clone https://github.com/move-coop/parsons.git`  |
| `pull`     | Get all the changes from the remote host.                                                                                                                | `git pull`                                            |
| `branch`   | List all the branches.                                                                                                                                   | `git branch`                                          |
| `checkout` | Start working on a specific branch. Adding the `-b` creates the branch.                                                                                  | `git checkout master` or `git checkout -d new-branch` |
| `status`   | See what files you’re tracking/not tracking, have been modified and or are ready to commit.                                                              | `git status`                                          |
| `add`      | Add a file as ready to be committed aka stage a file.                                                                                                    | `git add modified_file.txt`                           |
| `commit`   | Save all the changes that have been added (staged). If you exclude `-m` and the message, your default terminal editor opens up for you to add a message. | `git commit -m "My commit message"`                   |
| `push`     | Send the changes and change history to the remote host.                                                                                                  | `git push`                                            |

## Sample Workflow

**Prerequisite:** A project that has been initialized with git and has a remote
host.

1. Get any changes from the remote host. `git pull`
1. Switch to the branch you're working on. `git checkout my-branch`
1. Make and save changes (as many time as necessary).
1. Make a change.
1. Stage the file. `git add modified_file.txt`
1. Commit the changes. `git commit -m "Made changes."`
1. Push your changes to the remote host. `git push`
1. Change back to the master branch. `git checkout master`

## Tips

- Before starting to work, remember to `git pull` to get any changes made from
  the remote host.
- When switching to other work, remember to `git commit` and `git push` your
  changes.

## Additional Resources

- [Git and GitHub at TMC](https://docs.google.com/presentation/d/1uLMlWmFaSAhLRbPLVGukt0CiJvJdqY83fgfSoEThcfM/preview?slide=id.g3cde414e0d_0_0)
- [Small Group Git Discussion](https://docs.google.com/document/d/1LH0ZqPOCtw6ukzlWPEENLOCBlqZSLdgQmMeyq4MeP18/preview)
