from lxml import etree
import logging

logger = logging.getLogger(__name__)


class Parser:

    def parse_file(self, xml):
        parser = etree.XMLParser(remove_comments=True)
        return etree.parse(xml, parser)

    def get_children(self, tree):
        return list(tree.iter())

    def get_attribute(self, tag):
        return tag.attrib

    def find_tag(self, root, tag_name):
        for tag in root.iter(tag_name):
            return tag

    def find_tag_by_name(self, tree, tag: str):
        for location in tree.findall('.//' + tag):
            logger.debug('Tag located at: ' + location.tag)
            return location

    def find_tag_by_text(self, tree, tag: str):
        for location in tree.xpath('.//*[contains(text(),"{}")]'.format(tag)):
            logger.debug('Tag located at: ' + location.tag)
            return location

    def find_tag_by_attrib(self, tree, tag: str, attrib: str, value: str):
        for location in tree.xpath('.//{}[@{}={}]'.format(tag, attrib, value)):
            logger.debug('Tag located at: ' + location.tag)
            return location

    def get_parent_nodes(self, tree, node):
        root_children = self.get_children(tree)
        node_children = root_children.index(node) + 1
        # Remove all nodes below the current node.
        parent_nodes = root_children[:node_children]
        logger.debug('Parent nodes are: ' + str(parent_nodes))
        return parent_nodes

    # def view_tree_levels(self, elem, func, level=0):
    #     """
    #     Recursive function that records the level of an element in the
    #     tree and prints the elements position.
    #     """
    #     func(elem, level)
    #     # todo: Replace getchildren.
    #     for child in elem.getchildren():
    #         self.eview_tree_levels(child, func, level+1)
    #
    # def print_level(self, elem, level):
    #     logger.debug(' '*level + '<' + elem.tag + '>')
