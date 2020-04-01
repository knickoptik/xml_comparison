import xml.etree.ElementTree as ET


class Parser:

    def get_root(self, document):
        tree = ET.parse(document)
        return tree.getroot()

    def find_tag(self, root, tag_name):
        for tag in root.find(tag_name):
            print(tag.text)

    def view_document(self, root):
        print(ET.tostring(root, encoding='utf8').decode('utf8'))


def main():
    parser = Parser()


if __name__ == "__main__":
    main()
