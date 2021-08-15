# Python imports
import email
import os
import pickle
import pathlib
import re
import string
import time
from email.message import Message
from typing import List, Tuple, TextIO

# Third-party imports
import pandas as pd

# Project imports
from libertas_plus.libertas_plus_client import LibertasPlusClient
from libertas_plus.libertas_plus_server import LibertasPlusServer
from zhao_nishide.zn_client import ZNClient
from zhao_nishide.zn_server import ZNServer


"""Libertas+ evaluation script

Enron dataset .csv file can be found at:
https://www.kaggle.com/yairishalev/enron-top-words-freq-in-emails-subjects-and-body/data?select=emails.csv
Put the file in `/assets` before running this script.
"""

enron_file_path = '../../assets/emails.csv'
dk_pairs_file_path = '../../generated/document_keyword_pairs.txt'
client_dump_file_path = '../../generated/libertas_plus_client_dump'
server_dump_file_path = '../../generated/libertas_plus_server_dump'
zn_client_dump_file_path = '../../generated/zn_client_dump'
zn_server_dump_file_path = '../../generated/zn_server_dump'


def dump_zn(
        client: ZNClient,
        server: ZNServer,
) -> None:
    """Dumps the Zhao and Nishide client and server objects in files to be used for later use.

    :param client: The Zhao and Nishide client to store in a file
    :type client: ZNClient
    :param server: The Zhao and Nishide server to store in a file
    :type server: ZNServer
    :returns: None
    :rtype: None
    """
    with open(zn_client_dump_file_path, 'wb') as zn_client_dump_file:
        pickle.dump(client, zn_client_dump_file)
    with open(zn_server_dump_file_path, 'wb') as zn_server_dump_file:
        pickle.dump(server, zn_server_dump_file)


def load_zn(
) -> Tuple[ZNClient, ZNServer]:
    """Loads the Zhao and Nishide client and server objects from files.

    :returns: Zhao and Nishide client and server
    :rtype: Tuple[ZNClient, ZNServer]
    """
    with open(zn_client_dump_file_path, 'rb') as zn_client_dump_file:
        client = pickle.load(zn_client_dump_file)
    with open(zn_server_dump_file_path, 'rb') as zn_server_dump_file:
        server = pickle.load(zn_server_dump_file)
    return client, server


def dump_libertas(
        client: LibertasPlusClient,
        server: LibertasPlusServer,
) -> None:
    """Dumps the Libertas+ client and server objects in files to be used for later use.

    :param client: The Libertas+ client to store in a file
    :type client: LibertasPlusClient
    :param server: The Libertas+ server to store in a file
    :type server: LibertasPlusServer
    :returns: None
    :rtype: None
    """
    with open(client_dump_file_path, 'wb') as libertas_client_dump_file:
        pickle.dump(client, libertas_client_dump_file)
    with open(server_dump_file_path, 'wb') as libertas_server_dump_file:
        pickle.dump(server, libertas_server_dump_file)


def load_libertas(
) -> Tuple[LibertasPlusClient, LibertasPlusServer]:
    """Loads the Libertas+ client and server objects from files.

    :returns: Libertas+ client and server
    :rtype: Tuple[LibertasPlusClient, LibertasPlusServer]
    """
    with open(client_dump_file_path, 'rb') as libertas_client_dump_file:
        client = pickle.load(libertas_client_dump_file)
    with open(server_dump_file_path, 'rb') as libertas_server_dump_file:
        server = pickle.load(libertas_server_dump_file)
    return client, server


def dump_document_keyword_pairs(
        document_keyword_pairs: List[Tuple[int, str]],
) -> None:
    """Writes document-keyword pairs to a file.

    :param document_keyword_pairs: Document-keyword pairs
    :type document_keyword_pairs: List[Tuple[int, str]]
    :returns: None
    :rtype: None
    """
    file: TextIO = open(dk_pairs_file_path, 'w')
    for (ind, w) in document_keyword_pairs:
        file.write('({0},{1})'.format(str(ind), w) + '\n')


def load_document_keyword_pairs(
) -> List[Tuple[int, str]]:
    """Reads document-keyword pairs from a file.

    :returns: A list of document-keyword pairs
    :rtype: List[Tuple[int, str]]
    """
    file: TextIO = open(dk_pairs_file_path, 'r')
    pairs_text = file.read().split('\n')[:-1]
    pairs = []
    for pair_text in pairs_text:
        ind = int(pair_text.split(',')[0][1:])
        w = pair_text.split(',')[1][:-1]
        pairs.append((ind, w))
    return pairs


def generate_document_keyword_pairs(
) -> List[Tuple[int, str]]:
    """Generates document-keyword pairs for the emails in the Enron data set. Emails are considered documents and the
    words in their content are considered keywords.

    :returns: The generated document-keyword pairs
    :rtype: List[Tuple[int, str]]
    """
    input_rows = 100
    emails_df = pd.read_csv(enron_file_path, nrows=input_rows)

    # Prepare emails dataframe
    messages = list(map(email.message_from_string, emails_df['message']))
    keys = messages[0].keys()
    for key in keys:
        emails_df[key] = [doc[key] for doc in messages]
    emails_df['content'] = list(map(get_text_from_email, messages))

    # Generate document-keyword pairs
    document_keyword_pairs = []
    for email_index in range(1, input_rows):
        if emails_df['X-Folder'][email_index] and 'sent' in emails_df['X-Folder'][email_index]:
            content = parse_text(emails_df['content'][email_index])
            subject = parse_text(emails_df['Subject'][email_index])
            email_parts = content + subject
            for part in email_parts:
                document_keyword_pairs.append((email_index, part))

    return document_keyword_pairs


def parse_text(
        text: str,
) -> List[str]:
    """Parses input text, removing irrelevant words, resulting in a list of relevant words.

    :param text: Input text string
    :type text: str
    :returns: List of relevant words in the input
    :rtype: List[str]
    """
    stop = ('fwd', 'RE', 'FW', 'forward')
    exclude = set(string.punctuation)
    text = text.rstrip()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    return [word for word in text.lower().split() if
            word not in stop and
            word not in exclude and
            not word.isdigit() and
            len(word) > 2
            ]


def get_text_from_email(
        message: Message,
) -> str:
    """Extracts all text from an email.

    :param message: The email as parsed by the email library
    :type message: Message
    :returns: The text in the email
    :rtype: str
    """
    message_parts = []
    for message_part in message.walk():
        if message_part.get_content_type() == 'text/plain':
            message_parts.append(message_part.get_payload().lower())
    return ''.join(message_parts)


if __name__ == '__main__':
    if not os.path.isfile(enron_file_path):
        print('Error: \'/assets/emails.csv\' is not present. Please download the file before running this script.')
    else:
        # Create '/generated' folder
        pathlib.Path('../../generated').mkdir(parents=True, exist_ok=True)

        # Document-keyword pairs generation
        start_time = time.process_time()
        if os.path.isfile(dk_pairs_file_path):
            print('Loading document-keyword pairs in memory...')
            dk_pairs = load_document_keyword_pairs()
        else:
            print('Generating document-keyword pairs from Enron dataset...')
            dk_pairs = generate_document_keyword_pairs()
            dump_document_keyword_pairs(dk_pairs)
        end_time = time.process_time()
        print('Done in ', end_time - start_time, 'seconds')

        # Zhao and Nishide initialization
        start_time = time.process_time()
        if os.path.isfile(zn_client_dump_file_path) and os.path.isfile(zn_server_dump_file_path):
            print('Restoring Zhao and Nishide...')
            zn_client, zn_server = load_zn()
        else:
            print('Initializing Zhao and Nishide...')
            zn_client = ZNClient()
            zn_client.setup(2048)
            zn_server = ZNServer()
            zn_server.build_index()

            print('Adding document-keyword pairs to Zhao and Nishide...')
            for i in range(len(dk_pairs)):
                (d, k) = dk_pairs[i]
                add_token = zn_client.add_token(int.to_bytes(d, byteorder='big', length=1), k)
                zn_server.add(add_token)
                if i % 1000 == 0:
                    progress = i / len(dk_pairs) * 100
                    print(progress, '% in', time.process_time() - start_time, 'seconds')

            dump_zn(zn_client, zn_server)
        end_time = time.process_time()
        print('Done in', end_time - start_time, 'seconds')

        # Libertas+ initialization
        start_time = time.process_time()
        if os.path.isfile(client_dump_file_path) and os.path.isfile(server_dump_file_path):
            print('Restoring Libertas+...')
            libertas_plus_client, libertas_plus_server = load_libertas()
        else:
            print('Initializing Libertas+...')
            libertas_plus_client = LibertasPlusClient(ZNClient())
            libertas_plus_client.setup((256, 2048))
            libertas_plus_server = LibertasPlusServer(ZNServer())
            libertas_plus_server.build_index()

            print('Adding document-keyword pairs to Libertas+...')
            for i in range(len(dk_pairs)):
                (d, k) = dk_pairs[i]
                add_token = libertas_plus_client.add_token(d, k)
                libertas_plus_server.add(add_token)
                if i % 1000 == 0:
                    progress = i / len(dk_pairs) * 100
                    print(progress, '% in', time.process_time() - start_time, 'seconds')

            dump_libertas(libertas_plus_client, libertas_plus_server)
        end_time = time.process_time()
        print('Done in', end_time - start_time, 'seconds')

        # Search
        srch_token = zn_client.srch_token('development')
        results = zn_server.search(srch_token)
        print(list(map(lambda result: int.from_bytes(result, byteorder='big'), results)))

        srch_token = libertas_plus_client.srch_token('development')
        encrypted_results = libertas_plus_server.search(srch_token)
        results, _ = libertas_plus_client.dec_search(encrypted_results)
        print(results)
