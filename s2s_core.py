class S2SError(Exception): pass
class S2STypeError(S2SError): pass
class S2SAttributeError(S2SError): pass
class S2SMethodError(S2SError): pass
class SVGError(S2SError): pass
class SVGTypeError(SVGError): pass


class S2SBlockInitData:
    def __init__(self, data = None):
        self._data = data


class S2SBlockInitDataDtype:
    def __init__(self, dtype = None, data = None):
        self._dtype = dtype
        self._data = data


class S2SBlockInitDataProc:
    def __init__(self, data = None):
        self._data = self.preprocess(data) if data is not None else None


class S2SBlockInitDataProcDtype:
    def __init__(self, dtype = None, data = None):
        self._dtype = dtype
        self._data = self.preprocess(data) if data is not None else None


class S2SBlockDataChangeable:
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data


class S2SBlockDtypeChangeable:
    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, dtype):
        self._dtype = dtype


class S2SBlockContainer:
    def __bool__(self):
        return True if self._data else False

    def __iter__(self):
        for obj in self._data:
            yield obj

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, val):
        self._data[key] = val

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, item):
        if any(obj.dtype == item for obj in self._data):
            return True
        else:
            return False


class SVGAttribute(S2SBlockInitDataProc, S2SBlockDataChangeable):
    @property
    def dtype(self):
        """Stores string with data type name.
        """
        
        raise S2SAttributeError(self.__class__.__name__ + ': "dtype" property is not redefined.')

    def preprocess(self, data):
        """Pre-processes data upon initialisation, if need be.
        
        Can use keyword-argument with default value of 'None' to check whether
        to pre-process or not. Such behaviour may be useful when data allready
        pre-processed.         
        """
        
        raise S2SMethodError(self.__class__.__name__ + ': "preprocess" method is not redefined.')

    def update(self, other):
        """Specifies update rules for attributes aka inheritance.
        
        Returns (is that still holds true?!):
        o. 'self' when property inheritance in SVG Rec. is 'yes', or
        o. 'other' when property inheritance in SVG Rec. is 'no'.
        """
        
        raise S2SMethodError(self.__class__.__name__ + ': "update" method is not redefined.')

    def convert(self):
        """Converts data to desired view/representation, which in this case is SSA format.

        It does not, or at least should not modify original data.
        """
        
        raise S2SAttributeError(self.__class__.__name__ + ': "convert" method is not redefined.')

    def __add__(self, other):
        """Shorthand for .update(). 
        """
        
        return self.update(other)

    def __repr__(self):
        """Helps to debug.
        """
        
        return '{0}( "{1}", {2} )'.format(self.__class__.__name__, str(self.dtype), str(self.data))
