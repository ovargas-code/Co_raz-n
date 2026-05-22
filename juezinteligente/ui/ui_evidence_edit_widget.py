# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'evidence_edit_widgetPsAiDu.ui'
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


class Ui_EvidenceEditForm(object):
    def setupUi(self, EvidenceEditForm):
        if not EvidenceEditForm.objectName():
            EvidenceEditForm.setObjectName(u"EvidenceEditForm")
        EvidenceEditForm.resize(452, 512)
        self.formLayout_2 = QFormLayout(EvidenceEditForm)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setRowWrapPolicy(QFormLayout.WrapAllRows)
        self.formLayout_2.setContentsMargins(2, 5, 2, 0)
        self.evidence_label = QLabel(EvidenceEditForm)
        self.evidence_label.setObjectName(u"evidence_label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.evidence_label)

        self.evidence_label_line_edit = QLineEdit(EvidenceEditForm)
        self.evidence_label_line_edit.setObjectName(u"evidence_label_line_edit")
        self.evidence_label_line_edit.setMaxLength(50)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.evidence_label_line_edit)

        self.evidence_type_label = QLabel(EvidenceEditForm)
        self.evidence_type_label.setObjectName(u"evidence_type_label")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.evidence_type_label)

        self.evidence_type_combo_box = QComboBox(EvidenceEditForm)
        self.evidence_type_combo_box.setObjectName(u"evidence_type_combo_box")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.evidence_type_combo_box)

        self.relevancia_label = QLabel(EvidenceEditForm)
        self.relevancia_label.setObjectName(u"relevancia_label")

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.relevancia_label)

        self.relevance_combo_box = QComboBox(EvidenceEditForm)
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.addItem("")
        self.relevance_combo_box.setObjectName(u"relevance_combo_box")

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.relevance_combo_box)

        self.credibility_label = QLabel(EvidenceEditForm)
        self.credibility_label.setObjectName(u"credibility_label")

        self.formLayout_2.setWidget(5, QFormLayout.LabelRole, self.credibility_label)

        self.credibility_combo_box = QComboBox(EvidenceEditForm)
        self.credibility_combo_box.addItem("")
        self.credibility_combo_box.addItem("")
        self.credibility_combo_box.addItem("")
        self.credibility_combo_box.addItem("")
        self.credibility_combo_box.addItem("")
        self.credibility_combo_box.addItem("")
        self.credibility_combo_box.addItem("")
        self.credibility_combo_box.setObjectName(u"credibility_combo_box")

        self.formLayout_2.setWidget(5, QFormLayout.FieldRole, self.credibility_combo_box)

        self.rule_text_edit = QPlainTextEdit(EvidenceEditForm)
        self.rule_text_edit.setObjectName(u"rule_text_edit")
        self.rule_text_edit.setReadOnly(True)

        self.formLayout_2.setWidget(7, QFormLayout.FieldRole, self.rule_text_edit)

        self.evidence_desc_text_edit = QPlainTextEdit(EvidenceEditForm)
        self.evidence_desc_text_edit.setObjectName(u"evidence_desc_text_edit")

        self.formLayout_2.setWidget(3, QFormLayout.SpanningRole, self.evidence_desc_text_edit)

        self.evidence_desc_label = QLabel(EvidenceEditForm)
        self.evidence_desc_label.setObjectName(u"evidence_desc_label")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.evidence_desc_label)

        self.rule_label = QLabel(EvidenceEditForm)
        self.rule_label.setObjectName(u"rule_label")

        self.formLayout_2.setWidget(6, QFormLayout.FieldRole, self.rule_label)


        self.retranslateUi(EvidenceEditForm)

        self.relevance_combo_box.setCurrentIndex(0)
        self.credibility_combo_box.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(EvidenceEditForm)
    # setupUi

    def retranslateUi(self, EvidenceEditForm):
        EvidenceEditForm.setWindowTitle(QCoreApplication.translate("EvidenceEditForm", u"Form", None))
        self.evidence_label.setText(QCoreApplication.translate("EvidenceEditForm", u"Evidence label:", None))
#if QT_CONFIG(whatsthis)
        self.evidence_label_line_edit.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.evidence_label_line_edit.setPlaceholderText(QCoreApplication.translate("EvidenceEditForm", u"Mandatory", None))
        self.evidence_type_label.setText(QCoreApplication.translate("EvidenceEditForm", u"Evidence type:", None))
#if QT_CONFIG(whatsthis)
        self.evidence_type_combo_box.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.relevancia_label.setText(QCoreApplication.translate("EvidenceEditForm", u"Pertinence:", None))
        self.relevance_combo_box.setItemText(0, QCoreApplication.translate("EvidenceEditForm", u"Unsupported", None))
        self.relevance_combo_box.setItemText(1, QCoreApplication.translate("EvidenceEditForm", u"Unlikely", None))
        self.relevance_combo_box.setItemText(2, QCoreApplication.translate("EvidenceEditForm", u"Likely", None))
        self.relevance_combo_box.setItemText(3, QCoreApplication.translate("EvidenceEditForm", u"Most likely", None))
        self.relevance_combo_box.setItemText(4, QCoreApplication.translate("EvidenceEditForm", u"Very likely", None))
        self.relevance_combo_box.setItemText(5, QCoreApplication.translate("EvidenceEditForm", u"Almost true", None))
        self.relevance_combo_box.setItemText(6, QCoreApplication.translate("EvidenceEditForm", u"True", None))

        self.credibility_label.setText(QCoreApplication.translate("EvidenceEditForm", u"Credibility:", None))
        self.credibility_combo_box.setItemText(0, QCoreApplication.translate("EvidenceEditForm", u"Unsupported", None))
        self.credibility_combo_box.setItemText(1, QCoreApplication.translate("EvidenceEditForm", u"Unlikely", None))
        self.credibility_combo_box.setItemText(2, QCoreApplication.translate("EvidenceEditForm", u"Likely", None))
        self.credibility_combo_box.setItemText(3, QCoreApplication.translate("EvidenceEditForm", u"Most likely", None))
        self.credibility_combo_box.setItemText(4, QCoreApplication.translate("EvidenceEditForm", u"Very likely", None))
        self.credibility_combo_box.setItemText(5, QCoreApplication.translate("EvidenceEditForm", u"Almost true", None))
        self.credibility_combo_box.setItemText(6, QCoreApplication.translate("EvidenceEditForm", u"True", None))

#if QT_CONFIG(whatsthis)
        self.evidence_desc_text_edit.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.evidence_desc_text_edit.setPlaceholderText(QCoreApplication.translate("EvidenceEditForm", u"Optional", None))
        self.evidence_desc_label.setText(QCoreApplication.translate("EvidenceEditForm", u"Evidence description:", None))
        self.rule_label.setText(QCoreApplication.translate("EvidenceEditForm", u"Experience rule:", None))
    # retranslateUi

