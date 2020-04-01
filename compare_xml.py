import xml.etree.ElementTree as ET
import logging


class Document:
    def __init__(self, form_id: str, contract_number: str, form: object):
        self.form_id = form_id
        self.contract_number = contract_number
        self.form = form


class Parser:
    def __init__(self, document):
        self.document = document

    def get_root(self):
        tree = ET.parse(self.document)
        return tree.getroot()

    def find_tag(self, root, tag_name):
        for tag in root.iter(tag_name):
            return tag

    def view_document(self, root):
        print(ET.tostring(root, encoding='utf8').decode('utf8'))


# todo: Only one parser instead of two parsers.
def main():
    logging.info('Parsing documents.')
    parser = Parser('VTB_Max_Muster_Produktion.xml')
    root = parser.get_root()
    parser.find_tag(root, 'formular')
    # document_production = Document()
    # document_test = Document()


if __name__ == "__main__":
    main()
