def create_chunks(reviews, chunk_size=100):
    return [
        reviews[i:i+chunk_size]
        for i in range(0, len(reviews), chunk_size)
    ]