try:
    import xml.etree.ElementTree as ET
    import os
    import sys
    import logging
    import unittest
except ImportError as e:
    logging.critical('Importing dependency failed with error: ' + e)


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
    def setUp(self):
        documents = dict()
        logger.info('Parsing documents.')
        for file in os.listdir('data'):
            try:
                if file.endswith('.xml'):
                    parser = Parser('data/' + file, documents)
                    root = parser.get_root()
                    xml = parser.find_tag(root, 'formular')
                    form_id = str(parser.get_attribute(xml).get('id'))
                    contract_number = parser.find_tag(root, 'v_vertragsnummer')
                    # todo: Document name should be given automatically.
                    documents[file] = Document(form_id, contract_number, xml)
                else:
                    logger.error('File is not in xml format.')
                    raise TypeError
            except ET.ParseError as e:
                logger.error('File ' + file + ' cannot be parsed.\n' + str(e))

    def test_compare(self):
        self.assertTrue(1 == 2)


# todo: Compare all tags and texts --> log mismatches.
# todo: Log where in the hierarchy of the xml - document the error occured.


if __name__ == "__main__":
    # Log output of test runner to log file.
    # log_file = 'comparison.log'
    # with open(log_file, 'w') as f:
    #     runner = unittest.TextTestRunner(f)
    #     unittest.main(testRunner=runner)
    unittest.main()
