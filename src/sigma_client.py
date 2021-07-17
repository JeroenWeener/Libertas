import os
import hashlib, hmac
from typing import List, Set

from bitarray import bitarray

from bloom_filter import BloomFilter


class SigmaClient(object):
    """Sigma client implementation."""

    def __init__(
            self,
    ) -> None:
        self.k = None

    def setup(
            self,
            security_parameter: int,
            r: int = 16,
    ) -> (bytes, bytes):
        k_h: List[bytes] = [os.urandom(security_parameter) for _ in range(r)]
        k_g: bytes = os.urandom(security_parameter)
        self.k = (k_h, k_g)
        return self.k

    def srch_token(
            self,
            q: str,
    ) -> (List[List[bytes]], List[List[bytes]]):
        (k_h, k_g) = self.k
        s_t = self._s_t(q)
        td1s = [[self._g(k, e) for k in k_h] for e in s_t]
        td2s = [[self._g2(k_g, p) for p in td1] for td1 in td1s]
        return td1s, td2s

    def add_token(
            self,
            ind: int,
            w: str,
    ) -> (bytes, bitarray):
        # TODO use secure hashing with k_h
        # TODO determine BF parameters
        s_k = self._s_k(w)
        (k_h, k_g) = self.k
        b_id = self._g(k_g, str(ind) + w)
        bloom_filter = BloomFilter(100, .05)
        bloom_filter.add_all(s_k)
        bit_array = bloom_filter.bit_array
        # Mask bit array
        for i in range(len(bit_array)):
            bit_array[i] ^= self._g(k_g, str(i))[0] & 1 == 1
        return b_id, bit_array

    def _g(
            self,
            k: bytes,
            e: str,
    ) -> bytes:
        a = hmac.new(k, e.encode('utf-8'), hashlib.sha256).digest()
        print(a)
        return a

    def _g2(
            self,
            k: bytes,
            e: bytes,
    ) -> bytes:
        return hmac.new(k, e, hashlib.sha256).digest()

    def _s_k(
            self,
            w: str,
    ) -> List[str]:
        """Generates the S_K set for a keyword, according to Zhao and Nishide.

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
        return [str(n) + ':' + c for n, c in zip(range(1, len(w) + 1), w)]

    def _s_k_p(
            self,
            w: str,
    ) -> List[str]:
        """Generates the S_K^(p) set for a keyword.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K set of the keyword
        :rtype: Set[str]
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
        pairs = [str(c2 - c1) + ':' + w[c1] + ',' + w[c2]
                 for c1 in range(len(w))
                 for c2 in range(c1 + 1, len(w))]
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
        Set items are of the form '{occurrence}:-:{character 1},{character 2}'.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K^(p2) set of the keyword
        :rtype: List[str]
        """
        pairs = ['-:' + w[c1] + ',' + w[c2]
                 for c1 in range(len(w))
                 for c2 in range(c1 + 1, len(w))]
        unique_pairs = list(set(pairs))
        pair_count_dict = {pair: pairs.count(pair) for pair in unique_pairs}
        return [str(count + 1) + ':' + pair
                for pair in pair_count_dict.keys()
                for count in range(pair_count_dict[pair])]

    def _s_t(
            self,
            q: str,
    ) -> List[str]:
        """Generates the S_T set for a keyword, according to Zhao and Nishide.

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
        solid_characters = q.split('*')[0]
        return [str(c + 1) + ':' + q[c] for c in range(len(solid_characters)) if q[c] != '_']

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
        Set items are of the form '{occurrence}:{distance}:{character 1},{character 2}'

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T^(p1) set of the query
        :rtype: List[str]
        """
        consecutive_character_groups = q.split('*')
        # Generate all pairs of characters within a consecutive character group
        pairs = [str(c2 - c1) + ':' + group[c1] + ',' + group[c2]
                 for group in consecutive_character_groups
                 for c1 in range(len(group)) if group[c1] != '_'
                 for c2 in range(c1 + 1, len(group)) if group[c2] != '_']
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
        Set items are of the form '{occurrence}:-:{character 1},{character 2}'

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T^(p2) set of the query
        :rtype: List[str]
        """
        return self._s_k_p2(q.replace('*', '').replace('_', ''))
