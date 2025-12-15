#!/usr/bin/env python3
"""
Test full-text search with special characters after escape_string fix
Testing: It's a test with 'quotes' and \\backslashes
"""
import tempfile
import shutil
import pyseekdb

print("=" * 80)
print("🔍 Testing Full-Text Search with Special Characters")
print("=" * 80)
print()

# Create temporary directory
temp_dir = tempfile.mkdtemp(prefix="pyseekdb_fulltext_test_")
print(f"📁 Test directory: {temp_dir}\n")

try:
    # Create admin client to ensure database exists
    print("🔧 Creating admin client...")
    admin = pyseekdb.AdminClient(path=temp_dir)
    
    # Create database if not exists
    try:
        admin.create_database("test_db")
        print("✅ Database 'test_db' created")
    except:
        print("ℹ️  Database 'test_db' already exists")
    
    # Create embedded client
    print("🔧 Creating client...")
    client = pyseekdb.Client(path=temp_dir, database="test_db")
    print("✅ Client created\n")
    
    # Create collection
    collection_name = "fulltext_test_collection"
    print(f"📦 Creating collection '{collection_name}'...")
    
    # Drop if exists
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.create_collection(name=collection_name)
    print(f"✅ Collection created (dimension: {collection.dimension})\n")
    
    # Test documents with special characters
    test_docs = [
        {
            "id": "doc1",
            "text": "It's a test with 'quotes' and \\backslashes",
            "metadata": {"category": "special_chars"}
        },
        {
            "id": "doc2", 
            "text": "Another document with simple text",
            "metadata": {"category": "simple"}
        },
        {
            "id": "doc3",
            "text": "Document with it's and quotes",
            "metadata": {"category": "quotes_only"}
        },
        {
            "id": "doc4",
            "text": "Path example: C:\\Users\\test\\file.txt",
            "metadata": {"category": "backslash"}
        },
    ]
    
    # Insert documents
    print("📝 Inserting test documents:")
    for doc in test_docs:
        print(f"   - {doc['id']}: {repr(doc['text'][:50])}")
    print()
    
    collection.add(
        ids=[doc["id"] for doc in test_docs],
        documents=[doc["text"] for doc in test_docs],
        metadatas=[doc["metadata"] for doc in test_docs]
    )
    print("✅ Documents inserted\n")
    
    # Test queries with special characters
    test_queries = [
        {
            "name": "Query with single quote",
            "text": "it's",
            "expected_docs": ["doc1", "doc3"]
        },
        {
            "name": "Query with quotes word",
            "text": "'quotes'",
            "expected_docs": ["doc1", "doc3"]
        },
        {
            "name": "Query with backslash",
            "text": "backslashes",
            "expected_docs": ["doc1"]
        },
        {
            "name": "Full query with special chars",
            "text": "test with 'quotes'",
            "expected_docs": ["doc1"]
        },
    ]
    
    print("🔬 Running full-text search queries:")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. {query['name']}")
        print(f"   Query: {repr(query['text'])}")
        
        try:
            # Query using text (will use embedding function)
            results = collection.query(
                query_texts=[query['text']],
                n_results=4,  # Get all results
                include=["documents", "metadatas", "distances"]
            )
            
            if results and len(results["ids"]) > 0 and len(results["ids"][0]) > 0:
                print(f"   ✅ Query executed successfully")
                print(f"   Found {len(results['ids'][0])} results:")
                
                for j, doc_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][j]
                    doc_text = results["documents"][0][j] if results.get("documents") else "N/A"
                    metadata = results["metadatas"][0][j] if results.get("metadatas") else {}
                    
                    print(f"      {j+1}. ID: {doc_id}, Distance: {distance:.4f}")
                    print(f"         Text: {repr(doc_text[:60])}")
                    print(f"         Category: {metadata.get('category', 'N/A')}")
                    
            else:
                print(f"   ⚠️  No results found")
                
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Additional test: Get documents by ID to verify storage
    print("\n" + "=" * 80)
    print("📋 Verifying stored documents (get by ID):")
    print("=" * 80)
    
    for doc in test_docs:
        try:
            result = collection.get(
                ids=[doc["id"]],
                include=["documents", "metadatas"]
            )
            
            if result and len(result["ids"]) > 0:
                stored_text = result["documents"][0] if result.get("documents") else "N/A"
                original_text = doc["text"]
                
                match = "✅" if stored_text == original_text else "❌"
                print(f"\n{match} {doc['id']}")
                print(f"   Original:  {repr(original_text)}")
                print(f"   Retrieved: {repr(stored_text)}")
                if stored_text != original_text:
                    print(f"   ⚠️  MISMATCH!")
            else:
                print(f"\n❌ {doc['id']} - Not found")
                
        except Exception as e:
            print(f"\n❌ {doc['id']} - Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Full-text search test completed!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Test error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    # Cleanup
    print(f"\n🧹 Cleaning up: {temp_dir}")
    try:
        shutil.rmtree(temp_dir)
        print("✅ Cleanup successful")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

