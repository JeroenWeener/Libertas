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
        k: bytes = os.urandom(security_parameter)
        iv: bytes = os.urandom(16)
        self.k = (k, iv)
        return self.k

    def srch_token(
            self,
            k: (bytes, bytes),
            q: str,
    ):
        """ TODO: define return type"""
        print('SrchToken')

    def add_token(
            self,
            k: (bytes, bytes),
            ind: bytes,
            w: str,
    ):
        """ TODO: define return type"""
        print('AddToken')
