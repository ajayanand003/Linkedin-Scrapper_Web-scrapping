from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from config import (
    IMPLICIT_WAIT, 
    PAGE_LOAD_TIMEOUT, 
    SEARCH_PARAMS, 
    BASE_URL, 
    OUTPUT_FILE
)

class LinkedInJobScraper:
    def __init__(self):
        self.setup_driver()
        self.jobs_data = []

    def setup_driver(self):
        """Initialize the Chrome WebDriver with appropriate settings"""
        options = webdriver.ChromeOptions()
        # Remove headless mode for better reliability
        # options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Add these new options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Execute CDP commands to prevent detection
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver.implicitly_wait(IMPLICIT_WAIT)
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    def scrape_jobs(self):
        """Main method to scrape jobs for all configured searches"""
        for keyword in SEARCH_PARAMS['keywords']:
            for location in SEARCH_PARAMS['locations']:
                print(f"Scraping jobs for {keyword} in {location}")
                self.scrape_job_listings(keyword, location)
        
        # Save results to CSV
        self.save_to_csv()
        self.driver.quit()

    def scrape_job_listings(self, keyword, location):
        """Scrape job listings for a specific keyword and location"""
        url = BASE_URL.format(keyword.replace(' ', '%20'), location.replace(' ', '%20'))
        
        for page in range(SEARCH_PARAMS['pages_per_search']):
            try:
                self.driver.get(f"{url}&start={page*25}")
                time.sleep(random.uniform(3, 5))  # Increased delay

                # Wait for job cards to load with longer timeout
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-card-container"))
                )

                # Add a small delay after page loads
                time.sleep(random.uniform(2, 3))
                
                # Parse the page
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_cards = soup.find_all('div', class_='job-card-container')

                for card in job_cards:
                    job_data = self.extract_job_data(card)
                    if job_data:
                        self.jobs_data.append(job_data)

            except Exception as e:
                print(f"Error scraping page {page}: {str(e)}")
                continue

    def extract_job_data(self, card):
        """Extract relevant data from a job card"""
        try:
            title = card.find('h3', class_='base-search-card__title').text.strip()
            company = card.find('h4', class_='base-search-card__subtitle').text.strip()
            location = card.find('span', class_='job-search-card__location').text.strip()
            link = card.find('a', class_='base-card__full-link')['href']

            return {
                'title': title,
                'company': company,
                'location': location,
                'link': link
            }
        except:
            return None

    def save_to_csv(self):
        """Save scraped data to CSV file"""
        df = pd.DataFrame(self.jobs_data)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Saved {len(self.jobs_data)} jobs to {OUTPUT_FILE}")

if __name__ == "__main__":
    scraper = LinkedInJobScraper()
    scraper.scrape_jobs()