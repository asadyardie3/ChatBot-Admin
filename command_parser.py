import re

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{3,}\d")
UPDATE_RE = re.compile(
    r"\b(?:update|change|set|edit)\s+(.+?)\s+(phone number|phone|city|name|email)\s+(?:to|as)\s+(.+?)\s*[.!]?$",
    re.I,
)
DELETE_RE = re.compile(
    r"\b(?:remove|delete|erase)\s+(?:the\s+)?(?:user\s+)?(.+?)\s*[?.!]?$", re.I
)


def parse(message):
    text = message.strip()
    for a, b in (("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'")):
        text = text.replace(a, b)
    low = text.lower()

    m = UPDATE_RE.search(text)
    if m:
        who = m.group(1).strip().strip('"')
        who = re.sub(r"^(?:the\s+)?(?:user\s+)?", "", who, flags=re.I)
        field = m.group(2).lower()
        if field == "phone number":
            field = "phone"
        value = m.group(3).strip().strip('"')
        return {"action": "update", "who": who, "field": field, "value": value}

    if re.search(r"\b(remove|delete|erase)\b", low):
        e = EMAIL_RE.search(text)
        if e:
            return {"action": "delete", "who": e.group(0)}
        m = DELETE_RE.search(text)
        if m:
            return {"action": "delete", "who": m.group(1).strip().strip('"')}

    if re.search(r"\b(add|create|register|insert)\b", low):
        e = EMAIL_RE.search(text)
        if not e:
            return {"action": "add", "email": None, "phone": None}
        rest = text.replace(e.group(0), " ")
        p = PHONE_RE.search(rest)
        return {
            "action": "add",
            "email": e.group(0),
            "phone": p.group(0).strip() if p else None,
        }

    if re.search(r"\b(list|show|display)\b", low) and "user" in low:
        return {"action": "list"}

    if "help" in low:
        return {"action": "help"}

    return {"action": "unknown"}