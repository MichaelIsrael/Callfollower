

#######################################
# ParserTypeAbst                      #
#######################################
class ParserTypeAbst(object):
    def __init__(self, name, queryClass):
        self._name = name
        self._class = queryClass

    def __repr__(self):
        return "<CodeParser type {}>".format(self._name)

    def __str__(self):
        return self._name

    def __call__(self, *args, **kwargs):
        return self._class(*args, **kwargs)


#######################################
# ParserMetaType                      #
#######################################
class ParserMetaType(type):
    __parser_dict__ = {}
    # Using a lit of one element to avoid a recursion in __setattr__ when
    # overwriting a member.
    __default_parser__ = None

    def __getattr__(cls, attr):
        # if the default parser is requested, return __default_parser__.
        if attr.title() == "Default":
            return cls.__default_parser__

        # Otherwise, try to return the requested parser.
        try:
            return cls.__parser_dict__[attr]
        except KeyError:
            raise AttributeError("Parser '" + attr +
                                 "' is unknown. Available parsers are " +
                                 str(list(cls.__parser_dict__.keys())) + ".") \
                    from None

    def __setattr__(cls, name, value):
        if not cls.__default_parser__:
            # Set the first added parser as the default one.
            super().__setattr__("__default_parser__", value)
        # Add the new parser to the dict.
        cls.__parser_dict__[name] = value


#######################################
# ParserType                          #
#######################################
class ParserType(metaclass=ParserMetaType):
    @classmethod
    def addType(cls, name, parserCls):
        setattr(cls, name, ParserTypeAbst(name, parserCls))

    @classmethod
    def getList(cls):
        return list(cls.__parser_dict__.keys())
