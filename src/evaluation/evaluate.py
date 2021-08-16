# Python imports
import email
import math
import os
import pickle
import pathlib
import random
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
queries_file_path = '../../generated/queries.txt'
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


def dump_queries(
        queries: List[str],
) -> None:
    """Writes queries to a file.

    :param queries: Queries
    :type queries: List[str]
    :returns: None
    :rtype: None
    """
    file: TextIO = open(queries_file_path, 'w')
    for query in queries:
        file.write(query + '\n')


def load_queries(
) -> List[str]:
    """Read queries from a file.

    :returns: A list of queries
    :rtype: List[str]
    """
    file: TextIO = open(queries_file_path, 'r')
    return file.read().split('\n')[:-1]


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


def generate_queries(
        keywords: List[str],
) -> List[str]:
    """Generates queries based off a list of keywords.

    Queries are generated as follows:
    - Decide the number of wildcards randomly from 0 to ceil(l/5), where l is the length of the keyword
    - If there should be n wildcards, divide the keyword in n equal parts
    - for every part, pick a random position and a random wildcard (_ or *)
        - for every _ wildcard, replace the character at the position with _
        - for every * wildcard, insert the * wildcard between characters at the position
    - consume a random number of characters left and right of * wildcards, considering the intermediate query as a
      whole

    :param keywords: A list of keywords to generate queries from
    :type keywords: List[str]
    :returns: A list of queries
    :rtype: List[str]
    """
    queries = []
    for keyword in keywords:
        number_of_wildcards = random.randint(0, math.ceil(len(keyword) / 5))
        if number_of_wildcards == 0:
            queries.append(keyword)
        else:
            part_length = math.ceil(len(keyword) / number_of_wildcards)
            parts = [keyword[n:n + part_length] for n in range(0, len(keyword), part_length)]
            query = ''
            for part in parts:
                wildcard_type = random.randint(0, 1)
                if wildcard_type == 0:
                    position = random.randint(0, len(part) - 1)
                    part = part[:position] + '_' + part[position + 1:]
                else:
                    position = random.randint(0, len(part))
                    part = part[:position] + '*' + part[position:]
                query += part

            # Consume a random number of characters surrounding * wildcards
            xs = query.split('*')
            for i in range(0, len(xs) - 1):
                left = xs[i]
                wildcard_index = left.find('_')
                left = left[:random.randint(wildcard_index + 1, len(left))]

                right = xs[i + 1]
                wildcard_index = right.find('_')
                if wildcard_index == -1:
                    right = right[random.randint(0, len(right)):]
                else:
                    right = right[random.randint(0, wildcard_index):]

                xs = xs[:i] + [left] + [right] + xs[i + 2:]

            query = '*'.join(xs)
            queries.append(query)

    return queries


def start_evaluation(
) -> None:
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
        print()

        # Query generation
        start_time = time.process_time()
        if os.path.isfile(queries_file_path):
            print('Loading queries in memory...')
            queries = load_queries()
        else:
            print('Generating queries from document-keyword pairs')
            queries = generate_queries(list(set(map(lambda pair: pair[1], dk_pairs))))
            dump_queries(queries)
        end_time = time.process_time()
        print('Done in', end_time - start_time, 'seconds')
        print()

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
                add_token = zn_client.add_token(d, k)
                zn_server.add(add_token)
                if i % 1000 == 0:
                    progress = i / len(dk_pairs) * 100
                    print(progress, '% in', time.process_time() - start_time, 'seconds')

            dump_zn(zn_client, zn_server)
        end_time = time.process_time()
        print('Done in', end_time - start_time, 'seconds')
        print()

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
        print()

        # Search
        srch_token = zn_client.srch_token('development')
        results = zn_server.search(srch_token)
        print(results)

        srch_token = libertas_plus_client.srch_token('development')
        encrypted_results = libertas_plus_server.search(srch_token)
        results, _ = libertas_plus_client.dec_search(encrypted_results)
        print(results)


if __name__ == '__main__':
    start_evaluation()
    # q = generate_queries(
    #     ['testtest', 'testtest', 'testtest', 'testtest', 'testtest', 'testtest', 'testtest', 'testtest',
    #      'testtest', 'testtest', 'testtest', 'testtest', 'testtest', 'testtest', 'testtest', 'testtest',
    #      'testtest', 'testtest', 'testtest', 'testtest', 'testtest', 'testtest', 'testtest', 'testtest', ])
    # print(q)
