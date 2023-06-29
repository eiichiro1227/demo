import time
from bigquery_app.common import Selector


class SmsSelector(Selector):
    _PROJECT_NAME = 'remarketing-mail'
    _CONSTRAINTS_TABLE_NAME = 'sms_history'
    _SLEEP_SECONDS = 2

    def __init__(self, client_name, table_name='log'):
        """Obtains users information to whom smss are sent from the DB
        Information required for tables:
        1. for access logs table:
            1-1: datetime, user_id, event_name (='get_phone_number'), phone_number
            1-2: datetime, user_id, event_name (='purchase')
        2. for sending histories table:
            timestamp, phone_number

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
            self.BQ.SchemaField("phone_number", "STRING", mode="REQUIRED"),
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
                phone_number,
                COALESCE(product_type, 'main') AS product_type
            FROM (
                SELECT
                    user_id,
                    datetime,
                    phone_number,
                    MAX(product_type) AS product_type,
                    LOGICAL_OR(is_purchased) AS is_purchased
                    FROM (

                        SELECT
                            user_id,
                            FIRST_VALUE(datetime) OVER(PARTITION BY user_id ORDER BY datetime DESC
                            ) AS datetime,
                            FIRST_VALUE(
                                # 'get_phone_number', 'get_mail_address' いずれかのイベントで取得した電話番号情報を使う
                                CASE WHEN event_name in ('get_phone_number', 'get_mail_address') THEN phone_number ELSE NULL END
                                IGNORE NULLS
                                ) OVER (PARTITION BY user_id ORDER BY datetime DESC
                                ) AS phone_number,
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
                        phone_number

            )
            WHERE
                # 直近の指定された期間にユーザーログが更新されたこと
                DATETIME_DIFF(
                    CURRENT_DATETIME("Asia/Tokyo"),
                    datetime,
                    MINUTE) >= {minutes_older_than} # x分前よりは古い
                AND DATETIME_DIFF(
                    CURRENT_DATETIME("Asia/Tokyo"),
                    datetime,
                    MINUTE) < {minutes_newer_than} # x分前よりは新しい
                    # minutes_older_than < minutes_newer_than ...
                    # 差が大きいほど昔、差が小さいほど最近
                #フォームCVフラグがtrueでないこと
                AND is_purchased is NULL        #まだそのユーザーがCVしていないこと
                AND phone_number is NOT NULL    #電話番号が存在すること
                AND phone_number not in (       #まだSMSを送っていないこと
                    SELECT phone_number FROM `{self._path_constraint}`
                    WHERE DATE(timestamp, 'Asia/Tokyo') >= "2021-01-01" #充分前の日時を指定
                )
        '''
        # print('select_targets() Query: ', query)
        return self.CLIENT.query(query)
