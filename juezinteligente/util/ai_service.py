import logging
from typing import List, Optional, Callable
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from juezinteligente.model.judge import Case, Hypothesis, Fact, Evidence

logger = logging.getLogger(__name__)

# Define Pydantic models for Structured Output (Flat Representation to avoid RecursionError in google-genai SDK)
class EvidenceJson(BaseModel):
    label: str = Field(description="Etiqueta muy corta de la prueba (máx 50 caracteres). Ejemplo: 'Testimonio de Juan'")
    type: str = Field(description="Tipo de prueba. Debe ser uno de los tipos permitidos.")
    desc: str = Field(description="Descripción detallada de la prueba en el texto.")
    favorability: bool = Field(description="True si la prueba apoya el hecho, False si lo contradice o refuta.")
    relevance: Optional[str] = Field(None, description="Relevancia asignada a la prueba. Debe ser uno de los permitidos.")

class FactJson(BaseModel):
    id: str = Field(description="Identificador único para este hecho (por ejemplo: 'H1', 'H2', 'H1.1', 'H1.2', 'H1.1.1'). Usa formato jerárquico con puntos para denotar subordinación.")
    label: str = Field(description="Etiqueta muy corta del hecho (hecho principal o secundario) (máx 50 caracteres). Ejemplo: 'Firma de contrato'")
    desc: str = Field(description="Descripción detallada del hecho.")
    source: str = Field(description="Origen o proponente del hecho: 'demandante' si proviene de la demanda (apoya la pretensión), 'demandado' si proviene de la contestación (refuta o se opone a la pretensión).")
    favorability: bool = Field(description="True si el hecho apoya a su elemento padre (la pretensión u otro hecho), False si lo contradice. Para hechos principales (parent_id = null): si source es 'demandante' debe ser True, si es 'demandado' debe ser False.")
    relevance: Optional[str] = Field(None, description="Relevancia asignada al hecho. Debe ser uno de los permitidos.")
    parent_id: Optional[str] = Field(None, description="El identificador (id) del hecho padre al cual este hecho está subordinado. Debe ser null/None para hechos principales que se derivan directamente de la pretensión.")
    evidence: List[EvidenceJson] = Field(default_factory=list, description="Pruebas asociadas a este hecho en particular.")

class PretenseJson(BaseModel):
    label: str = Field(description="Etiqueta muy corta de la pretensión principal (máx 50 caracteres). Ejemplo: 'Declarar incumplimiento'")
    desc: str = Field(description="Descripción detallada de la pretensión.")
    facts: List[FactJson] = Field(description="Lista plana de todos los hechos y subhechos correspondientes. Usa parent_id para enlazar subhechos con sus hechos padres.")

class CaseJson(BaseModel):
    case_name: str = Field(description="Nombre descriptivo para el caso/proceso judicial.")
    claimant: str = Field(description="Nombre completo del demandante.")
    defendant: str = Field(description="Nombre completo del demandado.")
    radicado: str = Field(description="Número de radicado (debe tener exactamente 25 dígitos numéricos). Si no se encuentra completo, autocompletar con ceros hasta 25 dígitos.")
    subsidiary_pretensions: Optional[str] = Field(None, description="Pretensiones subsidiarias, acumulativas o alternativas si las hay.")
    pretense: PretenseJson = Field(description="La pretensión principal (Hipótesis central del caso).")


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto de un archivo PDF usando pypdf."""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def parse_lawsuit_with_gemini(
    demanda_text: str,
    contestacion_text: str,
    api_key: str,
    allowed_probabilities: List[str],
    allowed_evidence_types: List[str],
    status_callback: Optional[Callable[[str], None]] = None
) -> dict:
    """Envía los textos judiciales a Gemini y retorna el JSON estructurado con política de reintentos."""
    client = genai.Client(api_key=api_key)
    
    if contestacion_text.strip():
        system_instruction = (
            "Eres un analista legal experto y juez inteligente. Tu tarea es analizar dos textos del mismo proceso judicial: "
            "el texto de la DEMANDA y el texto de la CONTESTACIÓN. Tu objetivo es comparar ambos textos y extraer "
            "de forma estructurada únicamente los HECHOS CONTROVERTIDOS (aquellos hechos que una de las partes afirma y "
            "la otra niega, contradice o discute; es decir, en los que no están de acuerdo).\n"
            "Reglas críticas:\n"
            "1. NO incluyas hechos pacíficos o admitidos por ambas partes.\n"
            "2. Identifica el origen del hecho en el campo 'source': 'demandante' si el hecho proviene de la demanda (y es discutido por el demandado), "
            "o 'demandado' si el hecho proviene de la contestación (y es discutido por el demandante).\n"
            "3. Para los hechos principales (parent_id = null): si el hecho es del 'demandante', debe ser favorable a la pretensión (favorability: True). "
            "Si el hecho es del 'demandado', debe ser desfavorable a la pretensión (favorability: False).\n"
            "4. Para los subhechos (parent_id != null) y pruebas (evidence): dado que apoyan a su respectivo elemento padre, su favorabilidad siempre debe ser True.\n"
            "5. En las pruebas (evidence), NO asignes valor al campo de credibilidad (no existe en el esquema). Para la relevancia (relevance), "
            f"elige EXCLUSIVAMENTE uno de estos valores: {allowed_probabilities}.\n"
            f"6. Para el campo 'type' en las pruebas, debes elegir EXCLUSIVAMENTE uno de estos valores: {allowed_evidence_types}.\n"
            "7. El campo 'radicado' debe ser un string numérico de exactamente 25 dígitos (autocompleta con ceros si es necesario).\n"
            "8. Organiza los hechos de forma jerárquica plana usando 'id' (ej: 'H1', 'H1.1') y 'parent_id' para enlazarlos."
        )
        
        prompt = (
            "Analiza y compara detalladamente el texto de la demanda y de la contestación adjuntos a continuación. "
            "Extrae únicamente los hechos controvertidos y genera la estructura del caso en formato JSON según el esquema:\n\n"
            "=== TEXTO DE LA DEMANDA ===\n"
            f"{demanda_text}\n\n"
            "=== TEXTO DE LA CONTESTACIÓN ===\n"
            f"{contestacion_text}\n"
        )
    else:
        system_instruction = (
            "Eres un analista legal experto y juez inteligente. Tu tarea es analizar el texto de una demanda judicial "
            "y extraer de forma estructurada los datos del proceso, la pretensión principal, los hechos que la sustentan y las pruebas aportadas.\n"
            "Reglas críticas:\n"
            "1. Identifica el origen de los hechos siempre como 'demandante' en el campo 'source'.\n"
            "2. Todos los hechos y subhechos deben ser favorables a la pretensión o a su hecho padre (favorability: True).\n"
            "3. Todas las pruebas deben apoyar a su hecho correspondiente (favorability: True).\n"
            "4. En las pruebas (evidence), NO asignes valor al campo de credibilidad (no existe en el esquema). Para la relevancia (relevance), "
            f"elige EXCLUSIVAMENTE uno de estos valores: {allowed_probabilities}.\n"
            f"5. Para el campo 'type' en las pruebas, debes elegir EXCLUSIVAMENTE uno de estos valores: {allowed_evidence_types}.\n"
            "6. El campo 'radicado' debe ser un string numérico de exactamente 25 dígitos (autocompleta con ceros si es necesario).\n"
            "7. Organiza los hechos de forma jerárquica plana usando 'id' (ej: 'H1', 'H1.1') y 'parent_id' para enlazarlos."
        )
        
        prompt = (
            "Analiza el siguiente texto de demanda y genera la estructura del caso en formato JSON según el esquema:\n\n"
            f"{demanda_text}"
        )
    
    import time
    import random
    import json
    
    max_retries = 5
    base_delay = 2.0
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CaseJson,
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            return json.loads(response.text)
        except Exception as e:
            err_msg = str(e)
            # Determinar si el error es transitorio (ej: 503 ocupado, rate limit, quota, etc.)
            is_transient = any(term in err_msg.lower() for term in [
                "503", "unavailable", "rate limit", "quota", "exhausted", 
                "capacity", "timeout", "resource_exhausted", "temporary"
            ])
            
            if not is_transient or attempt == max_retries - 1:
                logger.error(f"Error definitivo llamando a Gemini: {err_msg}")
                raise e
            
            sleep_time = (base_delay * (2 ** attempt)) + random.uniform(0.1, 1.0)
            retry_msg = f"API ocupada (503). Reintentando en {sleep_time:.1f}s (intento {attempt+1}/{max_retries})..."
            logger.warning(retry_msg)
            if status_callback:
                status_callback(retry_msg)
            time.sleep(sleep_time)



def build_case_from_json(data: dict) -> Case:
    """Construye un objeto Case de mongoengine a partir de la representación plana JSON extraída."""
    pretense_data = data['pretense']
    pretense = Hypothesis(name="P", label=pretense_data['label'], desc=pretense_data['desc'])
    
    case = Case(
        name=data['case_name'],
        claimant=data['claimant'],
        defendant=data['defendant'],
        radicado=data['radicado'],
        subsidiary_pretensions=data.get('subsidiary_pretensions', ''),
        pretense=pretense
    )
    
    evidence_counter = 0
    
    # Store all facts by their JSON id to easily look up parents and sort by depth
    facts_list = pretense_data.get('facts', [])
    facts_dict = {fact['id']: fact for fact in facts_list if 'id' in fact}
    
    def get_depth(fact):
        depth = 0
        current = fact
        for _ in range(20):  # limit to avoid cycles
            p_id = current.get('parent_id')
            if not p_id or p_id not in facts_dict:
                break
            depth += 1
            current = facts_dict[p_id]
        return depth

    # Sort facts by depth so parents are processed and created before their children
    sorted_facts = sorted(facts_list, key=get_depth)
    
    # Keep track of created Fact mongoengine nodes mapped to their JSON id
    created_nodes = {}
    
    for fact_item in sorted_facts:
        f_id = fact_item.get('id')
        label = fact_item['label']
        desc = fact_item['desc']
        source = fact_item.get('source', 'demandante')
        parent_id = fact_item.get('parent_id')
        
        # Programmatically enforce favorability:
        # 1. Main facts (direct children of pretense, parent_id is None):
        #    If source is 'demandado' -> unfavorable (False)
        #    If source is 'demandante' -> favorable (True)
        # 2. Sub-facts (parent_id is not None) always support their parent fact -> True
        if not parent_id:
            fav = False if source == 'demandado' else True
        else:
            fav = True
            
        relevance = fact_item.get('relevance', None)
        
        # Decide parent node: either another Fact node or the root Hypothesis
        if parent_id and parent_id in created_nodes:
            parent_node = created_nodes[parent_id]
            fact_node = parent_node.add_sub_fact(label, desc, favorability=fav, relevance=relevance)
        else:
            fact_node = pretense.add_fact(label, desc, favorability=fav, relevance=relevance)
            
        if f_id:
            created_nodes[f_id] = fact_node
            
        # Add associated evidence
        for ev_item in fact_item.get('evidence', []):
            evidence_counter += 1
            ev_label = ev_item['label']
            ev_type = ev_item['type']
            ev_desc = ev_item['desc']
            # All evidence from either party favors/supports their respective fact
            ev_fav = True
            ev_cred = None  # credibility is always None so user enters it manually
            ev_rel = ev_item.get('relevance', None)
            
            fact_node.add_evidence(
                number=evidence_counter,
                label=ev_label,
                desc=ev_desc,
                favorability=ev_fav,
                evidence_type=ev_type,
                credibility=ev_cred,
                relevance=ev_rel
            )
            
    case.evidence_counter = evidence_counter
    return case
