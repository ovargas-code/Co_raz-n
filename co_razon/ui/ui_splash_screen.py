# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'splash_screenAAkuyd.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SplashScreen(object):
    def setupUi(self, SplashScreen):
        if not SplashScreen.objectName():
            SplashScreen.setObjectName(u"SplashScreen")
        SplashScreen.resize(800, 474)
        self.centralwidget = QWidget(SplashScreen)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.dropShadowFrame = QFrame(self.centralwidget)
        self.dropShadowFrame.setObjectName(u"dropShadowFrame")
        self.dropShadowFrame.setStyleSheet(u"QFrame{\n"
"	background-color: rgb(15, 23, 42);\n"
"	color: rgb(241, 245, 249);\n"
"	border-radius: 10px;\n"
"}")
        self.dropShadowFrame.setFrameShape(QFrame.StyledPanel)
        self.dropShadowFrame.setFrameShadow(QFrame.Raised)
        self.label_title = QLabel(self.dropShadowFrame)
        self.label_title.setObjectName(u"label_title")
        self.label_title.setGeometry(QRect(0, 110, 781, 91))
        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(44)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet(u"color: rgb(251, 113, 133); font-weight: bold;")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_description = QLabel(self.dropShadowFrame)
        self.label_description.setObjectName(u"label_description")
        self.label_description.setGeometry(QRect(0, 190, 781, 41))
        font1 = QFont()
        font1.setFamily(u"Segoe UI")
        font1.setPointSize(14)
        self.label_description.setFont(font1)
        self.label_description.setStyleSheet(u"color: rgb(148, 163, 184);")
        self.label_description.setAlignment(Qt.AlignCenter)
        self.progressBar = QProgressBar(self.dropShadowFrame)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(60, 270, 661, 20))
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"	color: rgb(241, 245, 249);\n"
"	background-color:  rgb(30, 41, 59);\n"
"	border-style: none;\n"
"	border-radius: 10px;\n"
"	text-align: center;\n"
"}\n"
"QProgressBar::chunk{\n"
"	border-radius: 10px;\n"
"	background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(251, 113, 133, 255), stop:1 rgba(99, 102, 241, 255))\n"
"}")
        self.progressBar.setValue(24)
        self.label_loading = QLabel(self.dropShadowFrame)
        self.label_loading.setObjectName(u"label_loading")
        self.label_loading.setGeometry(QRect(0, 300, 781, 31))
        font2 = QFont()
        font2.setFamily(u"Segoe UI")
        font2.setPointSize(11)
        self.label_loading.setFont(font2)
        self.label_loading.setStyleSheet(u"color: rgb(148, 163, 184);")
        self.label_loading.setAlignment(Qt.AlignCenter)
        self.label_credits = QLabel(self.dropShadowFrame)
        self.label_credits.setObjectName(u"label_credits")
        self.label_credits.setGeometry(QRect(430, 400, 331, 31))
        font3 = QFont()
        font3.setFamily(u"Segoe UI")
        font3.setPointSize(9)
        self.label_credits.setFont(font3)
        self.label_credits.setStyleSheet(u"color: rgb(100, 116, 139);")
        self.label_credits.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_image = QLabel(self.dropShadowFrame)
        self.label_image.setObjectName(u"label_image")
        self.label_image.setGeometry(QRect(0, 0, 0, 0))
        self.label_image.setStyleSheet(u"")
        self.label_image.setPixmap(QPixmap())
        self.label_image.setScaledContents(False)
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_credits_2 = QLabel(self.dropShadowFrame)
        self.label_credits_2.setObjectName(u"label_credits_2")
        self.label_credits_2.setGeometry(QRect(340, 400, 91, 31))
        self.label_credits_2.setFont(font3)
        self.label_credits_2.setStyleSheet(u"color: rgb(100, 116, 139);")
        self.label_credits_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout.addWidget(self.dropShadowFrame)

        SplashScreen.setCentralWidget(self.centralwidget)

        self.retranslateUi(SplashScreen)

        QMetaObject.connectSlotsByName(SplashScreen)
    # setupUi

    def retranslateUi(self, SplashScreen):
        SplashScreen.setWindowTitle(QCoreApplication.translate("SplashScreen", u"MainWindow", None))
        self.label_title.setText(QCoreApplication.translate("SplashScreen", u"Co_razón", None))
        self.label_description.setText(QCoreApplication.translate("SplashScreen", u"The proof of an illusion", None))
        self.label_loading.setText(QCoreApplication.translate("SplashScreen", u"Loading...", None))
        self.label_credits.setText(QCoreApplication.translate("SplashScreen", u"<html><head/><body><p>Ori\u00f3n Vargas</p></body></html>", None))
        self.label_image.setText("")
        self.label_credits_2.setText(QCoreApplication.translate("SplashScreen", u"<html><head/><body><p><span style=\" font-weight:600;\">Created by:</span></p></body></html>", None))
    # retranslateUi

