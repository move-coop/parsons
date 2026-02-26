===========================
Getting Set Up With Parsons
===========================

This training guide will walk you through setting up Parsons on your computer. It provides in-depth explanations of each of the tools we recommend you use, including the command line, virtual environments, and git/version control. No prior experience should be necessary to follow this guide.

You can suggest improvements to this guide or request additional guides by filing an issue in our issue tracker or telling us in Slack. To get added to our Slack, email us at *engineering@movementcooperative.org*.

****************************************
Step 1: Open Up a Command Line Interface
****************************************

Command line interfaces let you do a lot of different things on your computer, including installing and running programs and navigating the directory structure of your computer.

On Macs/Linux the default command line interface is called a **Terminal** and on Windows it is called the **Command Prompt**. Command line interfaces are also sometimes called *shells*. Look for this program on your computer and open it up.

The commands you can use in the command line differ somewhat dependning on whether you're using Mac/Linux or windows.

**Mac/Linux**:

* You can use ``pwd`` (“print working directory”) to figure out where you currently are.
* To move around, use ``cd`` (for example ``cd ..`` means "go up one directory" or ``cd my_folder`` which means "go into my_folder").
* Use ``ls`` to list all the files and folders in your current directory.
* A `Mac/Linux command line cheat sheet <https://www.guru99.com/linux-commands-cheat-sheet.html>`_ can help you keep track of which commands are which.

**Windows**:

* You can use ``cd`` to figure out where you currently are.
* To move around, use ``cd`` (for example ``cd ..`` means "go up one directory" or ``cd my_folder`` which means "go into my_folder").
* Use ``dir`` to list all the files and folders in a directory.
* A `Windows command line cheat sheet <http://www.cs.columbia.edu/~sedwards/classes/2017/1102-spring/Command%20Prompt%20Cheatsheet.pdf>`_ can help you keep track of which commands are which.

You do not have to type everything on the command line out by hand. You can auto-complete the names of files/folders in your current directory by tapping the tab key. On Mac/Linux you can also tab-complete installed programs. And you can access previous commands via the up and down arrows. Save your hands! Learn these tricks.

***************************************
Step 2: Set Up Your Virtual Environment
***************************************

Normally, tools like `pip <https://pip.pypa.io/en/stable/>`_ install Python libraries directly to your system. When your Python programs run, they look for the libraries they depend upon in your system. But this can cause problems when different programs need different versions of the same library.

To handle this issue, we recommend you use virtual environments to install Parsons. Virtual environments allow you to install libraries into an isolated environment specific to a project. That way you can use different versions of the same libraries for different projects.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Mac/Linux Virtual Environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before getting started, check which version of Python you’re running by typing ``python --version`` in your command line. Python 3.4+ includes a virtual environment manager called `venv <https://docs.python.org/3/library/venv.html>`_.  If your version is lower than Python 3.4, you'll have to install a virtual environment manager like `virtualenv <https://virtualenv.pypa.io/en/latest/>`_ if you haven't already. You can do this by typing ``pip install virtualenv`` in the command line.

Next, create a directory to store your virtual environments, for example at the path */home/your_name/virtualenvs*. (Not sure what a path is?  see :ref:`Paths vs $PATHs<path-explainer>`.)

You can use the ``mkdir`` command to create a new directory, ie: ``mkdir /home/username/virtualenvs``. We'll refer to the full path to this directory as **$path_to_your_env** below.

The next step is to create your virtual environment within this directory. The commands are different based on whether you're on Python 3.4+ and using venv, or whether you're using an older version with the virtualenv program you just installed.

**If you’ve got Python 3.4 or higher**, type ``python -m venv $path_to_your_env/$your_env_name``. The path should be the directory you created to store the virtual environments, and the environment name is a new name chosen by you.

**If you’ve got a lower Python version**, type ``virtualenv $path_to_your_env/$your_env_name``. Again, the path should be the directory for storing virtual environments, and the env name is a new name.

Regardless of what version you're on, you can activate your virtual environment with the command: ``source $path_to_your_env/$your_env_name/bin/activate``.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Windows Virtual Environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Start by installing virtualenvwrappers from source::

  	git clone git://github.com/davidmarble/virtualenvwrapper-win.git
  	cd virtualenvwrapper-win
  	python setup.py install

Not familiar with git? Read :ref:`our intro below<git-explainer>`.

Find the Scripts\ directory for your Python installation, such as ``C:\Users\<User>\AppData\Local\Programs\Python\Python37\Scripts\``.

Add the Scripts\ directory to your $PATH. (Not sure what a $PATH is?  see :ref:`Paths vs $PATHs<path-explainer>`.)

To create a virtual environment for Parsons, execute: ``mkvirtualenv parsons``

To use this virtual environment, execute: ``workon parsons``

.. _path-explainer:

^^^^^^^^^^^^^^^
Paths vs $PATHs
^^^^^^^^^^^^^^^

Paths are how we refer to a file or program's location in the file system. For example, ``/home/janedoe/virtualenvs`` says that within the top-level directory ``home`` there is a directory named ``janedoe``, and within ``janedoe`` there is a directory ``virtualenvs``.

``/home/janedoe/virtualenvs`` is an **absolute path** because it specifies exactly how to get there no matter where you are in the system. The path ``janedoe/virtualenvs`` is a **relative path** because it only works if you use it from the home directory. Trying to use a relative path from the wrong location is a common source of command line errors!

On Windows, absolute paths look a little different. They start with the letter of the hard drive they're in, ie ``C:\Users\JaneDoe\Virtualenvs``.

In these instructions we try to use absolute paths, even though they're a little wordier, because it's less likely to cause problems for you if you run them from an unexpected place.

In addition to paths, there's an important environmental variable called **$PATH**. The $PATH is a list of absolute paths your computer will check when searching for installed libraries and scripts. You can check what's currently in your $PATH by typing ``echo $PATH`` (Mac/Linux) or ``echo %PATH%`` (Windows).

When you activate your virtual environment, the path to the environment is placed as the first path. Paths are checked in order from first to last. You can check what packages have been installed in your virtualenv (and thus should be available on the path when the virtualenv is activated) by looking in ``lib/site-packages``.

If you’re trying to run something you’ve installed, but your computer says it doesn’t exist, it may be because the computer doesn't have the right information in its $PATH. This happens to me all the time when I forget to activate my virtual environment!

************************************
Step 3: Download and Install Parsons
************************************

We're going to go over two different ways to download and install Parsons: using pip, and using git. Use pip if you just want to install Parsons and start using it. Use git if you might want to change Parsons to customize its behavior and/or contribute those changes back.

^^^^^^^^^
Using Pip
^^^^^^^^^

`Pip <https://pip.pypa.io/en/stable/>`_ is the Python package manager. Packages (also commonly known as “libraries”) are Python code that have been bundled up in a certain way (“packaged”) so they can be easily installed and used.

By default, pip installs from the `Python Package Index or PyPI <https://pypi.org/>`_, but you can tell pip to install from a branch on Github or even from a folder on your machine. All you need is a package with the right files. The specifics of those files, and how to create your own package, is a `much more advanced topic <https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_.

Essentially when you type ``pip install parsons[all]`` (or pip install anything!) you’re saying “Go find this project on PyPI and install it.” (Here’s `Parsons <https://pypi.org/project/parsons/>`_ on PyPI!)

To install Parsons using pip, make sure your virtual environment is activated and type ``pip install parsons[all]``. It's that simple!

.. _git-explainer:

^^^^^^^^^
Using Git
^^^^^^^^^

`Git <https://git-scm.com/>`_ is a popular version control system used primarily by programmers. Many people use git by way of `Github <https://github.com/>`_, a company which provides free hosting (and other helpful features) for git repositories. Parsons, like many others, `hosts our code <https://github.com/move-coop/parsons/>`_ on Github.

Start by making sure git is installed on your computer. To do this, type ``git version`` at the command line. If it gives you a version number, great! You've got git installed. If you get an error message of some kind, you'll need to `install git <https://github.com/git-guides/install-git>`_.

Once you've installed git, you can execute the following commands::

    git clone https://github.com/move-coop/parsons.git
    cd parsons
    pip install -r requirements.txt
    python setup.py install

These commands say, in order:

* make a copy of the Parsons repository on my computer
* change directories so I'm now in the top level of that repository
* install all the libraries listed in the file ``requirements.txt``
* see the file in this directory named ``setup.py``? run it to install this package

You should now have a copy of Parsons installed locally and ready to use!

.. note::

    When you install Parsons from git, you're getting the most up to date version of Parsons there is. When you install Parsons from PyPI via pip, you might get a slightly older version, since we have to take the extra step of making a "release" to move changes from Github to PyPI. We make releases fairly frequently, so this shouldn't be an issue, but it's something to keep in mind if Parsons is behaving unexpectedly.

$$$$$$$$$$
Git Basics
$$$$$$$$$$

Giving you a full tour of git is beyond the scope of this tutorial, but here's a quick intro.

Git allows you to connect the work you're doing locally with a central shared repository. When you enter a command like ``git clone https://github.com/move-coop/parsons.git``, git creates a copy of the repository on your local computer. It also keeps track of the source of your repository, by listing it as a **remote**. Git's default name for remotes is **origin**.

You can see all the remotes for a repository by typing the following command when within the repository: ``git remote -v``. (The -v stands for "verbose".) The result should look something like this::

    origin	https://github.com/move-coop/parsons.git (fetch)
    origin	https://github.com/move-coop/parsons.git (push)

*Wait*, you might be asking, *what's this 'fetch' and 'pull' business?* **Fetch** is the command you use to get changes from a remote. **Push** is the command you use to send changes to a remote. Although the locations you fetch/pull from and push to can be different, practically speaking they're almost always the same.

To get the most recent version of a remote, use the command ``git fetch origin main``. That means "get any changes from the branch named main on the remote named origin, but don't apply it yet". You apply what you've gotten with the command ``git merge origin main``. Many people combine these two steps with the command ``git pull origin main``.

Let's say you've made some local changes you want to send back to the remote. You can add your changes to a list of things to be committed with the command ``git add $filename``. You have to add at least one file, but you can add as many as you want. If you get confused about what's available to be added, the command ``git status`` will show you what's changed in your repository since the last commit, and whether or not its been added with ``git add`` yet.

Once you're done adding, bundle everything together with the command ``git commit -m "message"``. Use the "message" to briefly summarize your changes. Once you have added and committed your code, you can send it back to the remote with the command ``git push origin main``.

Pushing might be a bit more complicated than that, dependening on who else has pushed to the origin while you were working, or whether you're pushing to a codebase like Parsons that requires you to submit changes via Pull Requests, but that's enough for now.

Interested in learning more? Try `this tutorial <https://gitimmersion.com/>`_ or reach out on Slack to request a mentor or more advanced training.

**********
Conclusion
**********

You should now have Parsons installed on your computer, and hopefully you're also more comfortable with the command line, virtual environments, paths, and git.
