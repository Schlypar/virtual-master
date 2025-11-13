import re
from typing import List


def parse_number_list(text: str) -> List[float]:
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    out = []
    for n in nums:
        out.append(float(n) if '.' in n else float(int(n)))
    return out
