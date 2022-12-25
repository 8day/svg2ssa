"""Core data structures upon which models of SVG attributes and elements are built."""


class SVGBasicEntity:
    """Abstract class for modeling misc SVG entities: elements, attributes, and their data."""

    def __init__(self, data):
        self.data = data
        """Any: Data."""

    @property
    def svg_name(self):
        """Name of the entity in SVG standard.

        Returns:
            str: Name of the entity in SVG standard.
        """

        raise NotImplementedError(f"{self.__class__.__name__}: 'svg_name' property is not redefined.")

    @classmethod
    def from_raw_data(cls, data):
        """Converts raw SVG data to classes with proper data.

        Args:
            cls (type): Class to be constructed.
            data (Any): Data to be processed before passing it to class constructor.
        Returns:
            Any: Instance of a class that called this method.

        E.g., converts data passed to :class:`svg2ssa.attributes.opacity.SVGOpacity` from ``"0.0"`` to ``0.0`` and then passes it for construction of :class:`svg2ssa.attributes.opacity.SVGOpacity` itself.
        """

        raise NotImplementedError(f"{cls.__name__}: 'from_raw_data' class method is not redefined.")

    def ssa_repr(self, ssa_repr_config):
        """Returns SSA representation of SVG data.

        Args:
            ssa_repr_config (dict): See :attr:`s2s.SVG.default_ssa_repr_config`.
        Returns:
            str: SSA representation.
        """

        raise NotImplementedError(f"{self.__class__.__name__}: 'ssa_repr' method is not redefined.")

    def __add__(self, other):
        """Returns concatenated ``self`` and ``other``.

        Specifies update rules for attributes a.k.a. inheritance:
        - returns ``self`` when property inheritance in SVG Rec. is ``yes``;
        - returns ``other`` when property inheritance in SVG Rec. is ``no``.
        """

        raise NotImplementedError(f"{self.__class__.__name__}: '__add__' method is not redefined.")

    def __repr__(self):
        """Returns representation of :attr:`data` suitable for debugging."""

        return f"{self.__class__.__name__}( '{self.svg_name!s}', {self.data!s} )"


class SVGContainerEntity(SVGBasicEntity):
    """Similar to :class:`SVGBasicEntity`, but not an abstract class (mixin), and only for containers."""

    def __bool__(self):
        return bool(self.data)

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

    def __contains__(self, obj):
        return any(obj == existing_obj for existing_obj in self.data)

    def contains_obj_with_svg_name(self, svg_name):
        """Returns boolean telling whether there is an item with attribute ``svg_name`` set to certain value."""

        return any(svg_name == obj.svg_name for obj in self.data)
