from field_types import Address1CsvField
from field_types import CopyCsvField

address2_data = [
	Address1CsvField('address1', 'Address1 name'),
	CopyCsvField('name', 'Address2 name', False),
	CopyCsvField('level', 'Level', False),
	CopyCsvField('latitude', 'Latitude', False),
	CopyCsvField('longitude', 'Longitude', False)	
]

def get_address2_export_rows(address2s):
	rows = []
	headers = []
	for field in address2_data:
		headers.append(field.title)
	rows.append(headers)

	for address2 in address2s:
		row = []
		for field in address2_data:
			row.append(field.exportField(address2))
			
		rows.append(row)
		
	return rows