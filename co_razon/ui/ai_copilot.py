import json
from PySide2.QtCore import QObject, Qt, QThread, Signal, QSettings
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton,
    QLineEdit, QPlainTextEdit, QComboBox, QScrollArea, QGroupBox, QFormLayout,
    QMessageBox
)
from co_razon.model.judge import Hypothesis, Fact, Evidence
from co_razon.ui.constants import Constants
from co_razon.util.containers import Container
from dependency_injector.wiring import Provide, inject

class GeminiWorker(QThread):
    finished_signal = Signal(str, str)  # Emits (result_json, error_message)

    def __init__(self, api_key, prompt):
        super().__init__()
        self.api_key = api_key
        self.prompt = prompt

    def run(self):
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=self.prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            self.finished_signal.emit(response.text.strip(), "")
        except Exception as e:
            self.finished_signal.emit("", str(e))


class AICopilotWidget(QWidget):
    @inject
    def __init__(self, window, constants: Constants = Provide[Container.constants],
                 evidence_type_repr = Provide[Container.evidence_type_repr], parent=None):
        super(AICopilotWidget, self).__init__(parent)
        self.window = window
        self.constants = constants
        self.evidence_type_repr = evidence_type_repr
        self.settings = QSettings("Orion", "CoRazon")
        self.active_worker = None

        self.setup_ui()
        self.refresh_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(6, 6, 6, 6)

        # Style sheet
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: #f8fafc;
                font-family: 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #334155;
                background-color: #0f172a;
            }
            QTabBar::tab {
                background-color: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                padding: 6px 10px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0f172a;
                color: #f8fafc;
                border-bottom-color: #0f172a;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4f46e5;
                border: none;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6366f1;
            }
            QPushButton:disabled {
                background-color: #334155;
                color: #64748b;
            }
            QLineEdit, QPlainTextEdit, QComboBox {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px;
                color: #f8fafc;
            }
            QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
                border: 1px solid #6366f1;
            }
            QLabel {
                color: #cbd5e1;
                font-weight: bold;
            }
        """)

        # API Key configuration area (shows only if missing)
        self.api_key_group = QGroupBox("Configuración de API Key de Gemini")
        api_layout = QHBoxLayout(self.api_key_group)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Ingresa tu Gemini API Key...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.settings.value("gemini_api_key", ""))
        self.save_api_key_btn = QPushButton("Guardar")
        self.save_api_key_btn.clicked.connect(self.save_api_key)
        api_layout.addWidget(self.api_key_input)
        api_layout.addWidget(self.save_api_key_btn)
        self.main_layout.addWidget(self.api_key_group)

        # Status label
        self.status_lbl = QLabel("Selecciona un caso para comenzar")
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setStyleSheet("color: #6366f1; font-size: 12px;")
        self.main_layout.addWidget(self.status_lbl)

        # Main tabs (Claimant / Defendant)
        self.main_tabs = QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        # ---------------- CLAIMANT TAB ----------------
        self.claimant_widget = QWidget()
        self.claimant_layout = QVBoxLayout(self.claimant_widget)
        self.claimant_tabs = QTabWidget()
        self.claimant_layout.addWidget(self.claimant_tabs)
        self.main_tabs.addTab(self.claimant_widget, "Demandante (Favorable)")

        # Claimant Facts subtab
        self.fav_fact_widget = QWidget()
        self.fav_fact_layout = QVBoxLayout(self.fav_fact_widget)
        self.setup_fact_panel(self.fav_fact_layout, is_favorable=True)
        self.claimant_tabs.addTab(self.fav_fact_widget, "Sugerir Hecho")

        # Claimant Evidence subtab
        self.fav_ev_widget = QWidget()
        self.fav_ev_layout = QVBoxLayout(self.fav_ev_widget)
        self.setup_evidence_panel(self.fav_ev_layout, is_favorable=True)
        self.claimant_tabs.addTab(self.fav_ev_widget, "Sugerir Prueba")

        # ---------------- DEFENDANT TAB ----------------
        self.defendant_widget = QWidget()
        self.defendant_layout = QVBoxLayout(self.defendant_widget)
        self.defendant_tabs = QTabWidget()
        self.defendant_layout.addWidget(self.defendant_tabs)
        self.main_tabs.addTab(self.defendant_widget, "Demandado (Desfavorable)")

        # Defendant Facts subtab
        self.unfav_fact_widget = QWidget()
        self.unfav_fact_layout = QVBoxLayout(self.unfav_fact_widget)
        self.setup_fact_panel(self.unfav_fact_layout, is_favorable=False)
        self.defendant_tabs.addTab(self.unfav_fact_widget, "Sugerir Hecho")

        # Defendant Evidence subtab
        self.unfav_ev_widget = QWidget()
        self.unfav_ev_layout = QVBoxLayout(self.unfav_ev_widget)
        self.setup_evidence_panel(self.unfav_ev_layout, is_favorable=False)
        self.defendant_tabs.addTab(self.unfav_ev_widget, "Sugerir Prueba")

    def save_api_key(self):
        key = self.api_key_input.text().strip()
        self.settings.setValue("gemini_api_key", key)
        QMessageBox.information(self, "API Key Guardada", "La API Key de Gemini ha sido guardada.")
        self.refresh_ui()

    def setup_fact_panel(self, layout, is_favorable):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form = QFormLayout(content)

        header = QLabel("Pretensión actual:")
        pretension_lbl = QLabel("Sin pretensión seleccionada")
        pretension_lbl.setStyleSheet("color: #94a3b8;")
        pretension_lbl.setWordWrap(True)
        if is_favorable:
            self.fav_pretension_lbl = pretension_lbl
        else:
            self.unfav_pretension_lbl = pretension_lbl
        form.addRow(header, pretension_lbl)

        btn_suggest = QPushButton("Sugerir hecho con IA")
        btn_suggest.clicked.connect(lambda: self.generate_fact_suggestion(is_favorable))
        form.addRow(btn_suggest)

        title_input = QLineEdit()
        desc_input = QPlainTextEdit()
        desc_input.setMaximumHeight(100)
        relevance_combo = QComboBox()
        relevance_combo.addItems([self.constants.RELEVANT, self.constants.IRRELEVANT])

        if is_favorable:
            self.fav_fact_btn = btn_suggest
            self.fav_fact_title = title_input
            self.fav_fact_desc = desc_input
            self.fav_fact_relevance = relevance_combo
        else:
            self.unfav_fact_btn = btn_suggest
            self.unfav_fact_title = title_input
            self.unfav_fact_desc = desc_input
            self.unfav_fact_relevance = relevance_combo

        form.addRow("Hecho sugerido:", title_input)
        form.addRow("Descripción:", desc_input)
        form.addRow("Relevancia:", relevance_combo)

        btn_add = QPushButton("Agregar al caso")
        btn_add.clicked.connect(lambda: self.add_suggested_fact(is_favorable))
        form.addRow(btn_add)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def setup_evidence_panel(self, layout, is_favorable):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form = QFormLayout(content)

        header = QLabel("Seleccionar Hecho:")
        fact_combo = QComboBox()
        if is_favorable:
            self.fav_fact_combo = fact_combo
        else:
            self.unfav_fact_combo = fact_combo
        form.addRow(header, fact_combo)

        btn_suggest = QPushButton("Sugerir prueba con IA")
        btn_suggest.clicked.connect(lambda: self.generate_evidence_suggestion(is_favorable))
        form.addRow(btn_suggest)

        title_input = QLineEdit()
        type_combo = QComboBox()
        type_combo.addItems(list(self.evidence_type_repr.list_values()))
        desc_input = QPlainTextEdit()
        desc_input.setMaximumHeight(100)
        pert_combo = QComboBox()
        pert_combo.addItems([self.constants.PERTINENT, self.constants.IMPERTINENT])
        cred_combo = QComboBox()
        # Grab credibility list from weight definition
        cred_combo.addItems([self.constants.TRUE, self.constants.ALMOST_TRUE, self.constants.VERY_LIKELY,
                             self.constants.MOST_LIKELY, self.constants.LIKELY, self.constants.UNLIKELY,
                             self.constants.UNSUPPORTED])

        if is_favorable:
            self.fav_ev_btn = btn_suggest
            self.fav_ev_title = title_input
            self.fav_ev_type = type_combo
            self.fav_ev_desc = desc_input
            self.fav_ev_pert = pert_combo
            self.fav_ev_cred = cred_combo
        else:
            self.unfav_ev_btn = btn_suggest
            self.unfav_ev_title = title_input
            self.unfav_ev_type = type_combo
            self.unfav_ev_desc = desc_input
            self.unfav_ev_pert = pert_combo
            self.unfav_ev_cred = cred_combo

        form.addRow("Prueba sugerida:", title_input)
        form.addRow("Tipo de prueba:", type_combo)
        form.addRow("Descripción:", desc_input)
        form.addRow("Pertinencia:", pert_combo)
        form.addRow("Credibilidad:", cred_combo)

        btn_add = QPushButton("Agregar prueba al hecho")
        btn_add.clicked.connect(lambda: self.add_suggested_evidence(is_favorable))
        form.addRow(btn_add)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def refresh_ui(self):
        case = self.window.get_active_case()
        has_api_key = bool(self.settings.value("gemini_api_key", ""))

        if not has_api_key:
            self.api_key_group.setStyleSheet("QGroupBox { border: 2px solid #e11d48; }")
            self.status_lbl.setText("ADVERTENCIA: Por favor, guarda tu API Key de Gemini arriba para habilitar el asistente.")
            self.status_lbl.setStyleSheet("color: #e11d48; font-weight: bold;")
        else:
            self.api_key_group.setStyleSheet("")
            self.status_lbl.setText("Asistente listo.")
            self.status_lbl.setStyleSheet("color: #10b981;")

        if case:
            pretension_label = case.pretense.label if case.pretense else "Sin pretensión"
            self.fav_pretension_lbl.setText(pretension_label)
            self.unfav_pretension_lbl.setText(pretension_label)
            self.refresh_facts()
            self.setEnabled(True)
        else:
            self.fav_pretension_lbl.setText("Abre o crea un caso")
            self.unfav_pretension_lbl.setText("Abre o crea un caso")
            self.fav_fact_combo.clear()
            self.unfav_fact_combo.clear()
            self.setEnabled(False)

    def refresh_facts(self):
        case = self.window.get_active_case()
        if not case or not case.pretense:
            self.fav_fact_combo.clear()
            self.unfav_fact_combo.clear()
            return

        # Favorable facts list (Demandante)
        fav_list = []
        self._collect_facts(case.pretense.fav_facts or [], fav_list)
        current_fav_fact = self.fav_fact_combo.currentData()
        self.fav_fact_combo.clear()
        for fact in fav_list:
            self.fav_fact_combo.addItem(fact.label, fact)
        if current_fav_fact:
            idx = self.fav_fact_combo.findData(current_fav_fact)
            if idx != -1:
                self.fav_fact_combo.setCurrentIndex(idx)

        # Unfavorable facts list (Demandado)
        unfav_list = []
        self._collect_facts(case.pretense.unfav_facts or [], unfav_list)
        current_unfav_fact = self.unfav_fact_combo.currentData()
        self.unfav_fact_combo.clear()
        for fact in unfav_list:
            self.unfav_fact_combo.addItem(fact.label, fact)
        if current_unfav_fact:
            idx = self.unfav_fact_combo.findData(current_unfav_fact)
            if idx != -1:
                self.unfav_fact_combo.setCurrentIndex(idx)

    def _collect_facts(self, facts, result_list):
        for f in facts:
            result_list.append(f)
            if f.fav_facts:
                self._collect_facts(f.fav_facts, result_list)
            if f.unfav_facts:
                self._collect_facts(f.unfav_facts, result_list)

    def set_selected_node(self, selected_node):
        if not selected_node:
            return
        model = selected_node.model
        if isinstance(model, Fact):
            # Try to select in favorable combo
            idx = self.fav_fact_combo.findData(model)
            if idx != -1:
                self.fav_fact_combo.setCurrentIndex(idx)
                self.main_tabs.setCurrentIndex(0)  # Claimant
                self.claimant_tabs.setCurrentIndex(1)  # Evidence
            else:
                idx = self.unfav_fact_combo.findData(model)
                if idx != -1:
                    self.unfav_fact_combo.setCurrentIndex(idx)
                    self.main_tabs.setCurrentIndex(1)  # Defendant
                    self.defendant_tabs.setCurrentIndex(1)  # Evidence

    def generate_fact_suggestion(self, is_favorable):
        api_key = self.settings.value("gemini_api_key", "")
        if not api_key:
            QMessageBox.warning(self, "API Key Requerida", "Por favor ingresa tu API Key para utilizar la IA.")
            return

        case = self.window.get_active_case()
        if not case or not case.pretense:
            return

        pretension = case.pretense.label
        favorability_text = "favorable para el demandante" if is_favorable else "favorable para el demandado (desfavorable a la pretensión)"
        claimant = case.claimant
        defendant = case.defendant

        prompt = f"""
Dada la pretensión judicial principal: "{pretension}"
(Demandante: {claimant}, Demandado: {defendant})

Por favor, sugiere un hecho fáctico relevante que sea {favorability_text} en español.
El hecho debe presentarse en una sola frase breve e inequívoca de forma concreta.
Devuelve el resultado en formato JSON estructurado exactamente así:
{{
  "label": "Título corto y directo del hecho (ej: El demandado firmó la promesa de venta, máx. 50 caracteres)",
  "desc": "Descripción detallada del hecho y cómo apoya/desvirtúa la pretensión."
}}
No agregues explicaciones, markdown, ni nada fuera del objeto JSON.
"""
        self.status_lbl.setText("IA: Sugiriendo hecho...")
        self.status_lbl.setStyleSheet("color: #fb7185;")
        btn = self.fav_fact_btn if is_favorable else self.unfav_fact_btn
        btn.setEnabled(False)

        self.active_worker = GeminiWorker(api_key, prompt)
        self.active_worker.finished_signal.connect(lambda res, err: self.on_fact_suggested(res, err, is_favorable))
        self.active_worker.start()

    def on_fact_suggested(self, result_json, error_message, is_favorable):
        btn = self.fav_fact_btn if is_favorable else self.unfav_fact_btn
        btn.setEnabled(True)

        if error_message:
            self.status_lbl.setText(f"Error: {error_message}")
            self.status_lbl.setStyleSheet("color: #ef4444;")
            return

        try:
            data = json.loads(result_json)
            title = data.get("label", "")
            desc = data.get("desc", "")

            title_input = self.fav_fact_title if is_favorable else self.unfav_fact_title
            desc_input = self.fav_fact_desc if is_favorable else self.unfav_fact_desc

            title_input.setText(title)
            desc_input.setPlainText(desc)
            self.status_lbl.setText("IA: Sugerencia de hecho cargada.")
            self.status_lbl.setStyleSheet("color: #10b981;")
        except Exception as e:
            self.status_lbl.setText("Error al procesar sugerencia de la IA.")
            self.status_lbl.setStyleSheet("color: #ef4444;")

    def add_suggested_fact(self, is_favorable):
        case_view = self.window.get_active_case_view()
        if not case_view:
            return

        title_input = self.fav_fact_title if is_favorable else self.unfav_fact_title
        desc_input = self.fav_fact_desc if is_favorable else self.unfav_fact_desc
        relevance_combo = self.fav_fact_relevance if is_favorable else self.unfav_fact_relevance

        label = title_input.text().strip()
        desc = desc_input.toPlainText().strip()
        relevance = relevance_combo.currentText()

        if not label:
            QMessageBox.warning(self, "Campos Vacíos", "El título del hecho es obligatorio.")
            return

        # Find HypothesisNode in CaseView
        try:
            parent_node = next(node for node in case_view.scene().nodes.values() if isinstance(node.model, Hypothesis))
        except StopIteration:
            QMessageBox.warning(self, "Error", "No se encontró el nodo de pretensión en el gráfico.")
            return

        fav = 'Favorable' if is_favorable else 'Desfavorable'
        self.window.add_fact_node(parent_node, label, fav, desc)

        # The added node will need to have its relevance set if it is different from default
        fact_node = next(node for node in case_view.scene().nodes.values() if node.model.label == label)
        fact_node.model.relevance = relevance
        fact_node.recalculate_weights_upward()
        fact_node.update()

        title_input.clear()
        desc_input.clear()
        self.refresh_facts()
        self.status_lbl.setText(f"Hecho '{label}' agregado con éxito.")
        self.status_lbl.setStyleSheet("color: #10b981;")

    def generate_evidence_suggestion(self, is_favorable):
        api_key = self.settings.value("gemini_api_key", "")
        if not api_key:
            QMessageBox.warning(self, "API Key Requerida", "Por favor ingresa tu API Key para utilizar la IA.")
            return

        combo = self.fav_fact_combo if is_favorable else self.unfav_fact_combo
        fact = combo.currentData()
        if not fact:
            QMessageBox.warning(self, "Hecho requerido", "Por favor, selecciona o crea un hecho primero.")
            return

        case = self.window.get_active_case()
        pretension = case.pretense.label if case else ""
        allowed_types = list(self.evidence_type_repr.list_values())
        allowed_types_str = ", ".join([f'"{t}"' for t in allowed_types])

        prompt = f"""
Dado el hecho: "{fact.label}" (Descripción: "{fact.desc}")
Relacionado con la pretensión principal del caso: "{pretension}"

Por favor, sugiere una prueba/evidencia idónea para demostrar o respaldar este hecho en español.
Debes clasificar la prueba exactamente en uno de los siguientes tipos: [{allowed_types_str}].
Devuelve el resultado en formato JSON estructurado exactamente así:
{{
  "label": "Nombre corto de la prueba sugerida (ej: Declaración juramentada de María, Escritura pública N°12, máx. 50 caracteres)",
  "type": "El tipo exacto de prueba de la lista proporcionada",
  "desc": "Descripción detallada de la prueba y qué demuestra con relación al hecho."
}}
No agregues explicaciones, markdown, ni nada fuera del objeto JSON.
"""
        self.status_lbl.setText("IA: Sugiriendo prueba...")
        self.status_lbl.setStyleSheet("color: #fb7185;")
        btn = self.fav_ev_btn if is_favorable else self.unfav_ev_btn
        btn.setEnabled(False)

        self.active_worker = GeminiWorker(api_key, prompt)
        self.active_worker.finished_signal.connect(lambda res, err: self.on_evidence_suggested(res, err, is_favorable))
        self.active_worker.start()

    def on_evidence_suggested(self, result_json, error_message, is_favorable):
        btn = self.fav_ev_btn if is_favorable else self.unfav_ev_btn
        btn.setEnabled(True)

        if error_message:
            self.status_lbl.setText(f"Error: {error_message}")
            self.status_lbl.setStyleSheet("color: #ef4444;")
            return

        try:
            data = json.loads(result_json)
            title = data.get("label", "")
            ev_type = data.get("type", "")
            desc = data.get("desc", "")

            title_input = self.fav_ev_title if is_favorable else self.unfav_ev_title
            type_combo = self.fav_ev_type if is_favorable else self.unfav_ev_type
            desc_input = self.fav_ev_desc if is_favorable else self.unfav_ev_desc

            title_input.setText(title)
            desc_input.setPlainText(desc)

            idx = type_combo.findText(ev_type)
            if idx != -1:
                type_combo.setCurrentIndex(idx)

            self.status_lbl.setText("IA: Sugerencia de prueba cargada.")
            self.status_lbl.setStyleSheet("color: #10b981;")
        except Exception as e:
            self.status_lbl.setText("Error al procesar sugerencia de la IA.")
            self.status_lbl.setStyleSheet("color: #ef4444;")

    def add_suggested_evidence(self, is_favorable):
        case_view = self.window.get_active_case_view()
        if not case_view:
            return

        combo = self.fav_fact_combo if is_favorable else self.unfav_fact_combo
        fact_model = combo.currentData()
        if not fact_model:
            QMessageBox.warning(self, "Hecho requerido", "Por favor, selecciona un hecho.")
            return

        # Find FactNode in CaseView
        try:
            parent_node = next(node for node in case_view.scene().nodes.values() if node.model == fact_model)
        except StopIteration:
            QMessageBox.warning(self, "Error", "No se encontró el nodo del hecho en el gráfico.")
            return

        title_input = self.fav_ev_title if is_favorable else self.unfav_ev_title
        type_combo = self.fav_ev_type if is_favorable else self.unfav_ev_type
        desc_input = self.fav_ev_desc if is_favorable else self.unfav_ev_desc
        pert_combo = self.fav_ev_pert if is_favorable else self.unfav_ev_pert
        cred_combo = self.fav_ev_cred if is_favorable else self.unfav_ev_cred

        label = title_input.text().strip()
        ev_type = type_combo.currentText()
        desc = desc_input.toPlainText().strip()
        pert = pert_combo.currentText()
        cred = cred_combo.currentText()

        if not label:
            QMessageBox.warning(self, "Campos Vacíos", "El nombre de la prueba es obligatorio.")
            return

        self.window.add_evidence_node(parent_node, label, 'Favorable', ev_type, desc)

        # The added node will need to have its pertinence and credibility set
        ev_node = next(node for node in case_view.scene().nodes.values() if node.model.label == label)
        ev_node.model.relevance = pert
        ev_node.model.credibility = cred
        ev_node.recalculate_weights_upward()
        ev_node.update()

        title_input.clear()
        desc_input.clear()
        self.status_lbl.setText(f"Prueba '{label}' agregada con éxito.")
        self.status_lbl.setStyleSheet("color: #10b981;")
