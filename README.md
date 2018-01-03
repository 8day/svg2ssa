﻿## About
svg2ssa is a converter written in Python 3 that is intended to convert *vector graphics* from SVG produced by Inkscape (although there's a possibility that it can chew SVG from other editors as well) to SSA used by *VSFilter* (mainly because of handling progressive collisions with \org(0,0) w/o the need of change of sub's z-layer value).

The main audience of this software is "advanced" anime typesetters. SVG2SSA will help them to create their graphics inside more neat, usable & specifically designed editor like Inkscape. It's hard to enumerate all possible uses and benefits: for some they are minor and not worth it, but for others they may be almost infinite. E.g., Inkscape's feature to trace bitmaps (despite some limits), render Wavefront 3D *.OBJ files produced by Blender, convert text to shapes. BTW, conversion of text to shapes means that there's no need to embed fonts for a few titles containing a few letters, maybe even drop font embedding altogether, although from works of Irrational Typesetting Wizardry fansub group it's obvious that fonts are especially good for reuse of frequently occurring shapes (see "[Irrational Typesetting Wizardry] NouCome - 05 [49CCC27E].mkv").


## Misc info
The most notable features of Inkscape & svg2ssa combo:
* [bitmap tracing][1]:
    * load & select raster image;
    * go to `Menu > Path > Trace Bitmap...`;
    * apply filter with desired settings (try `Mode > Multiple scans > Colors`).
* [rendering of 3D objects][2] (plain models w/o smoothing since it'll require rasterization):
    * build you own model with Blender;
    * export it to Wevefront .obj by going here `Menu > File > Export > Wevefront (.obj)`;
    * place it in `Inkscape\App\Inkscape\share\extensions\Poly3DObjects\`;
    * in Inkscape go to `Menu > Extensions > Render > 3D Polyhedron > Object > Load from file`;
    * in `Filename` edit-box paste name of an *.OBJ;
    * in `Style > Z-sort faces by` you may want to select `Mean`.
* conversion of text to shape:
    * create some text inside Inkscape;
    * select it;
    * go to `Menu > Path > Object to Path`.

The most notable features of svg2ssa:
* subpixel precision by changing the size of coordinate system (\pN along with hardcoded scaling of drawings; S2S key: `-m natural_number`);
* saving of converted SSA into either external file or clipboard (S2S key: `-e {0,1}`);
* ability to choose whether to hardcode trafos or convert them to SSA equivalents (S2S key: `-t {'scale', 'translate', 'rotate'}`);
* other features and how-to can be found by typing `APP_NAME --help` in your terminal.

What you may want to know:
* as Aegisub, both SVG2SSA and Inkscape are cross-platform.
* there's no support for .gzip'ed files;
* stroke rendering in SVG & SSA are a bit different (see `Inkscape > Menu > Object > Fill and Stroke... > Stroke style > Join/Cap`):
	* in SVG you can set types of segment's joining & capping, but in SSA/VSFilter it's always `Round join` & `Round cap`;
	* see difference in how SVG & SSA lay down stroke in [`s2s-stroke-preservation.svg`][3] or [rendered PNG][4]: SVG lays down its stroke in the middle of shape's contour, but SSA lays it down outside.
* VSFilter always uses SVG's analogue of `fill-rule: nonzero`, so select it inside Inkscape so that your SSA drawings looked the same as SVG (`Inkscape > Menu > Object > Fill and Stroke... > Fill > *two V-like black shapes at the top right corner of the tab*`, select the one that is completely black);
* it may have some issues with relatively highlevel SVG concepts (especially raster images, text, clipping, masking, compositing etc.), but it should suffice as a replacement for ASSDraw/Aegisub: to draw graphics easier & faster.
* it supports only subset of drawing commands: M, L, H, V, C, S, Q, T and not Z or A (A may be converted to C/S inside of Inkscape);
* there might be erroneous conversions, especially with color and opacity (they are rear, but still they are present; in this case simplify your graphics/SVG structure by collapsing groups etc.);
* there are similar to this scripts, but which are not "standalone": tophf's [AegiDrawing][4] for CorelDRAW and torque's [AI2ASS][5] for Illustrator.

What you must know:
* this app has no Graphical User Interface, only Command Line Interface;
* in order for it to work you need to have some version of Python 3 installed on your computer (worked with [3.2.5][6]), or if you use Windows you can DL [standalone app][7] (you can DL either s2s-xml.etree.7z or s2s-lxml.7z which *should* be faster);
* since SVG is very complex, this software was made to work with SVGs generated by Inkscape. Illustrator won't work, also some other browser-based editors might not work;
* the initial purpose was to bridge the gap between fansubbers and a world of more advanced vector editing, but not to be a converter that supports SVG by a 100% (there's probably no such software at all (!));
* probably will work as intended only with VSFilter.
* to cx_Freeze:
    1. un-/comment necessary lines in s2s.py import section;
    2. run `cxfreeze ..\s2s.py --target-dir s2s --icon=s2s_logo.ico`;
        * when lxml is used, add line `--include-modules=lxml._elementpath,gzip,inspect`.

[1]: http://www.mediafire.com/view/brr1mywnm2r2lsr/FREEDOM.svg.ass.png                                  "Bitmap tracing"
[2]: http://www.mediafire.com/view/zqs18bg2xb2lw3j/plane.svg.ass.png                                    "Rendering of 3D objects"
[3]: http://www.mediafire.com/download/np7annb0loh3rh2/s2s-stroke-preservation.svg                      "s2s-stroke-preservation.svg"
[4]: http://www.mediafire.com/view/z86emgujwacmmb9/s2s-stroke-preservation.png                          "s2s-stroke-preservation.png"
[5]: http://www.fansubs.ru/forum/viewtopic.php?p=523046&sid=1312f5ed191ccf05e7af622a9e053f01#523046     "tophf's AegiDrawing"
[6]: http://github.com/torque/AI2ASS                                                                    "torque's AI2ASS"
[7]: http://www.python.org/download/releases/3.2.5/                                                     "Python 3.2.5"
[8]: http://www.mediafire.com/folder/ihrh3ti06fm14/s2s                                                  "extra files for svg2ssa"


## TODO
- Add support for arc-to drawing command. This one shouldn't be so hard since already I have the necessary code in another app.
- Make it an Inkscape extension. In this case I need to rewrite all code so that it would be compatible with Python 2.6.
