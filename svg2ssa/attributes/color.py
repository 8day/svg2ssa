"""Logic for the models of SVG document's attributes describing color."""


import re
from ..core import SVGBasicEntity


class SVGColor(SVGBasicEntity):
    """Class for SVG ``color`` attribute.

    Value:        <color> | inherit
    Initial:      depends on user agent
    Inherited:    yes
    """

    color_keywords = {
        "aliceblue": ("FF", "F8", "F0"),
        "antiquewhite": ("D7", "EB", "FA"),
        "aqua": ("00", "FF", "FF"),
        "aquamarine": ("D4", "FF", "7F"),
        "azure": ("FF", "FF", "F0"),
        "beige": ("DC", "F5", "F5"),
        "bisque": ("C4", "E4", "FF"),
        "black": ("00", "00", "00"),
        "blanchedalmond": ("CD", "EB", "FF"),
        "blue": ("00", "00", "FF"),
        "blueviolet": ("E2", "2B", "8A"),
        "brown": ("2A", "2A", "A5"),
        "burlywood": ("87", "B8", "DE"),
        "cadetblue": ("A0", "9E", "5F"),
        "chartreuse": ("00", "FF", "7F"),
        "chocolate": ("1E", "69", "D2"),
        "coral": ("50", "7F", "FF"),
        "cornflowerblue": ("ED", "95", "64"),
        "cornsilk": ("DC", "F8", "FF"),
        "crimson": ("3C", "14", "DC"),
        "cyan": ("00", "FF", "FF"),
        "darkblue": ("8B", "00", "00"),
        "darkcyan": ("8B", "8B", "00"),
        "darkgoldenrod": ("0B", "86", "B8"),
        "darkgray": ("A9", "A9", "A9"),
        "darkgreen": ("00", "64", "00"),
        "darkgrey": ("A9", "A9", "A9"),
        "darkkhaki": ("6B", "B7", "BD"),
        "darkmagenta": ("8B", "00", "8B"),
        "darkolivegreen": ("2F", "6B", "55"),
        "darkorange": ("00", "8C", "FF"),
        "darkorchid": ("CC", "32", "99"),
        "darkred": ("00", "00", "8B"),
        "darksalmon": ("7A", "96", "E9"),
        "darkseagreen": ("8F", "BC", "8F"),
        "darkslateblue": ("8B", "3D", "48"),
        "darkslategray": ("4F", "4F", "2F"),
        "darkslategrey": ("4F", "4F", "2F"),
        "darkturquoise": ("D1", "CE", "00"),
        "darkviolet": ("D3", "00", "94"),
        "deeppink": ("93", "14", "FF"),
        "deepskyblue": ("FF", "BF", "00"),
        "dimgray": ("69", "69", "69"),
        "dimgrey": ("69", "69", "69"),
        "dodgerblue": ("FF", "90", "1E"),
        "firebrick": ("22", "22", "B2"),
        "floralwhite": ("F0", "FA", "FF"),
        "forestgreen": ("22", "8B", "22"),
        "fuchsia": ("FF", "00", "FF"),
        "gainsboro": ("DC", "DC", "DC"),
        "ghostwhite": ("FF", "F8", "F8"),
        "gold": ("00", "D7", "FF"),
        "goldenrod": ("20", "A5", "DA"),
        "gray": ("80", "80", "80"),
        "green": ("00", "80", "00"),
        "greenyellow": ("2F", "FF", "AD"),
        "grey": ("80", "80", "80"),
        "honeydew": ("F0", "FF", "F0"),
        "hotpink": ("B4", "69", "FF"),
        "indianred": ("5C", "5C", "CD"),
        "indigo": ("82", "00", "4B"),
        "ivory": ("F0", "FF", "FF"),
        "khaki": ("8C", "E6", "F0"),
        "lavender": ("FA", "E6", "E6"),
        "lavenderblush": ("F5", "F0", "FF"),
        "lawngreen": ("00", "FC", "7C"),
        "lemonchiffon": ("CD", "FA", "FF"),
        "lightblue": ("E6", "D8", "AD"),
        "lightcoral": ("80", "80", "F0"),
        "lightcyan": ("FF", "FF", "E0"),
        "lightgoldenrodyellow": ("D2", "FA", "FA"),
        "lightgray": ("D3", "D3", "D3"),
        "lightgreen": ("90", "EE", "90"),
        "lightgrey": ("D3", "D3", "D3"),
        "lightpink": ("C1", "B6", "FF"),
        "lightsalmon": ("7A", "A0", "FF"),
        "lightseagreen": ("AA", "B2", "20"),
        "lightskyblue": ("FA", "CE", "87"),
        "lightslategray": ("77", "88", "99"),
        "lightslategrey": ("77", "88", "99"),
        "lightsteelblue": ("DE", "C4", "B0"),
        "lightyellow": ("E0", "FF", "FF"),
        "lime": ("00", "FF", "00"),
        "limegreen": ("32", "CD", "32"),
        "linen": ("E6", "F0", "FA"),
        "magenta": ("FF", "00", "FF"),
        "maroon": ("00", "00", "80"),
        "mediumaquamarine": ("AA", "CD", "66"),
        "mediumblue": ("CD", "00", "00"),
        "mediumorchid": ("D3", "55", "BA"),
        "mediumpurple": ("DB", "70", "93"),
        "mediumseagreen": ("71", "B3", "3C"),
        "mediumslateblue": ("EE", "68", "7B"),
        "mediumspringgreen": ("9A", "FA", "00"),
        "mediumturquoise": ("CC", "D1", "48"),
        "mediumvioletred": ("85", "15", "C7"),
        "midnightblue": ("70", "19", "19"),
        "mintcream": ("FA", "FF", "F5"),
        "mistyrose": ("E1", "E4", "FF"),
        "moccasin": ("B5", "E4", "FF"),
        "navajowhite": ("AD", "DE", "FF"),
        "navy": ("80", "00", "00"),
        "oldlace": ("E6", "F5", "FD"),
        "olive": ("00", "80", "80"),
        "olivedrab": ("23", "8E", "6B"),
        "orange": ("00", "A5", "FF"),
        "orangered": ("00", "45", "FF"),
        "orchid": ("D6", "70", "DA"),
        "palegoldenrod": ("AA", "E8", "EE"),
        "palegreen": ("98", "FB", "98"),
        "paleturquoise": ("EE", "EE", "AF"),
        "palevioletred": ("93", "70", "DB"),
        "papayawhip": ("D5", "EF", "FF"),
        "peachpuff": ("B9", "DA", "FF"),
        "peru": ("3F", "85", "CD"),
        "pink": ("CB", "C0", "FF"),
        "plum": ("DD", "A0", "DD"),
        "powderblue": ("E6", "E0", "B0"),
        "purple": ("80", "00", "80"),
        "red": ("FF", "00", "00"),
        "rosybrown": ("8F", "8F", "BC"),
        "royalblue": ("E1", "69", "41"),
        "saddlebrown": ("13", "45", "8B"),
        "salmon": ("72", "80", "FA"),
        "sandybrown": ("60", "A4", "F4"),
        "seagreen": ("57", "8B", "2E"),
        "seashell": ("EE", "F5", "FF"),
        "sienna": ("2D", "52", "A0"),
        "silver": ("C0", "C0", "C0"),
        "skyblue": ("EB", "CE", "87"),
        "slateblue": ("CD", "5A", "6A"),
        "slategray": ("90", "80", "70"),
        "slategrey": ("90", "80", "70"),
        "snow": ("FA", "FA", "FF"),
        "springgreen": ("7F", "FF", "00"),
        "steelblue": ("B4", "82", "46"),
        "tan": ("8C", "B4", "D2"),
        "teal": ("80", "80", "00"),
        "thistle": ("D8", "BF", "D8"),
        "tomato": ("47", "63", "FF"),
        "turquoise": ("D0", "E0", "40"),
        "violet": ("EE", "82", "EE"),
        "wheat": ("B3", "DE", "F5"),
        "white": ("FF", "FF", "FF"),
        "whitesmoke": ("F5", "F5", "F5"),
        "yellow": ("FF", "FF", "00"),
        "yellowgreen": ("32", "CD", "9A"),
    }
    """dict[str, str]: Mapping of `recognized color keyword names <https://www.w3.org/TR/SVG11/types.html#ColorKeywords>`__ to their string RGB form."""
    color_hex = r"#[0-9A-Fa-f]{0}\Z"
    color_hex_full = re.compile(color_hex.format("{6}"), re.I)
    color_hex_short = re.compile(color_hex.format("{3}"), re.I)
    color_funciri = r"rgb\({0},{0},{0}\)\Z"
    color_funciri_decimal = re.compile(color_funciri.format(r"(?:[01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"))
    color_funciri_percent = re.compile(color_funciri.format(r"(?:[0-9]?[0-9]|100)%"))

    @property
    def dtype(self):
        return "color"

    @classmethod
    def from_raw_data(cls, data):
        tmp = re.sub(r"\s+", "", data)
        if cls.color_hex_full.match(tmp):
            tmp = tmp.upper()
            tmp = tmp[1:3], tmp[3:5], tmp[5:7]
        elif cls.color_hex_short.match(tmp):
            tmp = tmp.upper()
            tmp = tmp[1:2] + tmp[1:2], tmp[2:3] + tmp[2:3], tmp[3:4] + tmp[3:4]
        elif tmp == "none":
            tmp = None
        elif cls.color_funciri_decimal.match(tmp):
            tmp = tmp[4:-1].split(",")
            tmp[0] = int(tmp[0])
            tmp[1] = int(tmp[1])
            tmp[2] = int(tmp[2])
            tmp = tuple(f"{comp:02X}" for comp in tmp)
        elif cls.color_funciri_percent.match(tmp):
            tmp = tmp[4:-1].replace("%", "").split(",")
            tmp[0] = int(tmp[0]) * 255 // 100
            tmp[1] = int(tmp[1]) * 255 // 100
            tmp[2] = int(tmp[2]) * 255 // 100
            tmp = tuple(f"{comp:02X}" for comp in tmp)
        elif tmp.lower() in cls.color_keywords:
            tmp = cls.color_keywords[tmp.lower()]
        else:
            # Fixme: Currently out-of-range values raise errors, which is wrong according to SVG Rec 1.1.
            raise TypeError(f"{cls.__name__}: The next color specified in SVG is malformed or unsupported: {data}.")
        return cls(tmp)

    def ssa_repr(self, ssa_repr_config):
        r, g, b = self.data
        return f"\\1c&H{b}{g}{r}&"

    def __add__(self, other):
        return self.__class__(self.data)


class SVGFill(SVGColor):
    """Class for SVG ``fill`` attribute.

    Value:        <paint>
    Initial:      black
    Inherited:    yes
    """

    @property
    def dtype(self):
        return "fill"


class SVGStroke(SVGColor):
    """Class for SVG ``stroke`` attribute.

    Value:        <paint>
    Initial:      none
    Inherited:    yes
    """

    @property
    def dtype(self):
        return "stroke"

    def ssa_repr(self, ssa_repr_config):
        r, g, b = self.data
        return f"\\3c&H{b}{g}{r}&"
