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
    def __init__(self, documents: dict):
        self.documents = documents

    def get_root(self, file):
        tree = ET.parse(file)
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
    parser: Parser = None

    def get_document(self, index):
        return list(self.documents.items())[index][1]

    def compare_form_id(self):
        try:
            self.assertEqual(self.get_document(0).form_id, self.get_document(1).form_id)
            logger.info('Form Ids match.')
        except AssertionError as e:
            logger.error('Form Ids do not match.\n' + str(e))
        else:
            return True

    def compare_contract_number(self):
        try:
            self.assertEqual(self.get_document(0).contract_number.text, self.get_document(1).contract_number.text)
            logger.info('Contract numbers match.')
        except AssertionError as e:
            logger.error('Contract numbers do not match.\n' + str(e))
        else:
            return True

    def file_is_xml(self, file):
        try:
            file.endswith('.xml')
        except TypeError as e:
            logger.error('File is not in xml format.\n' + str(e))

    @classmethod
    def setUpClass(cls):
        logger.debug('Parsing documents.')
        cls.parser = Parser(cls.documents)
        for file in os.listdir('data'):
            try:
                root = cls.parser.get_root('data/' + file)
                xml = cls.parser.find_tag(root, 'formular')
                form_id = str(cls.parser.get_attribute(xml).get('id'))
                contract_number = cls.parser.find_tag(root, 'v_vertragsnummer')
                cls.documents[file] = Document(form_id, contract_number, xml)
            except ET.ParseError as e:
                logger.error('File ' + file + ' cannot be parsed.\n' + str(e))

    def test_compare_documents(self):
        if self.compare_form_id() and self.compare_contract_number():
            logger.debug('Comparing documents.')


# todo: Compare all tags and texts --> log mismatches.
# todo: Log where in the hierarchy of the xml - document the error occured.


if __name__ == "__main__":
    unittest.main()
