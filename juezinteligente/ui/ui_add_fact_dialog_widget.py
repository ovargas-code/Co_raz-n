# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_fact_dialog_widgetDVAcWv.ui'
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


class Ui_AddFactForm(object):
    def setupUi(self, AddFactForm):
        if not AddFactForm.objectName():
            AddFactForm.setObjectName(u"AddFactForm")
        AddFactForm.resize(472, 348)
        self.formLayoutWidget = QWidget(AddFactForm)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 10, 451, 291))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.selected_label = QLabel(self.formLayoutWidget)
        self.selected_label.setObjectName(u"selected_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.selected_label)

        self.selected_line_edit = QLineEdit(self.formLayoutWidget)
        self.selected_line_edit.setObjectName(u"selected_line_edit")
        self.selected_line_edit.setReadOnly(True)
        self.selected_line_edit.setClearButtonEnabled(False)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.selected_line_edit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.formLayout.setItem(1, QFormLayout.LabelRole, self.horizontalSpacer)

        self.hecho_label = QLabel(self.formLayoutWidget)
        self.hecho_label.setObjectName(u"hecho_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.hecho_label)

        self.fact_label_line_edit = QLineEdit(self.formLayoutWidget)
        self.fact_label_line_edit.setObjectName(u"fact_label_line_edit")
        self.fact_label_line_edit.setMaxLength(50)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.fact_label_line_edit)

        self.favorabilidad_label = QLabel(self.formLayoutWidget)
        self.favorabilidad_label.setObjectName(u"favorabilidad_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.favorabilidad_label)

        self.fact_desc_label = QLabel(self.formLayoutWidget)
        self.fact_desc_label.setObjectName(u"fact_desc_label")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.fact_desc_label)

        self.fact_desc_text_edit = QPlainTextEdit(self.formLayoutWidget)
        self.fact_desc_text_edit.setObjectName(u"fact_desc_text_edit")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.fact_desc_text_edit)

        self.widget = QWidget(self.formLayoutWidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, -1, 0)
        self.fav_radio_button = QRadioButton(self.widget)
        self.favorability_button_group = QButtonGroup(AddFactForm)
        self.favorability_button_group.setObjectName(u"favorability_button_group")
        self.favorability_button_group.setExclusive(True)
        self.favorability_button_group.addButton(self.fav_radio_button)
        self.fav_radio_button.setObjectName(u"fav_radio_button")
        self.fav_radio_button.setChecked(True)

        self.horizontalLayout.addWidget(self.fav_radio_button)

        self.unfav_radio_button = QRadioButton(self.widget)
        self.favorability_button_group.addButton(self.unfav_radio_button)
        self.unfav_radio_button.setObjectName(u"unfav_radio_button")

        self.horizontalLayout.addWidget(self.unfav_radio_button)


        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.widget)

        self.button_box = QDialogButtonBox(AddFactForm)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setGeometry(QRect(270, 310, 193, 28))
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        QWidget.setTabOrder(self.fact_label_line_edit, self.fav_radio_button)
        QWidget.setTabOrder(self.fav_radio_button, self.unfav_radio_button)
        QWidget.setTabOrder(self.unfav_radio_button, self.fact_desc_text_edit)
        QWidget.setTabOrder(self.fact_desc_text_edit, self.selected_line_edit)

        self.retranslateUi(AddFactForm)

        QMetaObject.connectSlotsByName(AddFactForm)
    # setupUi

    def retranslateUi(self, AddFactForm):
        AddFactForm.setWindowTitle(QCoreApplication.translate("AddFactForm", u"Form", None))
        self.selected_label.setText(QCoreApplication.translate("AddFactForm", u"Selected:", None))
#if QT_CONFIG(whatsthis)
        self.selected_line_edit.setWhatsThis(QCoreApplication.translate("AddFactForm", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This field presents the label of the selected hypothesis or fact.</p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.hecho_label.setText(QCoreApplication.translate("AddFactForm", u"Fact label:", None))
#if QT_CONFIG(whatsthis)
        self.fact_label_line_edit.setWhatsThis(QCoreApplication.translate("AddFactForm", u"<html><head/><body><p>Fact label represents the text that is shown in the fact graphical node. It allows up to 50 characters.</p><p><span style=\" font-weight:600; font-style:italic;\">Mandatory field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.fact_label_line_edit.setPlaceholderText(QCoreApplication.translate("AddFactForm", u"Mandatory", None))
        self.favorabilidad_label.setText(QCoreApplication.translate("AddFactForm", u"Favorability:", None))
        self.fact_desc_label.setText(QCoreApplication.translate("AddFactForm", u"Fact description:", None))
#if QT_CONFIG(whatsthis)
        self.fact_desc_text_edit.setWhatsThis(QCoreApplication.translate("AddFactForm", u"<html><head/><body><p>In this field you may enter a detailed description of the fact being added.</p><p><span style=\" font-style:italic;\">Optional field</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.fact_desc_text_edit.setPlaceholderText(QCoreApplication.translate("AddFactForm", u"Optional", None))
#if QT_CONFIG(whatsthis)
        self.widget.setWhatsThis(QCoreApplication.translate("AddFactForm", u"<html><head/><body><p>Aqu\u00ed se selecciona la favorabilidad del hecho que se quiere agregar.</p><p><span style=\" font-weight:600; font-style:italic;\">Este campo es obligatorio</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.fav_radio_button.setText(QCoreApplication.translate("AddFactForm", u"Favorable", None))
        self.unfav_radio_button.setText(QCoreApplication.translate("AddFactForm", u"Unfavorable", None))
    # retranslateUi

