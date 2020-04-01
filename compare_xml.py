import xml.etree.ElementTree as ET


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


def main():
    parser = Parser('VTB_Max_Muster_Produktion.xml')
    root = parser.get_root()
    print(parser.find_tag(root, 'v_vertragsnummer'))

if __name__ == "__main__":
    main()
