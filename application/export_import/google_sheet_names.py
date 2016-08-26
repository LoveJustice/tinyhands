import re
 
def spreadsheet_header_from_export_header(hdr):
    hdr = hdr.lower()
    hdr = re.sub("[^a-z0-9\.\-]*","", hdr)
    hdr = re.sub("^[0-9\.\-]*","", hdr)
    return hdr