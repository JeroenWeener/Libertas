# Third-party imports
import hashlib
import hmac


def hash_string(
        k: bytes,
        e: str,
) -> bytes:
    """Hash a string using SHA-256.

    :param k: Hash key
    :type k: bytes
    :param e: Hash input
    :type e: str
    :returns: The SHA-256 hash of the input string
    :rtype: bytes
    """
    return hmac.new(k, e.encode('utf-8'), hashlib.sha256).digest()


def hash_int(
        k: bytes,
        e: int,
) -> bytes:
    """Hash an integer using SHA-256.

    :param k: Hash key
    :type k: bytes
    :param e: Hash input
    :type e: int
    :returns: The SHA-256 hash of the input integer
    :rtype: bytes
    """
    return hash_string(k, str(e))


def hash_bytes(
        k: bytes,
        e: bytes,
) -> bytes:
    """Hash bytes using SHA-256.

    :param k: Hash key
    :type k: bytes
    :param e: Hash input
    :type e: bytes
    :returns: The SHA-256 hash of the input bytes
    :rtype: bytes
    """
    return hmac.new(k, e, hashlib.sha256).digest()


def hash_string_to_int(
        k: bytes,
        e: str,
) -> int:
    """Hash a string using SHA-256 and convert the result to an integer.

    :param k: Hash key
    :type k: bytes
    :param e: Hash input
    :type e: str
    :returns: An integer representation of the SHA-256 hash of the input string
    :rtype: int
    """
    return int.from_bytes(hash_string(k, e), 'big')
