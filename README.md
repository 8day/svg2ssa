# Warning

SVG generated by Inkscape changed so much since svg2ssa was first written, that default output of modern Inkscape versions is more likely to be broken than before. E.g., svg2ssa doesn't understand elements like `circle` which in previous versions were stored as `path` (in this particular example it will suffice to select such objects and execute this command: `Menu > Path > Object to Path`). It still may be useful as an alternative to ASSDraw, but it's much less convenient than before. I guess someone could write accompanying Inkscape script to use Inkscape's own logic to simplify this, or even turn svg2ssa into Inkscape extension, but it won't be me... Esp. not now when Russians plan to continue their invasion in Ukraine.

# About
svg2ssa is a converter written in Python 3 that is intended to convert *vector graphics* from SVG produced by Inkscape (although there's a possibility that it can chew SVG from other editors as well) to SSA used by *VSFilter* (mainly because of handling progressive collisions with \\org(0,0) w/o the need of change of sub's z-layer value).

The main audience of this software is "advanced" anime typesetters. svg2ssa will help them to create their graphics inside more neat, usable & specifically designed editor like Inkscape. It's hard to enumerate all possible uses and benefits: for some they are minor and not worth it, but for others they may be almost infinite. E.g., Inkscape's feature to trace bitmaps (despite some limits), render 3D objects from Wavefront \*.OBJ files produced by Blender, convert text to shapes. BTW, conversion of text to shapes means that there's no need to embed fonts for a few titles containing a few letters, maybe even drop font embedding altogether.

# How to use
1. acquire version of `svg2ssa`:
	I. install from PyPI:
		a. `pip install svg2ssa` - for use with safe XML parser `defusedxml`.
		b. `pip install svg2ssa[fast-parsing]` - for use with fast XML parser `lxml`. Note that for it to be used, you'll have to add explicit flag `-p lxml.etree`.
	II. download one of the standalone executables for Windows at https://github.com/8day/svg2ssa/releases.
2. convert SVG to SSA: `python -m svg2ssa -i "c:\path to dir\with\file.svg" -o "c:\path to another dir\with\file.ass"`.
3. for more info: `python -m svg2ssa --help`.

# Misc info
### The most notable features of Inkscape & svg2ssa combo
* [bitmap tracing][1]:
    * load & select raster image;
    * go to `Menu > Path > Trace Bitmap...`;
    * apply filter with desired settings (try `Mode > Multiple scans > Colors`).
* [rendering of 3D objects][2] (plain models w/o smoothing since it'll require rasterization):
    * build your own model with Blender;
    * while in Blender, export it to Wevefront \*.OBJ by going to `Menu > File > Export > Wevefront (.obj)`;
    * in Inkscape go to `Menu > Extensions > Render > 3D Polyhedron > Model file > Object > Load from file`;
    * in `Filename` edit-box paste path to \*.OBJ file;
    * in `Style > Z-sort faces by` you *may* want to select `Centroid`.
* conversion of text to shape:
    * create some text inside Inkscape;
    * select it;
    * go to `Menu > Path > Object to Path`.

### The most notable features of svg2ssa
* subpixel precision by changing the size of coordinate system (\\pN along with hardcoded scaling of drawings; S2S key: `-m {int}`);
* ability to choose whether to hardcode trafos or convert them to SSA equivalents (S2S key: `-t {scale, translate, rotate}`);
* other features and how-to can be found by typing `python -m svg2ssa --help` in your terminal.

### What you may want to know
* as Aegisub, both svg2ssa and Inkscape are cross-platform;
* stroke rendering in SVG & SSA are a bit different (see `Inkscape > Menu > Object > Fill and Stroke... > Stroke style > Join/Cap`):
    * in SVG you can set types of segment's joining & capping, but in SSA/VSFilter it's always `Round join` & `Round cap`;
    * see difference in how SVG & SSA lay down stroke in [s2s-stroke-preservation.svg][3] or [rendered PNG][4]: SVG lays down its stroke in the middle of shape's contour, but SSA lays it down outside.
* VSFilter always uses SVG's analogue of `fill-rule: nonzero`, so select it inside Inkscape so that your SSA drawings looked the same as SVG (`Inkscape > Menu > Object > Fill and Stroke... > Fill > *two V-like black shapes at the top right corner of the tab*`, select the one that is completely black);
* it may have some issues with relatively highlevel SVG concepts (especially raster images, text, clipping, masking, compositing etc.), but it should suffice as a replacement for ASSDraw/Aegisub: to draw graphics easier & faster;
* it supports only subset of drawing commands: M, L, H, V, C, S, Q, T and not Z or A (A may be converted to C/S by selecting object in question and executing `Menu > Path > Simplify`; doesn't always work as expected);
* it supports only `path` elements. Some other elements, like `circle`, can be converted to `path` by selecting them and executing `Menu > Path > Object to Path`;
* `viewBox` attribute will mess up rendering (likely to be smaller than expected) -- make sure it's not used.
* there might be erroneous conversions, especially with color and opacity (they are rear, but still they are present; in this case simplify your graphics/SVG structure by collapsing groups etc.);
* there's no support for \*.gzip files;
* there are similar to this scripts, but which are not "standalone": tophf's [AegiDrawing][5] for CorelDRAW and torque's [AI2ASS][6] for Illustrator.

### What you must know
* this app has no Graphical User Interface, only Command Line Interface;
* in order for it to work you need to have some version of Python 3 installed on your computer (worked with [3.2.5][7]), or if you use Windows you can download [standalone app][8] (you can download either `s2s-xml.etree.7z` or `s2s-lxml.7z`, but latter *should* be faster);
* [XML can be dangerous][9], so you may want to use package `defusedxml` instead of either built-in `xml` or fast `lxml`. When installing `svg2ssa` through `pip`, you may want to use this command `pip install svg2ssa[safe-parsing]` to install `defusedxml` as well.
* since SVG is very complex, this software was made to work with SVGs generated by Inkscape. Illustrator won't work, also some other browser-based editors might not work;
* the initial purpose was to bridge the gap between fansubbers and a world of more advanced vector editing, but not to be a converter that supports SVG by a 100% (there's probably no such software at all (!));
* probably will work as intended only with VSFilter.

[1]: https://github.com/8day/svg2ssa/blob/pub/examples/traced-2d/liberty-leading-the-people.jpg.svg.ass.png         "Bitmap tracing"
[2]: https://github.com/8day/svg2ssa/blob/pub/examples/rendered-3d/eva-new-uvs-blender.fbx.blend.obj.svg.ass.png    "Rendering of 3D objects"
[3]: https://github.com/8day/svg2ssa/blob/pub/examples/s2s-stroke-preservation.svg                                  "s2s-stroke-preservation.svg"
[4]: https://github.com/8day/svg2ssa/blob/pub/examples/s2s-stroke-preservation.png                                  "s2s-stroke-preservation.png"
[5]: http://www.fansubs.ru/forum/viewtopic.php?p=523046&sid=1312f5ed191ccf05e7af622a9e053f01#523046                 "tophf's AegiDrawing"
[6]: http://github.com/torque/AI2ASS                                                                                "torque's AI2ASS"
[7]: http://www.python.org/download/releases/3.2.5/                                                                 "Python 3.2.5"
[8]: https://github.com/8day/svg2ssa/releases                                                                       "cx_Freeze'd binaries for Windows"
[9]: https://pypi.org/project/defusedxml/0.7.1/#description
