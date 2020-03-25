from CodeParser.ParserType import ParserType

SUPPORTED_FILE_TYPES = {"C": [r"c", r"cpp", r"h"]}

# Note: the first added parser is the default one.
try:
    from CodeParser.Cscope import Cscope
except Exception:
    pass
else:
    ParserType.addType("Cscope", Cscope)


__all__ = ["ParserType"]
