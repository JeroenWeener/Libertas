# Python imports
import random
import time
from typing import List

# Project imports
from evaluation.evaluation_utils import generate_data, NUMBER_OF_RUNS, ZN_FP_RATE, ZN_KEYWORD_LENGTH, \
    LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH
from libertas.libertas_client import LibertasClient
from libertas.libertas_server import LibertasServer
from libertas_plus.libertas_plus_client import LibertasPlusClient
from libertas_plus.libertas_plus_server import LibertasPlusServer
from zhao_nishide.zn_client import ZNClient
from zhao_nishide.zn_server import ZNServer


SEED_VALUE = 314


class ExactKeywordSearchExperiment:
    def __init__(self):
        index_sizes = [100, 1000, 10000, 100000]

        for index_size in index_sizes:
            random.seed(SEED_VALUE)
            queries = [str(random.randint(0, index_size - 1)).zfill(ZN_KEYWORD_LENGTH) for _ in range(NUMBER_OF_RUNS)]

            print('Running measurements for index size', index_size)

            (client, server) = self.prepare_zn(index_size)
            average_search_time = self.measure_zn(client, server, queries)
            print('ZN:       ', average_search_time)

            (client, server) = self.prepare_libertas(index_size)
            average_search_time = self.measure_libertas(client, server, queries)
            print('Libertas: ', average_search_time)

            (client, server) = self.prepare_libertas_plus(index_size)
            average_search_time = self.measure_libertas_plus(client, server, queries)
            print('Libertas+:', average_search_time)

            print()

    def prepare_zn(
            self,
            data_size: int,
    ) -> (ZNClient, ZNServer):
        client = ZNClient(ZN_FP_RATE, ZN_KEYWORD_LENGTH)
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
        client = LibertasClient(ZNClient(ZN_FP_RATE, ZN_KEYWORD_LENGTH))
        client.setup((LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH))

        server = LibertasServer(ZNServer())
        server.build_index()

        data_set = generate_data(data_size)

        for (ind, w) in data_set:
            add_token = client.add_token(ind, w)
            server.add(add_token)

        return client, server

    def prepare_libertas_plus(
            self,
            data_size: int,
    ) -> (LibertasPlusClient, LibertasPlusServer):
        client = LibertasPlusClient(ZNClient(ZN_FP_RATE, ZN_KEYWORD_LENGTH))
        client.setup((LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH))

        server = LibertasPlusServer(ZNServer())
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
            queries: List[str],
    ) -> float:
        total_time = 0

        for query in queries:
            start_time = time.process_time()

            srch_token = client.srch_token(query)
            server.search(srch_token)

            end_time = time.process_time()
            total_time += end_time - start_time

        return total_time / len(queries)

    def measure_libertas(
            self,
            client: LibertasClient,
            server: LibertasServer,
            queries: List[str],
    ) -> float:
        total_time = 0

        for query in queries:
            start_time = time.process_time()

            srch_token = client.srch_token(query)
            encrypted_results = server.search(srch_token)
            client.dec_search(encrypted_results)

            end_time = time.process_time()
            total_time += end_time - start_time

        return total_time / len(queries)

    def measure_libertas_plus(
            self,
            client: LibertasPlusClient,
            server: LibertasPlusServer,
            queries: List[str],
    ) -> float:
        total_time = 0

        for query in queries:
            start_time = time.process_time()

            srch_token = client.srch_token(query)
            encrypted_results = server.search(srch_token)
            (_, re_add_tokens) = client.dec_search(encrypted_results)
            for re_add_token in re_add_tokens:
                server.add(re_add_token)

            end_time = time.process_time()
            total_time += end_time - start_time

        return total_time / len(queries)


if __name__ == '__main__':
    ExactKeywordSearchExperiment()
