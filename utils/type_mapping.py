# utils/type_mapping.py

TYPE_MAP = {
    "доход": "income",
    "расход": "expense"
}

REVERSE_TYPE_MAP = {v: k for k, v in TYPE_MAP.items()}


def to_internal_type(display_type: str) -> str:
    """
    Преобразует 'доход' → 'income', 'расход' → 'expense'
    """
    return TYPE_MAP.get(display_type.lower(), display_type)


def to_display_type(internal_type: str) -> str:
    """
    Преобразует 'income' → 'доход', 'expense' → 'расход'
    """
    return REVERSE_TYPE_MAP.get(internal_type.lower(), internal_type)
