# Python imports
from typing import Dict, List

# Project imports
from src.libertas.libertas_client import LibertasClient
from src.utils import EncryptedUpdate, Update, Op, AddToken


class LibertasPlusClient(LibertasClient):
    """Libertas+ client implementation.

    Libertas+ is an extension to Libertas, as it features a clean-up procedure to mitigate storage blow-up due to
    updates. It uses a wildcard supporting SSE scheme internally. In addition to the security guarantees and
    functionality provided by the underlying scheme, Libertas+ provides Update Pattern Revealing Backward Privacy.
    """

    def dec_search(
            self,
            r_star: List[EncryptedUpdate],
    ) -> (List[int], List[AddToken]):
        """Decrypts encrypted results received from the server and determines which document identifiers are still
        relevant for the query. Document identifiers are relevant when there is a keyword-document pair that is
        added, but not deleted afterwards.

        As part of the clean-up protocol, the updates sent by the server are deleted there. Therefore, we need to re-add
        the document-keyword pairs that should still be in the index. Because of this, we additionally return add tokens
        for all document-keyword pairs.

        :param r_star: A list of encrypted results
        :type r_star: List[bytes]
        :returns: A list of document identifiers matching with the initial query and a list of add tokens to re-add
        relevant document-keyword pairs
        :rtype: List[int], List[AddTokens]
        """
        # Decrypt r_star and sort it according to timestamp t
        decrypted_updates: List[Update] = list(map(lambda e: self._decrypt_update(e), r_star))
        decrypted_updates.sort(key=lambda x: x[0])

        keyword_documents_dict: Dict[str, List[int]] = {}
        for update in decrypted_updates:
            # Unpack entry (see utils.Update)
            (t, op, ind, w) = update

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

        # Construct add tokens for document-keyword pairs that should be in the index
        re_add_tokens: List[AddToken] = []
        for w in keyword_documents_dict.keys():
            for ind in keyword_documents_dict[w]:
                re_add_token = self.add_token(ind, w)
                re_add_tokens.append(re_add_token)

        # Combine the ind values for all keywords and remove duplicates
        results = [ind for sub_results in keyword_documents_dict.values() for ind in sub_results]

        return list(set(results)), re_add_tokens
