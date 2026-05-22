from juezinteligente.model.judge import CheckerVisitor
from juezinteligente.persistence.data_access import DataAccessManager


class DataAccessManagerMock(DataAccessManager):
    def __init__(self):
        self.called = False

    def save_case(self, case, force_insert=False):
        self.called = True

    def list_cases(self):
        self.called = True

    def delete_case(self, case):
        self.called = True

    def export_cases(self, cases, zip_file_path: str):
        self.called = True

    def import_cases(self, zip_file_path: str):
        self.called = True


class MockVisitor(CheckerVisitor):
    pass