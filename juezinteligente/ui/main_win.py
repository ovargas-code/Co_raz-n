import logging

from PySide2.QtCore import QSize, Qt, QTimer, QCoreApplication, QRegExp
from PySide2.QtGui import QIcon, QStandardItem, QStandardItemModel, QColor, QPixmap, QRegExpValidator
from PySide2.QtWidgets import QMainWindow, QDialog, QTabWidget, QAction, QWidget, QMessageBox, \
    QPlainTextEdit, QComboBox, QLineEdit, QDockWidget, QButtonGroup, QListWidget, \
    QListWidgetItem, QListView, QTableView, QHeaderView, QInputDialog, QToolBar, \
    QGraphicsDropShadowEffect, QFileDialog, QHBoxLayout
from dependency_injector.wiring import Provide, inject

from juezinteligente.model.judge import Case, Hypothesis, Fact, Evidence, Observer, ModelChecker
from juezinteligente.persistence.data_access import DataAccessManager, ImportCasesError, NotValidFile
from juezinteligente.reports.report import DocxReportGenerator
from juezinteligente.ui.constants import Constants
from juezinteligente.ui.graph import CaseView, EvidenceNode, FactNode, HypothesisNode
from juezinteligente.ui.ui_add_evidence_dialog_widget import Ui_AddEvidenceForm
from juezinteligente.ui.ui_add_fact_dialog_widget import Ui_AddFactForm
from juezinteligente.ui.ui_case_edit_widget import Ui_CaseEditForm
from juezinteligente.ui.ui_evidence_edit_widget import Ui_EvidenceEditForm
from juezinteligente.ui.ui_fact_edit_widget import Ui_FactEditForm
from juezinteligente.ui.ui_manage_cases_dialog_widget import Ui_ManageCasesForm
from juezinteligente.ui.ui_new_case_dialog_widget import Ui_NewCaseForm
from juezinteligente.ui.ui_no_selection_widget import Ui_NoSelectionForm
from juezinteligente.ui.ui_open_case_dialog_widget import Ui_OpenCaseForm
from juezinteligente.ui.ui_splash_screen import Ui_SplashScreen
from juezinteligente.util.containers import Container
from juezinteligente.util.custom_exceptions import ProbatoryWeightException
from juezinteligente.ui.import_pdf_dialog import ImportPdfDialog

logger = logging.getLogger(__name__)
counter = 0


class SplashScreen(QMainWindow):
    def __init__(self):
        super(SplashScreen, self).__init__()
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        self.step = 0

        # Remove title bar
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set window icon
        self.setWindowIcon(QIcon(":/images/img/judge.png"))

        # Add judge image (hidden per user request)
        self.ui.label_image.hide()

        # Drop shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        # QTimer -> Start
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        # Timer in milliseconds
        self.timer.start(35)

        # Show Splash Screen
        self.show()

    def change_loading_text(self, text):
        self.step += 1
        QTimer.singleShot(1500 * self.step, lambda: self.ui.label_loading.setText(self.tr(text)))

    def progress(self):
        global counter

        # set value to progress bar
        self.ui.progressBar.setValue(counter)

        # close splash screen and open app
        if counter > 100:
            # stop timer
            self.timer.stop()

            # show main window
            main_win = JuezInteligenteWindow()
            main_win.showMaximized()

            # close splash screen
            self.close()

        # Increase counter
        counter += 1


class NoSelectionWidget(QWidget):
    """
    The widget to be shown in the properties view when no node is selected
    """
    def __init__(self, constants: Constants = Provide[Container.constants], parent=None):
        super(NoSelectionWidget, self).__init__(parent)
        self.ui = Ui_NoSelectionForm()
        self.ui.setupUi(self)
        self.window_title = constants.PROPERTIES_VIEW


class HypothesisEditorWidget(QWidget):
    """
    The widget that is shown in the properties view when an hypothesis node is selected
    """
    def __init__(self, node, constants: Constants = Provide[Container.constants], parent=None):
        super(HypothesisEditorWidget, self).__init__(parent)
        self.window_title = constants.HYPOTHESIS_PROPERTIES
        self.model: Hypothesis = node.model
        self.node = node

        self.ui = Ui_CaseEditForm()
        self.ui.setupUi(self)

        self.ui.subsidiary_hypothesis_text_edit.setPlaceholderText(constants.SUBSIDIARY_HYPO_PLACEHOLDER)

        self.ui.radicado_line_edit.setValidator(QRegExpValidator(QRegExp('\\d{25}'), self.ui.radicado_line_edit))

        self.ui.label_line_edit.setText(self.model.label)
        self.ui.pretension_text_edit.setPlainText(self.model.desc)
        self.ui.radicado_line_edit.setText(self.model._instance.radicado)
        self.ui.claimant_line_edit.setText(self.model._instance.claimant)
        self.ui.defendant_line_edit.setText(self.model._instance.defendant)
        self.ui.subsidiary_hypothesis_text_edit.setPlainText(self.model._instance.subsidiary_pretensions)

        self.ui.label_line_edit.textChanged.connect(self.update_model)
        self.ui.pretension_text_edit.textChanged.connect(self.update_model)
        self.ui.radicado_line_edit.textChanged.connect(self.update_model)
        self.ui.claimant_line_edit.textChanged.connect(self.update_model)
        self.ui.defendant_line_edit.textChanged.connect(self.update_model)
        self.ui.subsidiary_hypothesis_text_edit.textChanged.connect(self.update_model)

    def update_model(self):
        self.model.label = self.ui.label_line_edit.text()
        self.model.desc = self.ui.pretension_text_edit.toPlainText()
        self.model._instance.radicado = self.ui.radicado_line_edit.text()
        self.model._instance.claimant = self.ui.claimant_line_edit.text()
        self.model._instance.defendant = self.ui.defendant_line_edit.text()
        self.model._instance.subsidiary_pretensions = self.ui.subsidiary_hypothesis_text_edit.toPlainText()

        self.node.update()


@Observer.register
class FactEditorWidget(QWidget):
    """
    The widget that is shown in the properties view when a fact node is selected
    """
    def __init__(self, node, constants: Constants = Provide[Container.constants], parent=None):
        super(FactEditorWidget, self).__init__(parent)
        self.ui = Ui_FactEditForm()
        self.ui.setupUi(self)

        self.window_title = constants.FACT_PROPERTIES
        self.model: Fact = node.model
        self.model.register_observer(self)
        self.node = node

        # This field is for managing when the relevance combo box changes and updates the model.
        # Since the model has the widget as an observer, the selected data from the combo will be
        # lost when the model updates its observer. So we need a flag to avoid this
        self.relevance_change_flag: bool = False

        self.ui.fact_label_line_edit.setText(self.model.label)
        self.ui.fact_desc_text_edit.setPlainText(self.model.desc)
        self.ui.relevance_combo_box.setCurrentText(self.model.relevance)
        self.ui.rule_text_edit.setPlainText(self.model.generate_experience_rule())

        self.ui.fact_label_line_edit.textChanged.connect(self.update_model)
        self.ui.fact_desc_text_edit.textChanged.connect(self.update_model)
        self.ui.relevance_combo_box.currentIndexChanged.connect(self.update_model)

    def update_model(self):
        self.relevance_change_flag = True

        self.model.label = self.ui.fact_label_line_edit.text()
        self.model.desc = self.ui.fact_desc_text_edit.toPlainText()
        self.model.relevance = self.ui.relevance_combo_box.currentText()

        self.node.update()
        self.relevance_change_flag = False

    def update_observer(self, obj):
        self.ui.rule_text_edit.setPlainText(self.model.generate_experience_rule())

        if not self.relevance_change_flag:
            self.ui.relevance_combo_box.setCurrentText(self.model.relevance)


@Observer.register
class EvidenceEditorWidget(QWidget):
    """
    The widget that is shown in the properties view when an evidence node is selected
    """
    def __init__(self, node,
                 constants: Constants = Provide[Container.constants],
                 evidence_type_repr = Provide[Container.evidence_type_repr],
                 parent=None):
        super(EvidenceEditorWidget, self).__init__(parent)
        self.ui = Ui_EvidenceEditForm()
        self.ui.setupUi(self)

        self.window_title = constants.EVIDENCE_PROPERTIES
        self.resize(300, 200)
        self.model: Evidence = node.model
        self.model.register_observer(self)
        self.node = node
        # This field is for managing when the relevance combo box changes and updates the model.
        # Since the model has the widget as an observer, the selected data from the combo will be
        # lost when the model updates its observer. So we need a flag to avoid this
        self.relevance_change_flag: bool = False

        self.ui.evidence_type_combo_box.addItems(evidence_type_repr.list_values())

        self.ui.evidence_label_line_edit.setText(self.model.label)
        self.ui.evidence_desc_text_edit.setPlainText(self.model.desc)
        self.ui.relevance_combo_box.setCurrentText(self.model.relevance)
        self.ui.credibility_combo_box.setCurrentText(self.model.credibility)
        self.ui.evidence_type_combo_box.setCurrentText(self.model.type)
        self.ui.rule_text_edit.setPlainText(self.model.generate_experience_rule())

        self.ui.evidence_label_line_edit.textChanged.connect(self.update_model)
        self.ui.evidence_desc_text_edit.textChanged.connect(self.update_model)
        self.ui.relevance_combo_box.currentIndexChanged.connect(self.update_model)
        self.ui.credibility_combo_box.currentIndexChanged.connect(self.update_model)
        self.ui.evidence_type_combo_box.currentIndexChanged.connect(self.update_model)

    def update_model(self):
        self.relevance_change_flag = True

        self.model.label = self.ui.evidence_label_line_edit.text()
        self.model.desc = self.ui.evidence_desc_text_edit.toPlainText()
        self.model.relevance = self.ui.relevance_combo_box.currentText()
        self.model.credibility = self.ui.credibility_combo_box.currentText()
        self.model.type = self.ui.evidence_type_combo_box.currentText()

        self.node.update()
        self.relevance_change_flag = False

    def update_observer(self, obj):
        self.ui.rule_text_edit.setPlainText(self.model.generate_experience_rule())

        if not self.relevance_change_flag:
            self.ui.relevance_combo_box.setCurrentText(self.model.relevance)
            self.ui.credibility_combo_box.setCurrentText(self.model.credibility)


@Observer.register
class JuezInteligenteWindow(QMainWindow):
    """
    The main window of the application. This class is registered as an observer for the model elements.
    The @Observer.register decorator is a way to indicate that this class implements the Observer interface
    """
    @inject
    def __init__(self, data_access_manager: DataAccessManager = Provide[Container.data_access_manager],
                 constants: Constants = Provide[Container.constants],
                 evidence_type_repr = Provide[Container.evidence_type_repr],
                 parent=None):
        super(JuezInteligenteWindow, self).__init__(parent)

        self.data_access_manager: DataAccessManager = data_access_manager
        self.constants = constants
        self.evidence_type_repr = evidence_type_repr
        self.tab_container = QTabWidget(self)
        self.tab_container.setObjectName("tab_container")
        self.tab_container.setTabsClosable(True)
        self.tab_container.tabCloseRequested.connect(self.on_tab_closed)
        self.tab_container.currentChanged.connect(self.on_tab_changed)
        self.cases_views = dict()
        self.config_window()
        self.properties_editor_widget = QDockWidget()
        self.properties_editor_widget.setWindowTitle(self.constants.PROPERTIES_VIEW)
        self.properties_editor_widget.setWidget(NoSelectionWidget(parent=self))
        self.properties_editor_widget.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.properties_editor_widget.setAllowedAreas(Qt.RightDockWidgetArea)
        self.properties_editor_widget.closeEvent = self.on_properties_dock_widget_closed
        self.properties_editor_widget.showEvent = self.on_properties_dock_widget_showed
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_editor_widget)

        self.checklist_widget = QDockWidget()
        self.checklist_widget.setWindowTitle(self.constants.CHECK_LIST)
        self.checklist_widget.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.checklist_widget.setAllowedAreas(Qt.RightDockWidgetArea)
        self.checklist_widget.closeEvent = self.on_check_list_dock_widget_closed

        dock_layout = QHBoxLayout()
        dock_layout.setContentsMargins(0, 0, 0, 0)
        self.pending_list_widget = QListWidget()
        dock_layout.addWidget(self.pending_list_widget)
        self.checklist_widget.setLayout(dock_layout)

        self.checklist_widget.setWidget(self.pending_list_widget)

        self.pending_list_widget.itemClicked.connect(self.on_check_list_item_clicked)

        self.addDockWidget(Qt.RightDockWidgetArea, self.checklist_widget)

        self.resizeDocks([self.properties_editor_widget, self.checklist_widget],
                         [350, 350], Qt.Horizontal)
        self.resizeDocks([self.properties_editor_widget, self.checklist_widget],
                         [self.size().height()/2, self.size().height()/2], Qt.Vertical)

    def on_tab_changed(self):
        current_widget = self.tab_container.currentWidget()
        case_view = None
        if current_widget is not None:
            if type(current_widget) is CaseView:
                case_view = current_widget
            else:
                case_view = current_widget.case_view

        if case_view is not None:
            case_view.case.pretense.notify()

            if len(case_view.scene().selectedItems()) > 0:
                selected_item = case_view.scene().selectedItems()[0]
                self.select_node(selected_item)
            else:
                self.select_node()
        else:
            self.select_node()
            # pending_list = self.checklist_widget.findChild(QListWidget, "pending_list_widget")
            self.pending_list_widget.clear()
            self.checklist_widget.setWindowTitle(self.constants.CHECK_LIST)
    
    def close_active_case(self, index=None):
        case_view_wrapper = self.tab_container.currentWidget()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.constants.CLOSE_CASE)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText(self.constants.WANT_TO_SAVE_CASE)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        resp = msg_box.exec()
        if resp == QMessageBox.Yes:
            self.data_access_manager.save_case(case_view_wrapper.case_view.case)

        self.cases_views.pop(case_view_wrapper.case_view.case.id)
        if index is not None:
            self.tab_container.removeTab(index)
        else:
            idx = self.tab_container.currentIndex()
            self.tab_container.removeTab(idx)

    def on_tab_closed(self, index):
        self.close_active_case(index)

    def on_check_list_item_clicked(self, item):
        node_name = item.data(Qt.UserRole)
        view = self.get_active_case_view()
        if view is not None:
            node = view.scene().nodes[node_name]
            view.scene().clearSelection()
            node.setSelected(True)
            view.centerOn(node)

    def on_properties_dock_widget_showed(self, event):
        action = self.findChild(QAction, "properties_view_action")
        action.setChecked(True)
        event.accept()

    def on_properties_dock_widget_closed(self, event):
        action = self.findChild(QAction, "properties_view_action")
        action.setChecked(False)
        event.accept()

    def on_check_list_dock_widget_closed(self, event):
        action = self.findChild(QAction, "check_list_action")
        action.setChecked(False)
        event.accept()

    def update_observer(self, obj):
        """
        This methods is called by the observable object (some class of the model). It updates the check list view
        with the pending items of the model

        :param obj:
        """
        checker_visitor = ModelChecker()
        view = self.get_active_case_view()
        if view is None:
            return
        case = view.case
        case.pretense.accept(checker_visitor)
        self.pending_list_widget.clear()
        for item in checker_visitor.pending_items:
            list_item = QListWidgetItem(QIcon(":/images/img/warning.png"), item[0])
            list_item.setData(Qt.UserRole, item[1])
            self.pending_list_widget.addItem(list_item)

        total = len(checker_visitor.pending_items)
        extra_title = self.constants.MISSING_ITEMS
        if total == 1:
            extra_title = self.constants.MISSING_ITEM

        self.checklist_widget.setWindowTitle(f"{self.constants.CHECK_LIST} ({total} {extra_title})")

    def load_case(self, case):
        tab_container = self.findChild(QTabWidget, "tab_container")
        case_view = CaseView(parent=None, window=self, case=case)
        case.pretense.register_observer(self)

        # Create the hypothesis node
        node = case_view.create_node(model=case.pretense, node_type=HypothesisNode)

        # Create favorable facts
        for fact in case.pretense.fav_facts:
            self._load_fact(fact, case_view, node, True)

        for fact in case.pretense.unfav_facts:
            self._load_fact(fact, case_view, node, False)

        case_view.auto_layout()

        case_view_wrapper = CaseViewWindowWrapper(case_view=case_view)
        index = tab_container.addTab(case_view_wrapper, case.name)
        self.cases_views[case.id] = case_view
        tab_container.setCurrentIndex(index)

    def is_case_open(self, case):
        return case.id in self.cases_views.keys()

    def _load_fact(self, fact, case_view, parent_node, favorable):
        node = case_view.create_node(model=fact, node_type=FactNode, parent_node=parent_node, favorable=favorable)
        fact.register_observer(self)
        
        for sub_fact in fact.fav_facts:
            self._load_fact(sub_fact, case_view, node, True)

        for sub_fact in fact.unfav_facts:
            self._load_fact(sub_fact, case_view, node, False)

        for evidence in fact.fav_evidence:
            evidence.register_observer(self)
            case_view.create_node(model=evidence, node_type=EvidenceNode, parent_node=node, favorable=True)

        for evidence in fact.unfav_evidence:
            evidence.register_observer(self)
            case_view.create_node(model=evidence, node_type=EvidenceNode, parent_node=node, favorable=False)

    def create_case_tab(self, case_data: dict, pretense_label: str, pretense_desc: str = ""):
        pretense = Hypothesis(name="P", label=pretense_label, desc=pretense_desc)
        pretense.register_observer(self)
        case: Case = Case(name=case_data['case_name'], claimant=case_data['claimant'],
                          defendant=case_data['defendant'], radicado=case_data['radicado'],
                          subsidiary_pretensions=case_data['subsidiary_pretensions'], pretense=pretense)
        tab_container = self.findChild(QTabWidget, "tab_container")
        case_view = CaseView(parent=None, window=self, case=case)
        case_view.create_node(model=case.pretense, node_type=HypothesisNode)
        case_view_wrapper = CaseViewWindowWrapper(case_view=case_view)
        index = tab_container.addTab(case_view_wrapper, case.name)
        self.data_access_manager.save_case(case)
        self.cases_views[case.id] = case_view
        tab_container.setCurrentIndex(index)

    def add_fact_node(self, parent_node, fact_label, favorability, fact_desc=""):
        tab_container = self.findChild(QTabWidget, "tab_container")
        case_view = tab_container.currentWidget().case_view
        fav = favorability == 'Favorable'
        fact = case_view.case.pretense.add_fact(fact_label, fact_desc, fav)
        fact.register_observer(self)
        fact.notify()
        case_view.create_node(model=fact, node_type=FactNode, parent_node=parent_node, favorable=fav)
        case_view.auto_layout()

    def add_sub_fact_node(self, parent_node, fact_label, favorability, fact_desc=""):
        tab_container = self.findChild(QTabWidget, "tab_container")
        case_view = tab_container.currentWidget().case_view
        fav = favorability == 'Favorable'
        fact = parent_node.model.add_sub_fact(fact_label, fact_desc, fav)
        fact.register_observer(self)
        fact.notify()
        case_view.create_node(model=fact, node_type=FactNode, parent_node=parent_node, favorable=fav)
        case_view.auto_layout()

    def add_evidence_node(self, parent_node, evidence_label, favorability, evidence_type, evidence_desc=""):
        tab_container = self.findChild(QTabWidget, "tab_container")
        case_view = tab_container.currentWidget().case_view
        case_view.case.evidence_counter += 1
        fav = favorability == 'Favorable'
        evidence = parent_node.model.add_evidence(case_view.case.evidence_counter, evidence_label, evidence_desc,
                                                  fav, evidence_type)
        evidence.register_observer(self)
        evidence.notify()
        case_view.create_node(model=evidence, node_type=EvidenceNode, parent_node=parent_node, favorable=fav)
        case_view.auto_layout()

    def config_window(self):
        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle(self.constants.SMART_JUDGE)
        self.setWindowIcon(QIcon(":/images/img/judge.png"))
        self.statusBar()
        # noinspection PyTypeChecker
        self.setCentralWidget(self.findChild(QTabWidget, "tab_container"))

        # Menus
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(self.constants.FILE_MENU)
        view_menu = menu_bar.addMenu(self.constants.VIEW_MENU)

        # Add actions
        new_case_action = QAction(QIcon(":/images/img/new.png"), self.constants.NEW_PROCESS_ACTION, self)
        new_case_action.setStatusTip(self.constants.NEW_PROCESS_ACTION_STATUS)
        new_case_action.triggered.connect(self.new_case_dialog)
        file_menu.addAction(new_case_action)
        
        new_case_pdf_action = QAction(QIcon(":/images/img/new.png"), self.tr("New process from PDF..."), self)
        new_case_pdf_action.setStatusTip(self.tr("Create a new process from a PDF lawsuit using Gemini AI"))
        new_case_pdf_action.triggered.connect(self.new_case_from_pdf_dialog)
        file_menu.addAction(new_case_pdf_action)
        open_action = QAction(QIcon(":/images/img/open.png"), self.constants.OPEN_PROCESS_ACTION, self)
        open_action.setStatusTip(self.constants.OPEN_PROCESS_ACTION_STATUS)
        open_action.triggered.connect(self.open_case_dialog)
        file_menu.addAction(open_action)
        self.save_action = QAction(QIcon(":/images/img/save.png"), self.constants.SAVE_ACTION, self)
        self.save_action.setStatusTip(self.constants.SAVE_ACTION_STATUS)
        self.save_action.triggered.connect(self.save_active_case)
        file_menu.addAction(self.save_action)
        self.save_as_action = QAction(QIcon(":images/img/save-as.png"), self.constants.SAVE_AS_ACTION, self)
        self.save_as_action.setStatusTip(self.constants.SAVE_AS_ACTION_STATUS)
        self.save_as_action.triggered.connect(self.save_copy_of_active_case)
        file_menu.addAction(self.save_as_action)
        self.close_case_action = QAction(QIcon(":images/img/close-case.png"), self.constants.CLOSE_ACTION, self)
        self.close_case_action.setStatusTip(self.constants.CLOSE_ACTION_STATUS)
        self.close_case_action.triggered.connect(self.close_active_case)
        file_menu.addAction(self.close_case_action)

        file_menu.addSeparator()

        manage_cases_action = QAction(QIcon(":images/img/manage-list.png"), self.constants.MANAGE_PROCESSES, self)
        manage_cases_action.setStatusTip(self.constants.MANAGE_PROCESSES_ACTION_STATUS)
        manage_cases_action.triggered.connect(self.open_manage_cases_dialog)
        file_menu.addAction(manage_cases_action)

        file_menu.addSeparator()
        exit_app_action = QAction(QIcon(":images/img/exit.png"), self.constants.EXIT_ACTION, self)
        exit_app_action.setStatusTip(self.constants.EXIT_ACTION_STATUS)
        exit_app_action.triggered.connect(lambda: QCoreApplication.exit(0))
        file_menu.addAction(exit_app_action)

        file_menu.aboutToShow.connect(self.on_show_menu_file)

        properties_view_action = QAction(QIcon(":images/img/properties.png"), self.constants.PROPERTIES_VIEW_ACTION, self)
        properties_view_action.setObjectName("properties_view_action")
        properties_view_action.setCheckable(True)
        properties_view_action.setChecked(True)
        properties_view_action.triggered.connect(self.on_properties_view_action_triggered)
        check_list_action = QAction(QIcon(":images/img/checklist.png"), self.constants.CHECK_LIST_ACTION, self)
        check_list_action.setObjectName("check_list_action")
        check_list_action.setCheckable(True)
        check_list_action.setChecked(True)
        check_list_action.triggered.connect(self.on_check_list_action_triggered)
        auto_layout_action = QAction(self.constants.AUTO_LAYOUT_ACTION, self)
        auto_layout_action.setObjectName("auto_layout_action")
        auto_layout_action.setStatusTip(self.constants.AUTO_LAYOUT_ACTION_STATUS)
        auto_layout_action.triggered.connect(self.on_auto_layout_action_triggered)

        view_menu.addAction(properties_view_action)
        view_menu.addAction(check_list_action)
        view_menu.addSeparator()
        view_menu.addAction(auto_layout_action)

    def on_show_menu_file(self):
        tab_container = self.findChild(QTabWidget, "tab_container")
        if tab_container.currentIndex() == -1:
            self.save_action.setEnabled(False)
            self.save_as_action.setEnabled(False)
            self.close_case_action.setEnabled(False)
        else:
            self.save_action.setEnabled(True)
            self.save_as_action.setEnabled(True)
            self.close_case_action.setEnabled(True)

    def on_properties_view_action_triggered(self, checked):
        if checked:
            self.properties_editor_widget.show()
        else:
            self.properties_editor_widget.close()

    def on_check_list_action_triggered(self, checked):
        if checked:
            self.checklist_widget.show()
        else:
            self.checklist_widget.close()

    def on_auto_layout_action_triggered(self):
        case_view = self.get_active_case_view()
        if case_view:
            case_view.auto_layout()

    def get_active_case_view(self):
        tab_container = self.findChild(QTabWidget, "tab_container")
        current_widget = tab_container.currentWidget()
        if current_widget is not None and hasattr(current_widget, "case_view"):
            return current_widget.case_view
        return None

    def select_node(self, selected_node=None):
        if selected_node is None:
            widget = NoSelectionWidget(parent=self)
            self.properties_editor_widget.setWindowTitle(widget.window_title)
            self.properties_editor_widget.setWidget(widget)
        elif type(selected_node) is HypothesisNode:
            widget = HypothesisEditorWidget(node=selected_node, parent=self)
            self.properties_editor_widget.setWindowTitle(widget.window_title)
            self.properties_editor_widget.setWidget(widget)
            self.properties_editor_widget.show()
            self.properties_editor_widget.raise_()
        elif type(selected_node) is FactNode:
            widget = FactEditorWidget(node=selected_node, parent=self)
            self.properties_editor_widget.setWindowTitle(widget.window_title)
            self.properties_editor_widget.setWidget(widget)
            self.properties_editor_widget.show()
            self.properties_editor_widget.raise_()
        elif type(selected_node) is EvidenceNode:
            widget = EvidenceEditorWidget(node=selected_node, parent=self)
            self.properties_editor_widget.setWindowTitle(widget.window_title)
            self.properties_editor_widget.setWidget(widget)
            self.properties_editor_widget.show()
            self.properties_editor_widget.raise_()

    def new_case_dialog(self):
        dialog = NewCaseDialog(parent=self)
        resp = dialog.exec_()
        if resp == QDialog.Accepted:
            case_name = dialog.findChild(QLineEdit, "case_name_line_edit").text()
            claimant = dialog.findChild(QLineEdit, "claimant_line_edit").text()
            defendant = dialog.findChild(QLineEdit, "defendant_line_edit").text()
            radicado = dialog.findChild(QLineEdit, "radicado_line_edit").text()
            subsidiary_pretensions = dialog.findChild(QPlainTextEdit, "subsidiary_hypothesis_text_edit").toPlainText()
            pretension_desc = dialog.findChild(QPlainTextEdit, "pretension_text_edit").toPlainText()
            pretension_label = dialog.findChild(QLineEdit, "label_line_edit").text()
            case_data = {
                "case_name": case_name,
                "claimant": claimant,
                "defendant": defendant,
                "radicado": radicado,
                "subsidiary_pretensions": subsidiary_pretensions
            }
            self.create_case_tab(case_data, pretension_label, pretension_desc)

    def new_case_from_pdf_dialog(self):
        allowed_probs = [
            self.constants.UNSUPPORTED,
            self.constants.UNLIKELY,
            self.constants.LIKELY,
            self.constants.MOST_LIKELY,
            self.constants.VERY_LIKELY,
            self.constants.ALMOST_TRUE,
            self.constants.TRUE
        ]
        allowed_ev_types = list(self.evidence_type_repr.list_values())
        
        dialog = ImportPdfDialog(allowed_probs, allowed_ev_types, parent=self)
        resp = dialog.exec_()
        if resp == QDialog.Accepted and dialog.case_result is not None:
            case = dialog.case_result
            self.data_access_manager.save_case(case)
            self.load_case(case)
            self.statusBar().showMessage(f"Caso '{case.name}' importado con éxito desde PDF.")

    def get_active_case(self):
        tab_container = self.findChild(QTabWidget, "tab_container")
        case_view = tab_container.currentWidget().case_view
        if case_view is not None:
            return case_view.case
        else:
            return None

    def save_active_case(self):
        case: Case = self.get_active_case()
        if case is not None:
            self.data_access_manager.save_case(case)
            self.statusBar().showMessage(f"{self.constants.CASE} {case.name} {self.constants.SUCCESSFULLY_SAVED}")
        else:
            self.statusBar().showMessage(f"{self.constants.NO_CASE_TO_SAVE}")

    def save_copy_of_active_case(self):
        case: Case = self.get_active_case()
        if case is not None:
            q_dialog = QInputDialog(self)
            q_dialog.setInputMode(QInputDialog.TextInput)
            q_dialog.setWindowTitle(self.constants.SAVE_AS)
            q_dialog.setLabelText(self.constants.NAME_FOR_NEW_CASE)
            q_dialog.resize(300, 100)
            q_dialog.setTextValue(case.name)
            ok = q_dialog.exec_()

            if ok and q_dialog.textValue() is not None:
                cloned_case = case.clone()
                cloned_case.name = q_dialog.textValue()
                self.data_access_manager.save_case(cloned_case, force_insert=True)
                self.statusBar().showMessage(f"{self.constants.CASE} {cloned_case.name} {self.constants.SUCCESSFULLY_SAVED}")
        else:
            self.statusBar().showMessage(f"{self.constants.NO_CASE_TO_SAVE}")

    def open_manage_cases_dialog(self):
        dialog = ManageCasesDialog(parent=self)
        dialog.exec_()

    def open_case_dialog(self):
        dialog = OpenCaseDialog(parent=self)
        resp = dialog.exec_()
        if resp == QDialog.Accepted:
            list_view = dialog.findChild(QListView, "list_view_cases")
            model = list_view.model()
            item = model.itemFromIndex(list_view.selectedIndexes()[0])
            if not self.is_case_open(item.case):
                self.load_case(item.case)

    def on_new_fact_action_selected(self, parent_node):
        dialog = AddFactDialog(parent=self, parent_label=parent_node.model.label)
        resp = dialog.exec_()
        if resp == QDialog.Accepted:
            fact_label = dialog.findChild(QLineEdit, "fact_label_line_edit").text()
            favorability = dialog.findChild(QButtonGroup, "favorability_button_group").checkedButton().text()
            fact_desc = dialog.findChild(QPlainTextEdit, "fact_desc_text_edit").toPlainText()
            if type(parent_node.model) is Hypothesis:
                self.add_fact_node(parent_node, fact_label, favorability, fact_desc)
            else:
                self.add_sub_fact_node(parent_node, fact_label, favorability, fact_desc)

    def on_new_evidence_action_selected(self, parent_node):
        dialog = AddEvidenceDialog(parent=self, parent_label=parent_node.model.label)
        resp = dialog.exec_()
        if resp == QDialog.Accepted:
            evidence_label = dialog.findChild(QLineEdit, "evidence_label_line_edit").text()
            favorability = dialog.findChild(QButtonGroup, "favorability_button_group").checkedButton().text()
            evidence_type = dialog.findChild(QComboBox, "evidence_type_combo_box").currentText()
            evidence_desc = dialog.findChild(QPlainTextEdit, "evidence_desc_text_edit").toPlainText()
            self.add_evidence_node(parent_node, evidence_label, favorability, evidence_type, evidence_desc)

    def on_ignore_node_selected(self, node):
        model = node.model
        model.ignored = not model.ignored

    def on_delete_action_selected(self, node):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.constants.CONFIRMATION)
        msg_box.setText(self.constants.SURE_TO_DELETE_NODE)
        msg_box.setInformativeText(self.constants.ALL_NODE_BE_DELETED)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg_box.exec_() == QMessageBox.Yes:
            case_view = self.cases_views[self.get_active_case().id]
            case_view.delete_node(node)
            case_view.auto_layout()

    def on_calculate_evidential_weight(self, node):
        model = node.model
        try:
            model.calculate_evidential_weight()
        except ProbatoryWeightException as ex:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.constants.ERROR)
            msg_box.setText(self.constants.PROBATORY_WEIGHT_ERROR)
            msg_box.setInformativeText(str(ex))
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.exec_()

        node.update()


class CaseViewWindowWrapper(QMainWindow):
    def __init__(self, case_view, constants: Constants = Provide[Container.constants], parent=None):
        super(CaseViewWindowWrapper, self).__init__(parent)
        self.case_view = case_view
        self.constants = constants
        self.setCentralWidget(self.case_view)

        # Add toolbar
        report_toolbar = QToolBar()
        report_toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, report_toolbar)
        report_action = QAction(QIcon(":images/img/report.png"), self.constants.GENERATE_REPORT, self)
        report_action.triggered.connect(self.generate_report)
        report_toolbar.addAction(report_action)

    def generate_report(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, self.constants.GENERATE_REPORT,
                                                   f"reporte_caso_{self.case_view.case.name}.docx",
                                                   "*.docx",
                                                   "*.docx", options)

        if file_name:
            report_generator = DocxReportGenerator(self.case_view.case)
            report_generator.generate_report(file_name)
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.constants.GENERATE_REPORT)
            msg_box.setText(self.constants.REPORT_SUCCESS)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.exec_()


class OpenCaseDialog(QDialog):

    def __init__(self, data_access_manager: DataAccessManager = Provide[Container.data_access_manager],
                 constants: Constants = Provide[Container.constants], parent=None):
        super(OpenCaseDialog, self).__init__(parent)

        self.constants = constants

        self.ui = Ui_OpenCaseForm()
        self.ui.setupUi(self)

        self.ui.open_case_dialog_button_box.accepted.connect(self.accept)
        self.ui.open_case_dialog_button_box.rejected.connect(self.reject)

        self._init_dialog(data_access_manager)

        self.setFixedSize(QSize(600, 350))
        self.setWindowTitle(self.constants.OPEN_PROCESS)

    def _init_dialog(self, data_access_manager: DataAccessManager):
        self.ui.list_view_cases.setModel(QStandardItemModel())
        for case in data_access_manager.list_cases():
            item = QStandardItem(f"{case.name} ({self.constants.CREATED_ON}: {case.id.generation_time})")
            item.case = case
            item.setEditable(False)
            self.ui.list_view_cases.model().appendRow(item)

    def accept(self):
        indexes = self.ui.list_view_cases.selectedIndexes()
        if len(indexes) > 0:
            super(OpenCaseDialog, self).accept()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.constants.ERROR)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("%s" % self.constants.OPEN_CASE_TEXT_MSG)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()


class NewCaseDialog(QDialog):

    def __init__(self, constants: Constants = Provide[Container.constants], parent=None):
        super(NewCaseDialog, self).__init__(parent)

        self.constants = constants

        self.ui = Ui_NewCaseForm()
        self.ui.setupUi(self)

        self.ui.subsidiary_hypothesis_text_edit.setPlaceholderText(self.constants.SUBSIDIARY_HYPO_PLACEHOLDER)
        self.ui.radicado_line_edit.setValidator(QRegExpValidator(QRegExp('\\d{25}'), self.ui.radicado_line_edit))

        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)
        self.setFixedSize(QSize(470, 445))
        self.setWindowTitle(self.constants.NEW_PROCESS_ACTION_STATUS)

    def accept(self) -> None:
        if self.ui.label_line_edit.text() != "" and self.ui.case_name_line_edit.text() != "" and \
           self.ui.claimant_line_edit.text() != "" and self.ui.defendant_line_edit.text() != "" and \
           self.ui.radicado_line_edit.text() != "":
            super(NewCaseDialog, self).accept()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.constants.ERROR)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("%s" % self.constants.FORM_TEXT_MSG)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()


class AddFactDialog(QDialog):

    def __init__(self, constants: Constants = Provide[Container.constants], parent=None, parent_label: str = ""):
        super(AddFactDialog, self).__init__(parent)

        self.constants = constants

        self.ui = Ui_AddFactForm()
        self.ui.setupUi(self)

        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)

        self.ui.selected_line_edit.setText(parent_label)

        self.setFixedSize(QSize(472, 350))
        self.setWindowTitle(self.constants.ADD_NEW_FACT)

    def accept(self) -> None:
        if self.ui.fact_label_line_edit.text() != "":
            super(AddFactDialog, self).accept()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.constants.ERROR)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("%s" % self.constants.FORM_TEXT_MSG)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()


class AddEvidenceDialog(QDialog):

    def __init__(self,
                 constants: Constants = Provide[Container.constants],
                 evidence_type_repr=Provide[Container.evidence_type_repr],
                 parent=None, parent_label: str = ""):
        super(AddEvidenceDialog, self).__init__(parent)

        self.constants = constants

        self.ui = Ui_AddEvidenceForm()
        self.ui.setupUi(self)

        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)

        self.ui.selected_fact_line_edit.setText(parent_label)

        self._setup_evidence_type_combo(evidence_type_repr)

        self.setFixedSize(QSize(472, 375))
        self.setWindowTitle(self.constants.ADD_NEW_EVIDENCE)

    def _setup_evidence_type_combo(self, evidence_type_repr):
        self.ui.evidence_type_combo_box.addItems(evidence_type_repr.list_values())
        self.ui.evidence_type_combo_box.setCurrentIndex(0)

    def accept(self) -> None:
        if self.ui.evidence_label_line_edit.text() != "":
            super(AddEvidenceDialog, self).accept()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.constants.ERROR)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("%s" % self.constants.FORM_TEXT_MSG)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()


class ManageCasesDialog(QDialog):

    EXTENSION = "*.zip"

    def __init__(self, data_access_manager: DataAccessManager = Provide[Container.data_access_manager],
                 constants: Constants = Provide[Container.constants], parent=None):
        super(ManageCasesDialog, self).__init__(parent)

        self.constants = constants

        self.ui = Ui_ManageCasesForm()
        self.ui.setupUi(self)

        self.data_access_manager = data_access_manager

        self._init_dialog(data_access_manager)

        self.setMinimumSize(QSize(600, 350))
        self.setWindowTitle(self.constants.MANAGE_PROCESSES)

    def _init_dialog(self, data_access_manager: DataAccessManager):
        table_model = QStandardItemModel()
        table_model.setHorizontalHeaderLabels([self.constants.ID, self.constants.NAME, self.constants.CREATION_DATE])
        self.ui.table_view_cases.setModel(table_model)
        header = self.ui.table_view_cases.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_style = "::section{font-weight: bold;}"
        header.setStyleSheet(header_style)
        self.ui.table_view_cases.setSelectionBehavior(QTableView.SelectRows)
        table_model.dataChanged.connect(self.on_item_changed)

        for case in data_access_manager.list_cases():
            col_1 = QStandardItem(str(case.id))
            col_1.setEditable(False)
            col_2 = QStandardItem(case.name)
            col_3 = QStandardItem(str(case.id.generation_time))
            col_3.setEditable(False)
            col_1.case = case

            table_model.appendRow([col_1, col_2, col_3])

        self.ui.pbutton_delete.clicked.connect(self.delete_cases)
        self.ui.pbutton_export.clicked.connect(self.export_cases)
        self.ui.pbutton_import.clicked.connect(self.import_cases)

    def reload_cases_table(self):
        table_model = QStandardItemModel()
        table_model.setHorizontalHeaderLabels([self.constants.ID, self.constants.NAME, self.constants.CREATION_DATE])
        self.ui.table_view_cases.setModel(table_model)
        header = self.ui.table_view_cases.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_style = "::section{font-weight: bold;}"
        header.setStyleSheet(header_style)
        self.ui.table_view_cases.setSelectionBehavior(QTableView.SelectRows)
        table_model.dataChanged.connect(self.on_item_changed)

        for case in self.data_access_manager.list_cases():
            col_1 = QStandardItem(str(case.id))
            col_1.setEditable(False)
            col_2 = QStandardItem(case.name)
            col_3 = QStandardItem(str(case.id.generation_time))
            col_3.setEditable(False)
            col_1.case = case
            table_model.appendRow([col_1, col_2, col_3])

    def import_cases(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, self.constants.IMPORT_CASES, "",
                                                   self.EXTENSION, self.EXTENSION, options)

        if file_name:
            try:
                self.data_access_manager.import_cases(file_name)
            except ImportCasesError as err:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(self.constants.WARNING)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setText(f"{self.constants.ERRORS_IMPORTING}\n\n{err.msj}")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec()
            except NotValidFile as err:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(self.constants.ERROR)
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setText(f"{err.msj}")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec()
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(self.constants.INFORMATION)
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setText(self.constants.CASES_IMPORTED_SUCCESS)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec()
            finally:
                self.reload_cases_table()

    def export_cases(self):
        selection_model = self.ui.table_view_cases.selectionModel()

        if len(selection_model.selectedRows()) > 0:

            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, self.constants.EXPORT_CASES, "",
                                                       self.EXTENSION, self.EXTENSION, options)

            if file_name:
                cases = list()
                model = self.ui.table_view_cases.model()
                for sel_index in selection_model.selectedRows():
                    row_index = sel_index.row()
                    table_item = model.item(row_index)
                    cases.append(table_item.case)

                try:
                    self.data_access_manager.export_cases(cases, file_name)
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle(self.constants.INFORMATION)
                    msg_box.setIcon(QMessageBox.Information)
                    msg_box.setText(self.constants.CASES_EXPORTED_SUCCESS)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    msg_box.exec()
                except NotImplementedError:
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle(self.constants.WARNING)
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setText(self.constants.OPERATION_UNSUPPORTED)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    msg_box.exec()

        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.constants.WARNING)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText(self.constants.AT_LEAST_ONE_CASE)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

    def delete_cases(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.constants.CONFIRMATION)
        msg_box.setText(self.constants.SURE_TO_DELETE_CASES)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg_box.exec_() == QMessageBox.Yes:
            selection_model = self.ui.table_view_cases.selectionModel()
            model = self.ui.table_view_cases.model()
            while len(selection_model.selectedRows()) > 0:
                row_index = selection_model.selectedRows()[0].row()
                table_item = model.item(row_index)
                self.data_access_manager.delete_case(table_item.case)
                model.removeRow(row_index)

    def on_item_changed(self, item):
        model = self.ui.table_view_cases.model()
        case = model.item(item.row()).case
        case.name = item.data()
        case.save()
