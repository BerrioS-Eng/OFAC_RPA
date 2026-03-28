import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    """"""
    candidates: list = field(default_factory= list)
    incompletes: list = field(default_factory= list)
    not_cross: list = field(default_factory= list)
    not_consult: list = field(default_factory= list)


def classify_persons(registers):
    """"""
    result = ClassificationResult()

    for reg in registers:
        if not reg["cruzaConMaestra"]:
            result.not_cross.append(reg)
        
        elif reg["direccion"] is None or reg["pais"] is None:
            result.incompletes.append(reg)

        elif reg["aConsultar"] == "No":
            result.not_consult.append(reg)

        else:
            result.candidates.append(reg)
    
    logger.info(
        "Classification made: ",
        f"{len(result.candidates)} web process candidates",
        f"{len(result.incompletes)} incomplete information",
        f"{len(result.not_cross)} they do not cross with MaestraDetallePersonas"
    )

    return result

