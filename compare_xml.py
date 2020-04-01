import xml.etree.ElementTree as ET

def main():
    tree = ET.parse('VTB_Max_Muster_Produktion.xml')
    root = tree.getroot()
    print(root)

if __name__ == "__main__":
    main()
