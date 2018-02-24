from io import StringIO, BytesIO
from z3c.rml import document
from django.template.loader import render_to_string
from lxml import etree


class BasePDFCreator(object):
    def __init__(self, template_name, data):
        self.template_name = template_name
        self.data = data

    def create(self):
        buffer = StringIO()
        rml = render_to_string(self.template_name, self.data)

        buffer.write(rml)
        buffer.seek(0)
        root = etree.parse(buffer).getroot()
        doc = document.Document(root)

        new_buffer = BytesIO()
        doc.process(new_buffer)
        
        return new_buffer
