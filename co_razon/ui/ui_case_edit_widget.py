# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'case_edit_widgetrvTYml.ui'
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


class Ui_CaseEditForm(object):
    def setupUi(self, CaseEditForm):
        if not CaseEditForm.objectName():
            CaseEditForm.setObjectName(u"CaseEditForm")
        CaseEditForm.resize(472, 513)
        self.verticalLayout = QVBoxLayout(CaseEditForm)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.verticalLayout.setContentsMargins(2, 5, 2, 0)
        self.frame = QFrame(CaseEditForm)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.formLayout_2 = QFormLayout(self.frame)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label)

        self.radicado_line_edit = QLineEdit(self.frame)
        self.radicado_line_edit.setObjectName(u"radicado_line_edit")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.radicado_line_edit)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.claimant_line_edit = QLineEdit(self.frame)
        self.claimant_line_edit.setObjectName(u"claimant_line_edit")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.claimant_line_edit)

        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.defendant_line_edit = QLineEdit(self.frame)
        self.defendant_line_edit.setObjectName(u"defendant_line_edit")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.defendant_line_edit)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(CaseEditForm)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.frame_2)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.etiqueta_label = QLabel(self.frame_2)
        self.etiqueta_label.setObjectName(u"etiqueta_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.etiqueta_label)

        self.pretension_label = QLabel(self.frame_2)
        self.pretension_label.setObjectName(u"pretension_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.pretension_label)

        self.label_4 = QLabel(self.frame_2)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_4)

        self.pretension_text_edit = QPlainTextEdit(self.frame_2)
        self.pretension_text_edit.setObjectName(u"pretension_text_edit")
        self.pretension_text_edit.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.pretension_text_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        self.formLayout.setWidget(3, QFormLayout.SpanningRole, self.pretension_text_edit)

        self.subsidiary_hypothesis_text_edit = QPlainTextEdit(self.frame_2)
        self.subsidiary_hypothesis_text_edit.setObjectName(u"subsidiary_hypothesis_text_edit")
        self.subsidiary_hypothesis_text_edit.setReadOnly(True)

        self.formLayout.setWidget(5, QFormLayout.SpanningRole, self.subsidiary_hypothesis_text_edit)

        self.label_line_edit = QLineEdit(self.frame_2)
        self.label_line_edit.setObjectName(u"label_line_edit")
        self.label_line_edit.setMaxLength(50)

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.label_line_edit)


        self.verticalLayout.addWidget(self.frame_2)


        self.retranslateUi(CaseEditForm)

        QMetaObject.connectSlotsByName(CaseEditForm)
    # setupUi

    def retranslateUi(self, CaseEditForm):
        CaseEditForm.setWindowTitle(QCoreApplication.translate("CaseEditForm", u"Form", None))
        self.label.setText(QCoreApplication.translate("CaseEditForm", u"Process number:", None))
        self.radicado_line_edit.setPlaceholderText(QCoreApplication.translate("CaseEditForm", u"Mandatory", None))
        self.label_2.setText(QCoreApplication.translate("CaseEditForm", u"Claimant:", None))
        self.claimant_line_edit.setPlaceholderText(QCoreApplication.translate("CaseEditForm", u"Mandatory", None))
        self.label_3.setText(QCoreApplication.translate("CaseEditForm", u"Defendant:", None))
        self.defendant_line_edit.setPlaceholderText(QCoreApplication.translate("CaseEditForm", u"Mandatory", None))
        self.etiqueta_label.setText(QCoreApplication.translate("CaseEditForm", u"Main hypothesis:", None))
        self.pretension_label.setText(QCoreApplication.translate("CaseEditForm", u"Main hypothesis description:", None))
        self.label_4.setText(QCoreApplication.translate("CaseEditForm", u"Subsidiary pretensions:", None))
#if QT_CONFIG(whatsthis)
        self.pretension_text_edit.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.pretension_text_edit.setPlaceholderText(QCoreApplication.translate("CaseEditForm", u"Optional", None))
        self.subsidiary_hypothesis_text_edit.setPlaceholderText(QCoreApplication.translate("CaseEditForm", u"Optional", None))
#if QT_CONFIG(whatsthis)
        self.label_line_edit.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.label_line_edit.setPlaceholderText(QCoreApplication.translate("CaseEditForm", u"Mandatory", None))
    # retranslateUi

