from xml.etree import ElementTree as ET
from io import StringIO
from .fontmapper import FontMapper
from .exceptions import UnsupportedMapToException
import os
import zipfile
import tempfile
import shutil


class DocxHandler:

    def __init__(self, rules_file, default_unicode_font_name="Kalimati"):
        self.mapper = FontMapper(rules_file)
        self.supported_ttf_fonts = self.mapper.supported_maps
        self.default_unicode_font_name = default_unicode_font_name
        self.known_devanagari_unicode_fonts = ["Kalimati", "Mangal", "Noto Sans Devanagari"]

    @staticmethod
    def __get_xml(docx_file_path):
        with zipfile.ZipFile(docx_file_path) as zf:
            with zf.open('word/document.xml') as xf:
                xml_content = xf.read().decode('utf-8')
        return xml_content

    @staticmethod
    def __save_docx(xml_content, output_file_path, original_file_path):
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(original_file_path, 'r') as zipObj:
            zipObj.extractall(tmp_dir)
            filenames = zipObj.namelist()
        with open(os.path.join(tmp_dir, 'word/document.xml'), 'w') as f:
            f.write(xml_content)
        with zipfile.ZipFile(output_file_path, "w") as docx:
            for filename in filenames:
                docx.write(os.path.join(tmp_dir, filename), filename)
        shutil.rmtree(tmp_dir)
        return True

    @staticmethod
    def __register_namespaces(xml):
        namespaces = dict([node for _, node in ET.iterparse(xml, events=['start-ns'])])
        for ns in namespaces:
            ET.register_namespace(ns, namespaces[ns])

    @staticmethod
    def __get_font_data_from_relation_property(relation_property):
        used_font = "dummyFontThatWillNeverBeUsed"
        used_unicode_font = "dummyFontThatWillNeverBeUsed"
        font_property = relation_property.find(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
        if font_property is not None:
            try:
                used_font = font_property.attrib[
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii"
                ]
            except KeyError:
                used_unicode_font = font_property.attrib[
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs"
                ]
                used_font = "unicode"
        return font_property, used_font, used_unicode_font

    def __map_now(self, map_to, font_property, text_container=None, used_font=None):
        # Strip un necessary font related attributes. Make it minimal.. Word processor
        # will add them back if necessary
        font_property.attrib = self.__strip_font_attributes(font_property.attrib)
        if map_to.lower() == "preeti":
            font_property.attrib[
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii"
            ] = "Preeti"
            font_property.attrib[
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi"
            ] = "Preeti"
            # Replace original text with mapped text
            if text_container is not None:
                original_text = text_container.text
                text_container.text = self.mapper.map_to_preeti(original_text, used_font, True)
        elif map_to.lower() == "unicode":
            font_property.attrib[
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs"
            ] = self.default_unicode_font_name
            # Replace original text with mapped text
            if text_container is not None:
                original_text = text_container.text
                text_container.text = self.mapper.map_to_unicode(original_text, used_font, True)
        else:
            raise UnsupportedMapToException("Document cannot be mapped to target ")

    @staticmethod
    def __strip_font_attributes(dictionary):
        # Don't know why but removing cstheme and eastAsiaTheme does magic and fixes map to incorrect font
        # So yes.... This is needed
        return {key: value for key, value in dictionary.items()
                if key not in [
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cstheme",
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsiaTheme",
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii",
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi",
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs"
                ]}

    def __handle_wp_containers_in_paragraphs(self, paragraphs, from_font="auto", to_font="unicode",
                                             known_unicode_fonts=None):
        if known_unicode_fonts is None:
            known_unicode_fonts = []
        for paragraph in paragraphs:
            for relation in paragraph.iterfind("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r"):
                relation_property = relation.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr")
                if relation_property is not None:
                    font_property, used_font, used_unicode_font = self.__get_font_data_from_relation_property(
                        relation_property
                    )
                    text_container = relation.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
                    if text_container is not None:
                        continue_mapping = True
                        set_from_font = None
                        if from_font == "auto":
                            # Check if the used font is in supported ttf fonts + "unicode"
                            if used_font in self.supported_ttf_fonts:
                                set_from_font = used_font
                                if to_font == "Preeti":
                                    if used_unicode_font not in (self.known_devanagari_unicode_fonts +
                                                                 known_unicode_fonts + self.supported_ttf_fonts):
                                        continue_mapping = False
                            else:
                                continue_mapping = False
                        else:
                            # Since this is manual mode.. Do no checks and set used font to the font set to "from_font"
                            # variable. This will change font of whole document to "to_font", every text content will
                            # be interpreted as "from_font" and will be mapped to "to_font"
                            # Exception will be thrown while trying to map from/to unsupported fonts
                            set_from_font = from_font
                        # All checks must have been done. Now start mapping the fonts
                        if continue_mapping:
                            self.__map_now(to_font, font_property,
                                           text_container=text_container,
                                           used_font=set_from_font)

            # A "Not so quick" fix for pPr inside w:p inside "w:txbxcontent"
            for paragraph_property in paragraph.iterfind(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr"):
                relation_property = paragraph_property.find(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr")
                if relation_property is not None:
                    font_property, used_font, used_unicode_font = self.__get_font_data_from_relation_property(
                        relation_property
                    )
                    continue_mapping = True
                    # If on auto auto mode, only change base font when mapping is possible
                    if from_font == "auto":
                        if used_font in self.supported_ttf_fonts:
                            if to_font == "Preeti":
                                if used_unicode_font not in (self.known_devanagari_unicode_fonts +
                                                             known_unicode_fonts + self.supported_ttf_fonts):
                                    continue_mapping = False
                        else:
                            continue_mapping = False
                    if continue_mapping:
                        self.__map_now(to_font, font_property)
        return True

    def detect_used_fonts(self, docx_file_path):
        detected_supported_fonts = []

        tree = ET.ElementTree(ET.fromstring(self.__get_xml(docx_file_path)))
        root = tree.getroot()

        font_property_containers = root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
        for container in font_property_containers:
            used_font = container.attrib.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii",
                                             "SomeUnsupportedFonts6576")
            if used_font in self.supported_ttf_fonts and used_font not in detected_supported_fonts:
                detected_supported_fonts.append(used_font)
        return detected_supported_fonts

    def map_fonts(self, original_file_path, output_file_path="mapped.docx", from_font="auto", to_font="unicode",
                  components=None, known_unicode_fonts=None):
        if known_unicode_fonts is None:
            known_unicode_fonts = []
        if components is None:
            components = ["body_paragraph", "table", "shape"]
        xml_string = self.__get_xml(original_file_path)
        tree = ET.ElementTree(ET.fromstring(xml_string))
        root = tree.getroot()
        # GET INSIDE DA BODIE
        for body in root.iterfind("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body"):
            # Process normal paragraphs. They (w:p) lie directly inside body as child
            general_paragraphs = body.findall("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
            if "body_paragraph" in components:
                self.__handle_wp_containers_in_paragraphs(general_paragraphs,
                                                          from_font=from_font,
                                                          to_font=to_font,
                                                          known_unicode_fonts=known_unicode_fonts)

            # Process paragraphs. They (w:p) lie inside "w:tbl" as child of table row and column, but we can just
            # iterate inside table to get them
            if "table" in components:
                for table in body.iterfind("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl"):
                    # Now since we are not direct child of normal paragraphs but inside a table, We can use .iter()
                    # to get all the paragraphs inside current table without modifying other components
                    paragraphs = table.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
                    self.__handle_wp_containers_in_paragraphs(paragraphs,
                                                              from_font=from_font,
                                                              to_font=to_font,
                                                              known_unicode_fonts=known_unicode_fonts)

            # Process shapes. They lie inside "w:p" (Main paragraphs), find them. Shapes wont be processed in
            # "body_paragraph" and SHOULD NOT BE as content in shape lie much deeper
            if "shape" in components:
                for paragraph in general_paragraphs:
                    tbx_content = paragraph.iter(
                        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}txbxContent")
                    # They contain  data for (t)e(x)t(b)o(x)/Shapes. They content another "w:p" which has actual
                    # text content
                    for txbx in tbx_content:
                        paragraphs = txbx.iterfind(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
                        self.__handle_wp_containers_in_paragraphs(paragraphs,
                                                                  from_font=from_font,
                                                                  to_font=to_font,
                                                                  known_unicode_fonts=known_unicode_fonts)

        # Make a temp directory for working, extract the original docx file in that temp directory
        # Replace content of document.xml in temporary directory with modified xml data . Repack everything back
        # And save the resulting package with the passed filename

        tmp_dir = tempfile.mkdtemp()
        self.__register_namespaces(StringIO(xml_string))
        tree.write(os.path.join(tmp_dir, "document.xml"), encoding="utf-8", xml_declaration=True)
        with open(os.path.join(tmp_dir, "document.xml"), "r") as f:
            xml_content = f.read()
        self.__save_docx(xml_content, output_file_path, original_file_path)
        shutil.rmtree(tmp_dir)
