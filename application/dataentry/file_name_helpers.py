import re

def remove_hidden_whitespace_characters(string: str):
    """
    Removes the following Unicode characters:
      - Non-breaking space (\u00A0)
      - Zero-width space (\u200B)
      - Zero-width non-joiner (\u200C)
      - Zero-width joiner (\u200D)
      - Zero-width no-break space (\uFEFF)
    """
    pattern = r'[\u00A0\u200B\u200C\u200D\uFEFF]'
    return re.sub(pattern, '', string)
