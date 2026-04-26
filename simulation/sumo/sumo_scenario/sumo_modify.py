import xml.etree.ElementTree as ET
tree = ET.parse('in/route/most.pedestrian.rou.xml')
root = tree.getroot()
import random
ped = {}

count = 18000

# Parse the XML string
tree = ET.parse('in/route/most.pedestrian.rou.xml')
root = tree.getroot()
# tree1 = ET.parse('in/route/most.special.rou.xml')
# root1 = tree1.getroot()

# Loop through all 'person' elements with type 'pedestrian' and modify their 'depart' attribute
for person in root.findall(".//person[@type='pedestrian']"):
    print(person.get('id'), count)
    person_id = person.get('id')
    if count >= 18200:
        count = 18200
    else:
        count = 18001 #round(random.uniform(18001, 18050), 0)# + round(random.uniform(1, 1), 0)
    person.set('depart', str(count))

# count = 18000
# for person in root1.findall(".//vehicle[@type='special']"):
#     print(person.get('id'), count)
#     person_id = person.get('id')
#     if count >= 18200:
#         count = 18200
#     else:
#         count = count + round(random.uniform(1, 5), 0)
#     person.set('depart', str(count))

updated_pedestrian_xml = ET.tostring(root, encoding='unicode')
# updated_special_xml = ET.tostring(root1, encoding='unicode')

def write_xml_to_file(xml_string, filename):
    with open(filename, 'w') as file:
        file.write(xml_string)

# Write the updated pedestrian XML to a file
filename = 'in/route/most.pedestrian.rou.xml'
write_xml_to_file(updated_pedestrian_xml, filename)
