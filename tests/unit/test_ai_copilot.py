import sys
import json
import pytest
from unittest.mock import MagicMock, patch
from PySide2.QtCore import Qt, QSettings
from PySide2.QtWidgets import QTabWidget

import co_razon.ui.resources
from co_razon.model.judge import Hypothesis, Case, Fact, Evidence
from co_razon.ui.graph import CaseView, HypothesisNode, FactNode, EvidenceNode
from co_razon.ui.main_win import CoRazonWindow
from co_razon.ui.ai_copilot import AICopilotWidget, GeminiWorker
from co_razon.util.containers import Container
from tests.unit.mocks.mocks import DataAccessManagerMock


@pytest.fixture(scope="session", autouse=True)
def container_init():
    conta = Container()
    conta.init_resources()
    conta.wire(modules=[
        sys.modules[__name__],
        co_razon.ui.main_win,
        co_razon.ui.graph,
        co_razon.ui.ai_copilot
    ])
    return conta


@pytest.fixture
def main_window(container_init):
    with container_init.data_access_manager.override(DataAccessManagerMock()):
        window = CoRazonWindow()
        return window


@pytest.fixture
def case_with_pretense():
    hypothesis = Hypothesis(name="P", label="Isabel sufrió una fractura", desc="Pretensión principal de la demanda")
    case = Case(name="Caso Isabel", claimant="Isabel", defendant="Seguros S.A.", radicado="11001", pretense=hypothesis)
    return case


def test_copilot_initialization(main_window):
    copilot = main_window.ai_copilot_widget
    assert copilot is not None
    assert copilot.main_tabs.count() == 2
    assert copilot.main_tabs.tabText(0) == "Demandante (Favorable)"
    assert copilot.main_tabs.tabText(1) == "Demandado (Desfavorable)"


def test_refresh_ui_no_case(main_window):
    copilot = main_window.ai_copilot_widget
    copilot.refresh_ui()
    assert not copilot.isEnabled()
    assert copilot.fav_pretension_lbl.text() == "Abre o crea un caso"


def test_refresh_ui_with_case(main_window, case_with_pretense):
    copilot = main_window.ai_copilot_widget
    main_window.load_case(case_with_pretense)
    copilot.refresh_ui()
    assert copilot.isEnabled()
    assert copilot.fav_pretension_lbl.text() == "Isabel sufrió una fractura"


@patch('co_razon.ui.ai_copilot.GeminiWorker')
def test_generate_fact_suggestion(mock_worker_class, main_window, case_with_pretense):
    # Set a dummy API Key
    settings = QSettings("Orion", "CoRazon")
    settings.setValue("gemini_api_key", "dummy_key")

    main_window.load_case(case_with_pretense)
    copilot = main_window.ai_copilot_widget

    # Set up mock worker
    mock_worker = MagicMock()
    mock_worker_class.return_value = mock_worker

    copilot.generate_fact_suggestion(is_favorable=True)

    # Verify GeminiWorker was instantiated and started
    mock_worker_class.assert_called_once()
    mock_worker.start.assert_called_once()

    # Simulate worker response
    json_response = json.dumps({
        "label": "Isabel tenía un yeso en su brazo",
        "desc": "El video muestra claramente a Isabel con un yeso."
    })
    copilot.on_fact_suggested(json_response, "", is_favorable=True)

    assert copilot.fav_fact_title.text() == "Isabel tenía un yeso en su brazo"
    assert copilot.fav_fact_desc.toPlainText() == "El video muestra claramente a Isabel con un yeso."


def test_add_suggested_fact(main_window, case_with_pretense):
    main_window.load_case(case_with_pretense)
    copilot = main_window.ai_copilot_widget
    constants = copilot.constants

    copilot.fav_fact_title.setText("Isabel tenía un yeso")
    copilot.fav_fact_desc.setPlainText("Isabel tenía un yeso en el brazo derecho.")
    copilot.fav_fact_relevance.setCurrentText(constants.RELEVANT)

    copilot.add_suggested_fact(is_favorable=True)

    # Verify the fact is added to the case model
    assert len(case_with_pretense.pretense.fav_facts) == 1
    added_fact = case_with_pretense.pretense.fav_facts[0]
    assert added_fact.label == "Isabel tenía un yeso"
    assert added_fact.desc == "Isabel tenía un yeso en el brazo derecho."
    assert added_fact.relevance == constants.RELEVANT

    # Verify the inputs are cleared
    assert copilot.fav_fact_title.text() == ""
    assert copilot.fav_fact_desc.toPlainText() == ""


@patch('co_razon.ui.ai_copilot.GeminiWorker')
def test_generate_evidence_suggestion(mock_worker_class, main_window, case_with_pretense):
    # Set a dummy API Key
    settings = QSettings("Orion", "CoRazon")
    settings.setValue("gemini_api_key", "dummy_key")

    main_window.load_case(case_with_pretense)
    case_view = main_window.get_active_case_view()
    copilot = main_window.ai_copilot_widget

    # Add a mock fact first (both model and node)
    fact = case_with_pretense.pretense.add_fact("Isabel tenía un yeso", "Descripción", True)
    hypothesis_node = next(node for node in case_view.scene().nodes.values() if isinstance(node.model, Hypothesis))
    case_view.create_node(model=fact, node_type=FactNode, parent_node=hypothesis_node, favorable=True)
    copilot.refresh_facts()

    # Get translated type
    doc_type = list(copilot.evidence_type_repr.list_values())[1]

    # Set up mock worker
    mock_worker = MagicMock()
    mock_worker_class.return_value = mock_worker

    copilot.generate_evidence_suggestion(is_favorable=True)

    # Verify GeminiWorker was instantiated and started
    mock_worker_class.assert_called_once()
    mock_worker.start.assert_called_once()

    # Simulate worker response
    json_response = json.dumps({
        "label": "Video de la cámara de seguridad",
        "type": doc_type,
        "desc": "Video en el que se ve a Isabel con el yeso."
    })
    copilot.on_evidence_suggested(json_response, "", is_favorable=True)

    assert copilot.fav_ev_title.text() == "Video de la cámara de seguridad"
    assert copilot.fav_ev_type.currentText() == doc_type
    assert copilot.fav_ev_desc.toPlainText() == "Video en el que se ve a Isabel con el yeso."


def test_add_suggested_evidence(main_window, case_with_pretense):
    main_window.load_case(case_with_pretense)
    case_view = main_window.get_active_case_view()
    copilot = main_window.ai_copilot_widget
    constants = copilot.constants

    # Add a fact (model and node)
    fact = case_with_pretense.pretense.add_fact("Isabel tenía un yeso", "Descripción", True)
    hypothesis_node = next(node for node in case_view.scene().nodes.values() if isinstance(node.model, Hypothesis))
    case_view.create_node(model=fact, node_type=FactNode, parent_node=hypothesis_node, favorable=True)
    copilot.refresh_facts()

    # Select the fact in combo box
    idx = copilot.fav_fact_combo.findData(fact)
    copilot.fav_fact_combo.setCurrentIndex(idx)

    # Get translated type
    doc_type = list(copilot.evidence_type_repr.list_values())[1]

    # Set suggested evidence details
    copilot.fav_ev_title.setText("Video del accidente")
    copilot.fav_ev_type.setCurrentText(doc_type)
    copilot.fav_ev_desc.setPlainText("Video donde se ve la fractura.")
    copilot.fav_ev_pert.setCurrentText(constants.PERTINENT)
    copilot.fav_ev_cred.setCurrentText(constants.TRUE)

    copilot.add_suggested_evidence(is_favorable=True)

    # Verify evidence was added to fact
    assert len(fact.fav_evidence) == 1
    added_ev = fact.fav_evidence[0]
    assert added_ev.label == "Video del accidente"
    assert added_ev.type == doc_type
    assert added_ev.relevance == constants.PERTINENT
    assert added_ev.credibility == constants.TRUE


def test_set_selected_node_synchronization(main_window, case_with_pretense):
    main_window.load_case(case_with_pretense)
    case_view = main_window.get_active_case_view()
    copilot = main_window.ai_copilot_widget

    # Add a fact (model and node)
    fact = case_with_pretense.pretense.add_fact("Hecho Gráfico", "Desc", True)
    hypothesis_node = next(node for node in case_view.scene().nodes.values() if isinstance(node.model, Hypothesis))
    fact_node = case_view.create_node(model=fact, node_type=FactNode, parent_node=hypothesis_node, favorable=True)
    copilot.refresh_facts()

    # Call select_node, which should invoke set_selected_node
    main_window.select_node(fact_node)

    # Assert combo box selection matches
    assert copilot.fav_fact_combo.currentData() == fact
    # Assert tabs switched to Evidence
    assert copilot.main_tabs.currentIndex() == 0  # Claimant
    assert copilot.claimant_tabs.currentIndex() == 1  # Sugerir Prueba
