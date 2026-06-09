# rustchain_export.py — neutralize formula-leading strings
_DANGEROUS = ('=', '+', '-', '@', '\t', '\r', '\n')

def _safe_csv(value: str) -> str:
    if not isinstance(value, str):
        return value
    stripped = value.lstrip()
    if stripped and stripped[0] in _DANGEROUS:
        return "'" + value
    return value

def write_csv(rows):
    safe_rows = [[_safe_csv(cell) for cell in row] for row in rows]
    csv.DictWriter.writerows(safe_rows)