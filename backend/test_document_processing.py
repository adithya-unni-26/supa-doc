import unittest
import logging
from document_processing import process_and_store_document, extract_sitemap, scrape_content, generate_embeddings
from database import supabase
import os
from dotenv import load_dotenv
import uuid
import json
import time

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestDocumentProcessing(unittest.TestCase):
    def setUp(self):
        logger.info("Starting a new test case")
        self.test_user_id = str(uuid.uuid4())
        self.test_chatbot_id = str(uuid.uuid4())
        
        # Create a test chatbot
        chatbot_data = {
            "id": self.test_chatbot_id,
            "user_id": self.test_user_id,
            "name": "Test Chatbot"
        }
        supabase.table("chatbots").insert(chatbot_data).execute()
        logger.info(f"Created test chatbot with id: {self.test_chatbot_id}")

    def tearDown(self):
        logger.info("Cleaning up after test case")
        # Delete the test chatbot
        supabase.table("chatbots").delete().eq("id", self.test_chatbot_id).execute()
        logger.info(f"Deleted test chatbot with id: {self.test_chatbot_id}")

    def test_extract_sitemap(self):
        logger.info("Testing extract_sitemap function")
        urls = extract_sitemap("https://readme.facets.cloud")
        self.assertIsInstance(urls, list)
        self.assertTrue(len(urls) > 0)
        logger.info(f"Extracted {len(urls)} URLs from sitemap")

    def test_scrape_content(self):
        logger.info("Testing scrape_content function")
        urls = extract_sitemap("https://readme.facets.cloud")
        test_urls = urls[:10]  # Limit to first 10 URLs for testing
        content = scrape_content(test_urls)
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), len(test_urls))
        self.assertIn('url', content[0])
        self.assertIn('content', content[0])
        logger.info(f"Scraped content from {len(content)} URLs")

    def test_generate_embeddings(self):
        logger.info("Testing generate_embeddings function")
        text = "This is a test sentence for Facets readme."
        embeddings = generate_embeddings(text)
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 1536)  # OpenAI's ada-002 model produces 1536-dimensional embeddings
        logger.info(f"Generated embeddings of length: {len(embeddings)}")

    def test_process_and_store_document(self):
        logger.info("Testing process_and_store_document function")
        url = "https://readme.facets.cloud"
        document_id = str(uuid.uuid4())  # Generate a UUID
        logger.info(f"Generated document_id: {document_id}")
        
        # Create a test document
        document_data = {
            "id": document_id,
            "chatbot_id": self.test_chatbot_id,
            "url": url
        }
        supabase.table("documents").insert(document_data).execute()
        logger.info(f"Created test document with id: {document_id}")
        
        process_and_store_document(url, document_id)
        
        # Increase the delay to ensure all database operations have completed
        time.sleep(10)
        
        # Verify that embeddings were stored in the database
        logger.info("Verifying stored embeddings in the database")
        result = supabase.table("embeddings").select("*").eq("document_id", document_id).execute()
        logger.info(f"Query result: {result}")
        logger.info(f"Number of embeddings found: {len(result.data)}")
        self.assertTrue(len(result.data) > 0, f"No embeddings found for document_id: {document_id}")
        logger.info(f"Found {len(result.data)} embeddings in the database for the test document")

        # Verify that the embedding is stored as a JSONB
        for embedding in result.data:
            self.assertIsInstance(embedding['embedding_jsonb'], list)
            self.assertEqual(len(embedding['embedding_jsonb']), 1536)  # Verify the length of the embedding

        # Remove the cleanup code
        # supabase.table("embeddings").delete().eq("document_id", document_id).execute()
        # supabase.table("documents").delete().eq("id", document_id).execute()
        logger.info(f"Test completed. Data remains in the database for inspection.")

if __name__ == '__main__':
    logger.info("Starting document processing tests")
    unittest.main(verbosity=2)
    logger.info("Finished all document processing tests")