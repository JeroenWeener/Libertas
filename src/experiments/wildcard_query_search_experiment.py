# Python imports
import math
import random
import time
import timeit

# Third-party imports
from typing import List, Tuple

# Project imports
from experiments.experiment_utils import generate_data, ZN_FP_RATE, KEYWORD_LENGTH, LIBERTAS_KEY_LENGTH, \
    ZN_KEY_LENGTH, SEED_VALUE, INSTANCES, QUERIES, ITERATIONS
from libertas.libertas_client import LibertasClient
from libertas.libertas_server import LibertasServer
from zhao_nishide.zn_client import ZNClient
from zhao_nishide.zn_server import ZNServer


class WildcardQuerySearchExperiment:
    def __init__(
            self,
    ) -> None:
        print('--- Wildcard query search experiment ---')
        random.seed(SEED_VALUE)
        start_time = time.process_time()

        index_size = 10000
        data_set = generate_data(index_size)

        matching_keywords_array = [1, 10, 100, 1000, 10000]
        for matching_keywords in matching_keywords_array:
            print('Running measurements for', matching_keywords, 'matching',
                  'keyword' if matching_keywords == 1 else 'keywords')

            number_of_wildcards = int(math.log10(matching_keywords))
            search_times_zn = []
            search_times_lib = []

            for instance_number in range(INSTANCES):
                print('Running instance', instance_number)
                (client_zn, server_zn, client_lib, server_lib) = self.prepare_schemes(data_set)

                queries = [str(random.randint(0, index_size - 1)).zfill(KEYWORD_LENGTH) for _ in range(QUERIES)]
                queries = map(lambda q: q[:KEYWORD_LENGTH - number_of_wildcards] + '_' * number_of_wildcards, queries)

                for query in queries:
                    search_times_lib.append(self.measure_libertas(client_lib, server_lib, query))
                    search_times_zn.append(self.measure_zn(client_zn, server_zn, query))

                print('Taking', time.process_time() - start_time, 'seconds')

            print('ZN:      ', list(map(lambda t: '{:.3f}'.format(t), search_times_zn)))
            print('Libertas:', list(map(lambda t: '{:.3f}'.format(t), search_times_lib)))

            print('ZN   avg.:', sum(search_times_zn) / len(search_times_zn))
            print('Lib. avg.:', sum(search_times_lib) / len(search_times_lib))

    def prepare_schemes(
            self,
            data_set: List[Tuple[int, str]],
    ) -> (ZNClient, ZNServer, LibertasClient, LibertasServer):
        client_zn = ZNClient(ZN_FP_RATE, KEYWORD_LENGTH)
        client_zn.setup(ZN_KEY_LENGTH)
        server_zn = ZNServer()
        server_zn.build_index()

        client_lib = LibertasClient(ZNClient(ZN_FP_RATE, KEYWORD_LENGTH))
        client_lib.setup((LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH))
        # Set the key of the underlying ZN scheme to be the same as the ZN scheme. As the key greatly influences the
        # search time due to the nature of the search operation, we require them to be equal for a fair performance
        # comparison.
        client_lib.sigma.k = client_zn.k
        server_lib = LibertasServer(ZNServer())
        server_lib.build_index()

        for (ind, w) in data_set:
            add_token = client_zn.add_token(ind, w)
            server_zn.add(add_token)

            add_token = client_lib.add_token(ind, w)
            server_lib.add(add_token)

        return client_zn, server_zn, client_lib, server_lib

    def measure_zn(
            self,
            zn_client: ZNClient,
            zn_server: ZNServer,
            query: str,
    ) -> float:
        def time_zn(
                server: ZNServer,
                search_token: Tuple[List[int], List[bytes]],
        ) -> None:
            server.search(search_token)

        srch_token = zn_client.srch_token(query)
        t = timeit.Timer(lambda: time_zn(zn_server, srch_token))
        return t.timeit(ITERATIONS) / ITERATIONS

    def measure_libertas(
            self,
            lib_client: LibertasClient,
            lib_server: LibertasServer,
            query: str,
    ) -> float:
        def time_lib(
                client: LibertasClient,
                server: LibertasServer,
                search_token: Tuple[List[int], List[bytes]],
        ) -> None:
            encrypted_results = server.search(search_token)
            client.dec_search(encrypted_results)

        srch_token = lib_client.srch_token(query)
        t = timeit.Timer(lambda: time_lib(lib_client, lib_server, srch_token))
        return t.timeit(ITERATIONS) / ITERATIONS
