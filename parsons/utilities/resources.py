import logging
import tempfile


logger = logging.getLogger(__name__)


class _ResourceReference:
    def __init__(self, resource):
        self.resource = resource
        self.name = resource.name if getattr(resource, 'name') else None
        self.reference_count = 1

    def __del__(self):
        self.close()

    def close(self):
        self.reference_count -= 1
        if self.reference_count == 0:
            self.resource.close()

    def reference(self):
        self.reference_count += 1
        return self


class ResourceManager:
    """
    Class for managing any 'close'-able resources (e.g. temp files, connections).

    We can't rely exclusively on the "automatic removal" behavior of the built-in `tempfile`
    library, because of Parsons' use of petl. Specifically, if a petl table is loaded from a
    temporary file (eg. a CSV), petl may not actually read the file until much later, after the
    TemporaryFile object has already gone out of scope and the file removed. If this
    occurs, the petl load will fail since it's trying to read from a file that doesn't exist.

    The 'close' method on the ResourceManager can be used to clean up existing managed resources.

    `Args:`
        existing_manager: ResourceManager
            Another ResourceManager whose resources will be shared.
    `Returns:`
        ResouceManager Class
    """

    def __init__(self, existing_manager=None):
        existing_resources = existing_manager.resources if existing_manager else []
        self.resources = [
            resource.reference() for resource
            in existing_resources
        ]

    def release(self):
        """
        Close all of the resources for the resource manager.
        """
        # Go through each of our resources and run "close" on them
        for resource in self.resources:
            try:
                # Try to close the resource
                resource.close()
            except Exception as exc:
                # If something goes wrong, just log it, not much else we can do.
                logger.exception(f'Error closing resource: {exc}')

        # de-reference the sources by de-referencing the array. this will (hopefully) result in
        # them being garbage collected
        self.resources = []

    def close_temp_file(self, path):
        """
        Force closes a file managed by this class, which will cause it to be deleted immediately.

        Useful for when you just want to close one file that is being managed by the resource
        manager. eg, If you're running into system limits on open file descriptors.

        `Args:`
            path: str
                Path of a temp file created by ``create_temp_file``
        `Returns:`
            bool
                Whether the temp file was found and closed
        """
        for resource in self.resources:
            if resource.name == path:
                resource.close()
                self.resources.remove(resource)
                return True

        return False

    def create_temp_file(self, suffix=None):
        """
        Create a temp file that will exist until the resource manager is closed.

        `Args:`
            suffix: str
                A suffix/extension to add to the end of the temp file name
        `Returns:`
            str
                The path of the temp file
        """
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix)
        resource = _ResourceReference(temp_file)
        self.resources.append(resource)
        return temp_file.name

    def create_temp_file_for_path(self, path):
        """
        Creates a temp file that will exist as long until the resource manager is closed, and with
        a file name mimicking that of the provided path.

        `Args:`
            path: str
                Path (or just file name) of the file you want the temp file to mimick.
        `Returns:`
            str
                The path of the temp file
        """
        # Add the appropriate compression suffix to the file, so other libraries that check the
        # file's extension will know that it is compressed.
        # TODO Make this more robust, maybe even using the entire remote file name as the suffix.
        suffix = '.gz' if path[-3:] == '.gz' else None
        return self.create_temp_file(suffix=suffix)
