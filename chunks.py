def create_chunks(lines, chunk_size=100):
    return [
        lines[i:i+chunk_size]
        for i in range(0, len(lines), chunk_size)
    ]