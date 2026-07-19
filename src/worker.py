import gc

def process_data(data):
    # Process data logic
    result = some_processing_function(data)
    # Reclaim unused objects
    gc.collect()
    return result
