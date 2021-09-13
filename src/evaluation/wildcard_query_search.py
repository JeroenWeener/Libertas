# Python imports
import cProfile
import math
import pstats
import random
import timeit

# Third-party imports
import matplotlib.pyplot as plt
from typing import List, Tuple

# Project imports
from evaluation.evaluation_utils import generate_data, NUMBER_OF_RUNS, ZN_FP_RATE, KEYWORD_LENGTH, \
    LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH
from libertas.libertas_client import LibertasClient
from libertas.libertas_server import LibertasServer
from zhao_nishide.zn_client import ZNClient
from zhao_nishide.zn_server import ZNServer

SEED_VALUE = 314


class WildcardQuerySearchExperiment:
    def __init__(
            self,
    ) -> None:
        matching_keywords_array = [1, 10, 100, 1000, 10000]
        index_size = 100 #10000

        random.seed(SEED_VALUE)

        for matching_keywords in matching_keywords_array:
            queries = [str(random.randint(0, index_size - 1)).zfill(KEYWORD_LENGTH) for _ in range(10)]
            number_of_wildcards = int(math.log10(matching_keywords))
            queries = list(map(lambda q: q[:KEYWORD_LENGTH - number_of_wildcards] + '_' * number_of_wildcards, queries))

            print('Running measurements for', matching_keywords, 'matching',
                  'keyword' if matching_keywords == 1 else 'keywords')

            data_set = generate_data(index_size)
            (client_zn, server_zn, client_lib, server_lib) = self.prepare_schemes(data_set)
            search_times_zn = []
            search_times_lib = []
            for query in queries:
                search_times_lib.append(self.measure_libertas(client_lib, server_lib, query))
                search_times_zn.append(self.measure_zn(client_zn, server_zn, query))

            print('ZN:       ', list(map(lambda time: '{:.3f}'.format(time), search_times_zn)))
            print('Libertas: ', list(map(lambda time: '{:.3f}'.format(time), search_times_lib)))

            plt.scatter(range(len(search_times_zn)), search_times_zn, label='Zhao & Nishide')
            plt.scatter(range(len(search_times_lib)), search_times_lib, label='Libertas')
            plt.legend()
            plt.show()

            print()

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
        client_lib.sigma.k = client_zn.k  # Overwrite the key of ZN so it is exactly the same
        server_lib = LibertasServer(ZNServer())
        server_lib.build_index()

        for (ind, w) in data_set:
            add_token = client_zn.add_token(ind, w)
            server_zn.add(add_token)

            add_token = client_lib.add_token(ind, w)
            server_lib.add(add_token)

        return client_zn, server_zn, client_lib, server_lib

    def prepare_libertas(
            self,
            data_set: List[Tuple[int, str]],
    ) -> (LibertasClient, LibertasServer):
        client = LibertasClient(ZNClient(ZN_FP_RATE, KEYWORD_LENGTH))
        client.setup((LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH))

        server = LibertasServer(ZNServer())
        server.build_index()

        for (ind, w) in data_set:
            add_token = client.add_token(ind, w)
            server.add(add_token)

        return client, server

    def measure_zn(
            self,
            client: ZNClient,
            server: ZNServer,
            query: str,
    ) -> float:
        srch_token = client.srch_token(query)
        # print('111111111111111111111111111111111111111111111111')
        # profiler = cProfile.Profile()
        # profiler.enable()
        # for i in range(100):
        #     self.test_zn(server, srch_token)
        # profiler.disable()
        # stats = pstats.Stats(profiler).sort_stats('cumtime')
        # stats.print_stats()
        t = timeit.Timer(lambda: self.test_zn(server, srch_token))
        return t.timeit(NUMBER_OF_RUNS) / NUMBER_OF_RUNS
        # return 1

    def test_zn(
            self,
            server,
            srch_token,
    ) -> None:
        server.search(srch_token)

    def measure_libertas(
            self,
            client: LibertasClient,
            server: LibertasServer,
            query: str,
    ) -> float:
        srch_token = client.srch_token(query)
        # print('2222222222222222222222222222222222222222222')
        # profiler = cProfile.Profile()
        # profiler.enable()
        # for i in range(100):
        #     self.test_lib(client, server, srch_token)
        # profiler.disable()
        # stats = pstats.Stats(profiler).sort_stats('cumtime')
        # stats.print_stats()
        t = timeit.Timer(lambda: self.test_lib(client, server, srch_token))
        return t.timeit(NUMBER_OF_RUNS) / NUMBER_OF_RUNS
        # return 1

    def test_lib(
            self,
            client,
            server,
            srch_token,
    ) -> None:
        encrypted_results = server.search(srch_token)
        client.dec_search(encrypted_results)


if __name__ == '__main__':
    WildcardQuerySearchExperiment()
