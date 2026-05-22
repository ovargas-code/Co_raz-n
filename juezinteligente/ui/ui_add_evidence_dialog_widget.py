# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_evidence_dialog_widgetUeuyTf.ui'
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


class Ui_AddEvidenceForm(object):
    def setupUi(self, AddEvidenceForm):
        if not AddEvidenceForm.objectName():
            AddEvidenceForm.setObjectName(u"AddEvidenceForm")
        AddEvidenceForm.resize(472, 375)
        self.formLayoutWidget = QWidget(AddEvidenceForm)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 10, 451, 321))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.evidence_desc_label = QLabel(self.formLayoutWidget)
        self.evidence_desc_label.setObjectName(u"evidence_desc_label")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.evidence_desc_label)

        self.evidence_desc_text_edit = QPlainTextEdit(self.formLayoutWidget)
        self.evidence_desc_text_edit.setObjectName(u"evidence_desc_text_edit")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.evidence_desc_text_edit)

        self.selected_fact_label = QLabel(self.formLayoutWidget)
        self.selected_fact_label.setObjectName(u"selected_fact_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.selected_fact_label)

        self.selected_fact_line_edit = QLineEdit(self.formLayoutWidget)
        self.selected_fact_line_edit.setObjectName(u"selected_fact_line_edit")
        self.selected_fact_line_edit.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.selected_fact_line_edit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.formLayout.setItem(1, QFormLayout.LabelRole, self.horizontalSpacer)

        self.evidence_label = QLabel(self.formLayoutWidget)
        self.evidence_label.setObjectName(u"evidence_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.evidence_label)

        self.evidence_label_line_edit = QLineEdit(self.formLayoutWidget)
        self.evidence_label_line_edit.setObjectName(u"evidence_label_line_edit")
        self.evidence_label_line_edit.setMaxLength(50)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.evidence_label_line_edit)

        self.widget = QWidget(self.formLayoutWidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, -1, 0)
        self.fav_radio_button = QRadioButton(self.widget)
        self.favorability_button_group = QButtonGroup(AddEvidenceForm)
        self.favorability_button_group.setObjectName(u"favorability_button_group")
        self.favorability_button_group.addButton(self.fav_radio_button)
        self.fav_radio_button.setObjectName(u"fav_radio_button")
        self.fav_radio_button.setChecked(True)

        self.horizontalLayout.addWidget(self.fav_radio_button)

        self.unfav_radio_button = QRadioButton(self.widget)
        self.favorability_button_group.addButton(self.unfav_radio_button)
        self.unfav_radio_button.setObjectName(u"unfav_radio_button")

        self.horizontalLayout.addWidget(self.unfav_radio_button)


        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.widget)

        self.favorability_label = QLabel(self.formLayoutWidget)
        self.favorability_label.setObjectName(u"favorability_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.favorability_label)

        self.evidence_type_combo_box = QComboBox(self.formLayoutWidget)
        self.evidence_type_combo_box.setObjectName(u"evidence_type_combo_box")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.evidence_type_combo_box)

        self.evidence_type_label = QLabel(self.formLayoutWidget)
        self.evidence_type_label.setObjectName(u"evidence_type_label")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.evidence_type_label)

        self.button_box = QDialogButtonBox(AddEvidenceForm)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setGeometry(QRect(270, 340, 193, 28))
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        QWidget.setTabOrder(self.evidence_label_line_edit, self.fav_radio_button)
        QWidget.setTabOrder(self.fav_radio_button, self.unfav_radio_button)
        QWidget.setTabOrder(self.unfav_radio_button, self.evidence_type_combo_box)
        QWidget.setTabOrder(self.evidence_type_combo_box, self.evidence_desc_text_edit)
        QWidget.setTabOrder(self.evidence_desc_text_edit, self.selected_fact_line_edit)

        self.retranslateUi(AddEvidenceForm)

        QMetaObject.connectSlotsByName(AddEvidenceForm)
    # setupUi

    def retranslateUi(self, AddEvidenceForm):
        AddEvidenceForm.setWindowTitle(QCoreApplication.translate("AddEvidenceForm", u"Form", None))
        self.evidence_desc_label.setText(QCoreApplication.translate("AddEvidenceForm", u"Evidence description:", None))
#if QT_CONFIG(whatsthis)
        self.evidence_desc_text_edit.setWhatsThis(QCoreApplication.translate("AddEvidenceForm", u"<html><head/><body><p>In this field you may enter a detailed description of the evidence being added.</p><p><span style=\" font-style:italic;\">Optional field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.evidence_desc_text_edit.setPlaceholderText(QCoreApplication.translate("AddEvidenceForm", u"Optional", None))
        self.selected_fact_label.setText(QCoreApplication.translate("AddEvidenceForm", u"Selected fact:", None))
#if QT_CONFIG(whatsthis)
        self.selected_fact_line_edit.setWhatsThis(QCoreApplication.translate("AddEvidenceForm", u"<html><head/><body><p>This field show the label of the selected fact.</p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.evidence_label.setText(QCoreApplication.translate("AddEvidenceForm", u"Evidence label:", None))
#if QT_CONFIG(whatsthis)
        self.evidence_label_line_edit.setWhatsThis(QCoreApplication.translate("AddEvidenceForm", u"<html><head/><body><p>Evidence label represents the text that is shown in the evidence graphical node. It allows up to 50 characters.</p><p><span style=\" font-weight:600; font-style:italic;\">Mandatory field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.evidence_label_line_edit.setPlaceholderText(QCoreApplication.translate("AddEvidenceForm", u"Mandatory", None))
#if QT_CONFIG(whatsthis)
        self.widget.setWhatsThis(QCoreApplication.translate("AddEvidenceForm", u"<html><head/><body><p>Aqu\u00ed se selecciona la favorabilidad del hecho que se quiere agregar.</p><p><span style=\" font-weight:600; font-style:italic;\">Este campo es obligatorio</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.fav_radio_button.setText(QCoreApplication.translate("AddEvidenceForm", u"Favorable", None))
        self.unfav_radio_button.setText(QCoreApplication.translate("AddEvidenceForm", u"Unfavorable", None))
        self.favorability_label.setText(QCoreApplication.translate("AddEvidenceForm", u"Favorability", None))
#if QT_CONFIG(whatsthis)
        self.evidence_type_combo_box.setWhatsThis(QCoreApplication.translate("AddEvidenceForm", u"<html><head/><body><p>In this field you can select the type of evidence to be added to the case.</p><p><span style=\" font-weight:600; font-style:italic;\">Mandatory field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.evidence_type_label.setText(QCoreApplication.translate("AddEvidenceForm", u"Evidence type:", None))
    # retranslateUi

