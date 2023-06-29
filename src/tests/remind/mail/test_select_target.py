import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from bigquery_app.remind.mail_selector import MailSelector


def test_bq_target_users():
    client = MailSelector(client_name='demo')
    records = client.select(minutes_newer_than=-6000, minutes_older_than=6000)
    assert str(type(records)) == "<class 'google.cloud.bigquery.job.query.QueryJob'>", 'This is not queryJob'
    for row in records:
        print(row)
        assert str(
            type(row)) == "<class 'google.cloud.bigquery.table.Row'>", 'This is not table.Row'
        assert row.get('user_id'), 'user_id does not exist'
        assert row.get('mail_address'), 'mail_address does not exist'
        assert len(row['user_id']) >= 10, 'Correct user_id does not exist'
        assert '@' in row['mail_address'], 'Correct mail_address does not exist'
