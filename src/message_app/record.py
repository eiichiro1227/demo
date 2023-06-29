class Record:
    def __init__(self, record: dict) -> None:
        self.product: str = record.get('product_type')
        self.user: str = record.get('user_id')

        mail = record.get('mail_address')
        self.mail: str = self.handle_mail(mail)

        self.phone_num: str = record.get('phone_number')

    def handle_mail(self, mail: str):
        if mail:
            return mail.strip().replace(' ', '').replace('＠', '@')
        else:
            return None
