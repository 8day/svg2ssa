import re
import tkinter
# Uncomment when cx_Freeze'ing.
# from lxml import etree
# from xml.etree import ElementTree as etree
# Uncomment when used as is.
try:
    from lxml import etree
except ImportError:
    # See: http://lxml.de/compatibility.html
    from xml.etree import ElementTree as etree
import s2s_runtime_settings
from s2s_core import *
from s2s_utilities import convert_svglength_to_pixels
from s2s_svgatts_misc import *
from s2s_svgatts_color import *
from s2s_svgatts_opacity import *
from s2s_svgatts_trafos import SVGTransform, SVGTrafoRotate, SVGTrafoScale
from s2s_svgatts_path import SVGD


class SVGElement(S2SBlockInitDataProcDtype, S2SBlockDtypeChangeable, SVGAttribute, S2SBlockContainer):
    """Converts all the attributes that other classes feed him.
    
    Currently works only with "path" and "g".
    """
    
    atts_color = {'color', 'fill', 'stroke'}
    atts_opacity = {'opacity', 'fill-opacity', 'stroke-opacity'}
    atts_rest = {'stroke-width'}
    atts_style = atts_color | atts_opacity | atts_rest
    atts_path = {'d', 'id', 'transform', 'style'} | atts_style
    atts_group = {'transform', 'style'} | atts_style
    atts_to_class_mapping = {'transform': SVGTransform,
                             'color': SVGColor,
                             'fill': SVGFill,
                             'fill-opacity': SVGFillOpacity,
                             'opacity': SVGOpacity,
                             'stroke': SVGStroke,
                             'stroke-opacity': SVGStrokeOpacity,
                             'stroke-width': SVGStrokeWidth,
                             'd': SVGD,
                             'id': SVGId}

    
    @staticmethod
    def process_exceptional_cases(atts):
        # Process trafos.
        if 'transform' in atts:
            trafos = atts['transform']
            # Create \org if it is absent so that each next SSA layer
            # automatically layed on top of previous w/o any shifting.
            # ATM only VSFilter behaves like this, maybe libass as well,
            # but not ffdshow subtitles filter.
            # \pos also will do the trick, but if it's not \pos(0,0).
            if 'rotate' in trafos:
                if 'translate' in trafos:
                    for i in range(len(trafos)):
                        # If there's empty \pos, then there's no need in it, so remove \pos, -- there's still \org after all.
                        if trafos.data[i].dtype == 'translate' and (trafos.data[i].data[0] == 0 and trafos.data[i].data[1] == 0):
                            del trafos.data[i]
                            break
                else:
                    # There's still \org, so everything is OK.
                    pass
            else:
                if 'translate' in trafos:
                    for i in range(len(trafos)):
                        # If there's empty \pos, then there's no need in it, so remove \pos, but add \org(0,0) to maintain collision detection override.
                        if trafos.data[i].dtype == 'translate' and (trafos.data[i].data[0] == 0 and trafos.data[i].data[1] == 0):
                            del trafos.data[i]
                            atts['transform'] = trafos + SVGTrafoRotate((0, 0, 0))
                            break
                else:
                    # There's no \org, so add it.
                    atts['transform'] = trafos + SVGTrafoRotate((0, 0, 0))
            # Create CTM for path to emulate subpixel precision.
            if 'matrix' in trafos:
                val = 2 ** (s2s_runtime_settings.magnification_level - 1)
                val = val, val
                path_ctm = SVGTrafoScale(val).matrix + trafos.data[0]
            else:
                val = 2 ** (s2s_runtime_settings.magnification_level - 1)
                val = val, val
                path_ctm = SVGTrafoScale(val).matrix
        else:
            # Create trafos with \org(0,0) and CTM for path.
            trafos = SVGTransform()
            rotate = SVGTrafoRotate((0, 0, 0))
            trafos.data = [rotate]
            atts['transform'] = trafos
            val = 2 ** (s2s_runtime_settings.magnification_level - 1)
            val = val, val
            path_ctm = SVGTrafoScale(val).matrix
        # Process path.
        atts['d'].ctm = path_ctm
        # Process color. 'Fill' attribute has higher priority over 'color'!
        if 'fill' in atts:
            if atts['fill'].data is None:
                tmp = SVGFillOpacity()
                tmp.data = 0.0
                atts['fill-opacity'] = tmp
                del atts['fill']
            if 'color' in atts:
                del atts['color']
        if 'color' in atts:
            if atts['color'].data is None:
                tmp = SVGFillOpacity()
                tmp.data = 0.0
                atts['fill-opacity'] = tmp
            else:
                tmp = SVGFill()
                tmp.data = atts['color'].data
                # Fixme: since I stated that "'Fill' attribute has higher priority over 'color'!!!" (is that right at all?!),
                # maybe I should've checked first whether 'fill' exists so that I exidentally wouldn't override it?!
                # Todo: check in custom SVG.
                atts['fill'] = tmp
            del atts['color']
        if 'stroke' in atts:
            if atts['stroke'].data is None:
                tmp = SVGStrokeWidth()
                tmp.data = 0.0
                atts['stroke-width'] = tmp
                del atts['stroke']
        # Process opacity.
        if 'opacity' in atts:
            if 'fill-opacity' in atts and 'stroke-opacity' in atts:
                atts['fill-opacity'] += atts['opacity']
                atts['stroke-opacity'] += atts['opacity']
                del atts['opacity']
            elif 'fill-opacity' in atts:
                atts['fill-opacity'] += atts['opacity']
                del atts['opacity']
            elif 'stroke-opacity' in atts:
                atts['stroke-opacity'] += atts['opacity']
                del atts['opacity']
        # Process 'id'.
        if not 'id' in atts:
            atts['id'] = SVGId("")
        return atts


    def preprocess(self, data):
        # Select appropriate set of attributes.
        if self.dtype == 'path':
            supported = SVGElement.atts_path # IT IS COMPLETELY SAFE TO USE 'SELF' TO ACCESS CLASS VARS. IT'S UNSAFE, THOUGH, WHEN I WANT TO EDIT CLASS VARS: I'LL EDIT INSTANCE VARS INSTEAD.
        else:
            supported = SVGElement.atts_group
        # Filter out unsupported attributes.
        atts = {key: val for key, val in data.items() if key in supported}
        # Unpack properties from "style" to the common set of attributes.
        if 'style' in atts:
            tokens = re.sub('\s+', '', atts['style'])
            tokens = re.findall(r'(?:([^:]+?):([^;]+?)(?:;|;\Z|\Z))', tokens)
            if tokens:
                for key, val in tokens:
                    if key in SVGElement.atts_style:
                        atts.update({key: val})
            del atts['style']
        # Process attributes.
        atts = {key: SVGElement.atts_to_class_mapping[key](val) for key, val in atts.items()}
        return atts


    def update(self, other):
        # Note: beware of mutability issues.
        curr, prev = self.data, other.data
        for key in prev:
            curr[key] = curr[key] + prev[key] if key in curr else prev[key]
        return self


    def convert(self):
        atts = SVGElement.process_exceptional_cases(self.data)
        return {key: att.convert() for key, att in atts.items()}


class S2S:
    """This is 'main()', if you like. Spins all the machinery behind it.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.element_stack = []
        self.container_stack = []
        self.ssa_meta = {}


    @staticmethod
    def make_round_and_mod(nmb, mod):
        nmb = round(nmb)
        if nmb % mod != 0:
            nmb += mod - (nmb % mod)
        return nmb


    def start_event_for_g(self, atts):
        curr = SVGElement('g', atts)
        try:
            prev = self.container_stack[-1]
            curr += prev
        except IndexError:
            pass
        self.container_stack.append(curr)

        
    def end_event_for_g(self):
        if self.container_stack:
            del self.container_stack[-1]

            
    def start_event_for_path(self, atts):
        curr = SVGElement('path', atts)
        try:
            prev = self.container_stack[-1]
            curr += prev
        except IndexError:
            pass
        self.element_stack.append(curr)


    def end_event_for_path(self): pass


    def start_event_for_svg(self, atts):
        width = atts.get('width')
        height = atts.get('height')
        if width is not None and height is not None:
            width = atts['width']
            height = atts['height']
            width = convert_svglength_to_pixels(width)
            height = convert_svglength_to_pixels(height)
            width = S2S.make_round_and_mod(width, 16)
            height = S2S.make_round_and_mod(height, 16)
        else:
            width = s2s_runtime_settings.ssa_default_playresx
            height = s2s_runtime_settings.ssa_default_playresx
        self.ssa_meta['playresx'] = width
        self.ssa_meta['playresy'] = height

        
    def end_event_for_svg(self): pass


    start = dict(path = start_event_for_path,
                 g = start_event_for_g,
                 svg = start_event_for_svg)


    end = dict(path = end_event_for_path,
               g = end_event_for_g,
               svg = end_event_for_svg)


    def convert(self):
        filepath = self.filepath
        for action, element in etree.iterparse(filepath, ('start', 'end')):
            ns_name, local_name = re.search(r'^(\{.+?\})(.+)$', element.tag).group(1, 2)
            if action == 'start':
                if local_name in S2S.start:
                    S2S.start[local_name](self, element.attrib)
            else:
                if local_name in S2S.end:
                    S2S.end[local_name](self)

        ssa_table = []
        for element in self.element_stack:
            atts = element.convert()
            ssa_table.append(s2s_runtime_settings.ssa_event.format(actor = atts.pop('id'), trans = atts.pop('transform'), drwng = atts.pop('d'), m_lev = s2s_runtime_settings.magnification_level, codes = ''.join(obj for key, obj in atts.items())))
        ssa_table = '\n'.join(ssa_table)

        if s2s_runtime_settings.export_type == 0:
            tk = tkinter.Tk()
            tk.withdraw()
            tk.clipboard_clear()
            tk.clipboard_append(ssa_table)
            tk.destroy()
            print('Successfully converted:', filepath if len(filepath) < 52 else '...' + filepath[-52:])
        elif s2s_runtime_settings.export_type == 1:
            ssa_header = s2s_runtime_settings.ssa_header.format(width = self.ssa_meta['playresx'], height = self.ssa_meta['playresy'])
            with open(filepath + '.ass', 'w+t', buffering = 65536) as fh:
                fh.write(ssa_header)
                fh.write('\n')
                fh.write(ssa_table)
                fh.write('\n')
                print('Successfully converted:', filepath if len(filepath) < 52 else '...' + filepath[-52:])
        
        self.element_stack = []
        self.container_stack = []
        self.ssa_meta = {}
