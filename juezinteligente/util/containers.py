import importlib
import os
import sys

from PySide2.QtWidgets import QApplication
from dependency_injector import containers, providers

from juezinteligente.ui.constants import Constants, EvidenceTypeRepr
from juezinteligente.util import app_config, db_config

DB_URI = f"mongodb+srv://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['db_name']}" \
         f"?retryWrites=true&w=majority"
FS_URI = os.path.join(os.getcwd(), app_config['cases_repository'])


class Container(containers.DeclarativeContainer):

    app = providers.Singleton(lambda: QApplication.instance() or QApplication(sys.argv))

    constants = providers.Singleton(
        Constants,
        parent=app,
    )

    evidence_type_repr = providers.Singleton(
        EvidenceTypeRepr,
        parent=app,
    )

    data_access_manager = providers.Singleton(
        getattr(importlib.import_module("juezinteligente.persistence.data_access"),
                app_config['persistence_manager']),
        db_uri=DB_URI,
        fs_uri=FS_URI,
    )