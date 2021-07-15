import functools
import os
from typing import List, Set


class SigmaClient:
    """Sigma client implementation."""

    def __init__(
            self,
    ) -> None:
        self.k = None

    def setup(
            self,
            security_parameter: int,
    ) -> (bytes, bytes):
        key: bytes = os.urandom(security_parameter)
        iv: bytes = os.urandom(32)
        self.k = (key, iv)
        return self.k

    def srch_token(
            self,
            q: str,
    ):
        """ TODO: define return type"""
        print('SrchToken')

    def add_token(
            self,
            ind: bytes,
            w: str,
    ):
        """ TODO: define return type"""
        print('AddToken')

    def s_k(
            self,
            w: str,
    ) -> Set[str]:
        """Generates the S_K set for a keyword, according to Zhao and Nishide.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K set of the keyword
        :rtype: Set[str]
        """
        return self._s_k_o(w) | self._s_k_p(w)

    def _s_k_o(
            self,
            w: str,
    ) -> Set[str]:
        """Generates the S_K^(o) set for a keyword.
        Set items are of the form '{position}:{character}'.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K^(o) set of the keyword
        :rtype: Set[str]
        """
        return set([str(n) + ':' + c for n, c in zip(range(1, len(w) + 1), w)])

    def _s_k_p(
            self,
            w: str,
    ) -> Set[str]:
        """Generates the S_K^(p) set for a keyword.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K set of the keyword
        :rtype: Set[str]
        """
        return set(self._s_k_p1(w) | self._s_k_p2(w))

    def _s_k_p1(
            self,
            w: str,
    ) -> Set[str]:
        """Generates the S_K^(p1) set for a keyword.
        Set items are of the form '{occurrence}:{character distance}:{character 1},{character 2}'.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K^(p1) set of the keyword
        :rtype: Set[str]
        """
        pairs = [str(c2 - c1) + ':' + w[c1] + ',' + w[c2] for c1 in range(len(w)) for c2 in range(c1 + 1, len(w))]
        unique_pairs = list(set(pairs))
        pair_count_dict = {pair: pairs.count(pair) for pair in unique_pairs}
        return set([str(count + 1) + ':' + pair for pair in pair_count_dict.keys() for count in
                range(pair_count_dict[pair])])

    def _s_k_p2(
            self,
            w: str,
    ) -> Set[str]:
        """Generates the S_K^(p2) set for a keyword.
        Set items are of the form '{occurrence}:-:{character 1},{character 2}'.

        :param w: The keyword for which the set is to be generated
        :type w: str
        :returns: The S_K^(p2) set of the keyword
        :rtype: Set[str]
        """
        pairs = ['-:' + w[c1] + ',' + w[c2] for c1 in range(len(w)) for c2 in range(c1 + 1, len(w))]
        unique_pairs = list(set(pairs))
        pair_count_dict = {pair: pairs.count(pair) for pair in unique_pairs}
        return set([str(count + 1) + ':' + pair for pair in pair_count_dict.keys() for count in
                range(pair_count_dict[pair])])

    def s_t(
            self,
            q: str,
    ) -> Set[str]:
        """Generates the S_T set for a keyword, according to Zhao and Nishide.

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T set of the query
        :rtype: Set[str]
        """
        return self._s_t_o(q) | self._s_t_p(q)

    def _s_t_o(
            self,
            q: str,
    ) -> Set[str]:
        """Generates the S_T^(o) set for a query.
        Set items are of the form '{position}:{character}' and contain all characters in the query that have a specific
        appearance order, which are all characters (except the _ wildcard), up until the first * wildcard.

        :param q: The query for which the set is to be generated. A string, possibly containing _ and * wildcards
        :type q: str
        :return: The S_T^(o) set of the query
        :rtype: Set[str]
        """
        solid_characters = q.split('*')[0]
        return set([str(c + 1) + ':' + q[c] for c in range(len(solid_characters)) if q[c] != '_'])

    def _s_t_p(
            self,
            q: str,
    ) -> Set[str]:
        """Generates the S_T^(p) set for a keyword.

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T set of the query
        :rtype: Set[str]
        """
        return self._s_t_p1(q) | self._s_t_p2(q)

    def _s_t_p1(
            self,
            q: str,
    ) -> Set[str]:
        """Generates the S_T^(p1) set for a query.
        Set items are of the form '{occurrence}:{distance}:{character 1},{character 2}'

        TODO: investigate what happens with multiple occurrences, as they are now considered per character group pair
        rather than for the set as a whole

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T^(p1) set of the query
        :rtype: Set[str]
        """
        character_groups = (q + '_').replace('_', '_^').replace('*', '*^').split('^')
        # All pairs of neighbouring character groups
        character_group_pairs = [character_groups[c] + character_groups[c + 1] for c in range(len(character_groups) - 1)
                                 if len(character_groups[c]) > 1 and len(character_groups[c + 1]) > 1]
        # Remove all * wildcards as they are not considered for the distance between characters
        character_group_pairs = map(lambda pair: pair.replace('*', ''), character_group_pairs)

        # Generate the character pairs of neighbouring character group pair
        character_pairs = map(lambda pair: self._generate_character_pairs(pair), character_group_pairs)
        return set(functools.reduce(lambda pair_a, pair_b: pair_a + pair_b, character_pairs))

    def _generate_character_pairs(
            self,
            s: str,
    ) -> List[str]:
        """Generates all possible pairs of a string of characters.
        Results are of the form TODO.

        :param s: A string of characters
        :type s: str
        :return: TODO
        :rtype: List[str]
        """
        pairs = [str(c2 - c1) + ':' + s[c1] + ',' + s[c2]
                 for c1 in range(len(s)) if s[c1] != '_'
                 for c2 in range(c1 + 1, len(s)) if s[c2] != '_']
        unique_pairs = list(set(pairs))
        pair_count_dict = {pair: pairs.count(pair) for pair in unique_pairs}
        return [str(count + 1) + ':' + pair for pair in pair_count_dict.keys() for count in
                range(pair_count_dict[pair])]

    def _s_t_p2(
            self,
            q: str,
    ) -> Set[str]:
        """Generates the S_T^(p2) set for a query.
        Set items are of the form '{occurrence}:-:{character 1},{character 2}'

        :param q: The query for which the set is to be generated
        :type q: str
        :returns: The S_T^(p2) set of the query
        :rtype: Set[str]
        """
        return self._s_k_p2(q.replace('*', '').replace('_', ''))
