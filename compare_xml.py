# todo: Imports should be in a try/catch block.
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
    logging.basicConfig(
        filename='comparison.log',
        level=logging.DEBUG, filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )
    logging.info('Parsing documents.')
    for file in os.listdir('data'):
        try:
            parser = Parser('data/' + file)
            root = parser.get_root()
            xml = parser.find_tag(root, 'formular')
            form_id = str(parser.get_attribute(xml).get('id'))
            contract_number = parser.find_tag(root, 'v_vertragsnummer').text
            Document(form_id, contract_number, xml)
        except ET.ParseError as e:
            logging.warning('File ' + file + ' cannot be parsed.\n' + str(e))


if __name__ == "__main__":
    main()
