import sys
import pytest
from PySide2.QtCore import QPointF

import co_razon.ui.resources

from co_razon.model.judge import Hypothesis, Case, Fact, Evidence
from co_razon.ui.graph import CaseView, HypothesisNode, FactNode, EvidenceNode, ConnectionItem
from co_razon.ui.main_win import CoRazonWindow
from co_razon.util.containers import Container
from tests.unit.mocks.mocks import DataAccessManagerMock


import co_razon.ui.ai_copilot

@pytest.fixture(scope="session", autouse=True)
def container():
    conta = Container()
    conta.init_resources()
    conta.wire(modules=[sys.modules[__name__],
                        co_razon.ui.main_win,
                        co_razon.ui.graph,
                        co_razon.ui.ai_copilot])
    return conta



@pytest.fixture
def case_view(container):
    """Creates a CaseView object"""
    with container.data_access_manager.override(DataAccessManagerMock()):
        window = CoRazonWindow()
        hypothesis = Hypothesis(name="P", label="Label", desc="Description")
        case = Case(name="Test Case", pretense=hypothesis)
        return CaseView(None, window, case)


@pytest.fixture
def hypothesis_node(case_view):
    return case_view.create_node(model=Hypothesis(name="P", label="Label", desc="Description"),
                                 node_type=HypothesisNode)


@pytest.mark.parametrize("model, node_type", [
    (Hypothesis(name="P", label="Label", desc="Description"), HypothesisNode),
    (Fact(name="F", label="Label", desc="Description"), FactNode),
    (Evidence(name="E", label="Label", desc="Description"), EvidenceNode)
])
def test_view_creates_node_of_specific_type(case_view, model, node_type):
    node = case_view.create_node(model=model, node_type=node_type)
    assert type(node) is node_type


def test_favorable_connection_is_created_when_node_created_with_parent(case_view, hypothesis_node):
    fact = Fact(name="F", label="Label", desc="Description")
    fact_node = case_view.create_node(model=fact, node_type=FactNode, parent_node=hypothesis_node, favorable=True)
    in_conn = filter(lambda item: isinstance(item, ConnectionItem) and item.target_plug.parentItem() == fact_node,
                     case_view.scene().items())
    assert fact_node in hypothesis_node.fav_children
    assert len(list(in_conn)) == 1


def test_unfavorable_connection_is_created_when_node_created_with_parent(case_view, hypothesis_node):
    fact = Fact(name="F", label="Label", desc="Description")
    fact_node = case_view.create_node(model=fact, node_type=FactNode, parent_node=hypothesis_node, favorable=False)
    in_conn = filter(lambda item: isinstance(item, ConnectionItem) and item.target_plug.parentItem() == fact_node,
                     case_view.scene().items())
    assert fact_node in hypothesis_node.unfav_children
    assert len(list(in_conn)) == 1


@pytest.mark.parametrize("favorable, expected_point", [
    (True, QPointF(-250, 145)),
    (False, QPointF(50, 145))
])
def test_position_of_new_node_with_parent(case_view, hypothesis_node, favorable, expected_point):
    fact = Fact(name="F", label="Label", desc="Description")
    fact_node = case_view.create_node(model=fact, node_type=FactNode, parent_node=hypothesis_node, favorable=favorable)
    assert fact_node.pos() == expected_point


def test_position_of_new_hypothesis_node(case_view):
    node = case_view.create_node(model=Hypothesis(name="P", label="Label", desc="Description"),
                                 node_type=HypothesisNode)
    assert node.pos().x() == -100
    assert abs(node.pos().y() - (-290 / 6.0 * 5.2)) < 1e-4


def test_auto_layout_compactness(case_view, hypothesis_node):
    root = hypothesis_node
    
    f1 = Fact(name="F1", label="Fact 1", desc="Desc")
    f1_node = case_view.create_node(model=f1, node_type=FactNode, parent_node=root, favorable=True)
    
    f2 = Fact(name="F2", label="Fact 2", desc="Desc")
    f2_node = case_view.create_node(model=f2, node_type=FactNode, parent_node=root, favorable=True)
    
    e1 = Evidence(name="E1", label="Evidence 1", desc="Desc")
    e1_node = case_view.create_node(model=e1, node_type=EvidenceNode, parent_node=f1_node, favorable=True)
    
    e2 = Evidence(name="E2", label="Evidence 2", desc="Desc")
    e2_node = case_view.create_node(model=e2, node_type=EvidenceNode, parent_node=f1_node, favorable=True)
    
    case_view.auto_layout()
    
    assert f1_node.pos().x() != f2_node.pos().x()
    assert e1_node.pos().x() != e2_node.pos().x()


def test_recalculate_weights_upward(case_view, hypothesis_node):
    h_node = hypothesis_node
    hypothesis = h_node.model
    constants = case_view.constants
    
    # Add a Fact to the Hypothesis model
    fact = hypothesis.add_fact(label="Fact 1", desc="Fact Description", favorability=True, relevance=constants.RELEVANT)
    fact_node = case_view.create_node(model=fact, node_type=FactNode, parent_node=h_node, favorable=True)
    
    # Add an Evidence to the Fact model
    evidence = fact.add_evidence(number=1, label="Evidence 1", desc="Evidence Description", favorability=True, evidence_type="Testimonial", relevance=constants.PERTINENT)
    evidence_node = case_view.create_node(model=evidence, node_type=EvidenceNode, parent_node=fact_node, favorable=True)
    
    # Verify initially weight is None
    assert fact.probatory_weight is None
    assert hypothesis.probatory_weight is None
    
    # Simulate setting credibility on the EvidenceNode via update_credibility
    class MockAction:
        def __init__(self, text):
            self._text = text
        def text(self):
            return self._text
            
    evidence_node.update_credibility(MockAction(constants.ALMOST_TRUE))
    
    # Check that both the Fact's and Hypothesis's probatory weight was updated
    assert fact.probatory_weight == constants.ALMOST_TRUE
    assert hypothesis.probatory_weight == constants.ALMOST_TRUE



