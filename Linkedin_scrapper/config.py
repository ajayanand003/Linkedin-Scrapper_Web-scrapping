# LinkedIn search parameters
SEARCH_PARAMS = {
    'keywords': ['python developer', 'data engineer'],
    'locations': ['United States', 'Remote'],
    'pages_per_search': 5
}

# Selenium configurations
CHROME_DRIVER_PATH = 'chromedriver'
IMPLICIT_WAIT = 10  # seconds
PAGE_LOAD_TIMEOUT = 30  # seconds

# Output settings
OUTPUT_FILE = 'output/job_listings.csv'

# LinkedIn base URL
BASE_URL = "https://www.linkedin.com/jobs/search/?keywords={}&location={}"