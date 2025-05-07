import re

def clean_attachment_file_name(file_name: str):
    file_name = re.sub(r'[^\w _\-.]', '', file_name)

    return file_name
