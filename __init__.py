if __name__ == "__main__":
    import argparse
    import json
    import os
    import zipfile
    from base.docxhandler import DocxHandler as dh
    from base.exceptions import *
    from base.fontmapper import FontMapper as fm
    from base.txthandler import TxtHandler as th
    about = """ 
    Created by : Sabin Acharya (@trippygeese on github)
    License    :       
    Version    : v0.1A
    Email      : sabin2059@protonmail.com
    """
    modes = ['string', 'plain', 'docx']
    parser = argparse.ArgumentParser(description=about, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-V', '--version', action='version', version="0.1a")
    parser.add_argument('-m', '--mode', dest='mode', help='Conversion mode ', choices=modes, required=True)
    parser.add_argument('-f', '--font', dest='font', help='Font used in input file. ("auto" can be used for docx mode)', default='preeti', required=True)
    parser.add_argument('-i', '--input', dest='input', help='Input string or filepath', required=True)
    parser.add_argument('-o', '--output', dest='output', help='Output file path. Not required for string mode')
    parser.add_argument('-mf', '--map-file', dest='mapfile', help='Mapping defination file')
    args = parser.parse_args()
    font = args.font
    op_mode = args.mode
    rule_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "map.json")
    if args.mapfile is not None:
        rule_file = args.mapfile
    print("Using map file: "+rule_file)
    if op_mode == "string":
        try:
            converter = fm(rule_file)
            print(converter.map_to_unicode(args.input, args.font))
        except NoMapForOriginException:
            print("The mapping for selected origin font does not exist")
        except FileNotFoundError:
            print("Mapping defination file cannot be opened or does not exist.")
        except json.decoder.JSONDecodeError:
            print("Invalid mapping defination file")
        #except Exception as e:
        #    print("Unexpected error... Exiting !  "+str(e))
    elif op_mode == "plain" or op_mode == "docx":
        converter = None
        try:
            if op_mode == "plain":
                converter = th(rule_file)
            elif op_mode == "docx":
                converter = dh(rule_file)
            converter.map_fonts(args.input, args.output, args.font)
            print("Converted !")
        except NoMapForOriginException:
            print("The mapping for selected origin font does not exist")
        except FileNotFoundError:
            print("Mapping defination file cannot be opened or does not exist.")
        except json.decoder.JSONDecodeError:
            print("Invalid mapping defination file")
        except UnsupportedMapToException:
            print("Cannot map to given output font !")
        except TxtAutoModeException:
            print("Font autodetection does not work on txt files :(")
        except zipfile.BadZipFile:
            print("Improper docx file")
        except Exception as e:
            print("Unexpected error... Exiting !  "+str(e))
    else:
        print("Unsupported operation mode")
else:
    from .base.fontmapper import *
    from .base.docxhandler import *
    from .base.txthandler import *
    from .base.exceptions import *
