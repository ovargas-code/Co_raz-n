from abc import ABCMeta, abstractmethod
from copy import deepcopy
from enum import Enum, unique, auto

from PySide2.QtCore import QObject, QLocale
from bson.objectid import ObjectId
from dependency_injector.wiring import Provide
from multipledispatch import dispatch
from mongoengine import Document, StringField, EmbeddedDocument, ListField, EmbeddedDocumentField, IntField, \
    FloatField, BooleanField

from juezinteligente.ui.constants import Constants
from juezinteligente.util.containers import Container
from juezinteligente.util.custom_exceptions import EvidenceException, FactException, FactRelevanceException, \
    HypothesisException


class CheckableElement(metaclass=ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'accept') and
                callable(subclass.accept) or
                NotImplemented)

    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError


class Observer(metaclass=ABCMeta):

    @abstractmethod
    def update_observer(self, obj):
        raise NotImplementedError


class Observable:
    def __init__(self):
        self.observers = list()

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify(self):
        for o in self.observers:
            o.update_observer(self)


class NodePosition(EmbeddedDocument):
    x = FloatField(required=True, default=0)
    y = FloatField(required=True, default=0)


class Evidence(EmbeddedDocument, Observable):
    name = StringField(required=True)
    label = StringField(required=True, max_length=50)
    type = StringField(required=True)
    desc = StringField(required=True)
    relevance = StringField()
    credibility = StringField()
    position = EmbeddedDocumentField(NodePosition)
    ignored = BooleanField(required=True, default=False)
    parent_doc = None

    def __init__(self, *args, **kwargs):
        Observable.__init__(self)
        EmbeddedDocument.__init__(self, *args, **kwargs)

    def calculate_evidential_weight(self):
        """
        Calculates this evidence's evidential weight based on its relevance and credibility.
        """
        probabilities, weights = self.weight_definition()
        try:
            evidential_weight = weights[min(probabilities[self.relevance], probabilities[self.credibility])]
            self.evidential_weight = evidential_weight
            return evidential_weight
        except KeyError:
            raise EvidenceException(self)

    def weight_definition(self, constants: Constants = Provide[Container.constants]):
        """
        Defines the probability weight
        """
        probabilities = [constants.UNSUPPORTED, constants.UNLIKELY, constants.LIKELY, constants.MOST_LIKELY, 
                         constants.VERY_LIKELY, constants.ALMOST_TRUE, constants.TRUE]
        prob_dict = {probability: weight for weight, probability in enumerate(probabilities)}
        prob_dict[constants.IMPERTINENT] = 0
        prob_dict[constants.PERTINENT] = 6
        prob_dict[constants.IRRELEVANT] = 0
        prob_dict[constants.RELEVANT] = 6
        
        weight_dict = {weight: probability for weight, probability in enumerate(probabilities)}
        return prob_dict, weight_dict

    def generate_experience_rule(self, constants: Constants = Provide[Container.constants]):
        """
        This method generates a string with the experience rule for this evidence in relation with its fact(parent)
        """
        p_doc = self.parent_doc if self._instance is None else self._instance
        if self in p_doc.unfav_evidence:
            consequent = f"{constants.DENIAL_OF_THE_FACT_THAT} {p_doc.label}"
        else:
            consequent = f"{constants.THE_FACT_THAT} {p_doc.label}"

        probability = "_________" if self.relevance is None else self.relevance
        rule = f"{constants.IF_THE_EVIDENCE} {self.label} {constants.IS_TRUE_THEN_IS} {probability} {consequent}"
        return rule

    def accept(self, visitor):
        visitor.visit(self)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in ("relevance", "credibility", "label"):
            self.notify()


class Fact(EmbeddedDocument, Observable):
    name = StringField(required=True)
    label = StringField(required=True, max_length=50)
    desc = StringField(required=True)
    relevance = StringField()
    probatory_weight = StringField()
    fav_facts = ListField(EmbeddedDocumentField('Fact'))
    unfav_facts = ListField(EmbeddedDocumentField('Fact'))
    fav_evidence = ListField(EmbeddedDocumentField('Evidence'))
    unfav_evidence = ListField(EmbeddedDocumentField('Evidence'))
    ignored = BooleanField(required=True, default=False)
    position = EmbeddedDocumentField(NodePosition)
    parent_doc = None
    EVIDENCE_NAME_INITIAL = "MP"

    def __init__(self, *args, **kwargs):
        Observable.__init__(self)
        EmbeddedDocument.__init__(self, *args, **kwargs)

    def add_sub_fact(self, label: str, desc: str, favorability: bool = True, relevance: str = None,
                     constants: Constants = Provide[Container.constants]):
        if relevance is None:
            relevance = constants.RELEVANT
        code = len(self.fav_facts) + len(self.unfav_facts) + 1
        name = self.name + str(code)
        fact = Fact(name=name, label=label, desc=desc, relevance=relevance)
        fact.parent_doc = self
        if favorability:
            self.fav_facts.append(fact)
        else:
            self.unfav_facts.append(fact)
        return fact

    def add_evidence(self, number, label, desc, favorability, evidence_type, credibility: str = None,
                     relevance: str = None, constants: Constants = Provide[Container.constants]):
        if relevance is None:
            relevance = constants.PERTINENT
        name = self.EVIDENCE_NAME_INITIAL + str(number)
        evidence = Evidence(name=name, label=label, type=evidence_type, desc=desc, credibility=credibility,
                            relevance=relevance)
        evidence.parent_doc = self
        if favorability:
            self.fav_evidence.append(evidence)
        else:
            self.unfav_evidence.append(evidence)

        return evidence

    def delete_child(self, item):
        if item in self.fav_facts:
            self.fav_facts.remove(item)
        elif item in self.unfav_facts:
            self.unfav_facts.remove(item)
        elif item in self.fav_evidence:
            self.fav_evidence.remove(item)
        elif item in self.unfav_evidence:
            self.unfav_evidence.remove(item)
        self.notify()

    def weight_definition(self, constants: Constants = Provide[Container.constants]):
        probabilities = [constants.UNSUPPORTED, constants.UNLIKELY, constants.LIKELY, constants.MOST_LIKELY,
                         constants.VERY_LIKELY, constants.ALMOST_TRUE, constants.TRUE]
        prob_dict = {probability: weight for weight, probability in enumerate(probabilities)}
        prob_dict[constants.IMPERTINENT] = 0
        prob_dict[constants.PERTINENT] = 6
        prob_dict[constants.IRRELEVANT] = 0
        prob_dict[constants.RELEVANT] = 6
        
        weight_dict = {weight: probability for weight, probability in enumerate(probabilities)}
        return prob_dict, weight_dict

    def probability_balance(self, probatory_weight_fav, probatory_weight_unfav,
                            constants: Constants = Provide[Container.constants]):
        probability_matrix = [[constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED,
                               constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED,
                               constants.UNSUPPORTED],
                              [constants.UNLIKELY, constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED,
                               constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.LIKELY, constants.LIKELY, constants.UNSUPPORTED, constants.UNSUPPORTED,
                               constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.MOST_LIKELY, constants.MOST_LIKELY, constants.LIKELY, constants.UNSUPPORTED,
                               constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.VERY_LIKELY, constants.VERY_LIKELY, constants.MOST_LIKELY, constants.LIKELY,
                               constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.ALMOST_TRUE, constants.ALMOST_TRUE, constants.VERY_LIKELY,
                               constants.MOST_LIKELY, constants.LIKELY, constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.TRUE, constants.ALMOST_TRUE, constants.VERY_LIKELY, constants.MOST_LIKELY,
                               constants.LIKELY, constants.UNLIKELY, constants.UNSUPPORTED]]
        probabilities, weights = self.weight_definition()
        row_index = probabilities[probatory_weight_fav]
        column_index = probabilities[probatory_weight_unfav]
        return probability_matrix[row_index][column_index]

    def calculate_evidential_weight(self, constants: Constants = Provide[Container.constants]):
        """
        Calculates this fact's evidential weight.
        """
        fav_weights = []
        unfav_weights = []
        probabilities, weights = self.weight_definition()
        favorable = self.fav_evidence + self.fav_facts
        unfavorable = self.unfav_evidence + self.unfav_facts
        for fav in favorable:
            if not fav.ignored:
                if isinstance(fav, Fact):
                    fav_weights.append(weights[min(probabilities[fav.calculate_evidential_weight()], probabilities[fav.relevance])])
                else:
                    fav_weights.append(fav.calculate_evidential_weight())
        for unfav in unfavorable:
            if not unfav.ignored:
                if isinstance(unfav, Fact):
                    unfav_weights.append(weights[min(probabilities[unfav.calculate_evidential_weight()], probabilities[unfav.relevance])])
                else:
                    unfav_weights.append(unfav.calculate_evidential_weight())
        try:
            if (len(fav_weights) != 0) and (
                    len(unfav_weights) == 0):  # there is evidence or sub-facts in favor and not against
                if len(fav_weights) == 1:  # there is only one evidence or sub-fact in favor
                    self.probatory_weight = fav_weights[0]
                    return weights[min(probabilities[fav_weights[0]], probabilities[self.relevance])]
                else:  # there is more than one evidence or sub-facts in favor
                    probatory_weight = weights[max([probabilities[fav] for fav in fav_weights])]
            elif (len(unfav_weights) != 0) and (len(fav_weights) == 0):  # there is only evidence or sub-facts against
                probatory_weight = constants.UNSUPPORTED
            else:  # there are evidences and/or sub-facts in favor and against
                total_weight_fav = weights[max([probabilities[fav] for fav in fav_weights])]
                total_weight_unfav = weights[max([probabilities[unfav] for unfav in unfav_weights])]
                probatory_weight = self.probability_balance(total_weight_fav, total_weight_unfav)
            self.probatory_weight = probatory_weight
            return probatory_weight
        except ValueError:
            raise FactException(self)
        except KeyError:
            raise FactRelevanceException(self)

    def generate_experience_rule(self, constants: Constants = Provide[Container.constants]):
        """
        This method generates a string with the experience rule for this evidence in relation with its fact(parent)
        """
        p_doc = self.parent_doc if self._instance is None else self._instance
        parent_type = constants.FACT if isinstance(p_doc, Fact) else constants.PRETENSION

        if self in p_doc.unfav_facts:
            if parent_type == constants.FACT:
                consequent = f"{constants.DENIAL_OF} {parent_type} {constants.THAT} {p_doc.label}"
            else:
                consequent = f"{constants.DENIAL_OF} {parent_type} {constants.THAT} {p_doc.label}"
        else:
            if parent_type == constants.FACT:
                consequent = f"{parent_type} {constants.THAT} {p_doc.label}"
            else:
                consequent = f"{parent_type} {constants.THAT} {p_doc.label}"

        probability = "_________" if self.relevance is None else self.relevance

        locale = QLocale.system().name()
        conn_phrase = "es cierto, entonces es" if locale.startswith("es") else constants.IS_TRUE_THEN_IS
        rule = f"{constants.IF_THE_FACT_THAT} {self.label} {conn_phrase} {probability} {consequent}"
        return rule

    def accept(self, visitor):
        visitor.visit(self)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in ("relevance", "label"):
            self.notify()
        elif key in ("ignored",):
            sub_facts = []
            evidence = []

            if self.unfav_facts is not None and self.fav_facts is not None:
                sub_facts = self.unfav_facts + self.fav_facts

            if self.unfav_evidence is not None and self.fav_evidence is not None:
                evidence = self.fav_evidence + self.unfav_evidence

            for f in sub_facts:
                f.ignored = value

            for e in evidence:
                e.ignored = value


class Hypothesis(EmbeddedDocument, Observable):
    name = StringField(required=True)
    label = StringField(required=True, max_length=50)
    desc = StringField(required=True)
    probatory_weight = StringField()
    fav_facts = ListField(EmbeddedDocumentField(Fact))
    unfav_facts = ListField(EmbeddedDocumentField(Fact))
    position = EmbeddedDocumentField(NodePosition)

    FACT_NAME_INITIAL = 'H'

    def __init__(self, *args, **kwargs):
        Observable.__init__(self)
        EmbeddedDocument.__init__(self, *args, **kwargs)

    def add_fact(self, label, desc, favorability: bool = True, relevance=None,
                 constants: Constants = Provide[Container.constants]):
        if relevance is None:
            relevance = constants.RELEVANT
        code = len(self.fav_facts) + len(self.unfav_facts) + 1
        name = self.FACT_NAME_INITIAL + str(code)
        fact = Fact(name=name, label=label, desc=desc, relevance=relevance)
        fact.parent_doc = self
        if favorability:
            self.fav_facts.append(fact)
        else:
            self.unfav_facts.append(fact)

        self.notify()
        return fact

    def delete_child(self, item):
        if item in self.fav_facts:
            self.fav_facts.remove(item)
        elif item in self.unfav_facts:
            self.unfav_facts.remove(item)
        self.notify()

    def weight_definition(self, constants: Constants = Provide[Container.constants]):
        probabilities = [constants.UNSUPPORTED, constants.UNLIKELY, constants.LIKELY, constants.MOST_LIKELY,
                         constants.VERY_LIKELY, constants.ALMOST_TRUE, constants.TRUE]
        prob_dict = {probability: weight for weight, probability in enumerate(probabilities)}
        prob_dict[constants.IMPERTINENT] = 0
        prob_dict[constants.PERTINENT] = 6
        prob_dict[constants.IRRELEVANT] = 0
        prob_dict[constants.RELEVANT] = 6
        
        weight_dict = {weight: probability for weight, probability in enumerate(probabilities)}
        return prob_dict, weight_dict

    def probability_balance(self, probatory_weight_fav, probatory_weight_unfav,
                            constants: Constants = Provide[Container.constants]):
        probability_matrix = [[constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED,
                               constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.UNLIKELY, constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED,
                               constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.LIKELY, constants.LIKELY, constants.UNSUPPORTED, constants.UNSUPPORTED, constants.UNSUPPORTED,
                               constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.MOST_LIKELY, constants.MOST_LIKELY, constants.LIKELY, constants.UNSUPPORTED, constants.UNSUPPORTED,
                               constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.VERY_LIKELY, constants.VERY_LIKELY, constants.MOST_LIKELY, constants.LIKELY, constants.UNSUPPORTED,
                               constants.UNSUPPORTED, constants.UNSUPPORTED],
                              [constants.ALMOST_TRUE, constants.ALMOST_TRUE, constants.VERY_LIKELY, constants.MOST_LIKELY, constants.LIKELY, constants.UNSUPPORTED,
                               constants.UNSUPPORTED],
                              [constants.TRUE, constants.ALMOST_TRUE, constants.VERY_LIKELY, constants.MOST_LIKELY, constants.LIKELY, constants.UNLIKELY,
                               constants.UNSUPPORTED]]
        probabilities, weights = self.weight_definition()
        row_index = probabilities[probatory_weight_fav]
        column_index = probabilities[probatory_weight_unfav]
        return probability_matrix[row_index][column_index]

    def calculate_evidential_weight(self, constants: Constants = Provide[Container.constants]):
        """
        Calculates this hypothesis's evidential weight based on its associated facts
        """
        fav_weights = []
        unfav_weights = []
        probabilities, weights = self.weight_definition()
        for fav in self.fav_facts:
            if not fav.ignored:
                fav_weights.append(weights[min(probabilities[fav.calculate_evidential_weight()], probabilities[fav.relevance])])
        for unfav in self.unfav_facts:
            if not unfav.ignored:
                unfav_weights.append(weights[min(probabilities[unfav.calculate_evidential_weight()], probabilities[unfav.relevance])])
        try:
            if (len(fav_weights) != 0) and (len(unfav_weights) == 0):  # there are facts in favor and not against
                if len(fav_weights) == 1:  # there is only one fact in favor
                    probatory_weight = fav_weights[0]
                else:  # there is more than one fact in favor
                    probatory_weight = weights[max([probabilities[fav] for fav in fav_weights])]
            elif (len(unfav_weights) != 0) and (len(fav_weights) == 0):  # there are only facts against
                probatory_weight = constants.UNSUPPORTED
            else:  # there are facts in favor and against
                total_weight_fav = weights[max([probabilities[fav] for fav in fav_weights])]
                total_weight_unfav = weights[max([probabilities[unfav] for unfav in unfav_weights])]
                probatory_weight = self.probability_balance(total_weight_fav, total_weight_unfav)
            self.probatory_weight = probatory_weight
            return probatory_weight
        except ValueError:
            raise HypothesisException(self)

    def accept(self, visitor):
        visitor.visit(self)


class Case(Document):
    name = StringField(required=True)
    claimant = StringField(required=True)
    defendant = StringField(required=True)
    radicado = StringField(required=True, regex="\\d{25}")
    subsidiary_pretensions = StringField()
    pretense = EmbeddedDocumentField(Hypothesis)
    evidence_counter = IntField(default=0)
    meta = {'collection': 'cases'}

    def __init__(self,  *args, **kwargs):
        Document.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = ObjectId()

    def clone(self):
        cloned_object: Case = deepcopy(self)
        cloned_object.id = ObjectId()
        return cloned_object


class CheckerVisitor(metaclass=ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'visit') and
                callable(subclass.visit) or
                NotImplemented)

    @dispatch(Evidence)
    def visit(self, element: Evidence):
        raise NotImplementedError

    @dispatch(Fact)
    def visit(self, element: Fact):
        raise NotImplementedError

    @dispatch(Hypothesis)
    def visit(self, element: Hypothesis):
        raise NotImplementedError


class ModelChecker(CheckerVisitor):

    def __init__(self, constants: Constants = Provide[Container.constants]):
        super(ModelChecker).__init__()
        self.pending_items = list()
        self.constants = constants

    @dispatch(Evidence)
    def visit(self, element: Evidence):
        if not element.relevance:
            text = self.constants.RELEVANCE_OF_THE_EVIDENCE
            item = (f"{text} \"{element.label}\"", element.name)
            self.pending_items.append(item)
        if not element.credibility:
            text = self.constants.CREDIBILITY_OF_THE_EVIDENCE
            item = (f"{text} \"{element.label}\"", element.name)
            self.pending_items.append(item)

    @dispatch(Fact)
    def visit(self, element: Fact):
        for sub_fact in element.fav_facts:
            sub_fact.accept(self)

        for sub_fact in element.unfav_facts:
            sub_fact.accept(self)

        for evidence in element.fav_evidence:
            evidence.accept(self)

        for evidence in element.unfav_evidence:
            evidence.accept(self)

        if not element.relevance:
            text = self.constants.RELEVANCE_OF_THE_FACT
            item = (f"{text} \"{element.label}\"", element.name)
            self.pending_items.append(item)

    @dispatch(Hypothesis)
    def visit(self, element: Hypothesis):
        for fact in element.fav_facts:
            fact.accept(self)

        for fact in element.unfav_facts:
            fact.accept(self)
