SFTP
====

The ``SFTP`` class allows you to interact with `SFTP services <https://en.wikipedia.org/wiki/SSH_File_Transfer_Protocol>`_,
using the  `Paramiko SFTP library <http://docs.paramiko.org/en/2.7/api/sftp.html>`_ under the hood.

The class provides methods to:

- Create SFTP connections
- Make, remove, and list the contents of directories
- Get, put, remove, and check the size of files

.. note::

  Authentication
    Depending on the server provider, SFTP may require either password or public key authentication.
    The ``SFTP`` class supports both methods via ``password`` and ``rsa_private_key_file`` arguments.

**********
Quickstart
**********

To instantiate ``SFTP``, pass your host name, user name, and either a password or an authentication
key file as keyword arguments:

.. code-block:: python

   from parsons import SFTP

   sftp = SFTP(host='my_hostname', username='my_username', password='my_password')

   # List contents of a directory
   sftp.list_directory(remote_path='my_dir')

   # Get a file
   sftp.get_file(remote_path='my_dir/my_csv.csv', local_path='my_local_path/my_csv.csv')

To batch multiple methods using a single connection, you can create a connection and use
it in a ``with`` block:

.. code-block:: python

   connection = sftp.create_connection()

   with connection as conn:
       sftp.make_directory('my_dir', connection=conn)
       sftp.put_file('my_csv.csv', connection=conn)

***
API
***

.. autoclass:: parsons.sftp.sftp.SFTP
   :inherited-members:
   :members:
   