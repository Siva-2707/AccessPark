def safe_str(val):
    return ', '.join(map(str, val)) if isinstance(val, list) else str(val)