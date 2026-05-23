from enum import auto, Enum, unique

from PySide2.QtCore import QObject


class Constants(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.GENERATE_REPORT = self.tr("Generate report")
        self.FORM_TEXT_MSG = self.tr("You must enter all form mandatory fields")
        self.OPEN_CASE_TEXT_MSG = self.tr("You must select a case to be opened")
        self.PROPERTIES_VIEW = self.tr("Properties view")
        self.HYPOTHESIS_PROPERTIES = self.tr("Hypothesis properties")
        self.SUBSIDIARY_HYPO_PLACEHOLDER = self.tr("Optional\n\n"
                                                   "1. Consequential or successive\n"
                                                   "2. Eventual\n"
                                                   "3. Alternative")
        self.FACT_PROPERTIES = self.tr("Fact properties")
        self.EVIDENCE_PROPERTIES = self.tr("Evidence properties")
        self.CHECK_LIST = self.tr("Check list")
        self.CLOSE_CASE = self.tr("Close case")
        self.WANT_TO_SAVE_CASE = self.tr("Do you want to save the changes before closing the case?")
        self.MISSING_ITEMS = self.tr("missing items")
        self.MISSING_ITEM = self.tr("missing item")
        self.SMART_JUDGE = self.tr("Smart Judge")
        self.FILE_MENU = self.tr("&File")
        self.VIEW_MENU = self.tr("&View")
        self.NEW_PROCESS_ACTION = self.tr("&New process")
        self.NEW_PROCESS_ACTION_STATUS = self.tr("Create a new process")
        self.OPEN_PROCESS_ACTION = self.tr("&Open process")
        self.OPEN_PROCESS_ACTION_STATUS = self.tr("Open a process froM the repository")
        self.SAVE_ACTION = self.tr("&Save")
        self.SAVE_ACTION_STATUS = self.tr("Save changes of active process")
        self.SAVE_AS_ACTION = self.tr("Save &as")
        self.SAVE_AS_ACTION_STATUS = self.tr("Save a copy of the active process")
        self.CLOSE_ACTION = self.tr("&Close process")
        self.CLOSE_ACTION_STATUS = self.tr("Close the active process")
        self.MANAGE_PROCESSES = self.tr("Manage processes")
        self.MANAGE_PROCESSES_ACTION_STATUS = self.tr("Manage processes in the repository")
        self.EXIT_ACTION = self.tr("E&xit")
        self.EXIT_ACTION_STATUS = self.tr("Exit application")
        self.PROPERTIES_VIEW_ACTION = self.tr("&Properties view")
        self.CHECK_LIST_ACTION = self.tr("&Check list")
        self.AUTO_LAYOUT_ACTION = self.tr("&Auto-adjust graph")
        self.AUTO_LAYOUT_ACTION_STATUS = self.tr("Automatically layout nodes to avoid overlaps")
        self.CASE = self.tr("Case")
        self.SUCCESSFULLY_SAVED = self.tr("successfully saved")
        self.NO_CASE_TO_SAVE = self.tr("There is no active case to save")
        self.SAVE_AS = self.tr("Save case as")
        self.NAME_FOR_NEW_CASE = self.tr("Name for the new case")
        self.CONFIRMATION = self.tr("Confirmation")
        self.SURE_TO_DELETE_NODE = self.tr("Are you sure you want to delete the node?")
        self.ALL_NODE_BE_DELETED = self.tr("All children nodes will be deleted")
        self.ERROR = self.tr("Error")
        self.PROBATORY_WEIGHT_ERROR = self.tr("Error calculating probatory weight")
        self.REPORT_SUCCESS = self.tr("Report was successfully generated")
        self.OPEN_PROCESS = self.tr("Open process")
        self.CREATED_ON = self.tr("created on")
        self.ADD_NEW_FACT = self.tr("Add new fact")
        self.ADD_NEW_EVIDENCE = self.tr("Add new evidence")
        self.ID = self.tr("ID")
        self.NAME = self.tr("Name")
        self.CREATION_DATE = self.tr("Creation date")
        self.IMPORT_CASES = self.tr("Import cases")
        self.WARNING = self.tr("Warning")
        self.ERRORS_IMPORTING = self.tr("There were errors importing cases:")
        self.INFORMATION = self.tr("Information")
        self.CASES_IMPORTED_SUCCESS = self.tr("Cases were successfully imported")
        self.EXPORT_CASES = self.tr("Export cases")
        self.CASES_EXPORTED_SUCCESS = self.tr("Cases were successfully exported")
        self.OPERATION_UNSUPPORTED = self.tr("Export operation not supported yet")
        self.AT_LEAST_ONE_CASE = self.tr("You must select at least one case")
        self.SURE_TO_DELETE_CASES = self.tr("Are you sure you want to delete selected cases?")
        self.TRUE = self.tr('True')
        self.ALMOST_TRUE = self.tr('Almost true')
        self.VERY_LIKELY = self.tr('Very likely')
        self.MOST_LIKELY = self.tr('Most likely')
        self.LIKELY = self.tr('Likely')
        self.UNLIKELY = self.tr('Unlikely')
        self.UNSUPPORTED = self.tr('Unsupported')
        self.IMPERTINENT = self.tr('Impertinent')
        self.PERTINENT = self.tr('Pertinent')
        self.IRRELEVANT = self.tr('Irrelevant')
        self.RELEVANT = self.tr('Relevant')
        self.DENIAL_OF_THE_FACT_THAT = self.tr('the denial of the fact that')
        self.THE_FACT_THAT = self.tr('the fact that')
        self.IF_THE_EVIDENCE = self.tr('If the evidence of')
        self.IS_TRUE_THEN_IS = self.tr('is true, then is')
        self.FACT = self.tr('the fact')
        self.PRETENSION = self.tr('the pretension')
        self.DENIAL_OF= self.tr('the denial of')
        self.THAT = self.tr('that')
        self.THE = self.tr('the')
        self.IF_THE_FACT_THAT = self.tr('If the fact that')
        self.RELEVANCE_OF_THE_EVIDENCE = self.tr('Relevance of the evidence')
        self.CREDIBILITY_OF_THE_EVIDENCE = self.tr('Credibility of the evidence')
        self.RELEVANCE_OF_THE_FACT = self.tr('Relevance of the fact')
        self.UNASSIGNED = self.tr('Unassigned')
        self.NOT_YET_CALCULATED = self.tr('Not yet calculated')
        self.PROBATORY_WEIGHT_LABEL = self.tr('Probatory weight')
        self.ADD_FACT = self.tr('Add fact')
        self.ADD_SUB_FACT = self.tr('Add sub fact')
        self.ADD_EVIDENCE = self.tr('Add evidence')
        self.CALCULATE_PROBATORY_WEIGHT = self.tr('Calculate probatory weight')
        self.PERTINENCE = self.tr('Pertinence')
        self.CREDIBILITY = self.tr('Credibility')
        self.RELEVANCE = self.tr('Relevance')
        self.IGNORE = self.tr('Ignore')
        self.DELETE = self.tr('Delete')


@unique
class EvidenceType(Enum):
    TESTIMONIAL = auto()
    DOCUMENTARY = auto()
    EXPERT = auto()
    CIRCUMSTANTIAL = auto()
    INFORM = auto()
    INSPECTION = auto()
    CONFESSION = auto()
    OATH = auto()

    @classmethod
    def list_values(cls):
        return list(map(lambda e: e.name.capitalize(), cls))


class EvidenceTypeRepr(QObject):

    def __init__(self, parent):
        super().__init__(parent)
        self.data = {
            EvidenceType.TESTIMONIAL: self.tr('Testimonial'),
            EvidenceType.DOCUMENTARY: self.tr('Documentary'),
            EvidenceType.EXPERT: self.tr('Expert'),
            EvidenceType.CIRCUMSTANTIAL: self.tr('Circumstantial'),
            EvidenceType.INFORM: self.tr('Inform'),
            EvidenceType.INSPECTION: self.tr('Inspection'),
            EvidenceType.CONFESSION: self.tr('Confession'),
            EvidenceType.OATH: self.tr('Oath')
        }

    def list_values(self):
        return self.data.values()