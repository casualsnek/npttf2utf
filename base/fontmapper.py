import re
import json
import html
from .exceptions import NoMapForOriginException

class FontMapper():
	"""docstring for FontMapper"""
	def __init__(self, map_json):
		self.all_rules = json.load(open(map_json, 'r'))
		self.supported_maps = list(self.all_rules.keys())
        
	def map_to_unicode(self, string, from_font="Preeti", unescape_html=False):
		if from_font in self.supported_maps:
			if unescape_html:
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
				mapped_string = mapped_string+mapped_word
			if unescape_html:
				return html.escape(mapped_string)
			else:
				return mapped_string
		else:
			raise NoMapForOriginException
		
