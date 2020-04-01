import xml.etree.ElementTree as ET
import os
import logging


class Document:
    def __init__(self, form_id: str, contract_number: str, form: object):
        self.form_id = form_id
        self.contract_number = contract_number
        self.form = form


class Parser:
    def __init__(self, file):
        self.file = file

    def get_root(self):
        tree = ET.parse(self.file)
        return tree.getroot()

    def find_tag(self, root, tag_name):
        for tag in root.iter(tag_name):
            return tag

    def get_attribute(self, tag):
        return tag.attrib

    def to_string(self, element):
        return ET.tostring(element, encoding='utf8').decode('utf8')



# todo: Delete all objects after comparison --> too much memory.
def main():
    logging.info('Parse documents.')
    for file in os.listdir('data'):
        try:
            parser = Parser('data/' + file)
            root = parser.get_root()
            form = parser.find_tag(root, 'formular')
            form_id = str(parser.get_attribute(form).get('id'))
            print(form_id)
            contract_number = parser.find_tag(root, 'v_vertragsnummer').text
            print(contract_number)
            document = Document(form_id, contract_number, root)
            print(document)
        except ET.ParseError as e:
            logging.warning('File ' + file + ' cannot be parsed.\n' + str(e))


if __name__ == "__main__":
    main()
