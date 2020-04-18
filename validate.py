import sys
from lxml import etree

data = sys.argv[1]
xsd = sys.argv[2]

parsed_xsd = etree.parse(xsd)
schema = etree.XMLSchema(parsed_xsd)

try:
	parsed_data = etree.parse(data)

except etree.XMLSyntaxError as e:
	print("XML parsing failed")
	print(e.error_log)
	exit()

try:
	schema.assertValid(parsed_data)
	print('File is valid according to schema')
	exit()

except etree.DocumentInvalid as e:
	print("Unable to validate doc according to schema")
	print(e.error_log)
