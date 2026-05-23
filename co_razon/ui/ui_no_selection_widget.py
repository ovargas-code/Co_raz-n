# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'no_selection_widgetOKBaDs.ui'
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


class Ui_NoSelectionForm(object):
    def setupUi(self, NoSelectionForm):
        if not NoSelectionForm.objectName():
            NoSelectionForm.setObjectName(u"NoSelectionForm")
        NoSelectionForm.resize(286, 64)
        self.verticalLayout = QVBoxLayout(NoSelectionForm)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.no_selection_label = QLabel(NoSelectionForm)
        self.no_selection_label.setObjectName(u"no_selection_label")

        self.verticalLayout.addWidget(self.no_selection_label, 0, Qt.AlignTop)


        self.retranslateUi(NoSelectionForm)

        QMetaObject.connectSlotsByName(NoSelectionForm)
    # setupUi

    def retranslateUi(self, NoSelectionForm):
        NoSelectionForm.setWindowTitle(QCoreApplication.translate("NoSelectionForm", u"Form", None))
        self.no_selection_label.setText(QCoreApplication.translate("NoSelectionForm", u"<html><head/><body><p>Select a node to see its properties.</p></body></html>", None))
    # retranslateUi

