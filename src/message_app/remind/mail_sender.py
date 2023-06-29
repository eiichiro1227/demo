from message_app.mail.mail_app import Mail
from message_app.common import open_template
from message_app.record import Record


class RemindMail(Mail):
    OUTSCOPE_PRODUCT_TYPES: list = ['other']

    def __init__(self, client_name: str, record: dict, is_remail=True):
        """_summary_

        Args:
            client_name (str): _description_
            record (dict): _description_
            is_remail (bool, optional): _description_. Defaults to True.

        Attributes:
            record_obj (Record): .
            is_allow_send (bool): .
        """
        self.record_obj = Record(record)
        self.is_allow_send = self.__scope_items()

        if self.is_allow_send:
            body = RemindBody(client_name, self.record_obj.user, self.record_obj.product).text
            super().__init__(client_name, self.record_obj, body, is_remail)

    def __scope_items(self) -> bool:
        is_scope_items = (self.record_obj.product not in self.OUTSCOPE_PRODUCT_TYPES)
        if is_scope_items:
            return True
        else:
            print(f'Mail not to sent due to out of scope product type: "{self.record_obj.product}".')
            return False


class RemindBody:
    _analytics_server_host_name = 'https://remarketing-mail-api.herokuapp.com'

    def __init__(self, client_name: str, user_id: str, product_type: str) -> None:
        """_summary_

        Args:
            client_name (str): _description_
            user_id (str): _description_
            product_type (str): _description_

        Attributes:
            text (str): .
        """
        self._client_name = client_name
        self._user_id = user_id
        config = BodyConfig(client_name, product_type)
        self._body_path = config.path
        self._body_id = config.id

        self.text = self.__generate_body()

    def __open_event_tag(self):
        mail_open_url = f'{self._analytics_server_host_name}/open_mail/?client_name={self._client_name}&uid={self._user_id}&utm_content={self._body_id}'
        return f'<img height="1" src="{mail_open_url}" style="display:none" width="1">'

    def __generate_body(self):
        # optout_url = f'https://remail-stop.web.app/?service_name={self.client_name}&eclid={self._user_id}'
        click_query = f'utm_medium=email&utm_source=funk&eclid={self._user_id}&utm_content={self._body_id}'
        template = open_template(self._body_path)
        return template.substitute(
            click_query=click_query,
            open_event_tag=self.__open_event_tag(),
            # optout_url=optout_url
        )


import glob
import random
import os
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from helpers.client_config import ClientConfig


class BodyConfig:
    def __init__(self, client_name: str, product_type: str) -> None:
        """
        Args:
            client_name (str): _description_
            product_type (str): _description_

        Attrubutes:
            path (str): Mail template path
            id (str): Number at the end of the file name of a randomly selected email template.
        """
        client_path = ClientConfig(client_name).client_path()
        self.path = self.__get_template_path(client_path, product_type)
        self.id = re.findall(r'\d', self.path)[-1]

    def __get_template_path(self, client_path, product_type):
        file_name = f'mail_body_{product_type}_*.txt'
        template_paths_back_slash = glob.glob(f'{client_path}/{file_name}')
        template_paths_slash = [t.replace(os.sep, '/')
                                for t in template_paths_back_slash]
        try:
            template_path = random.choice(template_paths_slash)
        except IndexError as e:
            raise IndexError(
                f'There is no template of corresponding to the product-type "{product_type}" of requested data. Detail: "{e}"')

        return template_path


if __name__ == '__main__':
    text = RemindBody('belmise', 'xxx', 'corset').text
    print(text)

    record = {
            'mail_address': 'emata@espalhar.net',
            # 'phone_number': '080-2814-8359',
            'user_id': 'test_user_id_value',
            'product_type': 'corset'
        }
    mailapp = RemindMail('belmise', record)
    mailapp.send()
