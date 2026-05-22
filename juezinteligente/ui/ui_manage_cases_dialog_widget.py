# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'manage_cases_dialog_widgetGLKcou.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_ManageCasesForm(object):
    def setupUi(self, ManageCasesForm):
        if not ManageCasesForm.objectName():
            ManageCasesForm.setObjectName(u"ManageCasesForm")
        ManageCasesForm.resize(596, 354)
        self.verticalLayout = QVBoxLayout(ManageCasesForm)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.table_view_cases = QTableView(ManageCasesForm)
        self.table_view_cases.setObjectName(u"table_view_cases")

        self.verticalLayout.addWidget(self.table_view_cases)

        self.widget = QWidget(ManageCasesForm)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pbutton_delete = QPushButton(self.widget)
        self.pbutton_delete.setObjectName(u"pbutton_delete")

        self.horizontalLayout.addWidget(self.pbutton_delete)

        self.pbutton_import = QPushButton(self.widget)
        self.pbutton_import.setObjectName(u"pbutton_import")

        self.horizontalLayout.addWidget(self.pbutton_import)

        self.pbutton_export = QPushButton(self.widget)
        self.pbutton_export.setObjectName(u"pbutton_export")

        self.horizontalLayout.addWidget(self.pbutton_export)


        self.verticalLayout.addWidget(self.widget, 0, Qt.AlignRight)


        self.retranslateUi(ManageCasesForm)

        QMetaObject.connectSlotsByName(ManageCasesForm)
    # setupUi

    def retranslateUi(self, ManageCasesForm):
        ManageCasesForm.setWindowTitle(QCoreApplication.translate("ManageCasesForm", u"Form", None))
#if QT_CONFIG(whatsthis)
        self.table_view_cases.setWhatsThis(QCoreApplication.translate("ManageCasesForm", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.pbutton_delete.setText(QCoreApplication.translate("ManageCasesForm", u"Delete", None))
        self.pbutton_import.setText(QCoreApplication.translate("ManageCasesForm", u"Import", None))
        self.pbutton_export.setText(QCoreApplication.translate("ManageCasesForm", u"Export", None))
    # retranslateUi

