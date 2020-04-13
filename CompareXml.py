try:
    from lxml import etree
    import os
    import sys
    import logging
    import unittest
    from collections import defaultdict
    from Document import Document
    from Parser import Parser
except ImportError as e:
    logging.critical('Importing dependency failed with error: ' + str(e))


logging.basicConfig(
    filename='compare_xml.log',
    level=logging.INFO, filemode='w',
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
)

logger = logging.getLogger(__name__)
# Unittest module output should not overwrite logger output.
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class CompareXml(unittest.TestCase):
    documents = dict()

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
            self.assertEqual(self.get_document(0).get_form_id(), self.get_document(1).get_form_id())
            logger.debug('Form Ids match.')
        except AssertionError as e:
            logger.error('Form Ids do not match.\n' + str(e))
        else:
            return True

    def compare_contract_number(self):
        try:
            self.assertEqual(self.get_document(0).get_contract_number().text, self.get_document(1).get_contract_number().text)
            logger.debug('Contract numbers match.')
        except AssertionError as e:
            logger.error('Contract numbers do not match.\n' + str(e))
        else:
            return True

    def check_preconditions(self):
        if self.compare_form_id() and self.compare_contract_number():
            logger.info('Starting test suite for contract number ' + str(self.get_document(0).get_contract_number().text) + '\n')
        else:
            logger.error('Exiting test.')
            raise AssertionError

    def localize_difference(self, form, tag):
        parent_nodes = self.parser.get_parent_nodes(form, tag)
        location = self.get_tags(parent_nodes)
        # Use list comprehension to make tags more readable.
        location = ['<' + tag_name + '>' for tag_name in location]
        # Remove list brackets.
        location = (', '.join(location))
        return location

    def report_tag_differences(self, diff: list, form, message):
        for i in range(len(diff)):
            difference = self.parser.find_tag_by_name(form, diff[i])
            location = self.localize_difference(form, difference)
            logger.info('{}: Tag located at {}\n'.format(message, location))

    def report_text_differences(self, diff: list, form, message):
        for i in range(len(diff)):
            difference = self.parser.find_tag_by_text(form, diff[i])
            location = self.localize_difference(form, difference)
            logger.info('{}: "{}" located at {}\n'.format(message, difference.text, location))

    def report_attribute_differences(self, diff: list, form, message):
        tag = diff[0]
        attribute = diff[1][0].keys()[0]
        value = diff[1][0].values()[0]
        difference = self.parser.find_tag_by_attrib(form, tag, attribute, value)
        location = self.localize_difference(form, difference)
        logger.info('{}: "{}" with attribute "{}" located at {}\n'.format(message, difference.tag, difference.attrib, location))

    def get_attributes(self, elements):
        attributes = defaultdict(list)
        for child in elements:
            if child.attrib:
                attributes[child.tag].append(child.attrib)
        logger.debug(attributes)
        return attributes

    @classmethod
    def setUpClass(cls):
        logger.debug('Parsing documents.')
        cls.parser = Parser()
        setup = CompareXml()
        for file in os.listdir('data'):
            try:
                tree = cls.parser.parse_file('data/' + file)
                root = tree.getroot()
                form = cls.parser.find_tag(root, 'formular')
                form_id = str(cls.parser.get_attribute(form).get('id'))
                contract_number = cls.parser.find_tag(root, 'v_vertragsnummer')
                setup.documents[file] = Document(form_id, contract_number, root)
            except etree.ParseError as e:
                logger.error('File ' + file + ' cannot be parsed.\n' + str(e))
        setup.check_preconditions()

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

    def test_tag_differences(self):
        logger.info('Checking xml files for differences in tags.\n')

        nodes_prod = self.parser.get_children(self.get_document(0).get_form())
        nodes_test = self.parser.get_children(self.get_document(1).get_form())

        tags_prod = self.get_tags(nodes_prod)
        tags_test = self.get_tags(nodes_test)

        diff = self.retrieve_differences(tags_prod, tags_test)

        if diff:
            self.report_tag_differences(diff[1], self.get_document(1).get_form(), 'Difference test -> prod')
            self.report_tag_differences(diff[0], self.get_document(0).get_form(), 'Difference prod -> test')
        else:
            logger.info('No differences between tags.')

    def test_text_differences(self):
        logger.info('Checking xml files for differences in text content.\n')
        nodes_prod = self.parser.get_children(self.get_document(0).get_form())
        nodes_test = self.parser.get_children(self.get_document(1).get_form())

        texts_prod = self.get_texts(nodes_prod)
        texts_test = self.get_texts(nodes_test)

        diff = self.retrieve_differences(texts_prod, texts_test)

        if diff:
            self.report_text_differences(diff[1], self.get_document(1).get_form(), 'Difference test -> prod')
            self.report_text_differences(diff[0], self.get_document(0).get_form(), 'Difference prod -> test')
        else:
            logger.info('No differences between texts.')

    def test_attribute_differences(self):
        logger.info('Checking xml files for differences in attributes.\n')
        nodes_prod = self.parser.get_children(self.get_document(0).get_form())
        nodes_test = self.parser.get_children(self.get_document(1).get_form())
        # Get elements that have an attribute.
        attributes_prod = self.get_attributes(nodes_prod)
        attributes_test = self.get_attributes(nodes_test)
        success = True
        for attrib_prod, attrib_test in zip(attributes_prod.items(), attributes_test.items()):
            try:
                self.assertEqual(attrib_prod, attrib_test)
            except AssertionError:
                success = False
                self.report_attribute_differences(attrib_test, self.get_document(1).get_form(), 'Difference test -> prod')
                self.report_attribute_differences(attrib_prod, self.get_document(0).get_form(), 'Difference prod -> test')
        if success:
            logger.info('No differences between attributes.\n')


if __name__ == "__main__":
    unittest.main()
