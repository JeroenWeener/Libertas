# Python imports
import sys
from typing import List

# Project imports
from libertas_plus.libertas_plus_client import LibertasPlusClient
from libertas_plus.libertas_plus_server import LibertasPlusServer
from src.libertas.libertas_client import LibertasClient
from src.libertas.libertas_server import LibertasServer
from src.zhao_nishide.zn_client import ZNClient
from src.zhao_nishide.zn_server import ZNServer
from utils import underline_start, underline_end

"""Implementations of:

Zhao & Nishide: a DSSE scheme supporting wildcards.
Libertas: a wildcard supporting, backward private, DSSE scheme.
Libertas+: An extension to Libertas, featuring a clean-up procedure, mitigating the storage blow-up due to updates.

Reference paper: https://www.link-to-paper.nl

Author: Jeroen Weener
Created: 15-07-2021
"""


class CLI(object):
    """An interactive command line interface to operate a SSE client-server pair. Supports Libertas, Libertas+ and
    Zhao & Nishide. Data is never actually send over a network. Rather, both client and server are instantiated in the
    same Python environment and share data by passing variables.
    """

    def __init__(
            self,
    ) -> None:
        """Initialize CLI: setup Libertas client and server.

        :returns: None
        :rtype: None
        """
        self.client = None
        self.server = None
        self.scheme_string = None

        # Easy access to printable command line options
        self.add = underline_start + 'a' + underline_end + 'dd'
        self.delete = underline_start + 'd' + underline_end + 'elete'
        self.search = underline_start + 's' + underline_end + 'earch'
        self.reselect = underline_start + 'r' + underline_end + 'eselect'
        self.help = underline_start + 'h' + underline_end + 'elp'
        self.quit = underline_start + 'q' + underline_end + 'uit'

        self.one = underline_start + '1' + underline_end
        self.two = underline_start + '2' + underline_end
        self.three = underline_start + '3' + underline_end

    def query_sse_scheme(
            self,
    ) -> None:
        """Parses user input until a valid SSE scheme is selected

        :returns: None
        :rtype: None
        """
        print('------------')
        print('Pick a DSSE scheme')
        print('------------')
        print('    {0}:    Libertas+'.format(self.one))
        print('    {0}:    Libertas'.format(self.two))
        print('    {0}:    Zhao & Nishide'.format(self.three))
        print('    {0}  Quit the CLI'.format(self.quit))

        error_string = 'Invalid command. Please use \'{0}\', \'{1}\', \'{2}\' or \'{3}\'.' \
            .format(self.one, self.two, self.three, self.quit)

        while True:
            user_input = input('> ')
            input_parts = user_input.split()
            if len(input_parts) == 1:
                operation = input_parts[0].lower()
                if operation == '1':
                    self.init_libertas_plus()
                    break
                elif operation == '2':
                    self.init_libertas()
                    break
                elif operation == '3':
                    self.init_zhao_nishide()
                    break
                elif operation == 'q' or operation == 'quit':
                    sys.exit()
            print(error_string)

    def query_sse_input(
            self,
    ) -> None:
        """Prints available SSE commands and asks for user input continuously.

        :returns: None
        :rtype: None
        """
        self.print_commands()

        # Continuously ask the user for commands
        while True:
            user_input = input('> ')
            self.parse_input(user_input)

    def print_commands(
            self,
    ) -> None:
        """Prints the available commands to the user.

        :returns: None
        :rtype: None
        """
        print('Available commands:')
        print('    {0}    {{document id}} {{keyword}}    Add a document-keyword pair to the database'.format(self.add))
        print('    {0} {{document id}} {{keyword}}    Delete a document-keyword pair from the database'
              .format(self.delete))
        print('    {0} {{query}}                    Search the database. Use \'_\' to indicate any single character \
and \'*\' to indicate 0 or more characters'.format(self.search))
        print('    {0}                          Reselect SSE scheme'.format(self.reselect))
        print('    {0}                              Reprint this information'.format(self.help))
        print('    {0}                              Quit the CLI'.format(self.quit))

    def init_zhao_nishide(
            self,
    ) -> None:
        """Initializes a Z&N client and server.

        :returns: None
        :rtype: None
        """
        self.scheme_string = 'z&n'

        # Client setup
        self.client = ZNClient()
        self.client.setup(2048)

        # Server setup
        self.server = ZNServer()
        self.server.build_index()

    def init_libertas(
            self,
    ) -> None:
        """Initializes a Libertas client and server.

        :returns: None
        :rtype: None
        """
        self.scheme_string = 'libertas'

        # Client setup
        sigma_client = ZNClient()
        self.client = LibertasClient(sigma_client)
        self.client.setup((256, 2048))

        # Server setup
        sigma_server = ZNServer()
        self.server = LibertasServer(sigma_server)
        self.server.build_index()

    def init_libertas_plus(
            self,
    ) -> None:
        """Initializes a Libertas+ client and server.

        :returns: None
        :rtype: None
        """
        self.scheme_string = 'libertas+'

        # Client setup
        sigma_client = ZNClient()
        self.client = LibertasPlusClient(sigma_client)
        self.client.setup((256, 2048))

        # Server setup
        sigma_server = ZNServer()
        self.server = LibertasPlusServer(sigma_server)
        self.server.build_index()

    def parse_input(
            self,
            user_input: str,
    ) -> None:
        """Parses user input and delegates action or displays an error if the command is invalid.

        :param user_input: The input string, type by the user
        :type user_input: str
        :returns: None
        :rtype: None
        """
        error_string = 'Invalid command. Please use \'{0}\', \'{1}\', \'{2}\', \'{3}\', \'{4}\' or \'{5}\'.'\
            .format(self.add, self.delete, self.search, self.reselect, self.help, self.quit)
        input_parts = user_input.split()
        if len(input_parts) > 0:
            operation = input_parts[0].lower()
            if operation == 'a' or operation == 'add':
                self.handle_add(input_parts)
            elif operation == 'd' or operation == 'del' or operation == 'delete':
                self.handle_delete(input_parts)
            elif operation == 's' or operation == 'search':
                self.handle_search(input_parts)
            elif operation == 'r' or operation == 'reselect' or operation == 'reselect':
                self.query_sse_scheme()
                self.print_commands()
            elif operation == 'h' or operation == 'help':
                self.print_commands()
            elif operation == 'q' or operation == 'quit':
                sys.exit()
            else:
                print(error_string)
        else:
            print(error_string)

    def handle_add(
            self,
            input_parts: List[str],
    ) -> None:
        """Handles the add command issued by the user. If the parameters are valid, an add update is added to the
        database. If parameters are invalid, an error is displayed.

        :param input_parts: The words in the user's input
        :type input_parts: List[str]
        :returns: None
        :rtype: None
        """
        if len(input_parts) != 3:
            print('Invalid number of parameters. Expected 2, but received ' + str(len(input_parts) - 1) + '.')
            print('Format: \'{0} {{document id}} {{keyword}}\'.'.format(self.add))
        else:
            try:
                ind = int(input_parts[1])
                w = input_parts[2]
                add_token = self.client.add_token(ind, w)
                self.server.add(add_token)
            except ValueError:
                print('Invalid document id. Expected an integer, received \'' + input_parts[1] + '\'.')

    def handle_delete(
            self,
            input_parts: List[str],
    ) -> None:
        """Handles the delete command issued by the user. If the parameters are valid, a delete update is added to the
        database. If parameters are invalid, an error is displayed.

        :param input_parts: The words in the user's input
        :type input_parts: List[str]
        :returns: None
        :rtype: None
        """
        if len(input_parts) != 3:
            print('Invalid number of parameters. Expected 2, but received ' + str(len(input_parts) - 1) + '.')
            print('Format: \'{0} {{document id}} {{keyword}}'.format(self.delete) + '\'.')
        else:
            try:
                ind = int(input_parts[1])
                w = input_parts[2]
                del_token = self.client.del_token(ind, w)
                self.server.delete(del_token)
            except ValueError:
                print('Invalid document id. Expected an integer, received \'' + input_parts[1] + '\'.')

    def handle_search(
            self,
            input_parts: List[str],
    ) -> None:
        """Handles the search command issued by the user. If the parameters are valid, the matching document identifiers
        will be printed. If parameters are invalid, an error is displayed.

        :param input_parts: The words in the user's input
        :type input_parts: List[str]
        :returns: None
        :rtype: None
        """
        if len(input_parts) != 2:
            print('Invalid number of parameters. Expected 1, but received ' + str(len(input_parts) - 1) + '.')
            print('Format: \'{0} {{query}}'.format(self.search) + '\'.')
        else:
            q = input_parts[1]
            srch_token = self.client.srch_token(q)

            if self.scheme_string == 'z&n':
                results = self.server.search(srch_token)
            else:
                encrypted_results = self.server.search(srch_token)

                if self.scheme_string == 'libertas+':
                    (results, add_tokens) = self.client.dec_search(encrypted_results)

                    # Re-add document-keyword pairs
                    for add_token in add_tokens:
                        self.server.add(add_token)
                else:
                    results = self.client.dec_search(encrypted_results)

            if len(results) == 0:
                print('There are no matching documents.')
            else:
                print('Matching document ids: ' + ''.join(list(map(lambda i: str(i) + ', ', results)))[:-2] + '.')


def main(
) -> None:
    cli = CLI()
    cli.query_sse_scheme()
    cli.query_sse_input()


if __name__ == '__main__':
    main()
