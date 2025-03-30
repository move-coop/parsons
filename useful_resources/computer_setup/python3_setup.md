# Installing Python 3

## Why Python 3?

As you may have heard, starting [January 1, 2020][countdown] [Python 2.x is no
longer officially supported][eol_article].

Additionally, [Parsons] is only compatible with Python 3. So, in order to
use parsons, you need to have Python 3 installed.

## Getting Started

There are a number of ways to [install Python 3][install_py3]. Before you
install it, check what version, if any, you already have installed on your computer.

### Check Python Version

1. Open the **Terminal** app
1. Type `python --version`
   - If you see something like `Python 3.x.x` then you are all set.
     If not got to step 3
1. Type `python3 --version`
   - If you don't see any output then you need to install python 3.

### Install Python with Homebrew

MacOS/Linux only

1. Open the **Terminal** app on your Mac.
1. Type `xcode-select --install` and confirm the installation.
1. Type `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
   - You can check that brew installed by typing `brew doctor`
1. Type `brew install python3`
1. Check python version `python3 --version`

### Install Python with Installer

1. [Download][download_py] the latest python version
1. Run the installer
1. Check your **Applications** for the python app.

## Testing Code Locally

There a many ways to run code locally to make sure it works before submitting
it for review. For folks who are new to Python, we recommend using [Jupyter
Notebooks][jupyter] as it allows you to run blocks of code individually and to see
instant outputs.

[countdown]: https://pythonclock.org/
[download_py]: https://www.python.org/downloads/
[eol_article]: https://www.anaconda.com/end-of-life-eol-for-python-2-7-is-coming-are-you-ready/
[install_py3]: https://www.saintlad.com/install-python-3-on-mac/
[jupyter]: https://jupyter.readthedocs.io/en/latest/install.html
[parsons]: https://move-coop.github.io/parsons/html/index.html
