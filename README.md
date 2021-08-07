[![Test workflow](https://github.com/JeroenWeener/Libertas/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/JeroenWeener/Libertas/actions/workflows/python-app.yml)

# Libertas+
This repository contains Python implementations of Libertas+, Libertas [[1]](https://www.link-to-paper.nl) and Z&N [[2]](https://link.springer.com/chapter/10.1007/978-3-319-46298-1_18).
 
Libertas(+) is a novel dynamic symmetric searchable encryption scheme in the single-user environment that is backward-private and allows for wildcard queries.

## Installation
```bash
pip install -r Libertas/requirements.txt
```

The code comes with a command line interface where users can run the implemented schemes locally, showcasing the add, delete and search functionalities.
```
python3 Libertas
```

## Usage
To run Libertas(+) with a different wildcard supporting scheme, implement `SigmaClient` and `SigmaServer` (see `ZNClient` and `ZNServer` for an example). An example for Libertas is provided below.
```python
from src.libertas.libertas_client import LibertasClient
from src.libertas.libertas_server import LibertasServer
from src.wildcard_scheme.wildcard_client import WildcardClient
from src.wildcard_scheme.wildcard_server import WildcardServer


# Initialize Libertas client
wildcard_client = WildcardClient()
client = LibertasClient(wildcard_client)
security_parameter = (256, 2048)
client.setup(security_parameter)

# Initialize Libertas server
wildcard_server = WildcardServer()
server = LibertasServer(wildcard_server)
server.build_index()

# Add document-keyword pair
(ind, w) = (1, 'keyword')
add_token = client.add_token(ind, w)
server.add(add_token)

# Search keyword
w = 'keyword'
search_token = client.srch_token(w)
documents = server.search(search_token)

# Search wildcard query
q = 'k_y*'
srch_token = client.srch_token(q)
documents = server.search(srch_token)

# Delete document-keyword pair
(ind, w) = (1, 'keyword')
del_token = client.del_token(ind, w)
server.delete(del_token)
```

## Testing
Several tests are provided. These are run automatically by GitHub Actions. To run them locally, run:
```bash
pytest Libertas
```

## Contributing
Pull requests containing documented and tested code are welcome. Feel free to submit improvements, implementations of other wildcard schemes or otherwise relevant extensions to the code. For major changes, please open an issue first to discuss what you would like to change.

## License
The code is available under the [MIT](https://choosealicense.com/licenses/mit/) license.
