# Python imports
from enum import Enum
from typing import Tuple


class Op(Enum):
    """Enum representing the two types of update operations in dynamic SSE schemes: add and delete."""
    ADD = 1
    DEL = 2


"""Type declaration for Libertas updates, (t, op, ind, w) tuples."""
Update = Tuple[int, Op, int, str]

"""Type declaration for encrypted Libertas updates."""
EncryptedUpdate = bytes

"""Command line print values. Encapsulate text with these values to underline them."""
underline_start = '\033[4m'
underline_end = '\033[0m'
