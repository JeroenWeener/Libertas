from typing import List


class SigmaServer:
    """ Sigma server implementation """

    def __init__(
            self,
    ) -> None:
        print('Server')

    def build_index(
            self,
            security_parameter: int,
    ) -> None:
        print('BuildIndex')

    def search(
            self,
            srch_token,
    ) -> List[bytes]:
        """ TODO: define srch_token type"""
        return []

    def add(
            self,
            add_token,
    ) -> None:
        """ TODO: define add_token type"""
        print('Add')
