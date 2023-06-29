import click
from bigquery_app.remind.mail_selector import MailSelector
from bigquery_app.remind.sms_selector import SmsSelector
from bigquery_app.remind.mail_history import BigqueryMailSentUsers
from bigquery_app.remind.sms_history import BigquerySMSSentUsers
from message_app.remind.mail_sender import RemindMail
from message_app.remind.sms_sender import RemindSMS
from helpers.client_config import ClientConfig


def is_target_product(client_name: str, row: dict):
    current_product = row.get('product_type')
    conf_json = ClientConfig(client_name).load_config_file()
    product_types = [t.strip() for t in conf_json['mail']['templates']]
    is_target = (current_product in product_types)
    if not is_target:
        print(f'This is not target product: "{current_product}"; Target products are {product_types}')
    return is_target

class MailHandler:
    def __init__(self, client_name: str, minutes_older_than: int, minutes_newer_than: int) -> None:
        self._client_name = client_name
        self._minutes_older_than = minutes_older_than
        self._minutes_newer_than = minutes_newer_than
        self._hist = BigqueryMailSentUsers(client_name)

    def send_all(self):
        targets = self.__get_targets()
        for row in targets:
            if is_target_product(self._client_name, row):
                self.__handle_send(row)
        self._hist.insert(self._hist.rows_for_bq)

    def __get_targets(self):
        targets = MailSelector(self._client_name)
        return targets.select(self._minutes_older_than, self._minutes_newer_than)

    def __handle_send(self, row):
        mailer = RemindMail(self._client_name, row)
        if mailer.is_allow_send:
            result = mailer.send()
            if result:
                self._hist.add(row)
        else:
            print(f'Mail not to sent due to outscope product type: "{mailer.record_obj.product}".')


class SmsHandler:
    def __init__(self, client_name: str, minutes_older_than: int, minutes_newer_than: int, sms_item_list: list) -> None:
        self._client_name = client_name
        self._minutes_older_than = minutes_older_than
        self._minutes_newer_than = minutes_newer_than
        self._sms_item_list = sms_item_list
        self._hist = BigquerySMSSentUsers(client_name)

    def send_all(self):
        targets = self.__get_targets()
        for row in targets:
            if is_target_product(self._client_name, row):
                self.__handle_send(row)
        self._hist.insert(self._hist.rows_for_bq)

    def __get_targets(self):
        targets = SmsSelector(self._client_name)
        return targets.select(self._minutes_older_than, self._minutes_newer_than)

    def __handle_send(self, row):
        sms = RemindSMS(self._client_name, row, self._sms_item_list)
        if sms.is_allow_send:
            result = sms.send()
            if result:
                self._hist.add(row)


@click.command()
@click.option('--client_name', help='Client name in snake-case.')
@click.option('--sms_use', help='"True" if you want to send SMS.')
@click.option('--sms_items_str', help='Product type names (separate by "__") to be sent by SMS. If no input, send all.', default='')
@click.option('--minutes_older_than', help='To how many minutes before the user update datetime.', default=15)
@click.option('--minutes_newer_than', help='From how many minutes before the user update datetime.', default=25)
def run(client_name: str, minutes_older_than: str, minutes_newer_than: str, sms_use: str = None, sms_items_str: str = None):
    minutes_older_than = int(minutes_older_than)
    minutes_newer_than = int(minutes_newer_than)

    MailHandler(client_name, minutes_older_than, minutes_newer_than).send_all()

    sms_use = sms_use == 'True'
    if sms_use:
        sms_item_list = sms_items_str.split('__')
        SmsHandler(client_name, minutes_older_than, minutes_newer_than, sms_item_list).send_all()


if __name__ == '__main__':
    run()
