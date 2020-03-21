

#######################################
# ParserTypeAbst                      #
#######################################
class ParserTypeAbst(object):
    def __init__(self, name, queryClass):
        self._name = name
        self._class = queryClass

    def __repr__(self):
        return "<CodeQuery type {}>".format(self._name)

    def __str__(self):
        return self._name

    def __call__(self, *args, **kwargs):
        return self._class(*args, **kwargs)


#######################################
# ParserType                          #
#######################################
class ParserType(object):
    __all__ = []

    @classmethod
    def addType(cls, name, parserCls):
        cls.__all__.append(name)
        setattr(cls, name, ParserTypeAbst(name, parserCls))

    @classmethod
    def getList(cls):
        return cls.__all__
