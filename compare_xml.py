import xml.etree.ElementTree as ET


class Parser:
    def __init__(self, document):
        self.document = document

    def get_root(self, document):
        tree = ET.parse(document)
        return tree.getroot()

    def find_tag(self, root, tag_name):
        for tag in root.find(tag_name):
            print(tag.text)

    def view_document(self, root):
        print(ET.tostring(root, encoding='utf8').decode('utf8'))


def main():
    parser = Parser('VTB_Max_Muster_Produktion.xml')
    print(parser.document)


if __name__ == "__main__":
    main()
