import time
from helpers.datetime_helper import current_datetime
from bigquery_app.common import Insertor
from typing import List

class BigqueryMailSentUsers(Insertor):
    _PROJECT_NAME = 'remarketing-mail'
    _SLEEP_SECONDS = 2

    def __init__(self, client_name: str, table_name: str = 'mail_history') -> None:
        """_summary_

        Args:
            client_name (str): _description_
            table_name (str, optional): _description_. Defaults to 'mail_history'.

        Attributes:
            path (str): Path to bigquery table.
            CLIENT (bigquery.Client): Api client for bigquery.
        """
        super().__init__(self._PROJECT_NAME, client_name, table_name)
        self.create_table_if_not_exist()
        time.sleep(self._SLEEP_SECONDS)
        self.rows_for_bq: List[dict] = []

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

    def make_filtered_row(self, row: dict):
        return {
            'timestamp': str(current_datetime()),
            'mail_address': row.get('mail_address'),
            'user_id': row.get('user_id'),
            'product_type': row.get('product_type'),
        }

    def add(self, row: dict):
        new_row = self.make_filtered_row(row)
        self.rows_for_bq.append(new_row)
