import re
from typing import List


def parse_number_list(text: str) -> List[float]:
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    out = []
    for n in nums:
        out.append(float(n) if '.' in n else float(int(n)))
    return out


def split_string(text):
    # Find the last occurrence of @Name (or any word starting with @)
    match = re.search(r'(@\w+)(.*)', text)

    if match:
        name_part = match.group(1)  # The @Name part
        remaining_content = match.group(2).strip()  # The content after @Name

        # Check if there's content before @Name
        before_name = text[:match.start()].strip() if match.start() > 0 else ""

        if before_name:
            # Combine pre-content with the content after @Name
            combined_content = f"{before_name} {remaining_content}".strip()
            return [name_part, combined_content]
        else:
            return [name_part, remaining_content]

    # If no @Name pattern is found, return the original text as the content
    return ["", text]


def extract_names(text):
    # Pattern to match @ followed by one or more word characters
    pattern = r'@(\w+)'
    return re.findall(pattern, text)
