# src/linkedin_client.py

import requests
from logger import LOG  # Assuming you have a logger setup similar to GitHubClient
import os
from datetime import datetime

class LinkedInClient:
    def __init__(self, access_token=None):
        # Use the provided token or fetch from environment variable
        self.access_token = access_token or os.getenv('linkedin_token')
        if not self.access_token:
            raise ValueError("LinkedIn access token is required")
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def fetch_jobs_html(self, keywords, location):
        """
        Fetch job listings from LinkedIn based on specified keywords and location.

        :param keywords: A comma-separated string of job keywords (e.g., "NVIDIA,AMD")
        :param location: The location to search for jobs (e.g., "Taiwan")
        :return: A list of job listings
        """
        LOG.debug(f"Fetching jobs for keywords: {keywords} in location: {location}")
        url = "https://www.linkedin.com/jobs/search"
        params = {
            'keywords': keywords,
            'location': location
        }
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.text  # Return the HTML content
        except Exception as e:
            LOG.error(f"Failed to fetch jobs: {str(e)}")
            LOG.error(f"Response details: {response.text if 'response' in locals() else 'No response data available'}")
            return ""

    def export_jobs(self, keywords, location, date=None):
        LOG.debug("Exporting LinkedIn job listings.")
        html_content = self.fetch_jobs_html(keywords, location)

        if not html_content:
            LOG.warning("No LinkedIn jobs found.")
            return None

        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        dir_path = os.path.join('daily_progress', 'linkedin_jobs', date)
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, 'jobs.md')
        with open(file_path, 'w') as file:
            file.write(f"# LinkedIn Job Listings ({date})\n\n")
            file.write(html_content)  # Write the HTML content directly

        LOG.info(f"LinkedIn job listings file generated: {file_path}")
        return file_path

# Example usage
if __name__ == "__main__":
    linkedin_client = LinkedInClient()

    # Fetch jobs and print them
    # jobs = linkedin_client.fetch_jobs("NVIDIA,AMD", "Taiwan")
    # for job in jobs:
    #     print(f"Job Title: {job.get('title')}, Company: {job.get('company')}")

    # Export jobs to a markdown file
    file_path = linkedin_client.export_jobs()
    if file_path:
        print(f"Job listings have been exported to {file_path}")
    else:
        print("No job listings were exported.")
