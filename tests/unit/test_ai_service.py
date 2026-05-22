import pytest
from juezinteligente.util.ai_service import build_case_from_json
from juezinteligente.model.judge import Case, Hypothesis, Fact, Evidence


def test_build_case_from_json():
    # Sample structured flat JSON data from Gemini (flat structure)
    sample_data = {
        "case_name": "Proceso de Simulación",
        "claimant": "Juan Perez",
        "defendant": "Maria Gomez",
        "radicado": "1100131030252026001230000",
        "subsidiary_pretensions": "Pretensión subsidiaria de enriquecimiento sin causa.",
        "pretense": {
            "label": "Simulación de contrato",
            "desc": "Declarar la simulación absoluta del contrato de compraventa.",
            "facts": [
                {
                    "id": "H1",
                    "label": "Falta de pago del precio",
                    "desc": "El comprador nunca transfirió la suma pactada.",
                    "source": "demandante",
                    "favorability": True,
                    "relevance": "Muy probable",
                    "parent_id": None,
                    "evidence": [
                        {
                            "label": "Testimonio de la tía",
                            "type": "Testimonial",
                            "desc": "Declaró que el comprador le confesó no haber pagado.",
                            "favorability": True,
                            "credibility": "Probable",
                            "relevance": "Probable"
                        }
                    ]
                },
                {
                    "id": "H1.1",
                    "label": "Comprador insolvente",
                    "desc": "El comprador no disponía de fondos en sus cuentas bancarias.",
                    "source": "demandante",
                    "favorability": True,
                    "relevance": "Probable",
                    "parent_id": "H1",
                    "evidence": [
                        {
                            "label": "Extracto bancario",
                            "type": "Documental",
                            "desc": "Extracto del banco que muestra saldo de cero pesos.",
                            "favorability": True,
                            "credibility": "Cierto",
                            "relevance": "Muy probable"
                        }
                    ]
                },
                {
                    "id": "H2",
                    "label": "Posesión conservada",
                    "desc": "El vendedor continuó habitando el inmueble.",
                    "source": "demandante",
                    "favorability": True,
                    "relevance": "Casi cierto",
                    "parent_id": None,
                    "evidence": [
                        {
                            "label": "Facturas de servicios públicos",
                            "type": "Documental",
                            "desc": "Facturas a nombre del vendedor pagadas recientemente.",
                            "favorability": True,
                            "credibility": "Cierto",
                            "relevance": "Muy probable"
                        }
                    ]
                },
                {
                    "id": "H3",
                    "label": "Transacción real",
                    "desc": "El negocio jurídico fue real y las partes quisieron obligarse.",
                    "source": "demandado",
                    "favorability": False,
                    "relevance": "Poco probable",
                    "parent_id": None,
                    "evidence": []
                }
            ]
        }
    }

    case = build_case_from_json(sample_data)

    # Assert basic metadata
    assert case.name == "Proceso de Simulación"
    assert case.claimant == "Juan Perez"
    assert case.defendant == "Maria Gomez"
    assert case.radicado == "1100131030252026001230000"
    assert case.subsidiary_pretensions == "Pretensión subsidiaria de enriquecimiento sin causa."

    # Assert pretense (Hypothesis)
    assert isinstance(case.pretense, Hypothesis)
    assert case.pretense.name == "P"
    assert case.pretense.label == "Simulación de contrato"
    assert case.pretense.desc == "Declarar la simulación absoluta del contrato de compraventa."

    # Assert facts grouping
    # Should have 2 favorable facts (facts[0], facts[2]) and 1 unfavorable (facts[3])
    # When sorted by depth, H1, H2, H3 are depth 0 and H1.1 is depth 1.
    assert len(case.pretense.fav_facts) == 2
    assert len(case.pretense.unfav_facts) == 1

    # Check names
    assert case.pretense.fav_facts[0].name == "H1"
    assert case.pretense.fav_facts[1].name == "H2"
    assert case.pretense.unfav_facts[0].name == "H3"

    # Check sub-fact
    fact_1 = case.pretense.fav_facts[0]
    assert len(fact_1.fav_facts) == 1
    sub_fact = fact_1.fav_facts[0]
    assert sub_fact.name == "H11"
    assert sub_fact.label == "Comprador insolvente"
    assert sub_fact.relevance == "Probable"

    # Check evidence counts and names
    # Evidence counts are stored in case.evidence_counter
    # H1 is processed -> evidence #1 (Testimonio de la tía) -> MP1
    # H2 is processed -> evidence #2 (Facturas) -> MP2
    # H1.1 is processed -> evidence #3 (Extracto bancario) -> MP3
    assert case.evidence_counter == 3

    # Check evidence on H1
    assert len(fact_1.fav_evidence) == 1
    ev_tia = fact_1.fav_evidence[0]
    assert ev_tia.name == "MP1"
    assert ev_tia.label == "Testimonio de la tía"
    assert ev_tia.type == "Testimonial"
    assert ev_tia.credibility is None
    assert ev_tia.relevance == "Probable"

    assert len(sub_fact.fav_evidence) == 1
    ev_extracto = sub_fact.fav_evidence[0]
    assert ev_extracto.name == "MP3"

    fact_2 = case.pretense.fav_facts[1]
    assert len(fact_2.fav_evidence) == 1
    ev_servicios = fact_2.fav_evidence[0]
    assert ev_servicios.name == "MP2"
