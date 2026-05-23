import io
import logging

from abc import ABCMeta, abstractmethod
from json.decoder import JSONDecodeError
from zipfile import ZipFile

from mongoengine import connect, ConnectionFailure, OperationError, ValidationError
from co_razon.model import judge
from pathlib import Path
from co_razon.util import db_config

logger = logging.getLogger(__name__)


class DataAccessManager(metaclass=ABCMeta):

    @abstractmethod
    def save_case(self, case, force_insert=False):
        raise NotImplementedError

    @abstractmethod
    def list_cases(self):
        raise NotImplementedError

    @abstractmethod
    def delete_case(self, case):
        raise NotImplementedError

    @abstractmethod
    def export_cases(self, cases, zip_file_path: str):
        raise NotImplementedError

    @abstractmethod
    def import_cases(self, zip_file_path: str):
        raise NotImplementedError


class MongoEngineDataAccessManager(DataAccessManager):

    def __init__(self, **params):
        try:
            connect(host=params['db_uri'])
        except ConnectionFailure as err:
            logger.critical(f"No se pudo establecer la conexión con la base de datos: {err}")

    def save_case(self, case, force_insert=False):
        case.save(force_insert=force_insert)

    def list_cases(self):
        return judge.Case.objects

    def delete_case(self, case):
        try:
            case.delete()
        except OperationError as err:
            logger.critical(f"No se pudo borrar el caso: {err}")

    def export_cases(self, cases, zip_file_path: str):
        with ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.setpassword(db_config["export_pw"].encode())
            for case in cases:
                f = io.StringIO(case.to_json())
                zip_file.writestr(str(case.id), f.getvalue())

    def import_cases(self, zip_file_path: str):
        raise NotImplementedError


class FileSystemDataAccessManager(DataAccessManager):

    def __init__(self, **params):
        self.fs_uri = params['fs_uri']
        Path(self.fs_uri).mkdir(parents=True, exist_ok=True)

    def save_case(self, case, force_insert=False):
        json_str = case.to_json()
        file_path = Path(self.fs_uri).joinpath(str(case.id))
        file_path.write_text(json_str)

    def list_cases(self):
        cases_dir = Path(self.fs_uri)
        files = [f for f in cases_dir.iterdir() if f.is_file()]
        cases = []
        for file in files:
            content = file.read_text()
            case = judge.Case.from_json(content)
            cases.append(case)

        return cases

    def delete_case(self, case):
        file_path = Path(self.fs_uri).joinpath(str(case.id))
        file_path.unlink()

    def export_cases(self, cases, zip_file_path: str):
        with ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.setpassword(db_config["export_pw"].encode())
            cases_dir = Path(self.fs_uri)
            for case in cases:
                file = cases_dir.joinpath(str(case.id))
                zip_file.write(file, file.name)

    def _is_valid_zip_file(self, zip_file_path: str):
        with ZipFile(zip_file_path, 'r') as zip_file:
            for file_name in zip_file.namelist():
                with zip_file.open(file_name, mode='r', pwd=db_config['export_pw'].encode()) as case_file:
                    try:
                        judge.Case.from_json(case_file.read().decode())
                    except (JSONDecodeError, ValidationError) as err:
                        return False

        return True

    def import_cases(self, zip_file_path: str):
        # Get current cases in the repository
        current_cases = self.list_cases()
        cases_ids = [str(case.id) for case in current_cases]

        msj = "Los casos con los siguientes id ya están en el repositorio, por lo tanto no se importaron:"
        some_not_imported = False

        if self._is_valid_zip_file(zip_file_path):
            with ZipFile(zip_file_path, 'r') as zip_file:
                cases_dir = Path(self.fs_uri)
                for file_name in zip_file.namelist():
                    with zip_file.open(file_name, mode='r', pwd=db_config['export_pw'].encode()) as case_file:
                        # If there is a case in the repository with the same id, it will not be imported
                        if case_file.name not in cases_ids:
                            new_file_path = cases_dir.joinpath(case_file.name)
                            new_file_path.write_text(case_file.read().decode())
                        else:
                            some_not_imported = True
                            msj += f"\n{case_file.name}"

            if some_not_imported:
                raise ImportCasesError(msj)
        else:
            raise NotValidFile("El archivo no es válido para importar casos")

class ImportCasesError(Exception):
    def __init__(self, msj):
        self.msj = msj


class NotValidFile(Exception):
    def __init__(self, msj):
        self.msj = msj