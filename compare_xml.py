try:
    from lxml import etree
    import os
    import sys
    import logging
    import unittest
except ImportError as e:
    logging.critical('Importing dependency failed with error: ' + str(e))


logging.basicConfig(
    filename='compare_xml.log',
    level=logging.INFO, filemode='w',
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

    def parse_file(self, xml):
        parser = etree.XMLParser(remove_comments=True)
        return etree.parse(xml, parser)

    def get_children(self, tree):
        return list(tree.iter())

    def find_tag(self, root, tag_name):
        for tag in root.iter(tag_name):
            return tag

    def get_attribute(self, tag):
        return tag.attrib

    def find_tag_by_name_xpath(self, tree, item: str):
        for location in tree.findall('.//' + item):
            logger.debug('Tag located at: ' + location.tag)
            return location

    def find_tag_by_text_xpath(self, tree, item: str):
        for location in tree.xpath('.//*[contains(text(),"{}")]'.format(item)):
            logger.debug('Tag located at: ' + location.tag)
            return location

    def get_parent_nodes(self, tree, node):
        children = self.get_children(tree)
        temp = children.index(node) + 1
        res = children[:temp]
        logger.debug('Parent nodes are: ' + str(res))
        return res

    def view_tree_levels(self, elem, func, level=0):
        """
        Recursive function that records the level of an element in the
        tree and prints the elements position.
        """
        func(elem, level)
        # todo: Replace getchildren.
        for child in elem.getchildren():
            self.view_tree_levels(child, func, level+1)

    def print_level(self, elem, level):
        logger.debug(' '*level + '<' + elem.tag + '>')


class CompareXml(unittest.TestCase):
    documents = dict()
    parser: Parser = None

    def get_document(self, index):
        return list(self.documents.items())[index][1]

    def get_tags(self, elements):
        tags = []
        for element in elements:
            tags.append(element.tag)
        return tags

    def get_texts(self, elements):
        texts = []
        for element in elements:
            texts.append(element.text)
        return texts

    def compare_form_id(self):
        try:
            self.assertEqual(self.get_document(0).form_id, self.get_document(1).form_id)
            logger.debug('Form Ids match.')
        except AssertionError as e:
            logger.error('Form Ids do not match.\n' + str(e))
        else:
            return True

    def compare_contract_number(self):
        try:
            self.assertEqual(self.get_document(0).contract_number.text, self.get_document(1).contract_number.text)
            logger.debug('Contract numbers match.')
        except AssertionError as e:
            logger.error('Contract numbers do not match.\n' + str(e))
        else:
            return True

    def check_preconditions(self):
        if self.compare_form_id() and self.compare_contract_number():
            logger.info('Starting test suite for contract number ' + str(self.get_document(0).contract_number.text) + '\n')
        else:
            logger.error('Exiting test.')
            raise AssertionError

    def file_is_xml(self, file):
        try:
            file.endswith('.xml')
        except TypeError as e:
            logger.error('File is not in xml format.\n' + str(e))

    def localize_difference(self, form, location):
        parent_nodes = self.parser.get_parent_nodes(form, location)
        location = self.get_tags(parent_nodes)
        # Use list comprehension to make tags more readable.
        location = ['<' + s + '>' for s in location]
        # Remove list brackets.
        location = (', '.join(location))
        return location

    # todo: No message in case there are no differences.
    def report_tag_differences(self, diff, form, message):
        for i in range(len(diff)):
            difference = self.parser.find_tag_by_name_xpath(form, diff[i])
            location = self.localize_difference(form, difference)
            logger.info('{}: Tag located at {}\n'.format(message, location))

    def report_text_differences(self, diff, form, message):
        for i in range(len(diff)):
            difference = self.parser.find_tag_by_text_xpath(form, diff[i])
            location = self.localize_difference(form, difference)
            logger.info('{}: "{}" located at {}\n'.format(message, difference.text, location))

    @classmethod
    def setUpClass(cls):
        logger.debug('Parsing documents.')
        cls.parser = Parser(cls.documents)
        precondition = CompareXml()
        for file in os.listdir('data'):
            try:
                tree = cls.parser.parse_file('data/' + file)
                root = tree.getroot()
                form = cls.parser.find_tag(root, 'formular')
                form_id = str(cls.parser.get_attribute(form).get('id'))
                contract_number = cls.parser.find_tag(root, 'v_vertragsnummer')
                cls.documents[file] = Document(form_id, contract_number, root)
            except etree.ParseError as e:
                logger.error('File ' + file + ' cannot be parsed.\n' + str(e))
        precondition.check_preconditions()

    def retrieve_differences(self, list_prod, list_test):
        # Get all node tags.
        tags_prod = set(list_prod)
        tags_test = set(list_test)
        diff_prod_to_test = tags_prod.difference(tags_test)
        diff_prod_to_test = list(diff_prod_to_test)
        logger.debug('Difference texts prod -> test: ' + str(diff_prod_to_test))
        diff_test_to_prod = tags_test.difference(tags_prod)
        diff_test_to_prod = list(diff_test_to_prod)
        logger.debug('Difference texts test -> prod: ' + str(diff_test_to_prod))
        return [diff_prod_to_test, diff_test_to_prod]

    # todo: Eventuell refactoring: Differences ermitteln tags / texts.
    def test_tag_differences(self):
        logger.info('Checking xml files for differences in tags.\n')
        # Get all nodes.
        children_prod = self.parser.get_children(self.get_document(0).form)
        children_test = self.parser.get_children(self.get_document(1).form)

        tags_prod = self.get_tags(children_prod)
        tags_test = self.get_tags(children_test)

        # todo: Test Suite passes when no differences are found and reports success.
        # if len(diff_test_to_prod) == 0:
        diff = self.retrieve_differences(tags_prod, tags_test)

        self.report_tag_differences(diff[0], self.get_document(0).form, 'Difference prod -> test')
        self.report_tag_differences(diff[1], self.get_document(1).form, 'Difference test -> prod')

    def test_text_differences(self):
        logger.info('Checking xml files for differences in text content.\n')
        children_prod = self.parser.get_children(self.get_document(0).form)
        children_test = self.parser.get_children(self.get_document(1).form)

        texts_prod = self.get_texts(children_prod)
        texts_test = self.get_texts(children_test)

        diff = self.retrieve_differences(texts_prod, texts_test)

        self.report_text_differences(diff[0], self.get_document(0).form, 'Difference prod -> test')
        self.report_text_differences(diff[1], self.get_document(1).form, 'Difference test -> prod')

# todo: Check for differences in attributes.
# todo: Encapsulation -> Getter and setter for object properties.
# todo: User friendly report at INFO level.


if __name__ == "__main__":
    unittest.main()

# def test_print_tree_recursive(self):
#     root = self.get_document(0).form
#     self.parser.perf_func(root, self.parser.print_level)
