# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_case_dialog_widgetVWEfVX.ui'
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


class Ui_NewCaseForm(object):
    def setupUi(self, NewCaseForm):
        if not NewCaseForm.objectName():
            NewCaseForm.setObjectName(u"NewCaseForm")
        NewCaseForm.resize(469, 434)
        self.formLayoutWidget = QWidget(NewCaseForm)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 10, 451, 381))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.pretension_label = QLabel(self.formLayoutWidget)
        self.pretension_label.setObjectName(u"pretension_label")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.pretension_label)

        self.pretension_text_edit = QPlainTextEdit(self.formLayoutWidget)
        self.pretension_text_edit.setObjectName(u"pretension_text_edit")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.pretension_text_edit)

        self.case_name_line_edit = QLineEdit(self.formLayoutWidget)
        self.case_name_line_edit.setObjectName(u"case_name_line_edit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.case_name_line_edit)

        self.nombre_label = QLabel(self.formLayoutWidget)
        self.nombre_label.setObjectName(u"nombre_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.nombre_label)

        self.label_line_edit = QLineEdit(self.formLayoutWidget)
        self.label_line_edit.setObjectName(u"label_line_edit")
        self.label_line_edit.setMaxLength(50)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.label_line_edit)

        self.etiqueta_label = QLabel(self.formLayoutWidget)
        self.etiqueta_label.setObjectName(u"etiqueta_label")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.etiqueta_label)

        self.demandante_label = QLabel(self.formLayoutWidget)
        self.demandante_label.setObjectName(u"demandante_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.demandante_label)

        self.claimant_line_edit = QLineEdit(self.formLayoutWidget)
        self.claimant_line_edit.setObjectName(u"claimant_line_edit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.claimant_line_edit)

        self.demandado_label = QLabel(self.formLayoutWidget)
        self.demandado_label.setObjectName(u"demandado_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.demandado_label)

        self.defendant_line_edit = QLineEdit(self.formLayoutWidget)
        self.defendant_line_edit.setObjectName(u"defendant_line_edit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.defendant_line_edit)

        self.radicado_label = QLabel(self.formLayoutWidget)
        self.radicado_label.setObjectName(u"radicado_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.radicado_label)

        self.radicado_line_edit = QLineEdit(self.formLayoutWidget)
        self.radicado_line_edit.setObjectName(u"radicado_line_edit")
        self.radicado_line_edit.setInputMethodHints(Qt.ImhDigitsOnly)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.radicado_line_edit)

        self.subsidiary_hypothesis_label = QLabel(self.formLayoutWidget)
        self.subsidiary_hypothesis_label.setObjectName(u"subsidiary_hypothesis_label")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.subsidiary_hypothesis_label)

        self.subsidiary_hypothesis_text_edit = QPlainTextEdit(self.formLayoutWidget)
        self.subsidiary_hypothesis_text_edit.setObjectName(u"subsidiary_hypothesis_text_edit")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.subsidiary_hypothesis_text_edit)

        self.button_box = QDialogButtonBox(NewCaseForm)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setGeometry(QRect(270, 400, 193, 28))
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        QWidget.setTabOrder(self.case_name_line_edit, self.claimant_line_edit)
        QWidget.setTabOrder(self.claimant_line_edit, self.defendant_line_edit)
        QWidget.setTabOrder(self.defendant_line_edit, self.radicado_line_edit)
        QWidget.setTabOrder(self.radicado_line_edit, self.label_line_edit)
        QWidget.setTabOrder(self.label_line_edit, self.subsidiary_hypothesis_text_edit)
        QWidget.setTabOrder(self.subsidiary_hypothesis_text_edit, self.pretension_text_edit)

        self.retranslateUi(NewCaseForm)

        QMetaObject.connectSlotsByName(NewCaseForm)
    # setupUi

    def retranslateUi(self, NewCaseForm):
        NewCaseForm.setWindowTitle(QCoreApplication.translate("NewCaseForm", u"Form", None))
        self.pretension_label.setText(QCoreApplication.translate("NewCaseForm", u"Hypothesis description:", None))
#if QT_CONFIG(whatsthis)
        self.pretension_text_edit.setWhatsThis(QCoreApplication.translate("NewCaseForm", u"<html><head/><body><p>In this field you may enter a detailed description of the hypothesis.</p><p><span style=\" font-style:italic;\">Optional field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.pretension_text_edit.setPlaceholderText(QCoreApplication.translate("NewCaseForm", u"Optional", None))
#if QT_CONFIG(whatsthis)
        self.case_name_line_edit.setWhatsThis(QCoreApplication.translate("NewCaseForm", u"<html><head/><body><p>The name of the new process. Must be unique.</p><p><span style=\" font-weight:600; font-style:italic;\">Mandatory field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.case_name_line_edit.setInputMask("")
        self.case_name_line_edit.setPlaceholderText(QCoreApplication.translate("NewCaseForm", u"Mandatory", None))
        self.nombre_label.setText(QCoreApplication.translate("NewCaseForm", u"Process name:", None))
#if QT_CONFIG(whatsthis)
        self.label_line_edit.setWhatsThis(QCoreApplication.translate("NewCaseForm", u"<html><head/><body><p>This represents the text that is shown in the hypothesis graphical node. It allows up to 50 characters. </p><p><span style=\" font-weight:600; font-style:italic;\">Mandatory field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.label_line_edit.setPlaceholderText(QCoreApplication.translate("NewCaseForm", u"Mandatory", None))
        self.etiqueta_label.setText(QCoreApplication.translate("NewCaseForm", u"Main hypothesis:", None))
        self.demandante_label.setText(QCoreApplication.translate("NewCaseForm", u"Claimant:", None))
#if QT_CONFIG(whatsthis)
        self.claimant_line_edit.setWhatsThis(QCoreApplication.translate("NewCaseForm", u"<html><head/><body><p>Name of the process claimant.</p><p><span style=\" font-weight:600;\">Mandatory field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.claimant_line_edit.setPlaceholderText(QCoreApplication.translate("NewCaseForm", u"Mandatory", None))
        self.demandado_label.setText(QCoreApplication.translate("NewCaseForm", u"Defendant:", None))
#if QT_CONFIG(whatsthis)
        self.defendant_line_edit.setWhatsThis(QCoreApplication.translate("NewCaseForm", u"<html><head/><body><p>Name of the process defendant.</p><p><span style=\" font-weight:600;\">Mandatory field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.defendant_line_edit.setPlaceholderText(QCoreApplication.translate("NewCaseForm", u"Mandatory", None))
        self.radicado_label.setText(QCoreApplication.translate("NewCaseForm", u"Process number:", None))
#if QT_CONFIG(whatsthis)
        self.radicado_line_edit.setWhatsThis(QCoreApplication.translate("NewCaseForm", u"<html><head/><body><p>Process number. It only accepts up to 25 digits.</p><p><span style=\" font-weight:600;\">Mandatory field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.radicado_line_edit.setPlaceholderText(QCoreApplication.translate("NewCaseForm", u"Mandatory", None))
        self.subsidiary_hypothesis_label.setText(QCoreApplication.translate("NewCaseForm", u"Subsidiary pretensions::", None))
#if QT_CONFIG(whatsthis)
        self.subsidiary_hypothesis_text_edit.setWhatsThis(QCoreApplication.translate("NewCaseForm", u"<html><head/><body><p>Process subsidiary pretensions.</p><p>The following order is suggested:</p><p>1. Consequential or succesive</p><p>2. Eventual</p><p>3. Alternative</p><p><span style=\" font-style:italic;\">Optional field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.subsidiary_hypothesis_text_edit.setPlaceholderText(QCoreApplication.translate("NewCaseForm", u"Optional", None))
    # retranslateUi

