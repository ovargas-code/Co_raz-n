from abc import ABCMeta, abstractmethod
from copy import deepcopy
from enum import Enum, unique, auto

from PySide2.QtCore import QObject, QLocale, Signal, QThread, QSettings
from bson.objectid import ObjectId

class MainThreadNotifier(QObject):
    notify_signal = Signal(object)

    def __init__(self):
        super().__init__()

_notifier = MainThreadNotifier()
_notifier.notify_signal.connect(lambda func: func())
from dependency_injector.wiring import Provide
from multipledispatch import dispatch
from mongoengine import Document, StringField, EmbeddedDocument, ListField, EmbeddedDocumentField, IntField, \
    FloatField, BooleanField

from co_razon.ui.constants import Constants
from co_razon.util.containers import Container
from co_razon.util.custom_exceptions import EvidenceException, FactException, FactRelevanceException, \
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
        self._rule_cache = None
        self._cached_inputs = None
        self._fetching = False

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
        prob_dict = {}
        for weight, probability in enumerate(probabilities):
            p_str = str(probability)
            prob_dict[probability] = weight
            prob_dict[p_str] = weight
            prob_dict[p_str.lower()] = weight

        # Standard English keys for fallback/database compatibility
        english_mapping = {
            'unsupported': 0, 'unlikely': 1, 'likely': 2, 'most likely': 3,
            'very likely': 4, 'almost true': 5, 'true': 6,
            'impertinent': 0, 'pertinent': 6, 'irrelevant': 0, 'relevant': 6
        }
        for k, v in english_mapping.items():
            prob_dict[k] = v
            prob_dict[k.capitalize()] = v
            if ' ' in k:
                cap_k = ' '.join([p.capitalize() for p in k.split(' ')])
                prob_dict[cap_k] = v

        if constants:
            for item, val in [(constants.IMPERTINENT, 0), (constants.PERTINENT, 6),
                              (constants.IRRELEVANT, 0), (constants.RELEVANT, 6)]:
                prob_dict[item] = val
                prob_dict[str(item)] = val
                prob_dict[str(item).lower()] = val

        weight_dict = {weight: probability for weight, probability in enumerate(probabilities)}
        return prob_dict, weight_dict

    def generate_experience_rule(self, constants: Constants = Provide[Container.constants]):
        """
        This method generates a string with the experience rule for this evidence in relation with its fact(parent)
        """
        p_doc = self.parent_doc if self._instance is None else self._instance
        if not p_doc:
            return ""

        locale = QLocale.system().name()
        if not locale.startswith("es"):
            # Maintain original English template for compatibility/tests
            if self in p_doc.unfav_evidence:
                consequent = f"{constants.DENIAL_OF_THE_FACT_THAT} {p_doc.label}"
            else:
                consequent = f"{constants.THE_FACT_THAT} {p_doc.label}"

            probability = "_________" if self.relevance is None else self.relevance
            rule = f"{constants.IF_THE_EVIDENCE} {self.label} {constants.IS_TRUE_THEN_IS} {probability} {consequent}"
            return rule

        # Spanish rule generation logic (AI + local fallback template)
        relevance_str = self.relevance
        if not relevance_str:
            relevance_str = str(constants.PERTINENT) if constants else "Pertinent"
        else:
            relevance_str = str(relevance_str)

        inputs = (self.label, relevance_str, p_doc.label)

        # Reset fetching and cache if inputs change
        if getattr(self, "_cached_inputs", None) != inputs:
            self._fetching = False
            self._rule_cache = None

        # Check cache
        if getattr(self, "_cached_inputs", None) == inputs and getattr(self, "_rule_cache", None):
            return self._rule_cache

        # Fallback template logic in Spanish
        ev_label_clean = self.label
        if ev_label_clean and len(ev_label_clean) > 1 and ev_label_clean[0].isupper() and ev_label_clean[1].islower():
            ev_label_clean = ev_label_clean[0].lower() + ev_label_clean[1:]

        is_impertinent = (
            relevance_str.lower() in ("impertinente", "impertinent")
            or (constants and relevance_str.lower() == str(constants.IMPERTINENT).lower())
        )
        if is_impertinent:
            fallback = f"Si la prueba de {ev_label_clean} no hace más o menos probable el hecho que {p_doc.label}, entonces esta prueba es impertinente."
        else:
            fallback = f"Si la prueba de {ev_label_clean} hace más o menos probable el hecho que {p_doc.label}, entonces esta prueba es pertinente."

        # Fetch API key
        settings = QSettings("Orion", "CoRazon")
        api_key = settings.value("gemini_api_key", "")

        # Try to trigger background async fetch
        if api_key and not getattr(self, "_fetching", False):
            self._fetching = True
            self._cached_inputs = inputs
            self._rule_cache = fallback  # Show fallback while loading

            class RuleWorker(QThread):
                finished_signal = Signal(str)

                def __init__(self, api_key_val, ev_label, fact_label, rel_str, fallback_val):
                    super().__init__()
                    self.api_key = api_key_val
                    self.ev_label = ev_label
                    self.fact_label = fact_label
                    self.rel_str = rel_str
                    self.fallback = fallback_val

                def run(self):
                    try:
                        from google import genai
                        from google.genai import types

                        client = genai.Client(api_key=self.api_key)
                        prompt = f"""
Ajusta gramaticalmente la siguiente regla de la experiencia en español para que suene natural, fluida y con excelente redacción jurídica.

La regla de la experiencia debe relacionar una prueba con un hecho.
- La prueba es: "{self.ev_label}"
- El hecho es: "{self.fact_label}"
- La relevancia es: "{self.rel_str}" (pertinente o impertinente)

Estructuras requeridas:
1. Si la relevancia es pertinente (o por defecto si no está especificada):
"Si la prueba de [prueba] hace más o menos probable el hecho que [hecho], entonces esta prueba es pertinente."

2. Si la relevancia es impertinente:
"Si la prueba de [prueba] no hace más o menos probable el hecho que [hecho], entonces esta prueba es impertinente."

Ajusta la concordancia y los artículos necesarios en la parte de "[prueba]" y "[hecho]" para que la oración final sea una sola frase fluida y gramaticalmente perfecta en español. No agregues explicaciones, notas, ni formateo Markdown. Devuelve únicamente la frase final resultante.
"""
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.1
                            )
                        )
                        result = response.text.strip()
                        if result:
                            if result.startswith('"') and result.endswith('"'):
                                result = result[1:-1].strip()
                            self.finished_signal.emit(result)
                        else:
                            self.finished_signal.emit(self.fallback)
                    except Exception:
                        self.finished_signal.emit(self.fallback)

            self._worker = RuleWorker(api_key, self.label, p_doc.label, relevance_str, fallback)

            def on_finished(result):
                # Discard results if inputs changed while fetching
                if getattr(self, "_cached_inputs", None) == inputs:
                    self._rule_cache = result
                    self._fetching = False
                    _notifier.notify_signal.emit(self.notify)

            self._worker.finished_signal.connect(on_finished)
            self._worker.start()

        return getattr(self, "_rule_cache", None) or fallback

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
        self._rule_cache = None
        self._cached_inputs = None
        self._fetching = False

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
        prob_dict = {}
        for weight, probability in enumerate(probabilities):
            p_str = str(probability)
            prob_dict[probability] = weight
            prob_dict[p_str] = weight
            prob_dict[p_str.lower()] = weight

        # Standard English keys for fallback/database compatibility
        english_mapping = {
            'unsupported': 0, 'unlikely': 1, 'likely': 2, 'most likely': 3,
            'very likely': 4, 'almost true': 5, 'true': 6,
            'impertinent': 0, 'pertinent': 6, 'irrelevant': 0, 'relevant': 6
        }
        for k, v in english_mapping.items():
            prob_dict[k] = v
            prob_dict[k.capitalize()] = v
            if ' ' in k:
                cap_k = ' '.join([p.capitalize() for p in k.split(' ')])
                prob_dict[cap_k] = v

        if constants:
            for item, val in [(constants.IMPERTINENT, 0), (constants.PERTINENT, 6),
                              (constants.IRRELEVANT, 0), (constants.RELEVANT, 6)]:
                prob_dict[item] = val
                prob_dict[str(item)] = val
                prob_dict[str(item).lower()] = val

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
        if not p_doc:
            return ""

        parent_type = constants.FACT if isinstance(p_doc, Fact) else constants.PRETENSION

        locale = QLocale.system().name()
        if not locale.startswith("es"):
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
            rule = f"{constants.IF_THE_FACT_THAT} {self.label} {constants.IS_TRUE_THEN_IS} {probability} {consequent}"
            return rule

        # Spanish rule generation logic (AI + local fallback template)
        relevance_str = self.relevance
        if not relevance_str:
            relevance_str = str(constants.RELEVANT) if constants else "Relevant"
        else:
            relevance_str = str(relevance_str)

        parent_type_es = "el hecho" if isinstance(p_doc, Fact) else "la pretensión"
        inputs = (self.label, relevance_str, p_doc.label)

        # Reset fetching and cache if inputs change
        if getattr(self, "_cached_inputs", None) != inputs:
            self._fetching = False
            self._rule_cache = None

        # Check cache
        if getattr(self, "_cached_inputs", None) == inputs and getattr(self, "_rule_cache", None):
            return self._rule_cache

        # Fallback template logic in Spanish
        fact_label_clean = self.label
        if fact_label_clean and len(fact_label_clean) > 1 and fact_label_clean[0].isupper() and fact_label_clean[1].islower():
            fact_label_clean = fact_label_clean[0].lower() + fact_label_clean[1:]

        # parent_type is "el hecho" or "la pretensión" in Spanish
        is_irrelevant = (
            relevance_str.lower() in ("irrelevante", "irrelevant")
            or (constants and relevance_str.lower() == str(constants.IRRELEVANT).lower())
        )
        if is_irrelevant:
            fallback = f"Si el hecho que {fact_label_clean} no hace más o menos probable {parent_type_es} que {p_doc.label}, entonces el hecho es irrelevante."
        else:
            fallback = f"Si el hecho que {fact_label_clean} hace más o menos probable {parent_type_es} que {p_doc.label}, entonces el hecho es relevante."

        # Fetch API key
        settings = QSettings("Orion", "CoRazon")
        api_key = settings.value("gemini_api_key", "")

        # Try to trigger background async fetch
        if api_key and not getattr(self, "_fetching", False):
            self._fetching = True
            self._cached_inputs = inputs
            self._rule_cache = fallback  # Show fallback while loading

            class FactRuleWorker(QThread):
                finished_signal = Signal(str)

                def __init__(self, api_key_val, fact_label, parent_label, parent_type_str, rel_str, fallback_val):
                    super().__init__()
                    self.api_key = api_key_val
                    self.fact_label = fact_label
                    self.parent_label = parent_label
                    self.parent_type = parent_type_str
                    self.rel_str = rel_str
                    self.fallback = fallback_val

                def run(self):
                    try:
                        from google import genai
                        from google.genai import types

                        client = genai.Client(api_key=self.api_key)
                        prompt = f"""
Ajusta gramaticalmente la siguiente regla de la experiencia en español para que suene natural, fluida y con excelente redacción jurídica.

La regla de la experiencia debe relacionar un hecho secundario (o prueba indiciaria) con un hecho principal (o pretensión).
- El hecho secundario es: "{self.fact_label}"
- El hecho principal/pretensión es: "{self.parent_label}"
- La relación es con: "{self.parent_type}" (la pretensión o el hecho)
- La relevancia es: "{self.rel_str}" (relevante o irrelevante)

Estructuras requeridas:
1. Si la relevancia es relevante (o por defecto si no está especificada):
"Si el hecho que [hecho secundario] hace más o menos probable [la pretensión / el hecho] que [hecho principal], entonces el hecho es relevante."

2. Si la relevancia es irrelevante:
"Si el hecho que [hecho secundario] no hace más o menos probable [la pretensión / el hecho] que [hecho principal], entonces el hecho es irrelevante."

Ajusta la concordancia y los artículos necesarios en la parte de "[hecho secundario]", "[la pretensión / el hecho]" y "[hecho principal]" para que la oración final sea una sola frase fluida y gramaticalmente perfecta en español. No agregues explicaciones, notas, ni formateo Markdown. Devuelve únicamente la frase final resultante.
"""
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.1
                            )
                        )
                        result = response.text.strip()
                        if result:
                            if result.startswith('"') and result.endswith('"'):
                                result = result[1:-1].strip()
                            self.finished_signal.emit(result)
                        else:
                            self.finished_signal.emit(self.fallback)
                    except Exception:
                        self.finished_signal.emit(self.fallback)

            self._worker = FactRuleWorker(api_key, self.label, p_doc.label, parent_type_es, relevance_str, fallback)

            def on_finished(result):
                # Discard results if inputs changed while fetching
                if getattr(self, "_cached_inputs", None) == inputs:
                    self._rule_cache = result
                    self._fetching = False
                    _notifier.notify_signal.emit(self.notify)

            self._worker.finished_signal.connect(on_finished)
            self._worker.start()

        return getattr(self, "_rule_cache", None) or fallback

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
        prob_dict = {}
        for weight, probability in enumerate(probabilities):
            p_str = str(probability)
            prob_dict[probability] = weight
            prob_dict[p_str] = weight
            prob_dict[p_str.lower()] = weight

        # Standard English keys for fallback/database compatibility
        english_mapping = {
            'unsupported': 0, 'unlikely': 1, 'likely': 2, 'most likely': 3,
            'very likely': 4, 'almost true': 5, 'true': 6,
            'impertinent': 0, 'pertinent': 6, 'irrelevant': 0, 'relevant': 6
        }
        for k, v in english_mapping.items():
            prob_dict[k] = v
            prob_dict[k.capitalize()] = v
            if ' ' in k:
                cap_k = ' '.join([p.capitalize() for p in k.split(' ')])
                prob_dict[cap_k] = v

        if constants:
            for item, val in [(constants.IMPERTINENT, 0), (constants.PERTINENT, 6),
                              (constants.IRRELEVANT, 0), (constants.RELEVANT, 6)]:
                prob_dict[item] = val
                prob_dict[str(item)] = val
                prob_dict[str(item).lower()] = val

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
