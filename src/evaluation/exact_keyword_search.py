# Python imports
import random
import timeit

# Third-party imports
import matplotlib.pyplot as plt

# Project imports
from evaluation.evaluation_utils import generate_data, NUMBER_OF_RUNS, ZN_FP_RATE, KEYWORD_LENGTH, \
    LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH
from libertas.libertas_client import LibertasClient
from libertas.libertas_server import LibertasServer
from zhao_nishide.zn_client import ZNClient
from zhao_nishide.zn_server import ZNServer

SEED_VALUE = 314


class ExactKeywordSearchExperiment:
    def __init__(
            self,
    ) -> None:
        index_sizes = [100, 1000, 10000, 100000]

        random.seed(SEED_VALUE)

        for index_size in index_sizes:
            queries = [str(random.randint(0, index_size - 1)).zfill(KEYWORD_LENGTH) for _ in range(10)]

            print('Running measurements for index size', index_size)

            (client, server) = self.prepare_libertas(index_size)
            search_times_lib = []
            for query in queries:
                search_times_lib.append(self.measure_libertas(client, server, query))

            (client, server) = self.prepare_zn(index_size)
            search_times_zn = []
            for query in queries:
                search_times_zn.append(self.measure_zn(client, server, query))

            print('ZN:       ', list(map(lambda time: '{:.3f}'.format(time), search_times_zn)))
            print('Libertas: ', list(map(lambda time: '{:.3f}'.format(time), search_times_lib)))

            plt.scatter(range(len(search_times_zn)), search_times_zn, label='Zhao & Nishide')
            plt.scatter(range(len(search_times_lib)), search_times_lib, label='Libertas')
            plt.legend()
            plt.show()

            print()

    def prepare_zn(
            self,
            data_size: int,
    ) -> (ZNClient, ZNServer):
        client = ZNClient(ZN_FP_RATE, KEYWORD_LENGTH)
        client.setup(ZN_KEY_LENGTH)

        server = ZNServer()
        server.build_index()

        data_set = generate_data(data_size)

        for (ind, w) in data_set:
            add_token = client.add_token(ind, w)
            server.add(add_token)

        return client, server

    def prepare_libertas(
            self,
            data_size: int,
    ) -> (LibertasClient, LibertasServer):
        client = LibertasClient(ZNClient(ZN_FP_RATE, KEYWORD_LENGTH))
        client.setup((LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH))

        server = LibertasServer(ZNServer())
        server.build_index()

        data_set = generate_data(data_size)

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
        t = timeit.Timer(lambda: self.test_zn(server, srch_token))
        return t.timeit(NUMBER_OF_RUNS) / NUMBER_OF_RUNS

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
        t = timeit.Timer(lambda: self.test_lib(client, server, srch_token))
        return t.timeit(NUMBER_OF_RUNS) / NUMBER_OF_RUNS

    def test_lib(
            self,
            client,
            server,
            srch_token,
    ) -> None:
        encrypted_results = server.search(srch_token)
        client.dec_search(encrypted_results)


if __name__ == '__main__':
    ExactKeywordSearchExperiment()
