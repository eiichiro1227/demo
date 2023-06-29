import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from message_app.cvfollow.mail_sender import CVFollowMail


def test_mail_sender():
    client_name = 'belmise'
    record = {
        'mail_address': '020_retargeting_alert-aaaae54dmzt4nhrae2rdheuemy@espalharllcworkspace.slack.com',
        'user_id': 'test_user_id_value',
        'product_type': 'leggings'
    }
    mail = CVFollowMail(client_name, record)
    result = mail.send()

    assert result == True
    print('Check the mail box of test account. If test mail was sent then test is success.')
