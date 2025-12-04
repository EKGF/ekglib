from io import BytesIO


def str_to_binary(s: str) -> bytes:
    bts = BytesIO(b'')  # can't just do this: bts = value.encode('utf8')
    for c in (
        s
    ):  # need to convert the unicode characters to bytes, using ord() not via utf-8
        bts.write(ord(c).to_bytes(1, 'little'))
    return bts.getvalue()
