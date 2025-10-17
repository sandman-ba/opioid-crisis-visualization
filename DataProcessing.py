def fix_name(name: str) -> str:
    return name.split(maxsplit=1)[0] + " Opioid Related Mortality Rate"

def get_column_names(column_names: list[str]) -> list[str]:
    return [name.lower() if name=="FIPS" else fix_name(name) for name in column_names]

def int_to_column_name(year: int) -> str:
    return f"{year} Opioid Related Mortality Rate"
