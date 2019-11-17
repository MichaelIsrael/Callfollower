from pathlib import Path
import os
import re


ENTRY_REGEX = r"(?P<FileName>.+\.(c(pp)?|h))\s+(?P<Caller>(\S+))\s+(?P<Line>\d+)\s+(?P<Call>.*)"


class CodeQueryResult:
    def __init__(self, entry):
        m = re.match(ENTRY_REGEX, entry)
        if m:
            self.info = m.groupdict()
        else:
            raise Exception
        self.name = self.getCaller()  # Temp! TODO: Remove

    def __eq__(self, other):
        # TODO: Better check.
        return self.info['FileName'] == other.info['FileName'] and \
            self.info['Caller'] == other.info['Caller']

    def getCaller(self):
        return self.info["Caller"]

    getName = getCaller  # Temp! TODO: Remove.

    def getLine(self):
        return self.info["Line"]


class CodeQuery:
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
        # TODO:
        output = self._query(3, function)
        return [CodeQueryResult(line) for line in output]

    def getCalled(self, function):
        # TODO:
        output = self._query(2, function)
        return [CodeQueryResult(line) for line in output]

    def getGlobalDefinition(self, function):
        # TODO:
        pass

    def getSymbol(self, function):
        # TODO:
        pass
