FacebookAds
===========

********
Overview
********

The ``FacebookAds`` class allows you to interact with parts of the Facebook Business API.
Currently the connector provides methods for creating and deleting custom audiences, and for adding users to audiences.

The ``FacebookAds`` connector is a thin wrapper around the `FB Business SDK <https://github.com/facebook/facebook-python-business-sdk>`_,
so some of that SDK is exposed, e.g., you may see exceptions like ``FacebookRequestError``.

Facebook's advertising and Pages systems are massive. Check out the overviews for more information:

* `Facebook Business Overview <https://www.facebook.com/business>`_
* `Facebook Custom Audiences <https://www.facebook.com/business/a/custom-audiences>`_
* `Facebook Marketing API <https://developers.facebook.com/docs/marketing-api>`_

.. note::

  Authentication
    Before using ``FacebookAds``, you'll need the following:
    * A FB application, specifically the app ID and secret. See `<https://developers.facebook.com>`_ to find your app details or create a new app. Note that a Facebook app isn't necessarily visible to anyone but you: it's just needed to interact with the Facebook API.
    * A FB ad account. See `<https://business.facebook.com>`_ to find your ad accounts or create a new one.
    * A FB access token representing a user that has access to the relevant ad account. You can generate an access token from your app, either via the Facebook API itself, or via console at `<https://developers.facebook.com>`_.

**********
Quickstart
**********

To instantiate the FacebookAds class, you can either store your authentication credentials as environmental variables
(``FB_APP_ID``, ``FB_APP_SECRET``, ``FB_ACCESS_TOKEN``, and ``FB_AD_ACCOUNT_ID``) or pass them in as arguments:

.. code-block:: python

   from parsons import FacebookAds

   # First approach: Use environmental variables
   fb = FacebookAds()

   # Second approach: Pass credentials as argument
   fb = FacebookAds(app_id='my_app_id',
                    app_secret='my_app_secret',
                    access_token='my_access_token',
                    ad_account_id='my_account_id')

You can then use various methods:

.. code-block:: python

   # Create audience
   fb.create_custom_audience(name='audience_name', data_source='USER_PROVIDED_ONLY')

   # Delete audience
   fb.delete_custom_audience(audience_id='123')

***
API
***

.. autoclass:: parsons.facebook_ads.facebook_ads.FacebookAds
   :inherited-members:
   :members:
   