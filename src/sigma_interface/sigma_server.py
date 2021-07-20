# Python imports
from typing import List


class SigmaServer(object):
    """Server interface of a wildcard supporting SSE scheme to be used for a Libertas client."""

    def __init__(
            self,
    ) -> None:
        """Initializes a server.

        :returns: None
        :rtype: None
        """
        pass

    def build_index(
            self,
    ) -> None:
        """Sets up the server, initializing its index.

        :returns: None
        :rtype: None
        """
        pass

    def search(
            self,
            srch_token: any,
    ) -> List[bytes]:
        """Searches the index for a query represented by a search token.

        :param srch_token: The search token
        :type srch_token: any
        :returns: A list of results
        :rtype: List[bytes]
        """
        pass

    def add(
            self,
            add_token: any,
    ) -> None:
        """Adds a document-keyword pair, represented by an add token, to the index.

        :param add_token: An add token representing a document-keyword pair
        :type add_token: any
        :returns: None
        :rtype: None
        """
        pass
