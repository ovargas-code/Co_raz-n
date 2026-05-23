import os
from PySide2.QtCore import QThread, Signal, QSize, Qt, QSettings
from PySide2.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QProgressBar, QMessageBox, QDialogButtonBox
)
from co_razon.util.ai_service import extract_text_from_pdf, parse_lawsuit_with_gemini, build_case_from_json
from co_razon.model.judge import Case


class GeminiWorker(QThread):
    status_changed = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, api_key: str, demanda_path: str, contestacion_path: str, allowed_probabilities: list, allowed_evidence_types: list):
        super().__init__()
        self.api_key = api_key
        self.demanda_path = demanda_path
        self.contestacion_path = contestacion_path
        self.allowed_probabilities = allowed_probabilities
        self.allowed_evidence_types = allowed_evidence_types

    def run(self):
        try:
            if not self.demanda_path:
                raise ValueError("Se requiere al menos el archivo PDF de la demanda.")
                
            self.status_changed.emit("Extrayendo texto de la demanda...")
            if not os.path.exists(self.demanda_path):
                raise FileNotFoundError(f"No se encontró el archivo de la demanda: {self.demanda_path}")
            
            demanda_text = extract_text_from_pdf(self.demanda_path)
            if not demanda_text.strip():
                raise ValueError("El archivo PDF de la demanda parece estar vacío o no contiene texto extraíble.")

            contestacion_text = ""
            if self.contestacion_path:
                self.status_changed.emit("Extrayendo texto de la contestación...")
                if not os.path.exists(self.contestacion_path):
                    raise FileNotFoundError(f"No se encontró el archivo de la contestación: {self.contestacion_path}")
                contestacion_text = extract_text_from_pdf(self.contestacion_path)
                if not contestacion_text.strip():
                    raise ValueError("El archivo PDF de la contestación parece estar vacío o no contiene texto extraíble.")

            self.status_changed.emit("Llamando a la API de Gemini (analizando y comparando)...")
            case_data = parse_lawsuit_with_gemini(
                demanda_text=demanda_text,
                contestacion_text=contestacion_text,
                api_key=self.api_key,
                allowed_probabilities=self.allowed_probabilities,
                allowed_evidence_types=self.allowed_evidence_types,
                status_callback=self.status_changed.emit
            )
            self.finished.emit(case_data)
        except Exception as e:
            self.error.emit(str(e))


class ImportPdfDialog(QDialog):
    def __init__(self, allowed_probabilities: list, allowed_evidence_types: list, parent=None):
        super().__init__(parent)
        self.allowed_probabilities = allowed_probabilities
        self.allowed_evidence_types = allowed_evidence_types
        self.case_result = None

        self.settings = QSettings("Orion", "CoRazon")

        self.setWindowTitle("Nuevo Proceso desde PDF")
        self.setMinimumSize(QSize(450, 300))

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Gemini API Key section
        layout.addWidget(QLabel("API Key de Gemini (se guardará localmente):"))
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        saved_key = self.settings.value("gemini_api_key", "")
        self.api_key_edit.setText(saved_key)
        layout.addWidget(self.api_key_edit)

        # PDF selection section - DEMANDA
        layout.addWidget(QLabel("Archivo PDF de la Demanda (Requerido):"))
        demanda_layout = QHBoxLayout()
        self.demanda_path_edit = QLineEdit()
        self.demanda_path_edit.setReadOnly(True)
        demanda_layout.addWidget(self.demanda_path_edit)

        self.browse_demanda_btn = QPushButton("Examinar...")
        self.browse_demanda_btn.clicked.connect(self.browse_demanda)
        demanda_layout.addWidget(self.browse_demanda_btn)
        layout.addLayout(demanda_layout)

        # PDF selection section - CONTESTACION
        layout.addWidget(QLabel("Archivo PDF de la Contestación (Opcional):"))
        contestacion_layout = QHBoxLayout()
        self.contestacion_path_edit = QLineEdit()
        self.contestacion_path_edit.setReadOnly(True)
        contestacion_layout.addWidget(self.contestacion_path_edit)

        self.browse_contestacion_btn = QPushButton("Examinar...")
        self.browse_contestacion_btn.clicked.connect(self.browse_contestacion)
        contestacion_layout.addWidget(self.browse_contestacion_btn)
        layout.addLayout(contestacion_layout)

        # Loading / Progress section
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        # Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("Importar")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Cancelar")
        
        self.button_box.accepted.connect(self.start_import)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def browse_demanda(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar PDF de la Demanda", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.demanda_path_edit.setText(file_path)

    def browse_contestacion(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar PDF de la Contestación", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.contestacion_path_edit.setText(file_path)

    def start_import(self):
        api_key = self.api_key_edit.text().strip()
        demanda_path = self.demanda_path_edit.text().strip()
        contestacion_path = self.contestacion_path_edit.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Campos requeridos", "Por favor, introduce tu API Key de Gemini.")
            return

        if not demanda_path:
            QMessageBox.warning(self, "Campos requeridos", "Por favor, selecciona el archivo PDF de la demanda.")
            return

        # Save API key to QSettings
        self.settings.setValue("gemini_api_key", api_key)

        # Disable controls
        self.api_key_edit.setEnabled(False)
        self.browse_demanda_btn.setEnabled(False)
        self.browse_contestacion_btn.setEnabled(False)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.button(QDialogButtonBox.Cancel).setEnabled(False)

        # Show loading indicator
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) # Indeterminate status
        self.status_label.setText("Iniciando procesamiento...")

        # Run worker thread
        self.worker = GeminiWorker(api_key, demanda_path, contestacion_path, self.allowed_probabilities, self.allowed_evidence_types)
        self.worker.status_changed.connect(self.update_status)
        self.worker.finished.connect(self.on_success)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def update_status(self, text):
        self.status_label.setText(text)

    def on_success(self, case_data):
        try:
            self.case_result = build_case_from_json(case_data)
            self.accept()
        except Exception as e:
            self.on_error(f"Error al construir el caso: {str(e)}")

    def on_error(self, err_msg):
        QMessageBox.critical(self, "Error de Importación", f"Ocurrió un error al procesar el archivo:\n\n{err_msg}")
        
        # Re-enable controls
        self.api_key_edit.setEnabled(True)
        self.browse_demanda_btn.setEnabled(True)
        self.browse_contestacion_btn.setEnabled(True)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self.button_box.button(QDialogButtonBox.Cancel).setEnabled(True)
        
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
