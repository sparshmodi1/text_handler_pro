import multiprocessing
import time

# Rule-based word lists
positive_words = ["good", "excellent", "happy", "amazing", "great"]
negative_words = ["bad", "terrible", "sad", "worst", "poor"]

# Function to process each chunk
def process_chunk(text_chunk):
    words = text_chunk.lower().split()

    score = 0
    for word in words:
        if word in positive_words:
            score += 1
        elif word in negative_words:
            score -= 1
      
    #homework 1      
    countp, countn = 0, 0            
    for i in words:
        if i in positive_words:
            countp+=1
        elif i in negative_words:
            countn+=1
            
    if score > 0:
        tag = "positive"
    elif score < 0:
        tag = "negative"
    else:
        tag = "neutral"
        
    context = {
        "text_chunk" : text_chunk,
        "score" : score,
        "tag" : tag,
        "positive_words" : countp,
        "negative_words" : countn
    }
    return (context)


if __name__ == "__main__":

    text_data = [
        "This product is excellent and amazing",
        "This service is terrible and bad",
        "The experience was good but the delivery was poor",
        "I am very happy with this great product",
        "Worst quality and bad performance"
    ]

    start_time = time.time()

    # Create pool with 4 workers
    with multiprocessing.Pool(4) as pool:
        results = pool.map(process_chunk, text_data)

    end_time = time.time()

    for result in results:
        print(result)

    print("Time Taken:", end_time - start_time)