__all__ = ["ParserType"]
__author__ = "Michael Israel"


from .parsertype import ParserType
import logging


SUPPORTED_FILE_TYPES = {
    "C": [r"c", r"h"],
    "CPP": [r"c", r"cpp", r"cxx", r"h", r"hpp", r"hxx"],
    }

__logger = logging.getLogger("CallFollower.CodeParser")

# Note: the first added parser is the default one.
__logger.debug("Importing Cscope")
try:
    from .cscope import Cscope
except Exception as e:
    __logger.warning("Failed to import Cscope: {}".format(e))
else:
    ParserType.addType("Cscope", Cscope)
