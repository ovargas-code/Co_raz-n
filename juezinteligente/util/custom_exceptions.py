
class ProbatoryWeightException(Exception):

    def __init__(self, fact, message):
        self.fact = fact
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return (self.message + str(self.fact.label))


class FactException(ProbatoryWeightException):
    """Raised when there is an exception for the fact"""

    def __init__(self, fact, message='Debe agregar al menos una prueba o sub-hecho favorable no ignorado para '):
        self.fact = fact
        self.message = message
        super().__init__(self.fact, self.message)

    def __str__(self):
        return (self.message + str(self.fact.label))

class FactRelevanceException(ProbatoryWeightException):
    """Raised when there is an exception for the fact relevance"""

    def __init__(self, fact, message='Falta el valor de relevancia para '):
        self.fact = fact
        self.message = message
        super().__init__(self.fact, self.message)

    def __str__(self):
        return (self.message + str(self.fact.label))



class EvidenceException(ProbatoryWeightException):
    """Raised when there is an exception for the evidence"""

    def __init__(self, fact, message='Hay un dato faltante para el cálculo del peso probatorio de: '):
        self.fact = fact
        self.message = message
        super().__init__(self.fact, self.message)

    def __str__(self):
        if self.fact.relevance:
            return('Falta el valor de crédibilidad para la prueba {}'.format(self.fact.label))
        elif self.fact.credibility:
            return('Falta el valor de pertinencia para la prueba {}'.format(self.fact.label))
        else:
            return('Faltan los valores de pertinencia y credibilidad para la prueba {}'.format(self.fact.label))

class HypothesisException(ProbatoryWeightException):

    def __init__(self, fact, message='Debe agregar al menos un hecho que no esté ignorado a la pretensión '):
        self.fact = fact
        self.message = message
        super().__init__(self.fact, self.message)

    def __str__(self):
        return(self.message + self.fact.label)


