import sys
import logging
from pathlib import Path

from dependency_injector.wiring import Provide
from importlib.resources import files

import juezinteligente.ui.resources

from PySide2.QtCore import QLocale, QTranslator, QLibraryInfo
from PySide2.QtWidgets import QApplication

from juezinteligente.ui.main_win import SplashScreen
from juezinteligente.util.containers import Container

logging.basicConfig(filename=files('juezinteligente').joinpath(Path('log/juez-inteligente.log')),
                    level=logging.DEBUG,
                    format='[%(levelname)s] on %(asctime)s: (%(name)s) - %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p')


def main(app: QApplication = Provide[Container.app]):
    # CONFIGURE LOGGING
    logger = logging.getLogger(__name__)

    # LOAD TRANSLATIONS
    locale = QLocale.system().name()
    qt_translator = QTranslator(app)
    if qt_translator.load("qtbase_" + locale, QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
        app.installTranslator(qt_translator)
    else:
        logger.warning(f"No se pudo cargar la traducción de Qt para {locale}")

    app_translator = QTranslator(app)
    path = files("juezinteligente").joinpath(Path("i18n/"))
    if app_translator.load(locale, str(path)):
        app.installTranslator(app_translator)
    else:
        logger.warning(f"No se pudo cargar la traducción de la aplicación para {locale}: {path}")

    # CREATE SPLASH SCREEN
    splash_screen = SplashScreen()
    splash_screen.change_loading_text(app.tr("Loading translation files"))


    # splash_screen.set_data_access_manager(data_access_manager)
    splash_screen.change_loading_text(app.tr("Loading data source"))

    splash_screen.change_loading_text(app.tr("Loading graphical interface"))
    sys.exit(app.exec_())


if __name__ == '__main__':
    container = Container()
    container.init_resources()
    container.wire(modules=[sys.modules[__name__],
                            juezinteligente.ui.main_win,
                            juezinteligente.ui.graph,
                            juezinteligente.model.judge])
    main()


