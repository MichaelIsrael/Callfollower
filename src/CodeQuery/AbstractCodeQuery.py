from abc import ABC, abstractmethod
from pathlib import Path
import logging
import sys

positivier = 2 * (sys.maxsize + 1)


class CodeQueryException(Exception):
    pass


class InvalidRootDirError(CodeQueryException):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def __str__(self):
        return "'%s' is not a valid directory" % self.root_dir


class AbstractCodeQuery(ABC):
    def __init__(self, root_dir=r"."):
        # Create logger.
        self.log = logging.getLogger("CallFollower.CodeQuery")
        # Creating Path object.
        self.RootPath = Path(root_dir)
        self.log.debug("Creating a CodeQuery object at '%s'",
                       self.RootPath.resolve())
        # Make sure it is valid.
        if not self.RootPath.is_dir():
            self.log.critical("'%s' is not a valid directory", root_dir)
            raise InvalidRootDirError(root_dir)

    @abstractmethod
    def initialize(self):
        """ Initialize CodeQuery (reading and checking preprocessing
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
        return '"{}-{}:\n{}"'.format(self._file.name, self._line, self._name)

    def __hash__(self):
        return hash((self._file, self._line))

    def getUniqueId(self):
        return self._unique
