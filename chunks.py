import os
chunk_size = os.cpu_count() * 50
def create_chunks(reviews, chunk_size):
    return [
        reviews[i:i+chunk_size]
        for i in range(0, len(reviews), chunk_size)
    ]