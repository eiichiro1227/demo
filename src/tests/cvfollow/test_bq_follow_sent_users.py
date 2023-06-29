import time
from typing import List
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from bigquery_app.cvfollow.sent_users import BigQueryCVFollowSentUsers
from helpers.datetime_helper import current_datetime



class TestBigQueryCVFollowSentUsers(BigQueryCVFollowSentUsers):
    def __init__(self):
        client_name = 'demo'
        table_name = 'test__user_mail_history'
        super().__init__(client_name, table_name)

        self.original = self.make_filtered_row()

    def make_filtered_row(self, row=None):
        return {
            'timestamp': str(current_datetime()),
            'user_id': 'test_user_id_value11124_3',
            'mail_address': '020_retargeting_alert-aaaae54dmzt4nhrae2rdheuemy@espalharllcworkspace.slack.com',
        }


def exist_test_user(hist: TestBigQueryCVFollowSentUsers, results: List):
    print('START exist_test_user')
    for r in results:
        print('RESULT: ', r)
        if r['mail_address'] == hist.original['mail_address'] and r['user_id'] == hist.original['user_id']:
            return True
    return False


def demo():
    hist = TestBigQueryCVFollowSentUsers()
    hist.add(hist.original)
    print(hist.insert())
    time.sleep(4)

    query = f'SELECT * FROM {hist.path} WHERE DATE(timestamp) = DATE(TIMESTAMP_ADD(CURRENT_TIMESTAMP, INTERVAL 9 HOUR))'
    results = hist.CLIENT.query(query)
    assert exist_test_user(hist, results), 'Failed to regist a test user'
