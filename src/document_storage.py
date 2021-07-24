# Python imports
from typing import Dict


class DocumentStorage(object):
    """A document storage server that manages encrypted documents. This storage can be combined with the server running
    server code of SSE protocols, or it can be another party that is tasked purely with managing encrypted documents.
    """

    def __init__(
            self,
    ) -> None:
        """Initializes a dictionary where documents are stored.

        :returns: None
        :rtype: None
        """
        self.files: Dict[int, bytes] = {}
        self.last_file_id: int = 0

    def upload_file(
            self,
            file: bytes,
    ) -> int:
        """Adds an encrypted file to the storage with a generated document identifier.

        :param file: The encrypted file to add to the storage
        :type file: bytes
        :returns: The generated document identifier
        :rtype: int
        """
        self.last_file_id += 1
        self.files[self.last_file_id] = file
        return self.last_file_id

    def update_file(
            self,
            file: bytes,
            file_id: int,
    ) -> None:
        """Updates an existing file.

        :param file: The update file
        :type file: bytes
        :param file_id: The identifier of the file
        :type file_id: int
        :returns: None
        :rtype: None
        """
        self.files[file_id] = file

    def delete_file(
            self,
            file_id: int,
    ) -> None:
        """Deletes an encrypted file from the storage.

        :param file_id: The document identifier of the document to delete
        :type: int
        :returns: None
        :rtype: None
        """
        del self.files[file_id]

    def download_file(
            self,
            file_id: int,
    ) -> bytes:
        """Outputs the encrypted file corresponding to the given document identifier.

        :param file_id: The identifier of the encrypted file to fetch
        :type file_id: int
        :returns: The encrypted file corresponding to the document identifier
        :rtype: bytes
        """
        return self.files[file_id]
