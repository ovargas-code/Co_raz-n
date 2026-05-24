import sys
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import logging
from pathlib import Path

# pyrefly: ignore [missing-import]
from dependency_injector.wiring import Provide
from importlib.resources import files

import co_razon.ui.resources

from PySide2.QtCore import QLocale, QTranslator, QLibraryInfo, QCoreApplication
from PySide2.QtWidgets import QApplication

from co_razon.ui.main_win import SplashScreen
from co_razon.util.containers import Container

logging.basicConfig(filename=files('co_razon').joinpath(Path('log/co-razon.log')),
                    level=logging.DEBUG,
                    format='[%(levelname)s] on %(asctime)s: (%(name)s) - %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p')


def main(app: QApplication = Provide[Container.app]):
    # CONFIGURE LOGGING
    logger = logging.getLogger(__name__)

    # LOAD TRANSLATIONS
    locale = QLocale.system().name()
    if not locale.startswith("es"):
        locale = "es_CO"

    qt_translator = QTranslator(app)
    qt_loaded = qt_translator.load("qtbase_" + locale, QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    if not qt_loaded and locale.startswith("es"):
        qt_loaded = qt_translator.load("qtbase_es", QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    if qt_loaded:
        app.installTranslator(qt_translator)
        app.qt_translator = qt_translator
    else:
        logger.warning(f"No se pudo cargar la traducción de Qt para {locale}")

    app_translator = QTranslator(app)
    path = files("co_razon").joinpath(Path("i18n/"))
    app_loaded = app_translator.load(locale, str(path))
    if not app_loaded and locale.startswith("es"):
        app_loaded = app_translator.load("es_CO", str(path))
    if app_loaded:
        app.installTranslator(app_translator)
        app.app_translator = app_translator
    else:
        logger.warning(f"No se pudo cargar la traducción de la aplicación para {locale}: {path}")

    # CREATE SPLASH SCREEN
    splash_screen = SplashScreen()
    splash_screen.change_loading_text(QCoreApplication.translate("app", "Loading translation files"))


    # splash_screen.set_data_access_manager(data_access_manager)
    splash_screen.change_loading_text(QCoreApplication.translate("app", "Loading data source"))

    splash_screen.change_loading_text(QCoreApplication.translate("app", "Loading graphical interface"))
    sys.exit(app.exec_())


if __name__ == '__main__':
    container = Container()
    container.init_resources()
    container.wire(modules=[sys.modules[__name__],
                            co_razon.ui.main_win,
                            co_razon.ui.graph,
                            co_razon.model.judge])
    main()


