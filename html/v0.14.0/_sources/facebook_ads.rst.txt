FacebookAds
===========

********
Overview
********

The FacebookAds class allows you to interact with parts of the Facebook Business API.

Facebook's advertising and Pages systems are massive, so check out the overviews to get oriented:

* `Facebook Business Overview <https://www.facebook.com/business>`_
* `Facebook Custom Audiences <https://www.facebook.com/business/a/custom-audiences>`_
* `Facebook Marketing API <https://developers.facebook.com/docs/marketing-api>`_

Before using FacebookAds, you'll need to have the following:

* A FB application, specifically the app ID and secret. See `<https://developers.facebook.com>`_ to find your app details or create a new  app. (Note that a Facebook app isn't necessarily visible to anyone but you. It's just needed to interact with the FB API.)
* A FB ad account. See `<https://business.facebook.com>`_ to find your ad accounts or create one.
* A FB access token representing a user that has access to the relevant ad account. You can generate an access token from your app, either via the Facebook API itself, or via console at `<https://developers.facebook.com>`_.

In order to instantiate the class, you must pass valid Facebook credentials as kwargs or via the env vars:

* ``FB_APP_ID``
* ``FB_APP_SECRET``
* ``FB_ACCESS_TOKEN``
* ``FB_AD_ACCOUNT_ID``

***
API
***

.. autoclass :: parsons.FacebookAds
   :inherited-members:
   :members: