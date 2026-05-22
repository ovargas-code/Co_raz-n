# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fact_edit_widgetKJanlf.ui'
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


class Ui_FactEditForm(object):
    def setupUi(self, FactEditForm):
        if not FactEditForm.objectName():
            FactEditForm.setObjectName(u"FactEditForm")
        FactEditForm.resize(470, 352)
        self.formLayout_2 = QFormLayout(FactEditForm)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setRowWrapPolicy(QFormLayout.WrapAllRows)
        self.formLayout_2.setContentsMargins(2, 5, 2, 0)
        self.hecho_label = QLabel(FactEditForm)
        self.hecho_label.setObjectName(u"hecho_label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.hecho_label)

        self.fact_label_line_edit = QLineEdit(FactEditForm)
        self.fact_label_line_edit.setObjectName(u"fact_label_line_edit")
        self.fact_label_line_edit.setMaxLength(50)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.fact_label_line_edit)

        self.relevancia_label = QLabel(FactEditForm)
        self.relevancia_label.setObjectName(u"relevancia_label")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.relevancia_label)

        self.relevance_combo_box = QComboBox(FactEditForm)
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.setObjectName(u"relevance_combo_box")

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.relevance_combo_box)

        self.fact_desc_label = QLabel(FactEditForm)
        self.fact_desc_label.setObjectName(u"fact_desc_label")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.fact_desc_label)

        self.fact_desc_text_edit = QPlainTextEdit(FactEditForm)
        self.fact_desc_text_edit.setObjectName(u"fact_desc_text_edit")

        self.formLayout_2.setWidget(2, QFormLayout.SpanningRole, self.fact_desc_text_edit)

        self.rule_label = QLabel(FactEditForm)
        self.rule_label.setObjectName(u"rule_label")

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.rule_label)

        self.rule_text_edit = QPlainTextEdit(FactEditForm)
        self.rule_text_edit.setObjectName(u"rule_text_edit")
        self.rule_text_edit.setReadOnly(True)

        self.formLayout_2.setWidget(5, QFormLayout.SpanningRole, self.rule_text_edit)


        self.retranslateUi(FactEditForm)

        self.relevance_combo_box.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(FactEditForm)
    # setupUi

    def retranslateUi(self, FactEditForm):
        FactEditForm.setWindowTitle(QCoreApplication.translate("FactEditForm", u"Form", None))
        self.hecho_label.setText(QCoreApplication.translate("FactEditForm", u"Fact label:", None))
#if QT_CONFIG(whatsthis)
        self.fact_label_line_edit.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.fact_label_line_edit.setPlaceholderText(QCoreApplication.translate("FactEditForm", u"Mandatory", None))
        self.relevancia_label.setText(QCoreApplication.translate("FactEditForm", u"Relevance:", None))
        self.relevance_combo_box.setItemText(0, QCoreApplication.translate("FactEditForm", u"Unsupported", None))
        self.relevance_combo_box.setItemText(1, QCoreApplication.translate("FactEditForm", u"Unlikely", None))
        self.relevance_combo_box.setItemText(2, QCoreApplication.translate("FactEditForm", u"Likely", None))
        self.relevance_combo_box.setItemText(3, QCoreApplication.translate("FactEditForm", u"Most likely", None))
        self.relevance_combo_box.setItemText(4, QCoreApplication.translate("FactEditForm", u"Very likely", None))
        self.relevance_combo_box.setItemText(5, QCoreApplication.translate("FactEditForm", u"Almost true", None))
        self.relevance_combo_box.setItemText(6, QCoreApplication.translate("FactEditForm", u"True", None))

        self.fact_desc_label.setText(QCoreApplication.translate("FactEditForm", u"Fact description:", None))
#if QT_CONFIG(whatsthis)
        self.fact_desc_text_edit.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.fact_desc_text_edit.setPlaceholderText(QCoreApplication.translate("FactEditForm", u"Optional", None))
        self.rule_label.setText(QCoreApplication.translate("FactEditForm", u"Experience rule:", None))
    # retranslateUi

