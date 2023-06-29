from message_app.sms.sms_app import SMS
from message_app.common import open_template
from message_app.record import Record
from helpers.client_config import ClientConfig


class RemindSMS(SMS):
    OUTSCOPE_PRODUCT_TYPE = 'other'

    def __init__(self, client_name: str, record: dict, sms_item_list: list):
        """_summary_

        Args:
            client_name (str): _description_
            record (dict): _description_
            sms_item_list (list): _description_

        Attributes:
            product_type (str): .
            is_allow_send (bool): .
        """
        self.product_type = Record(record).product
        is_product_scope = self.scope_items()
        is_allow_items = self.allow_items(sms_item_list)
        self.is_allow_send = is_product_scope and is_allow_items

        if self.is_allow_send:
            body = RemindBody(client_name, self.product_type).text
            super().__init__(client_name, record, body)

    def scope_items(self) -> bool:
        is_scope_items = (self.product_type != self.OUTSCOPE_PRODUCT_TYPE)
        if is_scope_items:
            return True
        else:
            print(f'SMS not to sent due to out of scope product type: "{self.product_type}".')
            return False

    def allow_items(self, sms_item_list: list) -> bool:
        if sms_item_list == []:
            return True
        elif sms_item_list[0] == '':
            return True
        elif self.product_type in sms_item_list:
            return True
        else:
            print(f'SMS is not to sent due to out of allow items. This item:"{self.product_type}" vs Allow: {sms_item_list}')
            return False



class RemindBody:
    def __init__(self, client_name: str, product_type: str) -> None:
        """
        Args:
            client_name (str): _description_
            product_type (str): _description_

        Attrubutes:
            path (str): Mail template path
        """
        dir_path = ClientConfig(client_name).client_path()
        self.file_path = f'{dir_path}/sms_body_{product_type}.txt'
        self.text = self.__generate_body()

    def __generate_body(self):
        click_query = 'utm_medium=sms&utm_source=funk'
        template = open_template(self.file_path)
        return template.substitute(
            click_query=click_query
        )

if __name__ == '__main__':
    text = RemindBody('belmise', 'corset').text
    print(text)

    record = {
            'mail_address': 'emata@espalhar.net',
            'phone_number': '080-2814-8359',
            'user_id': 'test_user_id_value',
            'product_type': 'corset'
        }
    mailapp = RemindSMS('belmise', record, ['corset', 'demo'])
    mailapp.send()
