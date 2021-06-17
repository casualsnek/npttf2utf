import argparse
import json
import os
import zipfile
from .base.docxhandler import DocxHandler, ET
from .base.exceptions import *
from .base.fontmapper import FontMapper
from .base.txthandler import TxtHandler


def main():
    about = """ 
    Created by : Casual Snek (@casualsnek on GitHub)
    License    : GNU GENERAL PUBLIC LICENSE v3
    Version    : 0.3.7
    Email      : casualsnek@protonmail.com
    """
    modes = ['string', 'plain', 'docx']
    parser = argparse.ArgumentParser(description=about, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-V', '--version', action='version', version="0.1a")
    parser.add_argument('-m', '--mode', dest='mode', help='Conversion mode ', choices=modes, required=True)
    parser.add_argument('-if', '--input-font', dest='font',
                        help='Font used in input file. ("auto" can be used for docx mode)',
                        default='preeti', required=True)
    parser.add_argument('-of', '--output-font', dest='outputfont',
                        help='Font to which output will be mapped to. (If unspecified output font will be set to '
                             'unicode)',
                        default='unicode', choices=["Preeti", "unicode"], required=False)
    parser.add_argument('-dc', '--docx-components', dest='docxcomponents',
                        help='Component of docx which will be processed. (Comma separated) Available: '
                             '"body_paragraph,table,shape" (If not specified all components will be processed)',
                        default='body_paragraph,table,shape', required=False)
    parser.add_argument('-kf', '--known-unicode-fonts', dest='knownunicodefonts',
                        help='Fonts to add to known supported unicode fonts while converting to preeti (If '
                             'Unspecified "Kalimati,Mangal,Noto Sans Devanagari" will be set)',
                        default='', required=False)
    parser.add_argument('-i', '--input', dest='input', help='Input string or filepath', required=True)
    parser.add_argument('-o', '--output', dest='output', help='Output file path. Not required for string mode')
    parser.add_argument('-mf', '--map-file', dest='mapfile', help='Mapping definition file')
    args = parser.parse_args()
    font = args.font
    op_mode = args.mode

    def splitnclean(string):
        lis = string.split(",")
        for index, item in enumerate(lis):
            lis[index] = item.strip()
        return lis

    rule_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "map.json")
    if args.mapfile is not None:
        rule_file = args.mapfile
    try:
        if op_mode == "string":
            converter = FontMapper(rule_file)
            if args.outputfont.lower() == 'unicode':
                print(converter.map_to_unicode(args.input, from_font=args.font))
            elif args.outputfont.lower() == 'preeti':
                print(converter.map_to_preeti(args.input, from_font=args.font))
            else:
                raise UnsupportedMapToException
        elif op_mode == "plain" or op_mode == "docx":
            converter = None
            if op_mode == "plain":
                converter = TxtHandler(rule_file)
            elif op_mode == "docx":
                converter = DocxHandler(rule_file)
            converter.map_fonts(original_file_path=args.input, output_file_path=args.output, from_font=args.font,
                                to_font=args.outputfont, components=splitnclean(args.docxcomponents),
                                known_unicode_fonts=splitnclean(args.knownunicodefonts))
            print("The converted file is saved as : {}".format(args.output))
        else:
            print("Unsupported operation mode")
    except MapFileNotFoundException:
        print("Cannot find the map file '{}'".format(rule_file))
    except NoMapForOriginException:
        print("The mapping for selected origin font does not exist")
    except FileNotFoundError:
        print("Cannot find the input file at '{}'".format(args.input))
    except json.decoder.JSONDecodeError:
        print("Invalid mapping file. {}".format(rule_file))
    except UnsupportedMapToException:
        print("Cannot map to given output font ! ({}) ".format(args.outputfont))
    except TxtAutoModeException:
        print("Font auto detection does not work on plain text files :(")
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError, ET.ParseError):
        print("The type of file '{}' either does not match the conversion mode (-m) or "
              "the file is corrupted.".format(args.input))
    except PermissionError:
        print("Permission denied to read the input file or write the output file.")
