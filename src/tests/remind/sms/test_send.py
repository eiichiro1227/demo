import pytest
from dataclasses import dataclass, field
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from message_app.remind.sms_sender import RemindSMS


@dataclass
class Case:
    client: str = 'belmise'
    mail:str = 'emata@espalhar.net'
    user_id:str = 'test_user_id_value'
    phone:str = '080-2814-8359'
    product_type: str = 'corset'
    sms_item_list: list = field(default_factory=list)
    expected: bool = True


default = Case()

# default
case1 = (
    default.client,
    default.mail,
    default.user_id,
    default.phone,
    default.product_type,
    # default.sms_item_list,
    ['corset', 'leggings'],
    default.expected
)

# 1. non use '-' ; 2. all product allow for sms
case2_tmp = Case(
    mail='020_retargeting_alert-aaaae54dmzt4nhrae2rdheuemy@espalharllcworkspace.slack.com',
    phone='00028148359',
    # sms_item_list=[False],
    expected=False
)
case2 = (
    default.client,
    case2_tmp.mail,
    default.user_id,
    case2_tmp.phone,
    default.product_type,
    case2_tmp.sms_item_list,
    case2_tmp.expected
)

# invalid character
case3_tmp = Case(
    mail='$emata@espalhar.net',
    phone='080814835',
    expected=False
)
case3 = (
    default.client,
    case3_tmp.mail,
    default.user_id,
    case3_tmp.phone,
    default.product_type,
    case3_tmp.sms_item_list,
    case3_tmp.expected
)


# not allowed item
case4_tmp = Case(
    sms_item_list=['tights', 'leggings'],
    expected=False
)
case4 = (
    default.client,
    default.mail,
    default.user_id,
    default.phone,
    default.product_type,
    case4_tmp.sms_item_list,
    case4_tmp.expected
)

cases = [
    case1,
    # case2,
    # case3,
    # case4
    ]


@pytest.mark.parametrize('client,mail,user_id,phone,product_type,sms_item_list,expected', cases)
def test_mail_sender(client, mail, user_id, phone, product_type, sms_item_list, expected):
    sms = RemindSMS(
        client_name=client,
        record={
            'mail_address': mail,
            'user_id': user_id,
            'phone_number': phone,
            'product_type': product_type
        },
        sms_item_list=sms_item_list
    )
    if not sms.is_allow_send:
        assert expected == False
        return
    else:
        result = sms.send()
        assert result == expected


if __name__ == '__main__':
    test_mail_sender(
    default.client,
    default.mail,
    default.user_id,
    default.phone,
    default.product_type,
    case4_tmp.sms_item_list,
    case4_tmp.expected
    )
