import time
from bigquery_app.common import Selector


class MailSelector(Selector):
    _PROJECT_NAME = 'remarketing-mail'
    _CONSTRAINTS_TABLE_NAME = 'mail_history'
    _SLEEP_SECONDS = 1

    def __init__(self, client_name, table_name='log'):
        """Obtains users information to whom e-mails are sent from the DB
        Information required for tables:
        1. for access logs table:
            1-1: datetime, user_id, event_name (='get_mail_address'), mail_address
            1-2: datetime, user_id, event_name (='purchase')
        2. for sending histories table:
            timestamp, mail_address

        Args:
            client_name (_type_): _description_
            table_name (str, optional): _description_. Defaults to 'log'.

        Attributes:
            path (str): Path to bigquery table.
            CLIENT (bigquery.Client): Api client for bigquery.
        """
        super().__init__(self._PROJECT_NAME, client_name, table_name)
        self._path_constraint = f'{self._PROJECT_NAME}.{client_name}.{self._CONSTRAINTS_TABLE_NAME}'
        self.create_table_if_not_exist()
        time.sleep(self._SLEEP_SECONDS)

    def create_table(self):
        schema = [
            self.BQ.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            self.BQ.SchemaField("mail_address", "STRING", mode="REQUIRED"),
            self.BQ.SchemaField("user_id", "STRING"),
            self.BQ.SchemaField("product_type", "STRING"),
        ]
        table = self.BQ.Table(self.path, schema=schema)
        table.time_partitioning = self.BQ.TimePartitioning(field='timestamp')
        return self.CLIENT.create_table(table)


    def select(self, minutes_older_than, minutes_newer_than):
        query = f'''
            SELECT
                user_id,
                mail_address,
                COALESCE(product_type, 'main') AS product_type
            FROM (
                SELECT
                    user_id,
                    datetime,
                    mail_address,
                    MAX(product_type) AS product_type,
                    LOGICAL_OR(is_purchased) AS is_purchased
                    FROM (

                        # user_idをキーとして訪問者のデータを最新の値で集約する
                        # user_idがないレコードの値は集約されない。
                        # 特にメールアドレス・SMS取得および、CV時は必ずuser_idを取得する
                        SELECT
                            user_id,
                            FIRST_VALUE(datetime) OVER(PARTITION BY user_id ORDER BY datetime DESC  # 最新のアクセス日時
                            ) AS datetime,
                            FIRST_VALUE(
                                CASE WHEN event_name = 'get_mail_address' THEN mail_address ELSE NULL END
                                IGNORE NULLS # 確実にMail/Telが取得できるイベントの情報のみ使い、他のイベントの情報は無視するためNULLに集約する
                                ) OVER (PARTITION BY user_id ORDER BY datetime DESC
                                ) AS mail_address,
                            FIRST_VALUE(
                                CASE WHEN product_type != 'None' THEN product_type ELSE NULL END
                                ) OVER (PARTITION BY user_id ORDER BY datetime DESC
                                ) AS product_type,
                            FIRST_VALUE(
                                CASE WHEN event_name = 'purchase' THEN TRUE ELSE NULL END
                                IGNORE NULLS
                                ) OVER (PARTITION BY user_id ORDER BY datetime DESC
                                ) AS is_purchased,
                        FROM
                            `{self.path}`
                        )
                    GROUP BY
                        user_id,
                        datetime,
                        mail_address

            )
            WHERE
                # 直近の指定された期間にユーザーログが更新されたこと
                # minutes_older_than < minutes_newer_than ...
                # 差が大きいほど昔、差が小さいほど最近
                DATETIME_DIFF(
                    CURRENT_DATETIME("Asia/Tokyo"),
                    datetime,
                    MINUTE) >= {minutes_older_than} # x分前よりは古い
                AND DATETIME_DIFF(
                    CURRENT_DATETIME("Asia/Tokyo"),
                    datetime,
                    MINUTE) < {minutes_newer_than} # x分前よりは新しい

                AND is_purchased is NULL        #まだそのユーザーがCVしていないこと
                AND mail_address is NOT NULL    #メールアドレスが存在すること
                AND mail_address not in (       #まだメールを送っていないこと
                    SELECT mail_address FROM `{self._path_constraint}`
                    WHERE DATE(timestamp, 'Asia/Tokyo') >= "2021-01-01" #充分前の日時を指定
                )
        '''

        # print('select_targets() Query: ', query)
        return self.CLIENT.query(query)
