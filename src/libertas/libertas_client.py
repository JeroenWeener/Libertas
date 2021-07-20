# Python imports
import functools
from typing import Dict, List

# Third-party imports
from Crypto.Cipher import AES

# Project imports
from src.sigma_interface.sigma_client import SigmaClient
from src.utils import EncryptedUpdate, Update, Op
from src.zhao_nishide.zn_client import ZNClient


class LibertasClient(object):
    """Libertas client implementation.

    Libertas uses a wildcard supporting SSE scheme internally. In addition to the security guarantees and functionality
    provided by the underlying scheme, Libertas provides Update Pattern Revealing Backward Privacy.
    """

    def __init__(
            self,
            sigma: SigmaClient,
    ) -> None:
        """Initializes a Libertas client, setting the underlying client scheme that is used.

        :param sigma: The underlying SSE scheme used by this Libertas instance
        :type sigma: ZNClient
        :returns: None
        :rtype: None
        """
        self.sigma: SigmaClient = sigma
        self.k: (bytes, bytes) = None
        self.t: int = -1

    def setup(
            self,
            security_parameter: int,
    ) -> None:
        """Sets up the Libertas client, generating a key used for future operations and initializing the scheme's
        timestamp counter.

        :param security_parameter: The required security strength
        :type security_parameter: int
        :returns: None
        :rtype: None
        """
        # TODO set k (encryption, iv)
        self.k = -1
        self.t = 0

    def srch_token(
            self,
            q: str,
    ) -> any:
        """Creates a search token for a query, to be send to the server.

        :param q: The query, a string of characters, possibly containing wildcards
        :type q: str
        :returns: The search token
        :rtype: any
        """
        return self.sigma.srch_token(q)

    def add_token(
            self,
            ind: int,
            w: str,
    ) -> any:
        """Creates an add token for a document-keyword pair, to be send to the server.

        :param ind: The document identifier of the document in the document-keyword pair that is to be added
        :type ind: int
        :param w: The keyword in the document-keyword pair that is to be added
        :type w: str
        :returns: the add token
        :rtype: any
        """
        self.t = self.t + 1
        content = self._encrypt_update(self.k, self.t, Op.ADD, ind, w)
        return self.sigma.add_token(content, w)

    def del_token(
            self,
            ind: int,
            w: str,
    ) -> any:
        """Creates a delete token for a document-keyword pair, to be send to the server.

        :param ind: The document identifier of the document in the document-keyword pair that is to be deleted
        :type ind: int
        :param w: The keyword in the document-keyword pair that is to be deleted
        :type w: str
        :returns: the delete token
        :rtype: any
        """
        self.t = self.t + 1
        content = self._encrypt_update(self.k, self.t, Op.DEL, ind, w)
        return self.sigma.add_token(content, w)

    def dec_search(
            self,
            r_star: List[EncryptedUpdate],
    ) -> List[int]:
        """Decrypts encrypted results received from the server and determines which document identifiers are still
        relevant for the query. Document identifiers are relevant when there is a keyword-document pair that is
        added, but not deleted afterwards.

        :param r_star: A list of encrypted results
        :type r_star: List[bytes]
        :returns: A list of document identifiers matching with the initial query
        :rtype: List[int]
        """
        # Decrypt r_star and sort it according to timestamp t
        decrypted_updates: List[Update] = list(map(lambda e: self._decrypt_update(self.k, e), r_star))
        decrypted_updates.sort(key=lambda x: x[0])

        keyword_documents_dict: Dict[str, List[int]] = {}
        for update in decrypted_updates:
            # Unpack entry (see utils.Update)
            (_, op, ind, w) = update

            if w not in keyword_documents_dict:
                keyword_documents_dict[w] = []

            documents_list: List[int] = keyword_documents_dict[w]
            if op == Op.ADD and ind not in documents_list:
                # Add ind to the results for this keyword
                documents_list.append(ind)
                keyword_documents_dict[w] = documents_list
            elif op == Op.DEL and ind in documents_list:
                # Remove ind from the results for this keyword
                documents_list.remove(ind)
                keyword_documents_dict[w] = documents_list

        # Combine the ind values for all keywords and remove duplicates
        return list(set(functools.reduce(lambda cumulative_list, l:
                                         cumulative_list + l, keyword_documents_dict.values())))

    def _encrypt_update(
            self,
            k: (bytes, bytes),
            t: int,
            op: Op,
            ind: int,
            w: str,
    ) -> EncryptedUpdate:
        """Encrypts (t, op, ind, w) tuples.

        :param k: The encryption key
        :type k: (bytes, bytes)
        :param t: The timestamp in the tuple
        :type t: int
        :param op: The operation (add or delete) in the tuple
        :type op: Op
        :param ind: The document identifier in the tuple
        :type ind: int
        :param w: The keyword in the tuple
        :type w: str
        :returns: The tuple in encrypted form
        :rtype: EncryptedUpdate
        """
        key = k[0]
        iv = k[1]
        update_str: str = '{0} {1} {2} {3}'.format(t, op, ind, w)
        return self._encrypt(key, iv, update_str)

    def _decrypt_update(
            self,
            k: (bytes, bytes),
            cipher_text: EncryptedUpdate,
    ) -> Update:
        """Decrypts encryptions of (t, op, ind, w) tuples.

        :param k: The decryption key
        :type k: (bytes, bytes)
        :param cipher_text: The encrypted tuple
        :type cipher_text: EncryptedUpdate
        :returns: The (t, op, ind, w) tuple
        :rtype: Update
        """
        key = k[0]
        iv = k[1]
        update_str = self._decrypt(key, iv, cipher_text)
        (t, op, ind, w) = update_str.split()
        return t, op, ind, w

    def _encrypt(
            self,
            key: bytes,
            iv: bytes,
            raw: str,
    ) -> bytes:
        """Encrypts data using AES in CBC mode.

        :param key: The encryption key
        :type key: bytes
        :param iv: The initialization vector
        :type iv: bytes
        :param raw: The data to encrypt
        :type raw: str
        :returns: The encrypted form of the raw data
        :rtype: bytes
        """
        raw = self._pad(raw)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.encrypt(bytes(raw, 'utf-8'))

    def _decrypt(
            self,
            key: bytes,
            iv: bytes,
            cipher_text: bytes,
    ) -> str:
        """Decrypts cipher text using AES in CBC mode.

        :param key: The decryption key
        :type key: bytes
        :param iv: The initialization vector
        :type iv: bytes
        :param cipher_text: The cipher text to decrypt
        :type cipher_text: bytes
        :returns: The decryption of the cipher text
        :rtype: str
        """
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(cipher_text))

    def _pad(
            self,
            s: str,
            bs: int = 32,
    ) -> str:
        """Pads a string so its length is a multiple of a specified block size.

        :param s: The string that is to be padded
        :type s: str
        :param bs: The block size
        :type bs: int
        :returns: The initial string, padded to have a length that is a multiple of the specified block size
        :rtype: str
        """
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    def _unpad(
            self,
            s: bytes,
    ) -> str:
        """Unpads a string that was previously padded by _pad().

        :param s: The string to unpad
        :type s: TODO
        :returns: The unpadded string
        :rtype: str
        """
        return str(s[:-ord(s[len(s) - 1:])])
