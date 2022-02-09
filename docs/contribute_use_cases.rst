============================================
How to Contribute a Use Case & Sample Script
============================================

People use Parsons for a great many things. We like to document and share that usage to save work and inspire other members of the community.

A "use case" is a narrative description of any length (but usually at least a couple paragraphs) explaining the problem the user faced and why and how they used Parsons. The sample script is a cleaned-up version of the script they used that someone else can then take and adapt.

To submit a use case and sample script, please take the following steps. Please reach out to the community at any point if you have questions about these steps, need someone to pair with you on this process, or for any other reason.

Steps:

  1. Write up your use case in a file in ``docs/use_cases``. Use the guidelines below for style and content. The file should end with ``.rst``. (That means it's a `Restructured Text <https://www.writethedocs.org/guide/writing/reStructuredText/>`_ file. Note that the syntax for RST files can be a little tricky!)

  2. Test that your use case looks correctly by building the documentation. There are instructions `here <https://move-coop.github.io/parsons/html/contributing.html#documentation>`_. The important steps to follow there are making a virtual environment, installing the requirements.txt file, and then building the docs with `make html`.

  3. Write up your sample script in a Python (``.py``) and place it in ``useful_resources/sample_code``. Use the guidelines below for style and content. After you've adapted to our style, please test to make sure the script still works.

  4. Submit your changes as a pull request on Github. We will review your contribution and give you any feedback. When it's ready, we'll merge!

*******************
Use Case Guidelines
*******************

A use case should follow a structure that looks something like this:

  * Introduce yourself and your organization to the extent you're comfortable. Feel free to brag a little about the cool stuff you do!

  * Explain the problem you needed to solve. If you want, talk briefly about any previous attempts to solve the problem and why they weren't satisfactory.

  * Describe how you used Parsons to solve the problem. You can talk about any hurdles you faced or dead ends you went down, if you like, or you can just jump right into describing the working version. If you relied on a person or resource (like documentation or a Parsons Party) for help you can shout them out here.

  * If you have additional ideas for how to use and extend the sample script, feel free to include them.

You don't need to go into a line by line explanation of your sample script. That's what the sample script itself, and its inline code comments, are for. That said, your write-up should describe in broad strokes what the script does.

We are still working out the best structure for these write-ups, so feel free to be creative!

************************
Sample Script Guidelines
************************

^^^^^^^^^^^^^^^^^^^^^^^
Configuration Variables
^^^^^^^^^^^^^^^^^^^^^^^

Please separate out all configuration variables, including information like passwords and API keys, and move them to the top of the file. We recomment that sensitive information be stored in environmental variables and loaded into the script (see an example here (ADD_LINK)). Regardless, make sure to remove any sensitive information like passwords before submitting!

We ask you to separate out configuration variables to minimize the likelihood of other users needing to edit your code. That makes your script easier to reuse.

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

^^^^^^^^^^^^^^^^^^^^^^
Follow Our Style Guide
^^^^^^^^^^^^^^^^^^^^^^

You can see our full style guide here (ADD LINK).

In particular, please try to use meaningful and readable variable names. For example, instead of writing::

    for i in j:
      print(i)

Write something more like::

    for attendee in training_session:
      print(attendee)

^^^^^^^^^^^^^^^^^^^^^^^^^
Make Your Script Runnable
^^^^^^^^^^^^^^^^^^^^^^^^^

Make your script runnable from the command like using the ``__main__`` function.

