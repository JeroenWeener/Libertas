from enum import Enum
from typing import Tuple

"""Utils file containing programming constructs used in the project."""


class Op(Enum):
    """Enum representing the two types of update operations in dynamic SSE schemes: add and delete."""
    ADD = 1
    DEL = 2


"""Type declaration for (t, op, ind, w) tuples."""
Item = Tuple[int, Op, int, str]
