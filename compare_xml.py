try:
    import xml.etree.ElementTree as ET
    import os
    import sys
    import logging
    import unittest
except ImportError as e:
    logging.critical('Importing dependency failed with error: ' + str(e))


logging.basicConfig(
    filename='compare_xml.log',
    level=logging.DEBUG, filemode='w',
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
)

logger = logging.getLogger()
# Unittest module output should not overwrite logger output.
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class Document:
    def __init__(self, form_id: str, contract_number: object, form: object):
        self.form_id = form_id
        self.contract_number = contract_number
        self.form = form
        logger.debug('Created document: Form ID - {}, Contract Number - {}'.format(self.form_id, self.contract_number))


class Parser:
    def __init__(self, file: object, documents: dict):
        self.file = file
        self.documents = documents

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


class CompareXml(unittest.TestCase):
    documents = dict()

    def get_document(self, index):
        return list(self.documents.items())[index][1]

    def setUp(self):
        logger.debug('Parsing documents.')
        for file in os.listdir('data'):
            try:
                if file.endswith('.xml'):
                    parser = Parser('data/' + file, self.documents)
                    root = parser.get_root()
                    xml = parser.find_tag(root, 'formular')
                    form_id = str(parser.get_attribute(xml).get('id'))
                    contract_number = parser.find_tag(root, 'v_vertragsnummer')
                    self.documents[file] = Document(form_id, contract_number, xml)
                else:
                    logger.error('File is not in xml format.')
                    raise TypeError
            except ET.ParseError as e:
                logger.error('File ' + file + ' cannot be parsed.\n' + str(e))

    def test_compare_form_id(self):
        try:
            self.assertEqual(self.get_document(0).form_id, self.get_document(1).form_id)
            logger.info('Form Ids match.')
        except AssertionError as e:
            logger.error('Form Ids do not match.\n' + str(e))

    def test_compare_contract_number(self):
        try:
            self.assertEqual(self.get_document(0).contract_number.text, self.get_document(1).contract_number.text)
            logger.info('Contract numbers match.')
        except AssertionError as e:
            logger.error('Contract numbers do not match.\n' + str(e))

# todo: Stop test suite when form_id or contract_number do not match.
# todo: Compare all tags and texts --> log mismatches.
# todo: Log where in the hierarchy of the xml - document the error occured.


if __name__ == "__main__":
    unittest.main()
