import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from bigquery_app.cvfollow.target_users import BigqueryTargetUsers


def test_bq_target_users():
    client_name = 'belmise'
    handler = BigqueryTargetUsers(client_name)
    rows = handler.select()
    print(list(rows))
    assert len(list(rows)) > 0, 'There is no data.'


test_bq_target_users()
