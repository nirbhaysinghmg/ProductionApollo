#!/usr/bin/env bash
# reset-vectorstore.sh

echo "🧹 Cleaning up existing ChromaDB..."
rm -rf chroma_db

echo "📁 Creating fresh chroma_db directory with proper permissions..."
mkdir -p chroma_db
chmod 755 chroma_db

echo "📚 Recreating vector store..."
python3 -c "
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
except Exception as e:
    print(f'❌ Error creating vector store: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "🎉 Vector store reset complete!"
    echo "✅ ChromaDB has been recreated successfully"
else
    echo "❌ Vector store reset failed"
    exit 1
fi 