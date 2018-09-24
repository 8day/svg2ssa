if __name__ == '__main__':
    import sys
    import os
    import argparse
    import s2s_runtime_settings
    
    parser = argparse.ArgumentParser(description = 'Converts SVG (Rec 1.1) into SSA (v4.0+).', epilog="To run, use this syntax: APP_NAME KEYS PATH_TO_THE_FILE. Beware that 1) there's no key to specify output file (this file will be automatically placed inside same dir as SVG, with the same name as SVG, but with suffix \".ass\"); 2) only one file can be converted at a time, do not specify multiple files.")
    parser.add_argument('--unnecessary_transformations',
                        '-t',
                        help = 'Trafos that should be collapsed into matrix, i.e. "baked". If N trafos are used, then the key should be used N times: -t rotate -t skewX.',
                        default = [],
                        action = 'append',
                        choices = ['scale', 'translate', 'rotate'])
    parser.add_argument('--magnification_level',
                        '-m',
                        help = 'Magnification level of the coordinate system by this formula: (level - 1) ^ 2.',
                        default = 3,
                        type = int,
                        metavar = "natural_number")
    parser.add_argument('--stroke_preservation',
                        '-s',
                        help = 'Stroke transformation. "0" preserves stroke width (left untouched); "1" preserve stroke area (stroke size is divided by 2).',
                        default = 0,
                        type = int,
                        choices = range(2))
    parser.add_argument('--collapse_consecutive_path_segments',
                        '-cs',
                        help = 'Collapses consecutive path segments of the same type into one: l 10,10 l 20,20 >>> l 10,10 20,20.',
                        default = 1,
                        type = int,
                        choices = range(2))
    parser.add_argument('--ssa_default_playresx',
                        help = 'Custom PlayResX for SSA script. Should be equal to the video dimensions (and/or to the drawing being converted). When custom PlayResX is set, mod16 is checked.',
                        default = 1280,
                        type = int,
                        metavar = "natural_number")
    parser.add_argument('--ssa_default_playresy',
                        help = 'Custom PlayResY for SSA script. Should be equal to the video dimensions (and/or to the drawing being converted). When custom PlayResY is set, mod16 is checked.',
                        default = 720,
                        type = int,
                        metavar = "natural_number")
    parser.add_argument('--export_type',
                        '-e',
                        help = 'Destination (and thus formatting) for processed SVG. "0" copies SSA events into clipboard; "1" creates full SSA file in external file.',
                        default = 0,
                        type = int,
                        choices = range(2))
    parser.add_argument('path', nargs=argparse.REMAINDER)

    args = vars(parser.parse_args(sys.argv[1:]))
    path = " ".join(args["path"])
    del args["path"]

    for k, v in args.items():
        exec("s2s_runtime_settings.{0} = {1}".format(k, v))

    if s2s_runtime_settings.export_type == 0:
        s2s_runtime_settings.ssa_header = ""
        s2s_runtime_settings.ssa_event = "Dialogue: 0,0:00:00.00,0:00:02.00,Default,{actor},0000,0000,0000,,{{\\p{m_lev}\\an7{trans}{codes}}} {drwng} {{\\p0}}"
    elif s2s_runtime_settings.export_type == 1:
        s2s_runtime_settings.ssa_header = ("[Script Info]\n"
            "; Script generated by svg2ssa for use in Aegisub\n"
            "; svg2ssa: *somewhere-in-Internet*\n"
            "; Aegisub: http://www.aegisub.org/\n"
            "ScriptType: v4.00+\n"
            "Title: SSA subtitle generated from SVG\n"
            "WrapStyle: 0\n"
            "PlayResX: {width}\n"
            "PlayResY: {height}\n"
            "ScaledBorderAndShadow: yes\n"
            "Video File: ?dummy:23.976000:100000:{width}:{height}:255:255:255:\n"
            "\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: s2s.default,Arial,20,"
            "&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
            "0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1\n"
            "\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, "
            "MarginL, MarginR, MarginV, Effect, Text")
        s2s_runtime_settings.ssa_event = "Dialogue: 0,0:00:00.00,0:00:02.00,s2s.default,{actor},0000,0000,0000,,{{\\p{m_lev}{trans}{codes}}} {drwng} {{\\p0}}"
    
    import s2s_main
    if os.path.isfile(path):
        s2s_main.S2S(path).convert()
    else:
        # Print help info if path is invalid, or no path was specified.
        parser.parse_args(["-h"])
