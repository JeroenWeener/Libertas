class SigmaClient(object):
    """Client interface of a wildcard supporting SSE scheme to be used for a Libertas client."""

    def __init__(
            self,
    ) -> None:
        pass

    def setup(
            self,
            security_parameter: int,
    ) -> None:
        pass

    def srch_token(
            self,
            q: str,
    ) -> any:
        pass

    def add_token(
            self,
            ind: bytes,
            w: str,
    ) -> any:
        pass
