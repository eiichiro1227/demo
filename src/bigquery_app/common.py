from google.cloud import bigquery
from google.api_core.exceptions import NotFound
import abc


class Base(metaclass=abc.ABCMeta):
    BQ = bigquery
    CLIENT = BQ.Client()

    def __init__(self, project: str, dataset: str, table: str) -> None:
        """_summary_

        Args:
            project (str): _description_
            dataset (str): _description_
            table (str): _description_

        Attributes:
            path (str): Path to bigquery table.
            CLIENT (bigquery.Client): Api client for bigquery.
        """
        self.path = f'{project}.{dataset}.{table}'

    @abc.abstractmethod
    def create_table(self):
        pass

    def create_table_if_not_exist(self):
        try:
            return self.CLIENT.get_table(self.path)
        except NotFound as e:
            self.create_table()

class Insertor(Base):

    def __init__(self, project: str, dataset: str, table: str) -> None:
        super().__init__(project, dataset, table)

    def make_filtered_row(self, row: dict):
        pass

    def add(self, row: dict):
        pass

    def insert(self, rows_for_bq):
        if len(rows_for_bq) > 0:
            self.CLIENT.insert_rows_json(self.path, rows_for_bq)
            print(
                f'Inserted rows num are {len(rows_for_bq)}. Detail: {rows_for_bq}')
        else:
            print('There is no row -- Skip.')



class Selector(Base):
    def __init__(self, project: str, dataset: str, table: str) -> None:
        super().__init__(project, dataset, table)

    def select(self):
        pass
