import sys
from helpers.client_config import ClientConfig
from message_app.sms.sms_app_twilio import TwilioAPI


class Record:
    def __init__(self, record: dict) -> None:
        self.product = record.get('product_type')
        self.phone_num = record.get('phone_number')

class PhoneNumber:
    def __init__(self, phone_num: str) -> None:
        self.phone_num = phone_num

        if not self.__is_exist():
            self.phone_num = None
            return
        else:
            self.phone_num = self.__trim()

        if not self.__is_valid_num():
            self.phone_num = None
            return
        else:
            self.phone_num = self.__internationalize()

    def __is_exist(self):
        if self.phone_num:  # and (type(phone_num) == str)
            return True
        else:
            print('SMS is not to sent because there is no phone number.')
            return False

    def __trim(self):
        return self.phone_num.replace('-', '').replace(' ', '')

    def __internationalize(self):
        identificator = '+81'
        num_base = self.phone_num[1:]  # 80xxxxxxxx
        return f'{identificator}{num_base}'  # +8180xxxxxxxx

    def __is_valid_num(self):
        return self.__is_valid_area_code() and self.__is_valid_num_length() and self.__is_ok_patterns()


    def __is_valid_area_code(self):
        area_codes = ('070', '080', '090',)
        is_phone_area_code = self.phone_num.startswith(area_codes)
        if is_phone_area_code:
            return True
        else:
            print(f'SMS is not to sent due to invalid phone area code: "{self.phone_num}".')
            return False

    def __is_valid_num_length(self):
        is_phone_num_length = len(self.phone_num) == 11  # len(+8180xxxxxxxx)
        if is_phone_num_length:
            return True
        else:
            print(f'SMS is not to sent due to invalid phone num length: "{self.phone_num}".')
            return False

    def __is_ok_patterns(self):
        ng_patterns = tuple([str(n)*8 for n in range(10)])
        if not self.phone_num.endswith(ng_patterns):
            return True
        else:
            print(f'SMS is not to sent due to blocked phone num pattern: "{self.phone_num}".')
            return False


class Header:
    def __init__(self, to_: str, product_type: str, sms_dict: dict) -> None:
        """Sms header template info

        Args:
            to_ (str): _description_
            product (_type_): _description_
            sms_dict (dict): _description_

        Attributes:
            to_ (str): xxx
            subject (str): xxx
        """
        self.to_ = to_
        try:
            template = sms_dict['templates'][product_type]
            self.subject = template['subject']
        except KeyError as e:
            # print(f'KeyError: Check if the product name of data is correct. ... {e}')
            print(f'SMS failed. There is no template of corresponding to the product-type "{product_type}" of requested data. Detail: "{e}"')
            sys.exit()


class SMS:
    def __init__(self, client_name: str, record: dict, body: str) -> None:
        """_summary_

        Args:
            client_name (str): _description_
            record (dict): _description_
            sms_api_excute (Callable): _description_

        Attributes:
            sms_api_excute (Callable): .
        """
        sms_dict = ClientConfig(client_name).load_config_file()['sms']
        record_obj = Record(record)
        phone_num_cleaned = PhoneNumber(record_obj.phone_num).phone_num

        self._header = Header(phone_num_cleaned, record_obj.product, sms_dict)
        self._body = body

    def send(self):
        if not self._header.to_:
            return False
        try:
            api = TwilioAPI(self._body, self._header.subject, self._header.to_)
            api.send()
            print(f'SMS to: {self._header.to_}')
            return True
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f'SMS failed - {e}. Maybe there is no template of sms corresponding to the product-type of requested data. Original phone number is "{self._header.to_}"')
