.. highlight:: python

============================================
How to Contribute a Use Case & Sample Script
============================================

People use Parsons for a great many things. We like to document and share that usage to save work and inspire other members of the community.

A "use case" is a narrative description of any length (but usually at least a couple paragraphs) explaining the problem the user faced and why and how they used Parsons to solve it.
The "sample script" is a cleaned-up and standardized version of the original script that someone else can take and adapt.

To submit a use case and sample script, please take the following steps.
Please reach out to the community at any point if you have questions about these steps,
need someone to pair with you on this process, or for any other reason.
The best place to get help is the #contrib channel on the Parsons slack.
To request access to the Parsons slack, email *engineering@movementcooperative.org*.

.. note::

    The last step in this process involves submitting your contribution as a pull request.
    To do this, fork the repository by clicking the "fork" button in the top right-hand corner.
    Then you can make the edits described below, either locally or through the
    `Github web editor <https://docs.github.com/en/codespaces/the-githubdev-web-based-editor>`_.
    Once you've saved your changes (if you're working locally, this means doing a ``git push`` back to your fork)
    an alert asking you if you want to open a pull request should appear on your fork's main page.
    Go ahead and follow those instructions!

Steps:

  1. Write up your use case in a file in ``docs/use_cases``. Use the guidelines below for style and content.
     The file should end with ``.rst``. That means it's a `Restructured Text <https://www.writethedocs.org/guide/writing/reStructuredText/>`_ file.
     Note that the syntax for RST files can be a little tricky!

  2. Test that your use case looks correct by building the documentation.
     There are instructions `here <https://move-coop.github.io/parsons/html/contributing.html#documentation>`_.
     The important steps to follow there are making a virtual environment, installing parsons, and then building the docs with `make deploy_docs`.

  3. Write up your sample script in a Python (``.py``) file, place it in ``useful_resources/sample_code``,
     and add it to the ``use_cases_and_sample_scripts`` section of the table of contents in ``index.rst``.
     Use the guidelines below for style and content. After you've adapted to our style, please test to make sure the script still works.

  4. Submit your changes as a pull request on Github. We will review your contribution and give you any feedback. When it's ready, we'll merge!

*******************
Use Case Guidelines
*******************

A use case should follow a structure that looks something like this:

  * Introduce yourself and your organization to the extent you're comfortable. Feel free to brag a little about the cool stuff you do!
  * Explain the problem you needed to solve. If you want, talk briefly about any previous attempts to solve the problem and why they weren't satisfactory.
  * Describe how you used Parsons to solve the problem.
    You can talk about any hurdles you faced or dead ends you went down, if you like, or you can just jump right into describing the working version.
    If you relied on a person or resource (like documentation or a Parsons Party) for help you can shout them out here.
  * If you have additional ideas for how to use and extend the sample script, feel free to include them.

You don't need to go into a line by line explanation of your sample script.
That's what the sample script itself, and its inline code comments, are for. That said, your write-up should describe in broad strokes what the script does.

We are still working out the best structure for these write-ups, so feel free to be creative!

************************
Sample Script Guidelines
************************

^^^^^^^^^^^^^^^^^^^^^
Sensitive Information
^^^^^^^^^^^^^^^^^^^^^

Most scripts will include sensitive information like passwords and API keys.
We recommend these be stored in environmental variables.
Some environmental variables may need to be explicitly loaded into the script, but most will not.
This is because each Parsons connector automatically looks in the environment for specific variables and uses them when initializing the connector.
For example, the Zoom connector looks for ``ZOOM_API_KEY`` and ``ZOOM_API_SECRET``.

Your sample script should make clear to users what environmental variables need to be set, including the variables for the connectors you're using.
You can include a note to users reminding them to set environmental variables, something like: ::

    # To use the Zoom connector, set the ZOOM_API_KEY and ZOOM_API_SECRET environmental variables.

If you need to use other environmental variables beyond the ones automatically accessed by the connectors, make sure your script loads them from the environment::

    NEW_ENV_VARIABLE = os.getenv('NEW_ENV_VARIABLE')

Regardless of the approach you chose, make sure to remove any sensitive information like passwords before submitting!

.. note::

    Not sure how to set environmental variables? You can set them from the command line::

        set VARIABLE_NAME=VARIABLE_VALUE       # Windows
        export VARIABLE_NAME=VARIABLE_VALUE    # Linux/Mac

    Or you can run a Python script that looks like this::

        import os
        os.environ[VARIABLE_NAME] = VARIABLE_VALUE

    Hosting environments often have custom ways of setting environmental variables. You can look up their documentation and/or ask for help in the Parsons Slack.

^^^^^^^^^^^^^^^^^^^^^^^
Configuration Variables
^^^^^^^^^^^^^^^^^^^^^^^

Please separate out all configuration variables and move them to the top of the file.
We recommend that sensitive information be stored in environmental variables as shown above.
We ask you to separate out configuration variables in order to minimize the likelihood of other users needing to edit your code.
That makes your script easier to reuse.

For example, instead of doing this::

  if training_duration > 60:
    ...

Do something like this::

  # configuration variables
  MINIMUM_DURATION = 60    # minimum duration for attendee to count as trained (in hours)

  # within code
  if training_duration > MINIMUM_DURATION:
    ...

^^^^^^^^^^^^^^^^^
Comment Liberally
^^^^^^^^^^^^^^^^^

Please use code comments to describe what's happening in the code. Err on the side of too much exposition, rather than too little.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Write Code in the Parsons Style
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We're still working on our style guide, so for now, just try to write code that's in line with Python's `PEP8 <https://realpython.com/python-pep8/>`_.
If you're not used to writing code in this style, we're happy to help.

In particular, please try to use meaningful and readable variable names. For example, instead of writing::

    for i in j:
      print(i)

Write something more like::

    for attendee in training_session:
      print(attendee)

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Put Your Code In Callable Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Often people will write their Python code like this::

    user_name = "Maria"
    message = f"Hello {user_name}! Welcome to our community."
    print(message)

This works fine when running a script directly, but can cause trouble when importing into other files.
Code at the "top" level of a Python file automatically runs on import.
Most people importing your code into another file will not want to do that!

To make your code easier to re-use, stick it in one or more functions::

    def greet_user(user_name):
        message = f"Hello {user_name}! Welcome to our community."
        print(message)

Now other people can import your code and use it however they like.
But what if they still want to run it from the command line?
You can allow them to do that too by sticking this at the bottom of your Python file::

    if __name__ == "__main__":
        greet_user("Maria")  # or whatever you want to happen when the file is run

What's happening here? Well, ``__name__`` is a special, built-in Python variable that is set to ``__main__`` if you're running the file directly.
So this little piece of code says: if and only if you're running this code directly, execute the code within.

Now anyone using your code can run it directly, *or* they can import it and re-use it however they like!
