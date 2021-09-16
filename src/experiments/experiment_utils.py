# Python imports
from typing import List, Tuple

"""
Evaluation parameters
"""
SEED_VALUE = 314

INSTANCES = 10  # Number of scheme instances. Different instances use different keys
QUERIES = 10  # Number of queries to run for an instance of a scheme
ITERATIONS = 1  # Number of iterations of one query on one instance of a scheme

MAX_DATA_SIZE = 100000
KEYWORD_LENGTH = 5
ZN_FP_RATE = .01
ZN_KEY_LENGTH = 2048
LIBERTAS_KEY_LENGTH = 256


def generate_data(
        data_size: int,
) -> List[Tuple[int, str]]:
    """Generates at most 100,000 document-keyword pairs in the form [(0, '00000'), (1, '00001'), ..., (99999, '99999')].

    :param data_size: The number of document-keyword pairs to be generated
    :type data_size: int
    :returns: List[Tuple[int, str]]
    :rtype: A specified number of document-keyword pairs
    """
    if data_size > MAX_DATA_SIZE:
        raise AssertionError('Provided data size exceeds maximum')
    return [(n, str(n).zfill(KEYWORD_LENGTH)) for n in range(data_size)]
