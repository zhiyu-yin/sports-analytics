"""Suffix-equivalent full-name key; never surname-only report identity matching."""
import re
from injury_warning.longitudinal import canonical

def without_suffix(value):
    return re.sub(r'\b(?:Jr|Sr|II|III|IV)\.?(?=\s*(?:,|$))','',value,flags=re.I).strip()
def name_key(value):return canonical(without_suffix(value))
