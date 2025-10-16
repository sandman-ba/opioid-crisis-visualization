def fix_name(name: str) -> str:
    return "Year " + name.split(maxsplit=1)[0]

def get_column_names(column_names: list[str]) -> list[str]:
    return [name.lower() if name=="FIPS" else fix_name(name) for name in column_names]
