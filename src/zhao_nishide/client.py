# Python imports
import os
from typing import List

# Third-party imports
from bitarray import bitarray

# Project imports
from src.zhao_nishide.bloom_filter_parameters import BF_HASH_FUNCTIONS, BF_ARRAY_SIZE
from src.crypto import hash_string_to_int, hash_int, hash_string, hash_bytes


class ZNClient(object):
    """Zhao and Nishide client implementation.

    Based on: Fangming Zhao and Takashi Nishide. Searchable symmetric encryption supporting queries with
    multiple-character wildcards. In International Conference on Network and System Security, pages 266–282. Springer,
    2016.

    This implementation uses Bloom filters for the index. Search queries are allowed to contain both _ and * wildcard
    characters. A _ character is used to indicate the presence of any single character, while the * character marks the
    presence of 0 or more characters.
    """

    def __init__(
            self,
    ) -> None:
        """Initializes a Zhao and Nishide client.

        :returns: None
        :rtype: None
        """
        self.k = None

    def setup(
            self,
            security_parameter: int,
    ) -> (List[bytes], bytes):
        """Sets up the Z&N client, generating keys k_h and k_g.

        :param security_parameter: The required security strength
        :type security_parameter: int
        :returns: The generated keys
        :rtype: (List[bytes], bytes)
        """
        k_h: List[bytes] = [os.urandom(security_parameter) for _ in range(BF_HASH_FUNCTIONS)]
        k_g: bytes = os.urandom(security_parameter)
        self.k: (bytes, bytes) = (k_h, k_g)
        return self.k

    def srch_token(
            self,
            q: str,
    ) -> (List[int], List[bytes]):
        """Creates a search token for a query, to be send to a Z&N server.
        The first part of the search token consists of Bloom filter positions, one per element in s_t(q).
        The second part of the search token consists of hashes of these positions.

        :param q: The query, a string of characters, possibly containing singular _ and * wildcards
        :type q: str
        :returns: The search token
        :rtype: (List[int], List[bytes])
        """
        (k_h, k_g) = self.k
        s_t = self._s_t(q)
        td1s: List[int] = [hash_string_to_int(k, e) % BF_ARRAY_SIZE for e in s_t for k in k_h]
        td2s: List[bytes] = [hash_int(k_g, pos) for pos in td1s]
        return td1s, td2s

    def add_token(
            self,
            ind: int,
            w: str,
    ) -> (int, bitarray, bytes):
        """Creates an add token for a document-keyword pair, to be send to a Z&N server.
        Add tokens consist of the document identifier, Bloom filter and its ID.

        :param ind: The document identifier of the document-keyword pair to add
        :type ind: int
        :param w: The keyword of the document-keyword pair to add
        :returns: An add token, a tuple consisting of a document identifier, Bloom filter and its ID
        :rtype: (int, bitarray, bytes)
        """
        s_k = self._s_k(w)
        (k_h, k_g) = self.k
        b_id = hash_string(k_g, str(ind) + w)
        bloom_filter = bitarray(BF_ARRAY_SIZE)

        # Fill Bloom filter
        for e in s_k:
            for k in k_h:
                pos = hash_string_to_int(k, e) % BF_ARRAY_SIZE
                bloom_filter[pos] = True

        # Mask Bloom filter
        for pos in range(BF_ARRAY_SIZE):
            h = hash_bytes(b_id, hash_int(k_g, pos))
            first_hash_bit = h[0] & 1
            bloom_filter[pos] ^= first_hash_bit
        return ind, bloom_filter, b_id

    def _s_k(
            self,
            w: str,
    ) -> List[str]:
        """Generates the S_K set for a keyword.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K set of the keyword
        :rtype: List[str]
        """
        return self._s_k_o(w) + self._s_k_p(w)

    def _s_k_o(
            self,
            w: str,
    ) -> List[str]:
        """Generates the S_K^(o) set for a keyword.
        Set items are of the form '{position}:{character}'.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K^(o) set of the keyword
        :rtype: List[str]
        """
        return [str(n + 1) + ':' + c for n, c in zip(range(len(w)), w)]

    def _s_k_p(
            self,
            w: str,
    ) -> List[str]:
        """Generates the S_K^(p) set for a keyword.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K set of the keyword
        :rtype: List[str]
        """
        return self._s_k_p1(w) + self._s_k_p2(w)

    def _s_k_p1(
            self,
            w: str,
    ) -> List[str]:
        """Generates the S_K^(p1) set for a keyword.
        Set items are of the form '{occurrence}:{character distance}:{character 1},{character 2}'.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K^(p1) set of the keyword
        :rtype: List[str]
        """
        # Generate '{character distance}:{character 1},{character 2}' for every character pair in the keyword
        pairs = [str(c2 - c1) + ':' + w[c1] + ',' + w[c2]
                 for c1 in range(len(w))
                 for c2 in range(c1 + 1, len(w))]

        # Append '{occurrence}:'
        unique_pairs = list(set(pairs))
        pair_count_dict = {pair: pairs.count(pair) for pair in unique_pairs}
        return [str(count + 1) + ':' + pair
                for pair in pair_count_dict.keys()
                for count in range(pair_count_dict[pair])]

    def _s_k_p2(
            self,
            w: str,
    ) -> List[str]:
        """Generates the S_K^(p2) set for a keyword.
        Set items are of the form '{occurrence}:{character 1},{character 2}'.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K^(p2) set of the keyword
        :rtype: List[str]
        """
        # Generate '{character 1},{character 2}' for every character pair in the keyword
        pairs = [w[c1] + ',' + w[c2]
                 for c1 in range(len(w))
                 for c2 in range(c1 + 1, len(w))]

        # Append '{occurrence}:'
        unique_pairs = list(set(pairs))
        pair_count_dict = {pair: pairs.count(pair) for pair in unique_pairs}
        return [str(count + 1) + ':' + pair
                for pair in pair_count_dict.keys()
                for count in range(pair_count_dict[pair])]

    def _s_t(
            self,
            q: str,
    ) -> List[str]:
        """Generates the S_T set for a keyword.

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T set of the query
        :rtype: List[str]
        """
        return self._s_t_o(q) + self._s_t_p(q)

    def _s_t_o(
            self,
            q: str,
    ) -> List[str]:
        """Generates the S_T^(o) set for a query.
        Set items are of the form '{position}:{character}' and contain all characters in the query that have a specific
        appearance order, which are all characters (except the _ wildcard), up until the first * wildcard.

        :param q: The query for which the set is to be generated. A string, possibly containing _ and * wildcards
        :type q: str
        :returns: The S_T^(o) set of the query
        :rtype: List[str]
        """
        fixed_characters = q.split('*')[0]
        return [str(c + 1) + ':' + q[c] for c in range(len(fixed_characters)) if q[c] != '_']

    def _s_t_p(
            self,
            q: str,
    ) -> List[str]:
        """Generates the S_T^(p) set for a keyword.

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T set of the query
        :rtype: List[str]
        """
        return self._s_t_p1(q) + self._s_t_p2(q)

    def _s_t_p1(
            self,
            q: str,
    ) -> List[str]:
        """Generates the S_T^(p1) set for a query.
        Set items are of the form '{occurrence}:{character distance}:{character 1},{character 2}'

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T^(p1) set of the query
        :rtype: List[str]
        """
        consecutive_character_groups = q.split('*')
        # Generate all pairs of characters within a consecutive character group as
        # '{character distance}:{character 1},{character 2}'
        pairs = [str(c2 - c1) + ':' + group[c1] + ',' + group[c2]
                 for group in consecutive_character_groups
                 for c1 in range(len(group)) if group[c1] != '_'
                 for c2 in range(c1 + 1, len(group)) if group[c2] != '_']

        # Append '{occurrence}:'
        unique_pairs = list(set(pairs))
        pair_count_dict = {pair: pairs.count(pair) for pair in unique_pairs}
        return [str(count + 1) + ':' + pair
                for pair in pair_count_dict.keys()
                for count in range(pair_count_dict[pair])]

    def _s_t_p2(
            self,
            q: str,
    ) -> List[str]:
        """Generates the S_T^(p2) set for a query.
        Set items are of the form '{occurrence}:{character 1},{character 2}'

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T^(p2) set of the query
        :rtype: List[str]
        """
        return self._s_k_p2(q.replace('*', '').replace('_', ''))