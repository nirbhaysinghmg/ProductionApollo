#!/usr/bin/env python3
import os
# Set this before importing any protobuf modules
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import sys
from app.vector_store import get_vector_store
from app.config import settings

print(f'CSV Path: {settings.CSV_PATH}')
print(f'Persist Directory: {settings.PERSIST_DIRECTORY}')

# Check if CSV exists
if not os.path.exists(settings.CSV_PATH):
    print(f'❌ CSV file not found at {settings.CSV_PATH}')
    print('Please ensure the CSV file exists in the data directory')
    sys.exit(1)

# Check if we can write to the persist directory
if not os.access(settings.PERSIST_DIRECTORY, os.W_OK):
    print(f'❌ Cannot write to {settings.PERSIST_DIRECTORY}')
    print('Please check directory permissions')
    sys.exit(1)

print('✅ CSV file found, creating vector store...')
try:
    vector_store = get_vector_store()
    print('✅ Vector store created successfully!')
    print(f'✅ Vector store type: {type(vector_store)}')
except Exception as e:
    print(f'❌ Error creating vector store: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1) 