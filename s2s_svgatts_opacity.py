# Seems that a real problem is that not all properties is inherited from g-elements etc.
# For example, stroke-opacity with the same value on path-element and g-element doesn't have 1/2 effect,
# it stayed the same in IE browser. Seems that only 'opacity' affects sub-sequent elements
# and 'stroke-opacity', 'fill-opacity' etc. override the same properties on g-element/containers.
#
# Fix: fill-opacity & opacity conflict: fill-opacity should depend on opacity!
# I.e. when op = .5 and f-op = .5, ssa-obj-op should be equal .25, not .5!
#
# Todo: since all opacity classes mostly differ by SSA representation string, It'd be probably better
# to add some code to replace tha string to class corresponding one. I.e. r'\alpha&H{0:02X}&'
# replaced to r'\1a&H{0:02X}&' if class is SVGFillOpacity.
# Though it may be a bad idea, since the same thing can be done to color, but there this modification will
# be overwhelming, unnecessary. So, it's probably better to leave it as is (KISS; simple but not simpler,
# i.e. optimised but not overoptimised). Well, as I said, ATM this kind of optimisation is unnecessary.


from s2s_core import SVGAttribute


class SVGOpacity(SVGAttribute):
    """Class for SVG 'opacity' attribute.
    
    Value:        <opacity-value> | inherit
    Initial:      1
    Inherited:    no
    """
    
    @property
    def dtype(self):
        return 'opacity'

    def preprocess(self, data):
    
        # Todo: add clamping of out-of-range values.
        
        return float(data)

    def update(self, other):
        # Creation of the third object is neccessary
        # since w/o it 'self' or 'other' may (and will)
        # be modified later on, which is wrong.
        tmp = self.__class__()
        tmp.data = self.data * other.data
        return tmp

    def convert(self):
        val = 255 - (self.data * 255)
        return r'\alpha&H{0:02X}&'.format(round(val))


class SVGFillOpacity(SVGOpacity):
    """Class for SVG 'fill-opacity' attribute.
    
    Value:        <opacity-value> | inherit
    Initial:      1
    Inherited:    yes
    """
    
    @property
    def dtype(self):
        return 'fill-opacity'

    def convert(self):
        val = 255 - (self.data * 255)
        return r'\1a&H{0:02X}&'.format(round(val))


class SVGStrokeOpacity(SVGOpacity):
    """Class for SVG 'stroke-opacity' attribute.
    
    Value:        <opacity-value> | inherit
    Initial:      1
    Inherited:    yes
    """
    
    @property
    def dtype(self):
        return 'stroke-opacity'

    def convert(self):
        val = 255 - (self.data * 255)
        return r'\3a&H{0:02X}&'.format(round(val))
