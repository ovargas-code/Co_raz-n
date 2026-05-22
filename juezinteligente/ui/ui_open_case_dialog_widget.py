# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'open_case_dialog_widgetlSpCJQ.ui'
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


class Ui_OpenCaseForm(object):
    def setupUi(self, OpenCaseForm):
        if not OpenCaseForm.objectName():
            OpenCaseForm.setObjectName(u"OpenCaseForm")
        OpenCaseForm.resize(533, 347)
        self.verticalLayout = QVBoxLayout(OpenCaseForm)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(OpenCaseForm)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setFlat(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.list_view_cases = QListView(self.groupBox)
        self.list_view_cases.setObjectName(u"list_view_cases")

        self.verticalLayout_2.addWidget(self.list_view_cases)


        self.verticalLayout.addWidget(self.groupBox)

        self.open_case_dialog_button_box = QDialogButtonBox(OpenCaseForm)
        self.open_case_dialog_button_box.setObjectName(u"open_case_dialog_button_box")
        self.open_case_dialog_button_box.setOrientation(Qt.Horizontal)
        self.open_case_dialog_button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Open)

        self.verticalLayout.addWidget(self.open_case_dialog_button_box)


        self.retranslateUi(OpenCaseForm)

        QMetaObject.connectSlotsByName(OpenCaseForm)
    # setupUi

    def retranslateUi(self, OpenCaseForm):
        OpenCaseForm.setWindowTitle(QCoreApplication.translate("OpenCaseForm", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("OpenCaseForm", u"Processes repository", None))
    # retranslateUi

