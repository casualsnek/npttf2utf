from .fontmapper import FontMapper
from .exceptions import TxtAutoModeException, UnsupportedMapToException


class TxtHandler:

    def __init__(self, rules_file):
        self.mapper = FontMapper(rules_file)
        self.supported_ttf_fonts = self.mapper.supported_maps

    @staticmethod
    def detect_used_fonts(self, txt_file_path):
        return []

    def map_fonts(self, original_file_path, output_file_path="mapped.txt", from_font="Preeti", to_font="unicode",
                  components=[], known_unicode_fonts=[]):
        if from_font != "auto":
            with open(original_file_path, "r", encoding="utf-8") as original_file:
                lines_original = original_file.readlines()
            output_file = open(output_file_path, "w")
            for line in lines_original:
                if to_font.lower() == "unicode":
                    output_file.write(self.mapper.map_to_unicode(line, from_font, False))
                elif to_font.lower() == "preeti":
                    output_file.write(self.mapper.map_to_preeti(line, from_font, False))
                else:
                    raise UnsupportedMapToException
            output_file.close()
        else:
            raise TxtAutoModeException
        return True
