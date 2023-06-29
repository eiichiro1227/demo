from dns.resolver import resolve
import ssl

# for send mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
# for html-mail-template string to text-mail-template string
import markdown
import html2text
# import os
import sys
from message_app.record import Record
from helpers.client_config import ClientConfig

class MailAddress:
    def __init__(self, to_: str) -> None:
        self.to_ = to_
        if not self.__is_valid_to_():
            self.to_ = None

    def __is_valid_to_(self):
        domain = self.to_.rsplit('@', 1)[-1]
        try:
            return bool(resolve(domain, 'MX'))
        except Exception as e:
            print(f'Mail is not to sent due to: {e}. Address is {self.to_}')
            return False


class Header:
    def __init__(self, to_: str, is_remail: bool, product: str, mail_dict: dict) -> None:
        """Mail header template info

        Args:
            to_ (str): _description_
            is_remail (bool): _description_
            product (_type_): _description_
            mail_dict (dict): _description_

        Attributes:
            to_ (str): xxx
            from_ (str): xxx
            bcc_ (str): xxx
            subject_ (str): xxx
        """
        self.to_ = to_
        try:
            template = mail_dict['templates'][product]
            self.from_ = template['from']
            self.bcc_ = template.get('bcc_email')
            self.subject_ = template['subject'] if is_remail else template['subject_cv_follow']
        except KeyError as e:
            print(f'KeyError: Check if the product name of data is correct. ... {e}')
            sys.exit()


class Server:
    def __init__(self, mail_dict: dict) -> None:
        """Mail searve info

        Args:
            mail_dict (dict): Mail server information read from the client's configuration file.

        Atrributes:
            username (str): ...
            password (str): ...
            smtp_port (int): ...
            smtp_host (str): ...
        """
        dict = mail_dict['common']
        self.username = dict['username']
        self.password = dict['password']
        self.smtp_port = 587
        self.smtp_host = dict['smtp_host']


class Message:
    def __init__(self, header: Header, body_string: str) -> None:
        """_summary_

        Args:
            header (Header): _description_
            body_string (str): _description_

        Attributes:
            msg (MIMEMultipart): .
        """
        self._header = header
        self._body_string = body_string

        self.msg = MIMEMultipart('alternative')
        self.__attach_plain_body()
        self.__attach_html_body()
        self.__config_mail_header()

    def __plain_body(self, body_string: str):
        text_extractor = html2text.HTML2Text()
        text_extractor.ignore_links = True
        text_extractor.ignore_images = True
        html_object = markdown.markdown(body_string)
        return text_extractor.handle(html_object)

    def __attach_plain_body(self):
        part_plain = MIMEText(self.__plain_body(self._body_string), 'plain')
        self.msg.attach(part_plain)

    def __attach_html_body(self):
        part_html = MIMEText(self._body_string, 'html')
        self.msg.attach(part_html)

    def __config_mail_header(self):
        self.msg['Subject'] = self._header.subject_
        self.msg['To'] = self._header.to_
        self.msg['From'] = self._header.from_
        self.msg['Bcc'] = self._header.bcc_



class Mail:

    def __init__(self, client_name: str, record_obj: Record, body: str, is_remail=True):
        """_summary_

        Args:
            client_name (str): _description_
            record (Record): _description_
            body (str): _description_
            is_remail (bool, optional): _description_. Defaults to True.

        Attributes:
            client_name (str): _description_
        """
        self._record = record_obj

        mail_dict = ClientConfig(client_name).load_config_file()['mail']
        self._server = Server(mail_dict)
        to_ = MailAddress(self._record.mail).to_
        self._header = Header(to_, is_remail, self._record.product, mail_dict)
        self.client_name = client_name
        self._body = body

    def execute(self, msg: MIMEMultipart):

        try:
            server = smtplib.SMTP(self._server.smtp_host, self._server.smtp_port)
            server.ehlo()
            server.starttls()

        except ssl.SSLError:
            server = smtplib.SMTP(self._server.smtp_host, self._server.smtp_port)
            server.ehlo()
            # print('Sec level downgraded to avoid ssl error.')
            context = self.downgrade_security_level()
            server.starttls(context=context)

        server.ehlo()
        server.login(self._server.username, self._server.password)
        server.send_message(msg)
        server.quit()

    def downgrade_security_level(self):
        context=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # Either of the following context settings worked for me - choose one
        # context.set_ciphers('HIGH:!DH:!aNULL')
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        # https://askubuntu.com/questions/1231844/ssl-sslerror-ssl-dh-key-too-small-dh-key-too-small-ssl-c1108
        return context

    def send(self):
        if self._header.to_:
            msg = Message(self._header, self._body).msg
            self.execute(msg)
            return True
        else:
            return False
