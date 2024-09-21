import unittest
import logging
from database import supabase
import os
from dotenv import load_dotenv
import uuid
import json
import time
import numpy as np

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestEmbeddingsTable(unittest.TestCase):
    def setUp(self):
        logger.info("Starting a new test case")
        self.test_user_id = str(uuid.uuid4())  # Generate a test user_id
        self.test_chatbot_id = str(uuid.uuid4())
        self.test_document_id = str(uuid.uuid4())
        self.test_embedding = np.random.rand(1536).tolist()  # Create a dummy embedding with 1536 dimensions
        
        # Create a test chatbot
        chatbot_data = {
            "id": self.test_chatbot_id,
            "user_id": self.test_user_id,
            "name": "Test Chatbot"
            # 'created_at' and 'updated_at' will be automatically set by Supabase
        }
        chatbot_result = supabase.table("chatbots").insert(chatbot_data).execute()
        logger.info(f"Created test chatbot with id: {self.test_chatbot_id}")
        logger.info(f"Chatbot insert result: {chatbot_result}")

        # Create a test document
        document_data = {
            "id": self.test_document_id,
            "chatbot_id": self.test_chatbot_id,
            "url": "https://test.com"
            # 'created_at' will be automatically set by Supabase
        }
        document_result = supabase.table("documents").insert(document_data).execute()
        logger.info(f"Created test document with id: {self.test_document_id}")
        logger.info(f"Document insert result: {document_result}")

    def tearDown(self):
        logger.info("Cleaning up after test case")
        # Remove the deletion logic to keep the data in the database
        # Delete the test embedding
        # delete_embedding_result = supabase.table("embeddings").delete().eq("document_id", self.test_document_id).execute()
        # logger.info(f"Deleted {len(delete_embedding_result.data)} embeddings for document_id: {self.test_document_id}")
        
        # Delete the test document
        # delete_document_result = supabase.table("documents").delete().eq("id", self.test_document_id).execute()
        # logger.info(f"Deleted {len(delete_document_result.data)} documents with id: {self.test_document_id}")

        # Delete the test chatbot
        # delete_chatbot_result = supabase.table("chatbots").delete().eq("id", self.test_chatbot_id).execute()
        # logger.info(f"Deleted {len(delete_chatbot_result.data)} chatbots with id: {self.test_chatbot_id}")

    def test_insert_and_retrieve_embedding(self):
        logger.info("Testing insertion and retrieval of embedding")
        
        # Insert the test embedding
        insert_data = {
            "id": str(uuid.uuid4()),
            "document_id": self.test_document_id,
            "embedding_jsonb": self.test_embedding,  # Updated column name
            "content": "Test content",
            "url": "https://test.com"
        }
        insert_result = supabase.table("embeddings").insert(insert_data).execute()
        self.assertEqual(len(insert_result.data), 1, "Failed to insert test embedding")
        logger.info(f"Successfully inserted test embedding. Insert result: {insert_result}")

        # Retrieve the test embedding
        time.sleep(2)  # Wait for 2 seconds to ensure the data is available for retrieval
        retrieve_result = supabase.table("embeddings").select("*").eq("document_id", self.test_document_id).execute()
        self.assertEqual(len(retrieve_result.data), 1, "Failed to retrieve test embedding")
        self.assertIsInstance(retrieve_result.data[0]['embedding_jsonb'], list, "Retrieved embedding is not a list (JSONB)")
        logger.info(f"Successfully retrieved and verified test embedding. Retrieve result: {retrieve_result}")

    def test_update_embedding(self):
        logger.info("Testing update of embedding")
        
        # Insert the test embedding
        insert_data = {
            "id": str(uuid.uuid4()),
            "document_id": self.test_document_id,
            "embedding_jsonb": self.test_embedding,  # Updated column name
            "content": "Test content",  
            "url": "https://test.com"
        }
        insert_result = supabase.table("embeddings").insert(insert_data).execute()
        logger.info(f"Inserted test embedding for update test. Insert result: {insert_result}")

        # Update the embedding
        updated_embedding = np.random.rand(1536).tolist()
        update_data = {
            "embedding_jsonb": updated_embedding,  # Updated column name
            "content": "Updated test content"
        }
        update_result = supabase.table("embeddings").update(update_data).eq("document_id", self.test_document_id).execute()
        self.assertEqual(len(update_result.data), 1, "Failed to update test embedding")
        logger.info(f"Successfully updated test embedding. Update result: {update_result}")

        # Verify the update
        time.sleep(2)  # Wait for 2 seconds to ensure the data is updated
        retrieve_result = supabase.table("embeddings").select("*").eq("document_id", self.test_document_id).execute()
        retrieved_embedding = retrieve_result.data[0]['embedding_jsonb']  # Updated column name
        self.assertEqual(retrieved_embedding, updated_embedding, "Retrieved embedding does not match the updated embedding")
        self.assertEqual(retrieve_result.data[0]['content'], "Updated test content", "Content was not updated correctly")
        logger.info(f"Successfully verified updated embedding. Retrieve result after update: {retrieve_result}")

if __name__ == '__main__':
    logger.info("Starting embeddings table tests")
    unittest.main(verbosity=2)
    logger.info("Finished all embeddings table tests")