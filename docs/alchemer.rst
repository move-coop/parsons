Alchemer
========

********
Overview
********

`Alchemer <https://www.alchemer.com/>`_ is an online research tool that allows users to field surveys. This Parsons
class allows users to retrieve surveys and survey results.

.. note::

    Alchemer was formerly known as SurveyGizmo.

.. note::

  Authentication
    To use the class, you need to provide an Alchemer API token and API token secret. For more information,
    see Alchemer API `authentication documentation <https://apihelp.alchemer.com/help/authentication>`_.

***********
Quick Start
***********

To instantiate the ``Alchemer`` class, you can either store your API token and API secret
token as environmental variables (``SURVEYGIZMO_API_TOKEN`` and ``SURVEYGIZMO_API_TOKEN_SECRET``,
respectively) or pass in the tokens arguments.


***
API
***

.. autoclass:: parsons.alchemer.alchemer.Alchemer
   :inherited-members:
   :members:
   