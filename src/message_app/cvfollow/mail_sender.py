from message_app.mail.mail_app import Mail
from message_app.common import open_template
from message_app.record import Record
from helpers.client_config import ClientConfig


class CVFollowMail(Mail):
    def __init__(self, client_name: str, record: dict):
        record_obj = Record(record)
        body = CVFollowBody(client_name).text
        super().__init__(client_name, record_obj, body, is_remail=False)


class CVFollowBody:
    _FILE_NAME = 'mail_cv_follow.txt'

    def __init__(self, client_name: str) -> None:
        """_summary_

        Args:
            client_name (str): _description_

        Attributes:
            text (str): .
        """
        dir_path = ClientConfig(client_name).client_path()
        file_path = f'{dir_path}/{self._FILE_NAME}'
        self.text = open_template(file_path).substitute()


if __name__ == '__main__':
    text = CVFollowBody('belmise').text
    print(text)

    record = {
            'mail_address': 'emata@espalhar.net',
            # 'phone_number': '080-2814-8359',
            'user_id': 'test_user_id_value',
            'product_type': 'corset'
        }
    mailapp = CVFollowMail('belmise', record)
    mailapp.send()
