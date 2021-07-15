from sigma_server import SigmaServer
from typing import List


class Server:
    """Libertas server implementation."""

    def __init__(
            self,
            sigma: SigmaServer,
    ) -> None:
        """Initializes a Libertas server, setting the underlying server scheme that is used.

        :param sigma: The underlying SSE scheme used by this Libertas instance
        :type sigma: SigmaServer
        :returns: None
        :rtype: None
        """
        self.sigma: SigmaServer = sigma
        self.index = None

    def build_index(
            self,
            security_parameter: int,
    ) -> None:
        """Sets up the Libertas server, initializing its index.

        :param security_parameter: The required security strength
        :type security_parameter: int
        :returns: None
        :rtype: None
        """
        self.sigma.build_index(security_parameter)

    def search(
            self,
            srch_token,
    ) -> List[bytes]:
        """Searches the index using a search token.

        :param srch_token: The search token generated by the client
        :type srch_token: TODO
        :returns: A list of encrypted items
        :rtype: List[bytes]
        """
        return self.sigma.search(srch_token)

    def add(
            self,
            add_token,
    ) -> None:
        """Adds a (add) update item to the index (see Utils.Item)

        :param add_token: The add token generated from the update item by the client
        :type add_token: TODO
        :returns: None
        :rtype: None
        """
        self.sigma.add(add_token)

    def delete(
            self,
            del_token,
    ) -> None:
        """Adds a (delete) update item to the index (see Utils.Item)

        :param del_token: The delete token generated from the update item by the client
        :type del_token: TODO
        :returns: None
        :rtype: None
        """
        self.sigma.add(del_token)
