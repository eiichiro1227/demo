import pytest
from dataclasses import dataclass
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from message_app.remind.mail_sender import RemindMail


@dataclass
class Case:
    client: str = 'teinei'
    mail:str = 'emata@espalhar.net'
    user_id:str = 'test_user_id_value'
    product: str = 'main'
    expected: bool = True


default = Case()

# default
case1 = (
    default.client,
    default.mail,
    default.user_id,
    default.product,
    default.expected
)

# contain ' ', ' ', '＠'
case2_tmp = Case(
    mail='0 20_retargeting_alert-aaaae54dmzt4nhrae2rdheuemy＠espalharllcworkspace.slack.co m',
    product='waitless_ss_980_2'
)
case2 = (
    default.client,
    case2_tmp.mail,
    default.user_id,
    case2_tmp.product,
    default.expected
)
# invalid character
case3_tmp = Case(
    mail='0 20_retargeting_alert-aaaae54dmzt4nhrae2rdheuemy＠ espalharllcworkspace.slack.com',
    product='gyutto'
)
case3 = (
    default.client,
    case3_tmp.mail,
    default.user_id,
    case3_tmp.product,
    default.expected
)
# invalid character
case4_tmp = Case(
    mail='emata@espalharnet',
    expected=False
)
case4 = (
    default.client,
    case4_tmp.mail,
    default.user_id,
    default.product,
    case4_tmp.expected
)

# AssertionError: test_mail_sender.py Mail not to sent due to out of scope product type: "xxxx".
# case5_tmp = Case(
#     product='xxxx',
#     expected=False
# )
# case5 = (
#     default.client,
#     default.mail,
#     default.user_id,
#     case5_tmp.product,
#     case5_tmp.expected
# )

cases = [
    case1,
    # case2,
    # case3,
    # case4,
    # case5
]

@pytest.mark.parametrize('client,mail,user_id,product,expected', cases)
def test_mail_sender(client, mail, user_id, product, expected):
    result1 = RemindMail(
        client_name=client,
        record={
            'mail_address': mail,
            'user_id': user_id,
            'product_type': product
        }
    ).send()
    assert result1 == expected

default.client
RemindMail(
        client_name=default.client,
        record={
            'mail_address': default.mail,
            'user_id': default.user_id,
            'product_type': default.product
        }
    ).send()
