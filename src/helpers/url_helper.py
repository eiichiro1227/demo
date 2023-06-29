from urllib.parse import urlparse
import urllib

def queries(url: str):
    query_str = urlparse(url).query
    queries = urllib.parse.parse_qs(query_str)
    keys = list(queries.keys())
    values = [q[0] for q in queries.values()]
    return dict(zip(keys, values))

