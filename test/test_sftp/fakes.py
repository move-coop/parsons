"""In-memory fakes for the paramiko SFTP client, injected into SFTP methods.

Every SFTP method accepts a ``connection`` argument, so tests can pass a ``FakeSFTP``
instead of opening a real connection. ``FakeSFTP`` subclasses ``paramiko.SFTPClient``
(without its channel-hungry ``__init__``) so it also satisfies the ``isinstance``
check in ``parsons.sftp.utilities.connect`` — that is how the ``@connect``-decorated
methods recognise an injected connection. It records every call on ``self.calls`` and
returns programmed directory listings / file sizes.
"""

import stat
from pathlib import Path

import paramiko


class FakeAttr:
    """A stand-in for ``paramiko.SFTPAttributes`` with just ``filename`` + ``st_mode``."""

    def __init__(self, filename, is_dir=False):
        self.filename = filename
        self.st_mode = (stat.S_IFDIR if is_dir else stat.S_IFREG) | 0o755


class _FakeRemoteFile:
    def __init__(self, size):
        self._size = size

    def _get_size(self):
        return self._size


class FakeSFTP(paramiko.SFTPClient):
    def __init__(self, entries=None, size=0, get_source=None, listdir_attr_error=None):
        # Intentionally skip super().__init__ — it needs a live paramiko channel.
        self._entries = entries or []
        self._size = size
        self._get_source = get_source
        self._listdir_attr_error = listdir_attr_error
        self.calls = []

    def _record(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))

    def listdir(self, path="."):
        self._record("listdir", path=path)
        return [entry.filename for entry in self._entries]

    def listdir_attr(self, path="."):
        self._record("listdir_attr", path)
        if self._listdir_attr_error:
            raise self._listdir_attr_error
        return list(self._entries)

    def mkdir(self, path, mode=511):
        self._record("mkdir", path)

    def rmdir(self, path):
        self._record("rmdir", path)

    def remove(self, path):
        self._record("remove", path)

    def get(self, remotepath, localpath, callback=None, prefetch=True):
        self._record("get", remotepath, localpath)
        if self._get_source is not None:
            Path(localpath).write_bytes(Path(self._get_source).read_bytes())

    def put(self, localpath, remotepath, callback=None, confirm=True):
        self._record("put", localpath, remotepath, callback=callback)

    def file(self, filename, mode="r", bufsize=-1):
        self._record("file", filename, mode)
        return _FakeRemoteFile(self._size)
