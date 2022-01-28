class SVGBasicEntity:
    def __init__(self, data):
        self.data = data

    @property
    def dtype(self):
        """Stores string with data type name."""

        raise NotImplementedError(f"{self.__class__.__name__}: 'dtype' property is not redefined.")

    @classmethod
    def from_raw_data(cls, data):
        """Converts raw SVG data to classes with proper data.

        E.g., converts data passed to :class:`SVGOpacity` from ``"0.0"`` to ``0.0``
        and then passes it for construction of :class:`SVGOpacity` itself.
        """

        raise NotImplementedError(f"{cls.__name__}: 'from_raw_data' class method is not redefined.")

    def ssa_repr(self):
        """SSA representation of SVG data.

        It does not, or at least should not modify original data.
        """

        raise NotImplementedError(f"{self.__class__.__name__}: 'ssa_repr' method is not redefined.")

    def __add__(self, other):
        """Specifies update rules for attributes aka inheritance.

        Returns (is that still holds true?!):
        o. 'self' when property inheritance in SVG Rec. is 'yes', or
        o. 'other' when property inheritance in SVG Rec. is 'no'.
        """

        raise NotImplementedError(f"{self.__class__.__name__}: '__add__' method is not redefined.")

    def __repr__(self):
        """Helps to debug."""

        return f"{self.__class__.__name__}( '{self.dtype!s}', {self.data!s} )"


class SVGContainerEntity(SVGBasicEntity):
    def __bool__(self):
        return True if self.data else False

    def __iter__(self):
        for obj in self.data:
            yield obj

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    def __delitem__(self, key):
        del self.data[key]

    def __contains__(self, item):
        if any(obj.dtype == item for obj in self.data):
            return True
        else:
            return False
