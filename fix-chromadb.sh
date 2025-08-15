#!/usr/bin/env bash
# fix-chromadb.sh

echo "🔧 Fixing ChromaDB read-only issue..."

# Kill any processes that might be holding the database
echo "🛑 Stopping any processes using ChromaDB..."
pkill -f "python.*app.main" 2>/dev/null || true
pkill -f "uvicorn.*app.main" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

echo "📁 Fixing chroma_db directory permissions..."
if [ -d "chroma_db" ]; then
    chmod -R 755 chroma_db
    echo "✅ Permissions fixed for existing chroma_db"
else
    echo "📁 Creating new chroma_db directory..."
    mkdir -p chroma_db
    chmod 755 chroma_db
    echo "✅ New chroma_db directory created"
fi

echo "🧹 Cleaning up any lock files..."
find chroma_db -name "*.lock" -delete 2>/dev/null || true
find chroma_db -name "*.tmp" -delete 2>/dev/null || true

echo "✅ ChromaDB fix complete!"
echo "💡 You can now run ./reset-vectorstore.sh to recreate the vector store" 