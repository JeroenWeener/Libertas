from client import Client
from server import Server
from sigma_client import SigmaClient
from sigma_server import SigmaServer

"""Libertas

An implementation of Libertas: a wildcard supporting, backward private SSE scheme.

Reference paper: https://www.link-to-paper.nl

Author: Jeroen Weener
Created: 15-07-2021
"""

# Script parameters
security_parameter = 2048

# Setup
sigma_client = SigmaClient()
sigma_server = SigmaServer()
client = Client(sigma_client)
server = Server(sigma_server)

client.setup(security_parameter)
server.build_index(security_parameter)

# # Add '(1, keyword1)'
# tau_add = client.add_token(1, 'keyword1')
# server.add(tau_add)
#
# # Search 'keyword1'
# srch_token = client.srch_token('keyword1')
# r_star = server.search(srch_token)
# r = client.dec_search(r_star)
# print(r)
