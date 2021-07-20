# Project imports
from src.libertas.libertas_client import Client
from src.libertas.libertas_server import Server
from src.zhao_nishide.zn_client import ZNClient
from src.zhao_nishide.zn_server import ZNServer

"""Libertas

An implementation of Libertas: a wildcard supporting, backward private SSE scheme.

Reference paper: https://www.link-to-paper.nl

Author: Jeroen Weener
Created: 15-07-2021
"""

# Script parameters
security_parameter = 2048

# Setup
sigma_client = ZNClient()
sigma_server = ZNServer()
client = Client(sigma_client)
server = Server(sigma_server)

client.setup(security_parameter)
server.build_index(security_parameter)


# Test

tau_add = sigma_client.add_token(10, 'abcef\0')
sigma_server.add(tau_add)
tau_search = sigma_client.srch_token('*\0')
results = sigma_server.search(tau_search)
print(results)
