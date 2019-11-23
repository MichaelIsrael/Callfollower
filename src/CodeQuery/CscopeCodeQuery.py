from CodeQuery.AbstractCodeQuery import AbstractCodeQuery, CodeDefinition
from pathlib import Path
import os
import re


CSCOPE_ENTRY_REGEX = r"(?P<File>.+\.(c(pp)?|h))\s+(?P<Function>(\S+))\s+(?P<Line>\d+)\s+(?P<Code>.*)"


class CscopeResultFormatError(Exception):
    pass


class CscopeResult:
    def __init__(self, entry):
        match = re.match(CSCOPE_ENTRY_REGEX, entry)
        if match:
            self.info = match.groupdict()
        else:
            raise CscopeResultFormatError(entry)

    def getFunction(self):
        return self.info["Function"]

    def getFile(self):
        return self.info["File"]

    def getLine(self):
        return self.info["Line"]

    def getCode(self):
        return self.info["Code"]


class CscopeCodeDefinition(CodeDefinition):
    def __init__(self, entry):
        result = CscopeResult(entry)
        super(CscopeCodeDefinition, self).__init__(result.getFunction(),
                                                   result.getFile(),
                                                   result.getLine())


class CscopeCodeQuery(AbstractCodeQuery):
    def __init__(self, root_dir=r"."):
        self._args = []
        self.RootPath = Path(root_dir)
        try:
            CscopeOut = tuple(self.RootPath.glob("cscope.out"))[0]
        except IndexError:
            self._createFileList()
        else:
            if CscopeOut.is_file():
                self._args.append("-d")
            else:
                self._createFileList()

    def _createFileList(self):
        with open(self.RootPath.joinpath("cscope.files"), "w+") as files:
            self._addToList(files, "*.h")
            self._addToList(files, "*.c")
            self._addToList(files, "*.cpp")

    def _addToList(self, File, pattern):
        lst = self.RootPath.rglob(pattern)
        for f in lst:
            File.write(str(f.resolve())+"\n")

    def _query(self, num, string):
        query = "-L{num}{string}".format(num=num, string=string)
        cscopeCmd = " ".join(["cscope", *self._args, query])
        return os.popen(cscopeCmd).read().splitlines()

    def getCaller(self, function):
        output = self._query(3, function)
        return [definition
                for line in output
                for definition in
                self.getDefinition(CscopeResult(line).getFunction())]

    def getCalled(self, function):
        output = self._query(2, function)
        return [definition
                for line in output
                for definition in
                self.getDefinition(CscopeResult(line).getFunction())]

    def getDefinition(self, function):
        output = self._query(1, function)
        return [CscopeCodeDefinition(line) for line in output]
