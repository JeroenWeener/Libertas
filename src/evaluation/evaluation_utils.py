# Python imports
from typing import Tuple, List

NUMBER_OF_RUNS = 100
MAX_DATA_SIZE = 100000
KEYWORD_LENGTH = 5
ZN_FP_RATE = .01
ZN_KEY_LENGTH = 2048
LIBERTAS_KEY_LENGTH = 256


def generate_data(
        data_size: int,
) -> List[Tuple[int, str]]:
    """Generates at most 100,000 document-keyword pairs in the form ((0, '00000'), (1, '00001'), ..., (99999, '99999')).

    :param data_size: The number of document-keyword pairs to be generated
    :type data_size: int
    :returns: List[Tuple[int, str]]
    :rtype: A specified number of document-keyword pairs
    """
    if data_size > MAX_DATA_SIZE:
        raise AssertionError('Provided data size exceeds maximum')
    return [(n, str(n).zfill(KEYWORD_LENGTH)) for n in range(data_size)]
