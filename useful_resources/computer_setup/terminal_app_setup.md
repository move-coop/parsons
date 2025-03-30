# Setting Up Your Terminal

MacOS only

## Overview

These are some ways to make your terminal app more informative.

## Create A .bash_profile File

### What is a .bash_profile file?

This is often referred to as a _configuration script_. It can contain variable
declarations, export variables, and commands to be executed when you start up
your Terminal[\*][ref1]. One common use case is store your API keys and tokens so
that you **never** need to hard-code credentials in your scripts. All Parsons
classes that require credentials allow you to set environment variables.

### Create a .bash_profile file

Using the Terminal:

1. Open the **Terminal** app 2. Type `echo # "hello bash_profile" >> ~/.bash_profile`

Using a text editor:

1. Open a text editor (e.g. Atom, Sublime)
1. Type `# hello bash_profile`
1. Save to `~/.bash_profile`

## Add Branch Name To Prompt

This makes it so that your bash prompt shows the current git branch you are
working on. For example, `MyName@Macintosh-2 My_Directory (git_branch) $`

Copy and paste the following code into your `.bash_profile` file.

```
# Git branch in prompt.
parse_git_branch() {
  git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}

export PS1="\u@\h \W\[\033[32m\]\$(parse_git_branch)\[\033[00m\] $ "
```

[ref1]: https://www.quora.com/What-is-bash_profile-and-what-is-its-use#__w2_wgb5qZxj32_link
