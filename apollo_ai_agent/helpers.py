import os
from PIL import Image
import re

# Define no-op caching decorators
def cache_resource(func):
    return func

def cache_data(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

@cache_resource
def load_heavy_modules():
    import retrieval_func
    import llm_handler
    import llm_query_normalization
    import db_functions
    return retrieval_func, llm_handler, llm_query_normalization, db_functions

@cache_data(show_spinner=False)
def load_image_cached(path, size=None):
    if os.path.exists(path):
        img = Image.open(path)
        if size:
            try:
                # For Pillow 10.0.0 and above
                resample_mode = Image.Resampling.LANCZOS
            except AttributeError:
                # For older versions of Pillow
                resample_mode = Image.LANCZOS
            img = img.resize(size, resample_mode)
        return img
    return None

cleanup_pattern = re.compile(r"<think>.*?</think>|```structured|```markdown|```", flags=re.DOTALL)
