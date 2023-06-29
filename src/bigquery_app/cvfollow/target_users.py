import time
from bigquery_app.common import Selector


class BigqueryTargetUsers(Selector):
    _PROJECT_NAME = 'remarketing-mail'
    _CONSTRAINTS_TABLE_NAME1 = 'log'
    _CONSTRAINTS_TABLE_NAME2 = 'mail_history'
    _SLEEP_SECONDS = 2

    def __init__(self, client_name, table_name='history_cv_follow_mail'):
        super().__init__(self._PROJECT_NAME, client_name, table_name)
        self._path_constraint1 = f'{self._PROJECT_NAME}.{client_name}.{self._CONSTRAINTS_TABLE_NAME1}'
        self._path_constraint2 = f'{self._PROJECT_NAME}.{client_name}.{self._CONSTRAINTS_TABLE_NAME1}'
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

    def select(self):

        query = f'''
            -- 直リマケメール以外でCVした(条件1)ユーザーに対してリマケメールを送っていた(条件2)場合，CV済であることを通知するフォローメールを追加で1回(条件3)送信する
            -- 送信条件
            -- 条件1: 30分以内にリマケメール経由のLP以外でCVをした
            -- 条件2: 3時間以内にリマケメールを送信した
            -- 条件3: 30分以内にフォローメール送信履歴に登録されていない

            SELECT
                remail_history.mail_address,
                remail_history.user_id
            FROM (
            SELECT
                DISTINCT(user_id)
            FROM
                (SELECT
                user_id,
                FIRST_VALUE(
                    CASE WHEN event_name = "purchase" THEN datetime ELSE NULL END
                    IGNORE NULLS
                    ) OVER (PARTITION BY user_id ORDER BY datetime ASC
                    ) AS first_purchased_datetime, -- 最初に購入完了した日時
                FIRST_VALUE(
                    CASE WHEN event_name = "remarketing_lp_view_mail" THEN datetime ELSE NULL END
                    IGNORE NULLS
                    ) OVER (PARTITION BY user_id ORDER BY datetime ASC
                    ) AS first_rmk_lp_mail_datetime, -- 最初にリマケメールからLPにアクセスした日時
                FROM `{self._path_constraint1}` --★クライアントのテーブルを指定

                )
            WHERE
                first_rmk_lp_mail_datetime is not null
                and timestamp(first_rmk_lp_mail_datetime) > timestamp(first_purchased_datetime)
                AND TIMESTAMP_DIFF(TIMESTAMP_ADD(CURRENT_TIMESTAMP, INTERVAL 9 HOUR), TIMESTAMP(first_rmk_lp_mail_datetime, "Asia/Tokyo"), MINUTE) < 30
            ) as cv
            INNER JOIN (
                SELECT
                    user_id,
                    mail_address
                    -- datetime(timestamp, "Asia/Tokyo") as remail_datetime # SQL出力結果の検証用
                FROM `{self._path_constraint2}`

                WHERE
                    DATETIME_DIFF(CURRENT_DATETIME("Asia/Tokyo"), datetime, HOUR) < 3  # リマケメールの送信日時が現在から3時間以内
                    and DATE(datetime) >= "2021-08-18" # 実際は上の条件のほうが強いが，テーブルの制約条件でこれも指定
                GROUP BY 1,2
            ) as remail_history
            ON cv.user_id = remail_history.user_id
            WHERE remail_history.mail_address NOT IN (
                SELECT
                    mail_address
                FROM
                    `{self.path}`

                WHERE
                    TIMESTAMP_DIFF(TIMESTAMP_ADD(CURRENT_TIMESTAMP, INTERVAL 9 HOUR), TIMESTAMP(DATETIME(timestamp)), MINUTE) < 30  # CVフォローメールの送信日時が現在から30分以内
                    and DATE(timestamp) >= "2021-08-18"
            )
            GROUP BY 1, 2
        '''
        # print('select_targets() Query: ', query)
        return self.CLIENT.query(query)
