import hashlib
def generate_hash(value: str):
    return hashlib.md5(value.encode('utf-8')).hexdigest()
