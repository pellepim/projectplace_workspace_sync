import collections
import db
from models.document import Document
from models.container import Container


SearchResult = collections.namedtuple(
    'SearchResult',
    'type id name description location_identifier rank'
)


def container_search(query_tokens) -> [SearchResult]:
    match_query = ''
    for token in query_tokens:
        match_query += '%s* ' % token

    results = collections.defaultdict(int)

    with db.DBConnection() as dbconn:
        for row in dbconn.fetchall(
                '''
                select id, rank from search where name match ? and type = 'cont' order by rank
                ''', (match_query,)
        ):
            results[row[0]] += row[1]

        for row in dbconn.fetchall(
                '''
                select id, rank from search where description match ? and type = 'cont' order by rank
                ''', (match_query,)
        ):
            results[row[0]] += row[1]

    search_results = []

    for result_id, rank in results.items():
        container = Container.get_by_id(int(result_id))
        search_results.append(SearchResult('container', container.id, container.name, container.description, '', rank))

    search_results.sort(key=lambda x: x.rank)

    return search_results


def document_search(query_tokens) -> [SearchResult]:
    match_query = ''
    for token in query_tokens:
        match_query += '%s* ' % token

    results = collections.defaultdict(int)

    with db.DBConnection() as dbconn:
        for row in dbconn.fetchall(
            '''
            select id, rank from search where name match ? and type = 'doc' order by rank
            ''', (match_query,)
        ):
            results[row[0]] += row[1]

        for row in dbconn.fetchall(
            '''
            select id, rank from search where description match ? and type = 'doc' order by rank
            ''', (match_query,)
        ):
            results[row[0]] += row[1]

    search_results = []

    for result_id, rank in results.items():
        document = Document.get_by_id(int(result_id))
        search_results.append(SearchResult('document', document.id, document.name, document.description, '', rank))

    return search_results


def get_results(query, include_documents=True, include_containers=True, include_urls=True) -> [SearchResult]:
    query_tokens = query.replace('.', ' ').split(' ')
    search_result = []
    if include_documents:
        search_result += document_search(query_tokens)
    if include_containers:
        search_result += container_search(query_tokens)

    search_result.sort(key=lambda x: x.rank)
    return search_result
