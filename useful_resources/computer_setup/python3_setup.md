# Installing Python 3


## Why Python 3?

As you may have heard, starting [January 1, 2020][countdown] [Python 2.x is no
longer officially supported][eol_article].

Additionally, when using [Parsons][parsons], we use Python 3. Therefore, to make
collaboration, debugging and maintenance easier, we encourage that you install and
use Python 3 when writing scripts for TMC.


## Getting Started

There are a number of ways to [install Python 3][install_py3]. Before you
install it, check that what version you already have.

### Check Python Version

1. Open the **Terminal** app
2. Type `python --version`
  * If you see something like `Python 3.x.x` then you are all set.
    If not got to set 3
3. Type `python3 --version`
  * If you don't see any output then you need to install python 3.

### Install Python with Homebrew

1. Open the **Terminal** app on your Mac.
2. Type `xcode-select --install` and confirm the installation.
3. Type `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
  * You can check that brew installed by typing `brew doctor`
4. Type `brew install python3`
5. Check python version `python3 --version`


### Install Python with Installer

1. [Download][download_py] the latest python version
2. Run the installer
3. Check your **Applications** for the python app.


## Testing Code Locally

There a many ways to run code locally to make sure it works before submitting
it for review. For folks who are new to Python, we recommend using [Jupyter
Notebooks][jupyter] as it allows you to run blocks of code individually and to see
instant outputs.

[countdown]: https://pythonclock.org/
[eol_article]: https://www.anaconda.com/end-of-life-eol-for-python-2-7-is-coming-are-you-ready/
[parsons]: https://move-coop.github.io/parsons/html/index.html
[install_py3]: https://www.saintlad.com/install-python-3-on-mac/
[download_py]: https://www.python.org/downloads/
[jupyter]: https://jupyter.readthedocs.io/en/latest/install.html
