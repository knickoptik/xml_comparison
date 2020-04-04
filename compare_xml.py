try:
    import xml.etree.ElementTree as ET
    import os
    import sys
    import logging
    import unittest
    import xml.sax as sax
    import xml.sax.handler as saxhandler
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

    def get_children(self, tree):
        return list(tree.iter())

    def find_tag(self, root, tag_name):
        for tag in root.iter(tag_name):
            return tag

    def get_attribute(self, tag):
        return tag.attrib

    def view_tree(self, element):
        return logger.debug(ET.tostring(element, encoding='utf8').decode('utf8'))

    def find_tag_xpath(self, tree, item: str):
        for location in tree.findall('.//' + item):
            logger.debug('Tag located at: ' + location.tag)
            return location

    def get_parent_nodes(self, tree, node):
        children = self.get_children(tree)
        logger.debug('Complete form tree: ' + str(children))
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
    hierarchy_prod = dict()
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
                form = cls.parser.find_tag(root, 'formular')
                form_id = str(cls.parser.get_attribute(form).get('id'))
                contract_number = cls.parser.find_tag(root, 'v_vertragsnummer')
                cls.documents[file] = Document(form_id, contract_number, root)
            except ET.ParseError as e:
                logger.error('File ' + file + ' cannot be parsed.\n' + str(e))

    def test_tag_differences(self):
        children_prod = self.parser.get_children(self.get_document(0).form)
        children_test = self.parser.get_children(self.get_document(1).form)
        tags_prod = self.get_tags(children_prod)
        tags_test = self.get_tags(children_test)
        tags_prod = set(tags_prod)
        tags_test = set(tags_test)

        diff_prod_to_test = tags_prod.difference(tags_test)
        diff_prod_to_test = list(diff_prod_to_test)

        logger.debug('Difference tags prod -> test: ' + str(diff_prod_to_test))

        diff_test_to_prod = tags_test.difference(tags_prod)
        diff_test_to_prod = list(diff_test_to_prod)

        logger.debug('Difference tags test -> prod: ' + str(diff_test_to_prod))

        for i in range(len(diff_prod_to_test)):
            location = self.parser.find_tag_xpath(self.get_document(0).form, diff_prod_to_test[i])
            parent_nodes = self.parser.get_parent_nodes(self.get_document(0).form, location)
            tags = self.get_tags(parent_nodes)
            # Use list comprehension to make tags more readable.
            tags = ['<' + s + '>' for s in tags]
            # Remove list brackets.
            tags = (', '.join(tags))
            logger.info('Difference prod -> test: ' + tags)

    def test_text_differences(self):
        children_prod = self.parser.get_children(self.get_document(0).form)
        children_test = self.parser.get_children(self.get_document(1).form)
        texts_prod = self.get_texts(children_prod)
        texts_test = self.get_texts(children_test)
        texts_prod = set(texts_prod)
        texts_test = set(texts_test)
        #logger.debug(texts_prod.difference(texts_test))
        #logger.debug(texts_test.difference(texts_prod))

# todo: Compare all tags and texts -> log mismatches.
# todo: Save level of each element in root tree to retain knowledge about hierarchy.
# todo: Encapsulation -> Getter and setter for object properties.
# todo: Differences are recorded twice.


if __name__ == "__main__":
    unittest.main()

# if self.compare_form_id() and self.compare_contract_number():
#     for node_1 in self.get_document(0).form.iter():
#         for node_2 in self.get_document(1).form.iter():
#             if node_1.tag == node_2.tag:
#                 logger.error('Tags match: ' + node_1.tag + ' ' + node_2.tag)

# def test_print_tree_recursive(self):
#     root = self.get_document(0).form
#     self.parser.perf_func(root, self.parser.print_level)
