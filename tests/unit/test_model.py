import sys

import pytest
from PySide2.QtCore import QLocale, QTranslator, QLibraryInfo
from dependency_injector.wiring import Provide, inject
from importlib.resources import files

import co_razon
from co_razon.model.judge import Evidence, Case, Hypothesis, Fact, ModelChecker
from co_razon.ui.constants import Constants, EvidenceType
from co_razon.util.containers import Container
from co_razon.util.custom_exceptions import EvidenceException, HypothesisException
from tests.unit.mocks.mocks import MockVisitor

TRUE = 'True'
ALMOST_TRUE = 'Almost true'
VERY_LIKELY = 'Very likely'
MOST_LIKELY = 'Most likely'
LIKELY = 'Likely'
UNLIKELY = 'Unlikely'
UNSUPPORTED = 'Unsupported'
RELEVANT = 'Relevant'
PERTINENT = 'Pertinent'
IRRELEVANT = 'Irrelevant'
IMPERTINENT = 'Impertinent'


@pytest.fixture(scope="session", autouse=True)
def setup():
    from PySide2.QtCore import QLocale
    QLocale.system = lambda: QLocale('en_US')

    container = Container()
    container.init_resources()
    container.wire(modules=[sys.modules[__name__]])


@pytest.fixture
@inject
def const(constants: Constants = Provide[Container.constants]):
    return constants

@pytest.fixture
def evidence():
    """Return an Evidence instance with its relevance and credibility set"""
    return Evidence(name="P1", label="Test Evidence", type=EvidenceType.TESTIMONIAL,
                    desc="Test Description")


@pytest.fixture
def evidence_without_credibility(const):
    """Return an Evidence instance with its relevance and without its credibility """
    return Evidence(name="P1", label="Test Evidence", type=EvidenceType.TESTIMONIAL,
                    desc="Test Description", credibility=None, relevance=const.VERY_LIKELY)


@pytest.fixture
def evidence_without_relevance(const):
    """Return an Evidence instance without its relevance and with its credibility"""
    return Evidence(name="P1", label="Test Evidence", type=EvidenceType.TESTIMONIAL,
                    desc="Test Description", credibility=const.MOST_LIKELY, relevance=None)


@pytest.fixture
def evidence_without_relevance_credibility():
    """Return an Evidence instance without its relevance and without its credibility"""
    return Evidence(name="P1", label="Test Evidence", type=EvidenceType.TESTIMONIAL,
                    desc="Test Description", credibility=None, relevance=None)


@pytest.fixture
def pretense_without_facts():
    """ Return a Hypothesis without facts"""
    return Hypothesis(name='H1', label='Hypothesis', desc='Hypothesis description',
                      probatory_weight=None, fav_facts=None, unfav_facts=None)


@pytest.fixture
def fact():
    return Fact(name="F1", label="Test Fact", desc="Fact description")


@pytest.fixture
def fact_without_evidence_subfact(const):
    """ Return a Fact without evidence and subfacts"""
    return Fact(name='F1', label='Fact', desc='Fact description',
                relevance=const.UNLIKELY, probatory_weight=None)


@pytest.fixture
def case_simulation():
    """Return a case with several facts and evidence"""
    with open(files('tests.unit').joinpath('fixtures/caso_simulacion.json'), 'r', encoding='utf8') as file:
        content = file.read()

    case = Case.from_json(content)
    return case

@pytest.fixture
def test_case_1():
    """Return a case with facts and evidence all without relevance and credibility data"""
    with open(files('tests.unit').joinpath('fixtures/test_case_1.json'), 'r', encoding='utf8') as file:
        content = file.read()

    case = Case.from_json(content)
    return case


@pytest.fixture
def test_case_2():
    """Return a case with facts and subfacts all without relevance and credibility data"""
    with open(files('tests.unit').joinpath('fixtures/test_case_2.json'), 'r', encoding='utf8') as file:
        content = file.read()

    case = Case.from_json(content)
    return case


def test_hypothesis_calculate_evidential_weight(case_simulation, const):
    assert case_simulation.pretense.calculate_evidential_weight() == const.MOST_LIKELY


@pytest.mark.parametrize("cred, relev, expected_weight", [
    (LIKELY, MOST_LIKELY, LIKELY),
    (TRUE, ALMOST_TRUE, ALMOST_TRUE),
    (UNSUPPORTED, MOST_LIKELY, UNSUPPORTED),
    (UNLIKELY, UNLIKELY, UNLIKELY),
    (LIKELY, UNLIKELY, UNLIKELY),
    (LIKELY, PERTINENT, LIKELY),
    (UNSUPPORTED, PERTINENT, UNSUPPORTED),
    (LIKELY, IMPERTINENT, UNSUPPORTED),
    (TRUE, PERTINENT, TRUE),
])
def test_evidence_calculate_evidential_weight(evidence, cred, relev, expected_weight):
    evidence.credibility = cred
    evidence.relevance = relev
    assert evidence.calculate_evidential_weight() == expected_weight


def test_evidence_calculate_evidential_weight_raises_exception_credibility(evidence_without_credibility):
    with pytest.raises(EvidenceException):
        evidence_without_credibility.calculate_evidential_weight()


def test_evidence_calculate_evidential_weight_raises_exception_relevance(evidence_without_relevance):
    with pytest.raises(EvidenceException):
        evidence_without_relevance.calculate_evidential_weight()


def test_evidence_calculate_evidential_weight_raises_exception_relevance_credibility(
        evidence_without_relevance_credibility):
    with pytest.raises(EvidenceException):
        evidence_without_relevance_credibility.calculate_evidential_weight()


def test_pretense_without_facts(pretense_without_facts):
    with pytest.raises(HypothesisException):
        pretense_without_facts.calculate_evidential_weight()

def test_evidence_type_returns_list():
    values = ['Testimonial', 'Documentary', 'Expert', 'Circumstantial', 'Inform', 'Inspection', 'Confession',
              'Oath']
    assert EvidenceType.list_values() == values


def test_generate_experience_rule_for_fav_evidence(case_simulation):
    ev = case_simulation.pretense.fav_facts[0].fav_evidence[0]
    expected_rule = "If the evidence of Grabación de video is true, then is Very likely the " \
                    "fact that Nexo con el comprador"

    assert ev.generate_experience_rule() == expected_rule


def test_generate_experience_rule_for_unfav_evidence(case_simulation):
    ev = case_simulation.pretense.fav_facts[1].unfav_evidence[0]
    expected_rule = "If the evidence of Escritura pública is true, then is Very likely " \
                    "the denial of the fact that No entregó el bien"

    assert ev.generate_experience_rule() == expected_rule


def test_generate_experience_rule_for_fav_fact_of_hypothesis(case_simulation):
    fact = case_simulation.pretense.fav_facts[0]
    expected_rule = "If the fact that Nexo con el comprador is true, then is Very likely " \
                    "the pretension that El vendedor simuló la venta"

    assert fact.generate_experience_rule() == expected_rule


def test_generate_experience_rule_for_unfav_fact_of_hypothesis(case_simulation):
    fact = case_simulation.pretense.unfav_facts[0]
    expected_rule = "If the fact that Interés diferente a vender is true, then is Very likely " \
                    "the denial of the pretension that El vendedor simuló la venta"

    assert fact.generate_experience_rule() == expected_rule


def test_generate_experience_rule_for_fav_subfact(case_simulation):
    sub_fact = case_simulation.pretense.fav_facts[2].fav_facts[0]
    expected_rule = "If the fact that No hay transacción en cuenta is true, then is Likely " \
                    "the fact that No recibió el pago"

    assert sub_fact.generate_experience_rule() == expected_rule

def test_generate_experience_rule_for_unfav_subfact(case_simulation):
    sub_fact = case_simulation.pretense.fav_facts[2].unfav_facts[0]
    expected_rule = "If the fact that El vendedor tiene un comprobante de pago is true, then is Likely " \
                    "the denial of the fact that No recibió el pago"

    assert sub_fact.generate_experience_rule() == expected_rule


def test_add_fav_fact_to_empty_hypothesis(pretense_without_facts):
    fact = pretense_without_facts.add_fact("Nuevo Hecho", "desc", True)

    # Check fav_facts has increase in 1
    assert len(pretense_without_facts.fav_facts) == 1

    # Check the returned fact has the information that was passed to the method
    assert fact.label == "Nuevo Hecho"
    assert fact.desc == "desc"
    assert fact.relevance == RELEVANT
    assert fact.parent_doc == pretense_without_facts


def test_add_unfav_fact_to_empty_hypothesis(pretense_without_facts):
    fact = pretense_without_facts.add_fact("Nuevo Hecho", "desc", False)

    # Check unfav_facts has increase in 1
    assert len(pretense_without_facts.unfav_facts) == 1

    # Check the returned fact has the information that was passed to the method
    assert fact.label == "Nuevo Hecho"
    assert fact.desc == "desc"
    assert fact.relevance == RELEVANT
    assert fact.parent_doc == pretense_without_facts


def test_add_fav_sub_fact_to_empty_fact(fact_without_evidence_subfact):
    fact = fact_without_evidence_subfact.add_sub_fact("Subfact", "desc", True)

    # Check fav_facts has increase in 1
    assert len(fact_without_evidence_subfact.fav_facts) == 1

    # Check the returned fact has the information that was passed to the method
    assert fact.label == "Subfact"
    assert fact.desc == "desc"
    assert fact.relevance == RELEVANT
    assert fact.parent_doc == fact_without_evidence_subfact


def test_add_unfav_sub_fact_to_empty_fact(fact_without_evidence_subfact):
    fact = fact_without_evidence_subfact.add_sub_fact("Subfact", "desc", False)

    # Check fav_facts has increase in 1
    assert len(fact_without_evidence_subfact.unfav_facts) == 1

    # Check the returned fact has the information that was passed to the method
    assert fact.label == "Subfact"
    assert fact.desc == "desc"
    assert fact.relevance == RELEVANT
    assert fact.parent_doc == fact_without_evidence_subfact


def test_add_fav_evidence_to_empty_fact(fact_without_evidence_subfact):
    evidence = fact_without_evidence_subfact.add_evidence(1, "Evidence", "desc", True, EvidenceType.TESTIMONIAL)

    # Check fav_evidence has increase in 1
    assert len(fact_without_evidence_subfact.fav_evidence) == 1

    # Check the returned evidence has the information that was passed to the method
    assert evidence.name == "MP1"
    assert evidence.label == "Evidence"
    assert evidence.label == "Evidence"
    assert evidence.relevance == PERTINENT
    assert evidence.credibility is None
    assert evidence.type == EvidenceType.TESTIMONIAL
    assert evidence.parent_doc == fact_without_evidence_subfact


def test_add_unfav_evidence_to_empty_fact(fact_without_evidence_subfact):
    evidence = fact_without_evidence_subfact.add_evidence(1, "Evidence", "desc", False, EvidenceType.DOCUMENTARY)

    # Check unfav_evidence has increase in 1
    assert len(fact_without_evidence_subfact.unfav_evidence) == 1

    # Check the returned evidence has the information that was passed to the method
    assert evidence.name == "MP1"
    assert evidence.label == "Evidence"
    assert evidence.label == "Evidence"
    assert evidence.relevance == PERTINENT
    assert evidence.credibility is None
    assert evidence.type == EvidenceType.DOCUMENTARY
    assert evidence.parent_doc == fact_without_evidence_subfact


def test_delete_child_from_hypothesis(case_simulation):
    fav_fact_to_delete = case_simulation.pretense.fav_facts[0]
    unfav_fact_to_delete = case_simulation.pretense.unfav_facts[0]

    fav_facts_len_before_deleting = len(case_simulation.pretense.fav_facts)
    unfav_facts_len_before_deleting = len(case_simulation.pretense.unfav_facts)

    case_simulation.pretense.delete_child(fav_fact_to_delete)
    assert len(case_simulation.pretense.fav_facts) == fav_facts_len_before_deleting - 1

    case_simulation.pretense.delete_child(unfav_fact_to_delete)
    assert len(case_simulation.pretense.unfav_facts) == unfav_facts_len_before_deleting - 1


def test_delete_evidence_child_from_fact(case_simulation):
    fact_1 = case_simulation.pretense.fav_facts[1]
    fact_2 = case_simulation.pretense.fav_facts[2]

    fav_evidence_to_delete = fact_2.fav_evidence[0]
    unfav_evidence_to_delete = fact_1.unfav_evidence[0]

    fav_evidence_len_before_deleting = len(fact_2.fav_evidence)
    unfav_evidence_len_before_deleting = len(fact_1.unfav_evidence)

    fact_1.delete_child(unfav_evidence_to_delete)
    assert len(fact_1.unfav_evidence) == unfav_evidence_len_before_deleting - 1

    fact_2.delete_child(fav_evidence_to_delete)
    assert len(fact_2.fav_evidence) == fav_evidence_len_before_deleting - 1


def test_delete_sub_fact_child_from_fact(case_simulation):
    fact = case_simulation.pretense.fav_facts[2]

    fav_sub_fact_to_delete = fact.fav_facts[0]
    unfav_sub_fact_to_delete = fact.unfav_facts[0]

    fav_facts_len_before_deleting = len(fact.fav_facts)
    unfav_facts_len_before_deleting = len(fact.unfav_facts)

    fact.delete_child(fav_sub_fact_to_delete)
    assert len(fact.fav_facts) == fav_facts_len_before_deleting - 1

    fact.delete_child(unfav_sub_fact_to_delete)
    assert len(fact.unfav_facts) == unfav_facts_len_before_deleting - 1


def test_clone_case(case_simulation):
    clone = case_simulation.clone()

    assert clone.id != case_simulation.id
    assert clone.name == case_simulation.name
    assert clone.defendant == case_simulation.defendant
    assert clone.claimant == case_simulation.claimant
    assert clone.radicado == case_simulation.radicado
    assert clone.pretense == case_simulation.pretense
    assert clone.evidence_counter == case_simulation.evidence_counter


def test_pending_items_for_evidence(evidence):
    checker = ModelChecker()
    evidence.accept(checker)
    expected = [(f'Relevance of the evidence "{evidence.label}"', evidence.name),
                (f'Credibility of the evidence "{evidence.label}"', evidence.name)]
    assert checker.pending_items == expected


def test_pending_items_for_fact(fact):
    checker = ModelChecker()
    fact.accept(checker)
    expected = [(f'Relevance of the fact "{fact.label}"', fact.name)]
    assert checker.pending_items == expected


def test_pending_items_for_case_pretense_with_fact_and_evidence(test_case_1):
    checker = ModelChecker()
    test_case_1.pretense.accept(checker)
    expected = [('Relevance of the evidence "P1"', 'MP1'),
                ('Credibility of the evidence "P1"', 'MP1'),
                ('Relevance of the fact "H1"', 'H1'),
                ('Relevance of the evidence "P2"', 'MP2'),
                ('Credibility of the evidence "P2"', 'MP2'),
                ('Relevance of the fact "H2"', 'H2')]
    assert checker.pending_items == expected


def test_pending_items_for_case_pretense_with_fact_and_subfacts(test_case_2):
    checker = ModelChecker()
    test_case_2.pretense.accept(checker)
    expected = [('Relevance of the fact "H11"', 'H11'),
                ('Relevance of the fact "H1"', 'H1'),
                ('Relevance of the fact "H21"', 'H21'),
                ('Relevance of the fact "H2"', 'H2')]
    assert checker.pending_items == expected

def test_checker_visitor_unimplemented(test_case_1, fact, evidence):
    checker = MockVisitor()
    with pytest.raises(NotImplementedError):
        test_case_1.pretense.accept(checker)

    with pytest.raises(NotImplementedError):
        evidence.accept(checker)

    with pytest.raises(NotImplementedError):
        fact.accept(checker)

def test_generate_experience_rule_spanish(case_simulation):
    # Temporarily set system locale to Spanish
    from PySide2.QtCore import QLocale
    original_system = QLocale.system
    QLocale.system = lambda: QLocale('es_CO')
    
    try:
        ev = case_simulation.pretense.fav_facts[0].fav_evidence[0]
        ev.label = "Video en el que se ve a Isabel"
        p_doc = ev.parent_doc if ev._instance is None else ev._instance
        p_doc.label = "Isabel tenía un yeso en su brazo derecho"
        
        # Test pertinent rule
        ev.relevance = "Pertinente"
        rule = ev.generate_experience_rule()
        assert "Si la prueba de video en el que se ve a Isabel hace más o menos probable el hecho que Isabel tenía un yeso en su brazo derecho, entonces esta prueba es pertinente." in rule
        
        # Test impertinent rule
        ev.relevance = "Impertinente"
        rule = ev.generate_experience_rule()
        assert "Si la prueba de video en el que se ve a Isabel no hace más o menos probable el hecho que Isabel tenía un yeso en su brazo derecho, entonces esta prueba es impertinente." in rule
    finally:
        QLocale.system = original_system

def test_generate_experience_rule_fact_spanish(case_simulation):
    # Temporarily set system locale to Spanish
    from PySide2.QtCore import QLocale
    original_system = QLocale.system
    QLocale.system = lambda: QLocale('es_CO')

    try:
        fact = case_simulation.pretense.fav_facts[0]
        fact.label = "Isabel tenía un yeso en su brazo derecho"
        p_doc = fact.parent_doc if fact._instance is None else fact._instance
        p_doc.label = "Isabel sufrió una fractura en su brazo derecho"

        # Test relevant rule with hypothesis parent (la pretensión)
        fact.relevance = "Relevante"
        rule = fact.generate_experience_rule()
        assert "Si el hecho que isabel tenía un yeso en su brazo derecho hace más o menos probable la pretensión que Isabel sufrió una fractura en su brazo derecho, entonces el hecho es relevante." in rule

        # Test irrelevant rule with hypothesis parent (la pretensión)
        fact.relevance = "Irrelevante"
        rule = fact.generate_experience_rule()
        assert "Si el hecho que isabel tenía un yeso en su brazo derecho no hace más o menos probable la pretensión que Isabel sufrió una fractura en su brazo derecho, entonces el hecho es irrelevante." in rule

        # Test relevant rule with fact parent (el hecho)
        sub_fact = case_simulation.pretense.fav_facts[2].fav_facts[0]
        sub_fact.label = "Isabel tenía un yeso en su brazo derecho"
        p_sub = sub_fact.parent_doc if sub_fact._instance is None else sub_fact._instance
        p_sub.label = "Isabel sufrió una fractura en su brazo derecho"

        sub_fact.relevance = "Relevante"
        rule2 = sub_fact.generate_experience_rule()
        assert "Si el hecho que isabel tenía un yeso en su brazo derecho hace más o menos probable el hecho que Isabel sufrió una fractura en su brazo derecho, entonces el hecho es relevante." in rule2
    finally:
        QLocale.system = original_system


# TODO: Add test to calculate_evidential_weight of Hypothesis when there are facts in favor but not against,
#  including both cases: when there is only one fact, and when there is mor than one

# TODO: Add test to calculate_evidential_weight of Hypothesis when there are only facts against

# TODO: Add test to calculate_evidential_weight of Fact when there is only evidence or subfacts against

# TODO: Add test to calculate_evidential_weigh of Fact when it raises FactException and FactRelevanceException