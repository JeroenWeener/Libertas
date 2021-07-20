# Python imports
from typing import List


class SigmaServer(object):
    """Server interface of a wildcard supporting SSE scheme to be used for a Libertas client."""

    def __init__(
            self,
    ) -> None:
        pass

    def build_index(
            self,
    ) -> None:
        pass

    def search(
            self,
            srch_token: any,
    ) -> List[bytes]:
        pass

    def add(
            self,
            add_token: any,
    ) -> None:
        pass
