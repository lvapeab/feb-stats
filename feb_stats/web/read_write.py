def read_file(filename: str) -> bytes:
    with open(filename, mode="rb") as f:
        read_f = f.read()
    return read_f
