import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add src directory to module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from linkedin_client import LinkedInClient  # Import the LinkedInClient class

class TestLinkedInClient(unittest.TestCase):
    def setUp(self):
        """
        Run before each test method to set up the test environment.
        """
        self.token = "fake_token"  # Use a fake LinkedIn API token
        self.client = LinkedInClient(self.token)  # Initialize LinkedInClient with the token

    @patch('linkedin_client.requests.get')
    def test_fetch_jobs_html(self, mock_get):
        """
        Test if fetch_jobs_html correctly fetches job listings.
        """
        # Mock API response
        mock_response = MagicMock()
        mock_response.text = "<html>Job Listings</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response  # Assign the mocked response to mock_get

        # Call fetch_jobs_html and assert the response
        html_content = self.client.fetch_jobs_html("NVIDIA,AMD", "Taiwan")
        self.assertIn("Job Listings", html_content)  # Check if "Job Listings" is in the HTML content

    @patch('linkedin_client.requests.get')
    def test_export_jobs(self, mock_get):
        """
        Test if export_jobs correctly exports job listings to a markdown file.
        """
        # Mock API response
        mock_response = MagicMock()
        mock_response.text = "<html>Job Listings</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response  # Assign the mocked response to mock_get

        # Call export_jobs and assert the file creation
        file_path = self.client.export_jobs("NVIDIA,AMD", "Taiwan")
        self.assertTrue(file_path.endswith('jobs.md'))  # Check if the file path ends with 'jobs.md'
        self.assertTrue(os.path.exists(file_path))  # Check if the file exists

        # Clean up the created file after the test
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_initialization_without_token(self):
        """
        Test initialization of LinkedInClient without a token.
        """
        with self.assertRaises(ValueError):
            LinkedInClient()  # Should raise ValueError if no token is provided

if __name__ == '__main__':
    unittest.main()
