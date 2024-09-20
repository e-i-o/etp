import hashlib


def hash_file(filename: str, hasher = None):
    if hasher is None:
        hasher = hashlib.sha256()

    with open(filename, "rb") as f:
        while True:
            data = f.read(1 << 16)
            if not data:
                break
            hasher.update(data)

    return hasher


def hash_string(text: str, hasher = None):
    if hasher is None:
        hasher = hashlib.sha256()

    in_bytes = bytes(text, "utf8")
    hasher.update(in_bytes)
    return hasher
