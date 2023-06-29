import sys
from bigquery_app.cvfollow.target_users import BigqueryTargetUsers
from bigquery_app.cvfollow.sent_users import BigQueryCVFollowSentUsers
from message_app.cvfollow.mail_sender import CVFollowMail


client_name = sys.argv[1]
target = BigqueryTargetUsers(client_name)
hist = BigQueryCVFollowSentUsers(client_name)

records = target.select()
for row in records:
    result = CVFollowMail(client_name, row).send()
    if result:
        hist.add(row)
hist.insert(hist.rows_for_bq)
