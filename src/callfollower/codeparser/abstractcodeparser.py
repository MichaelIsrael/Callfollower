from abc import ABC, abstractmethod
from pathlib import Path
import logging
import sys

positivier = 2 * (sys.maxsize + 1)


class CodeParserException(Exception):
    pass


class InvalidRootDirError(CodeParserException):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def __str__(self):
        return "'%s' is not a valid directory" % self.root_dir


class AbstractCodeParser(ABC):
    def __init__(self, root_dir=r"."):
        # Create base logger.
        _log = logging.getLogger("CallFollower.CodeParser")
        # Creating Path object.
        self._rootPath = Path(root_dir)
        _log.debug("Creating a CodeParser object at '%s'",
                   self._rootPath.resolve())
        # Make sure it is valid.
        if not self._rootPath.is_dir():
            _log.critical("'%s' is not a valid directory", root_dir)
            raise InvalidRootDirError(root_dir)
        # Create child logger.
        self.log = _log.getChild("%s.%s" % (self.__class__.__name__,
                                            self.getRootDir().name))

    def getRootDir(self):
        return self._rootPath.resolve()

    @abstractmethod
    def initialize(self):
        """ Initialize CodeParser (reading and checking preprocessing
            files, etc.)."""
        raise NotImplementedError

    @abstractmethod
    def getCaller(self, function):
        """ Return the caller(s) of a certain functions. """
        raise NotImplementedError

    @abstractmethod
    def getCalled(self, function):
        """ Return the function(s) called by a certain functions. """
        raise NotImplementedError

    @abstractmethod
    def getDefinition(self, function):
        """ Return the definition(s) of a certain functions. """
        raise NotImplementedError

    @abstractmethod
    def clean(self):
        """ Clean preprocessing files. """
        raise NotImplementedError

    @abstractmethod
    def preprocess(self):
        """ Preprocess source files. """
        raise NotImplementedError


class CodeDefinition:
    def __init__(self, Function, File, Line):
        self.log = logging.getLogger("CallFollower.CodeDefinition.%s" %
                                     Function)
        self._name = Function
        self._file = Path(File)
        self._line = Line
        self._unique = hash(self) % positivier
        self.log.debug("Definition at %s:%d (Unique Id = %d).",
                       self._file, self._line, self._unique)

    def getName(self):
        return self._name

    def getLocation(self):
        return (self._file, self._line)

    def getFullName(self):
        return '{}-{}:\n{}'.format(self._file.name, self._line, self._name)

    def __hash__(self):
        return hash((self._file, self._line))

    def getUniqueId(self):
        return self._unique
