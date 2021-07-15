import os


class SigmaClient:
    """Sigma client implementation."""

    def __init__(
            self,
    ) -> None:
        self.k = None

    def setup(
            self,
            security_parameter: int,
    ) -> (bytes, bytes):
        key: bytes = os.urandom(security_parameter)
        iv: bytes = os.urandom(32)
        self.k = (key, iv)
        return self.k

    def srch_token(
            self,
            q: str,
    ):
        """ TODO: define return type"""
        print('SrchToken')

    def add_token(
            self,
            ind: bytes,
            w: str,
    ):
        """ TODO: define return type"""
        print('AddToken')
