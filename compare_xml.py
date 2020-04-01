import xml.etree.ElementTree as ET

def main():
    # Parse document and get root element.
    tree = ET.parse('VTB_Max_Muster_Produktion.xml')
    root = tree.getroot()

    # View document.
    print(ET.tostring(root, encoding='utf8').decode('utf8'))

if __name__ == "__main__":
    main()
