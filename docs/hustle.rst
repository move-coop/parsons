Hustle
======

Hustle is a Peer to Peer texting communication platform. The methods are built against the `Hustle v1 API <https://api.hustle.com/docs/>`.

* Access to the API is limited to 100 requests per second for endpoints returning resources. When this limit is reached the API will return an error and the request will need to be retried.

* Creating an access token is an exception in that it only limits the number of failed attempts to create an access token. After 10 failed attempts to create an access token the ip of the request will be blocked for some period of time, but only for the account in question. Additionally 100 failed attempts in a 24-hour period will result in the requester's ip being blocked.

*******
Methods
*******

.. autoclass :: parsons.Hustle
   :inherited-members:
   :members: