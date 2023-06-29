from twilio.rest import Client


class TwilioAPI:
    ACCOUNT_SID = 'AC576cee031a926549d4e9df13fbe1a2f7'
    AUTH_TOKEN  = '76bd87930bb39adb23ec74350673ccf9'
    MESSAGING_SERVICE_SID = 'MGf2df56a35178154cccc5502fef0094bd'

    def __init__(self, body: str, subject: str, to_: str):
        """_summary_

        Args:
            body (str): _description_
            subject (str): _description_
            to (str): _description_

        Attributes:
            None
        """
        self._body = body
        self._subject = subject
        self._to = to_

    def send(self):
        client = Client(self.ACCOUNT_SID, self.AUTH_TOKEN)
        message = client.messages.create(
            to=self._to,
            from_=self._subject,
            messaging_service_sid=self.MESSAGING_SERVICE_SID,
            body=self._body
        )
        print(f'message.sid: {message.sid}')
