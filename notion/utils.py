def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


def truncate(value: str, limit: int = 2000) -> str:
    if len(value) > limit:
        value = "{}...".format(value[: limit - 3])
    return value