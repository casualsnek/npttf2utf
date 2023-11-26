import re
import json
import html
from .exceptions import NoMapForOriginException, MapFileNotFoundException
from .preetimapper import convert as pmconvert
import os


class FontMapper:
    def __init__(self, map_json=None):
        if map_json is None:
            # If user does not provide map_json, use the default one in the project
            map_json = self.get_default_map_json()
        try:
            self.all_rules = json.load(open(map_json, 'r', encoding='utf-8'))
        except FileNotFoundError as e:
            raise MapFileNotFoundException(str(e))
        self.supported_maps = list(self.all_rules.keys())
        self.supported_maps.append("Unicode")
        self.known_devanagari_unicode_fonts = ["Kalimati", "Mangal", "Noto Sans Devanagari"]

    @staticmethod
    def get_default_map_json():
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "../map.json")

    def map_to_unicode(self, string, from_font="Preeti", unescape_html_input=False, escape_html_output=False):
        if not from_font.lower() == "unicode":
            if from_font in self.supported_maps:
                if unescape_html_input:
                    string = html.unescape(string)

                rules = self.all_rules[from_font]['rules']
                split_pattern = re.compile(r'(\s+|\S+)')
                mapped_string = ''

                for word in re.findall(split_pattern, string):
                    for rule in rules['pre-rules']:
                        word = re.sub(re.compile(rule[0]), rule[1], word)
                    mapped_word = ''.join(rules['character-map'].get(character, character) for character in word)
                    for rule in rules['post-rules']:
                        mapped_word = re.sub(re.compile(rule[0]), rule[1], mapped_word)
                    mapped_string = mapped_string + mapped_word
                if escape_html_output:
                    return html.escape(mapped_string)
                else:
                    return mapped_string
            else:
                raise NoMapForOriginException
        else:
            return string

    def map_to_preeti(self, string, from_font="Preeti", unescape_html_input=False, escape_html_output=False):
        if unescape_html_input:
            string = html.unescape(string)
        if not from_font.lower() == "preeti":
            # Map the string to unicode first
            unicode_mapped_string = self.map_to_unicode(string, from_font)
            # Now map the unicode to preeti
            mapped_string = pmconvert(unicode_mapped_string)
            if escape_html_output:
                return html.escape(mapped_string)
            else:
                return mapped_string
        else:
            return string
