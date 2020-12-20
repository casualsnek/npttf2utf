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

    def __get_xml(self, docx_file_path):
        with zipfile.ZipFile(docx_file_path) as zf:
            with zf.open('word/document.xml') as xf:
                xml_content = xf.read().decode('utf-8')
        return xml_content

    def __save_docx(self, xml_content, output_file_path, orginal_file_path):
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(orginal_file_path, 'r') as zipObj:
            zipObj.extractall(tmp_dir)
            filenames = zipObj.namelist()
        with open(os.path.join(tmp_dir,'word/document.xml'), 'w') as f:
            f.write(xml_content)
        with zipfile.ZipFile(output_file_path, "w") as docx:
            for filename in filenames:
                docx.write(os.path.join(tmp_dir,filename), filename)
        shutil.rmtree(tmp_dir)
        return True

    def __register_namespaces(self, xml):
        namespaces = dict([node for _, node in ET.iterparse(xml, events=['start-ns'])])
        for ns in namespaces:
            ET.register_namespace(ns, namespaces[ns])
    
    def __handleWPContainersInParagraphs(self, paragraphs, from_font="auto", to_font="unicode"):
        for paragraph in paragraphs:
            for relation in paragraph.iterfind("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r"):
                relation_property = relation.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr")
                if relation_property is not None:
                    font_property = relation_property.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
                    used_font = "dummYFontThatWillNeverBeUsed"
                    text_container = relation.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
                    if font_property is not None:
                        used_font = font_property.attrib.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii", "dummYFontThatWillNeverBeUsed")
                        font_property.attrib = {key:value for key,value in font_property.attrib.items() if not key in ["{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii", "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hansi"]}
                        font_property.attrib["{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs"] = self.default_unicode_font_name
                    if text_container is not None:
                        orginal_text = text_container.text
                        if from_font == "auto":
                            if used_font in self.supported_ttf_fonts:
                                if to_font == "unicode":
                                    text_container.text = self.mapper.map_to_unicode(orginal_text, used_font, True)
                                else:
                                    raise UnsupportedMapToException
                        else:
                            if to_font == "unicode":
                                text_container.text = self.mapper.map_to_unicode(orginal_text, from_font, True)
                            else:
                                raise UnsupportedMapToException
        return True

    
    def detect_used_fonts(self, docx_file_path):
        detected_supported_fonts = []

        tree = ET.ElementTree(ET.fromstring(self.__get_xml(docx_file_path)))
        root = tree.getroot()

        font_property_containers = root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
        for container in font_property_containers:
            used_font = container.attrib.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii", "SomeUnsupportedFonts6576")
            if used_font in self.supported_ttf_fonts and used_font not in detected_supported_fonts:
                detected_supported_fonts.append(used_font)
        return detected_supported_fonts

    def map_fonts(self, orginal_file_path, output_file_path="mapped.docx", from_font="auto", to_font="unicode", components=["body_paragraph", "table", "shape"]):
        xml_string = self.__get_xml(orginal_file_path)
        tree = ET.ElementTree(ET.fromstring(xml_string))
        root = tree.getroot()
        # GET INSIDE DA BODIE
        for body in root.iterfind("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body"):
            general_paragraphs = body.iterfind("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p") # Using iterfind instead as we dont need list here, generator seems better opttion

            # Process normal paragraphs. They (w:p) lie directly inside body as child
            if "body_paragraph" in components:
                self.__handleWPContainersInParagraphs(general_paragraphs, from_font=from_font, to_font=to_font)

            # Process paragraphs. They (w:p) lie inside "w:tbl" as child of table row and column, but we can just iterate inside table to get them
            if "table" in components:
                for table in body.iterfind("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl"):
                    # Now since we are not direct child of normal paragraphs but inside a table, We can use .iter() to get all the paragraphs inside current table without modifying other components
                    paragraphs = table.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
                    self.__handleWPContainersInParagraphs(paragraphs, from_font=from_font, to_font=to_font)
            
            # Process shapes. They lie inside "w:p" (Main paragraphs), find them. Shapes wont be processed in "body_paragraph" and SHOULD NOT BE as content in shape lie much deeper 
            if "shape" in components:
                for paragraph in general_paragraphs:
                    tbx_content = wps_txbx.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}txbxContent") # They contain  data for (t)e(x)t(b)o(x)/Shapes. They content another "w:p" which has actual text content
                    for txbx in txbxContent:
                        paragraphs = txbx.iterfind("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")
                        self.__handleWPContainersInParagraphs(paragraphs, from_font=from_font, to_font=to_font)
        tmp_dir = tempfile.mkdtemp()
        self.__register_namespaces(StringIO(xml_string))
        tree.write(os.path.join(tmp_dir, "document.xml"), encoding="utf-8", xml_declaration=True)
        with open(os.path.join(tmp_dir, "document.xml"), "r") as f:
            xml_content = f.read()
        self.__save_docx(xml_content, output_file_path, orginal_file_path)
        shutil.rmtree(tmp_dir)
