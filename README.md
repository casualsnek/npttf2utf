# **npTTF2UTF**

Python module/script to map Nepali ASCII font faces like Preeti, Sagarmatha, and more to devanagari unicode

This is mainly a python module to help in mapping of various nepali ASCII fontfaces to its unicode counterpart ~~and unicode back to Preeti font face~~. It currently supports directly mapping passed strings (fontmapper.py) as well font auto detection and selective component selection for docx files (docxhandler.py) and plaintext files (txthandler.py).

**Requirements**
- python3

<br>

## **Usage**

### **1) As standalone script**
```
$ git clone https://github.com/trippygeese/npttf2utf.git
$ cd npttf2utf
$ python __init__.py -m [mode] -f [origin font] -i [input file/string] -o [output file] -mf [mapping defination]
```
**Parameters:**

| Parameter | Help/Usage |
|--|--|
| -h*  | Shows help and information about the program |
| -v*  | Shows version information |
| -m  | Usage mode. "string" to pass input string and output on console window, "docx" for working on docx files and "plain" for working with plaintext files |
| -f  | The font face which  was used for the string or creating the file. In "docx" mode you can use "auto" to autodetect used fonts and map them |
| -i  | Input string or path to input file |
| -o*  | Path to output file. Not required for "string" mode|
| -mf*  | Path to mapping defination file. If not passed it will look for "map.json" in current script directory|

*Note: The parameters marked with * are optional*

Example usage:

1. To pass string in Preeti in terminal and map it to unicode ("string" mode)
```
$ python __init__.py -m string -f Preeti -i "asdfghjk"
```
It will map "asdfghjk" to unicode following mapping for Preeti and output "बकमानजवप"

.

2. To convert docx or txt file ("plain"/"docx" mode)
```
$ python __init__.py -m docx -f auto -i "document_with_ASCII_font_faces.docx" -o "document_mapped_to_unicode.docx"
```
It will map the content of document to unicode  and save it as "document_mapped_to_unicode.docx" ("auto" as font is available for "docx" mode only)

<br>

### **2) As python module**
- Clone the repository
- Import the module

```
$ git clone https://github.com/trippygeese/npttf2utf.git
$ python
>> import npttf2utf
```

<br>

## **Class: npttf2utf.FontMapper**

"npttf2utf.FontMapper" class can be used to map the fonts to their unicode conterpart. It is also the base for other document converters


### **Method: \_\_init \_\_**

This method initializes the FontMapper class
```
def __init__(self, map_json):
```
Returns: None

| Argument | Description |  Optional |
|--|--|--|
| map_json | Path to mapping defination file (Must be readable by current user) |  False |

<br>

### **Method: map_to_unicode**

This method maps the passed string written passed origin font to unicode using the mapping defination
```
def map_to_unicode(self, string, from_font="Preeti", unescape_html=False):
```
Returns: String

| Argument | Description |  Optional |
|--|--|--|
| string | String to map |  False |
| from_font | The origin font in which string was written. Defaults to "Preeti" if not passed|  True |
| unescape_html | Pass True if the string needs to be html unescaped.  (Defaults to False) |  True |

Example usage:

```
>> import npttf2utf
>> mapper = npttf2utf.FontMapper("npttf2utf/map.json")
>> mapper.map_to_unicode("asdfghjk", from_font="Preeti", unescape_html=False)
बकमानजवप
>> 
```

<br>

## **Class: npttf2utf.DocxHandler**

"npttf2utf.DocxHandler" class can be used to map docx files to unicode and save them


### **Method: \_\_init \_\_**

This method initializes the DocxHandler class which can be used to map docx files
```
def __init__(self, rules_file, default_unicode_font_name="Kalimati"):
```
Returns: None

| Argument | Description |  Optional |
|--|--|--|
| rules_file | Path to mapping defination file (Must be readable by current user) |  False |
| default_unicode_font_name | The name of font which will be set for converted segment of docx files. (Defaults to "Kalimati") |  True |

<br>

### **Method: detect_used_fonts**

This method returns list of fonts supported by mapping defination which are used in the docx file
```
def detect_used_fonts(self, docx_file_path):
```
Returns: List

| Argument | Description |  Optional |
|--|--|--|
| docx_file_path | Path to docx file whose fonts are to be detected |  False |

<br>

### **Method: map_fonts**

This method maps the font in docx file and creates new docx file with mapping applied
```
def map_fonts(self, orginal_file_path, output_file_path="mapped.docx", from_font="auto", to_font="unicode", components=["body_paragraph", "table", "shape"]):
```
Returns: None

| Argument | Description |  Optional |
|--|--|--|
| orginal_file_path | Path to docx file whose fonts are to be mapped |  False |
| output_file_path | Path where the mapped docx file is to saved (Defaults to "mapped.docx") |  True |
| from_font | The origin font in which string was written. (Defaults to "auto"). "auto" can be passed to detect used font automatically and map them accordingly and leave english characters untouched |  True |
| to_font | Target for font conversion. (Defaults to "unicode"). Only "unicode" is supported as of now |  True |
| components | [List] List of components of docx file which will be looked up for text contents. (Defaults to: ["body_paragraph", "table", "shape"]). "body_paragraph", "table" and "shape" are supported as of now|  False |

Example usage:

```
>> import npttf2utf
>> converter = npttf2utf.DocxHandler("npttf2utf/map.json", default_unicode_font_name="Kalimati")
>> converter.detect_used_fonts("document_with_ASCII_font_faces.docx")
["Preeti", "Sagarmaths"]
>> converter.map_fonts("document_with_ASCII_font_faces.docx", output_file_path="mapped_document.docx", from_font="auto", to_font="unicode", components=["body_paragraph", "table"])
>>
```

<br>

## **Class: npttf2utf.TxtHandler**

"npttf2utf.TxtHandler" class can be used to map plain text files to unicode and save them


### **Method: \_\_init \_\_**

This method initializes the TxtHandler class which can be used to map txt files
```
def __init__(self, rules_file):
```
Returns: None

| Argument | Description |  Optional |
|--|--|--|
| rules_file | Path to mapping defination file (Must be readable by current user) |  False |

<br>

### **Method: map_fonts**

This method maps the font in txt file and creates new txt file with mapping applied
```
def map_fonts(self, orginal_file_path, output_file_path="mapped.txt", from_font="Preeti", to_font="unicode", components=[]):
```
Returns: None

| Argument | Description |  Optional |
|--|--|--|
| orginal_file_path | Path to txt file whose fonts are to be mapped |  False |
| output_file_path | Path where the mapped txt file is to saved (Defaults to "mapped.txt") |  True |
| from_font | The origin font in which string was written. (Defaults to "Preeti"). |  True |
| to_font | Target for font conversion. (Defaults to "unicode"). Only "unicode" is supported as of now |  True |
| components | Serves no purpose, just there to match the method call of DocxHandler|  False |

```
>> import npttf2utf
>> converter = npttf2utf.TxTHandler("npttf2utf/map.json")
>> converter.map_fonts("txt_with_ASCII_font_faces.txt", output_file_path="mapped_txt.txt", from_font="Preeti", to_font="unicode", components=[])
>>
```
<br>

### Supported docx components

  - Text content in Textboxes/Shapes
  - General paragraphs
  - Text content in table
  
<br>

### Supported ASCII font faces

  - Preeti
  - Sagarmatha
  - Kantipur
  - fontasy_himali_tt
  - pcs_nepali
  
<br>

### Supported Output fonts

  - Devanagari Unicode

<br>

### Todos
 - Add support for headers/footers
 - Optimize the code
 - Ability to unify font to Preeti as well

### Adding support for new file type

Create a new file to handle the file type. (You can use docxhandler.py and modify it as needed). The class constructor should take map definition as the first parameter and the file handler class should contain "map_fonts" methods that take original user file, the path for converted file, from the font, to font, and a list of components as arguments. You can map a string to Unicode by using FontMapper.map_to_unicode if the mapping for origin font exists in the definition. (map_to_unicode takes unescape_html argument to that can be used to unescape HTML string before processing and escape it before returning)

### Adding mapping for a new font

Open "npttf2utf/map.json" and add a JSON key with this structure

```
"font_name":{
  "version": "v1",
  "rules": {
    "character-map": {
      "character-in-origin-font": "unicode-equivalent-character"
    },
    "pre-rules": [
      ["regex-string-search", "regex-string-replace"]
    ],
    "post-rules": [
      ["regex-string-search", "regex-string-replace"]
    ]
  }
}

```

pre-rules     - Regex find and replace to apply before mapping characters to Unicode
character map - Directly mappable character from source font to Unicode. For Preeti: a <-> ब
post-rules    - The words may not be as expected directly after mapping. So this contains regexes to find them and replace them with corrections (Regex find and replace to apply before mapping characters to Unicode)


### Feel free to use this project for any purpose and long as you comply with the license. Any contribution to the project is highly appreciated. If you find any bugs please report it