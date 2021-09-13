# Python imports
import copy
import random
import time

# Project imports
from evaluation.evaluation_utils import generate_data, NUMBER_OF_RUNS, ZN_FP_RATE, KEYWORD_LENGTH, \
    LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH
from libertas.libertas_client import LibertasClient
from libertas.libertas_server import LibertasServer
from libertas_plus.libertas_plus_client import LibertasPlusClient
from libertas_plus.libertas_plus_server import LibertasPlusServer
from zhao_nishide.zn_client import ZNClient
from zhao_nishide.zn_server import ZNServer

SEED_VALUE = 314


class CleanUpProcedure:
    def __init__(self):
        deletions_array = range(0, 11000, 1000)
        index_size = 10000

        random.seed(SEED_VALUE)

        for number_of_deletions in deletions_array:
            queries = [str(random.randint(0, index_size - 1)).zfill(KEYWORD_LENGTH) for _ in range(NUMBER_OF_RUNS)]

            print('Running measurements for', number_of_deletions, 'deletions')

            (client, server) = self.prepare_libertas(index_size, number_of_deletions)
            total_search_time = 0
            for query in queries:
                client_copy = copy.deepcopy(client)
                server_copy = copy.deepcopy(server)
                total_search_time += self.measure_libertas(client_copy, server_copy, query)
            print('Libertas:       ', total_search_time / len(queries))

            (client, server) = self.prepare_libertas_plus(index_size, number_of_deletions)
            total_search_time_first = 0
            total_search_time_second = 0
            for query in queries:
                client_copy = copy.deepcopy(client)
                server_copy = copy.deepcopy(server)
                total_search_time_first += self.measure_libertas_plus(client_copy, server_copy, query)
                total_search_time_second += self.measure_libertas_plus(client_copy, server_copy, query)
            print('Libertas+:      ', total_search_time_first / len(queries))
            print('Libertas+ (2nd):', total_search_time_second / len(queries))

            print()

    def prepare_libertas(
            self,
            data_size: int,
            number_of_deletions: int,
    ) -> (LibertasClient, LibertasServer):
        client = LibertasClient(ZNClient(ZN_FP_RATE, KEYWORD_LENGTH))
        client.setup((LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH))

        server = LibertasServer(ZNServer())
        server.build_index()

        data_set = generate_data(data_size)

        for (ind, w) in data_set:
            add_token = client.add_token(ind, w)
            server.add(add_token)

        for (ind, w) in data_set[:number_of_deletions]:
            del_token = client.del_token(ind, w)
            server.delete(del_token)

        return client, server

    def prepare_libertas_plus(
            self,
            data_size: int,
            number_of_deletions: int,
    ) -> (LibertasPlusClient, LibertasPlusServer):
        client = LibertasPlusClient(ZNClient(ZN_FP_RATE, KEYWORD_LENGTH))
        client.setup((LIBERTAS_KEY_LENGTH, ZN_KEY_LENGTH))

        server = LibertasPlusServer(ZNServer())
        server.build_index()

        data_set = generate_data(data_size)

        for (ind, w) in data_set:
            add_token = client.add_token(ind, w)
            server.add(add_token)

        for (ind, w) in data_set[:number_of_deletions]:
            del_token = client.del_token(ind, w)
            server.delete(del_token)

        return client, server

    def measure_libertas(
            self,
            client: LibertasClient,
            server: LibertasServer,
            query: str,
    ) -> float:
        start_time = time.process_time()

        srch_token = client.srch_token(query)
        encrypted_results = server.search(srch_token)
        client.dec_search(encrypted_results)

        end_time = time.process_time()
        return end_time - start_time

    def measure_libertas_plus(
            self,
            client: LibertasPlusClient,
            server: LibertasPlusServer,
            query: str,
    ) -> float:
        start_time = time.process_time()

        srch_token = client.srch_token(query)
        encrypted_results = server.search(srch_token)
        (_, re_add_tokens) = client.dec_search(encrypted_results)
        for re_add_token in re_add_tokens:
            server.add(re_add_token)

        end_time = time.process_time()
        return end_time - start_time


if __name__ == '__main__':
    CleanUpProcedure()
