import re
import os
import csv
import glob
import time
import logging
import datetime
import pandas as pd

from typing import List, Tuple
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from urllib.parse import urlencode
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

winter_destinations = {
    "Alabama": ["Mentone", "Guntersville"],
    "Alaska": ["Anchorage", "Fairbanks", "Girdwood"],
    "Arizona": ["Flagstaff", "Sedona", "Tucson"],
    "California": ["Lake Tahoe", "Mammoth Lakes", "Big Bear Lake"],
    "Colorado": ["Aspen", "Vail", "Breckenridge"],
    "Georgia": ["Savannah", "Helen", "Blue Ridge"],
    "Idaho": ["Sun Valley", "McCall", "Coeur d'Alene"],
    "Maine": ["Bar Harbor", "Bethel", "Camden"],
    "Massachusetts": ["The Berkshires", "Boston", "Salem"],
    "Michigan": ["Traverse City", "Mackinac Island", "Petoskey"],
    "Montana": ["Whitefish", "Big Sky", "Bozeman"],
    "New Mexico": ["Taos", "Santa Fe", "Ruidoso"],
    "New York": ["Lake Placid", "Hudson", "Saratoga Springs"],
    "North Carolina": ["Asheville", "Blowing Rock", "Boone"],
    "Oregon": ["Bend", "Mount Hood", "Sisters"],
    "Tennessee": ["Gatlinburg", "Pigeon Forge", "Chattanooga"],
    "Utah": ["Park City", "Salt Lake City", "Moab"],
    "Vermont": ["Stowe", "Burlington", "Killington"],
    "Washington": ["Leavenworth", "Snoqualmie", "Seattle"],
    "Wyoming": ["Jackson Hole", "Cody", "Sheridan"]
}

# PAGES_AMOUNT = 40
PROPERTIES_PER_PAGE = 25

WINTER_START_DATE = datetime.date(2025, 3, 15)
WINTER_END_DATE = datetime.date(2025, 3, 19)
DAYS_IN_WEEK = 7

class BookingcomScrapper:
    
    def __init__(self) -> None:
        self.options = Options()
        self.options.add_argument("-headless")
        self.service = Service('driver/geckodriver') 
        self.driver = webdriver.Firefox(service=self.service, options=self.options)

    def close_cookie_banner(self) -> None:
        """Try to close the cookie consent banner if it appears."""
        try:
            cookie_banner = self.driver.find_element(By.ID, 'onetrust-accept-btn-handler')
            cookie_banner.click()
            logging.info("Closed cookie banner")
            time.sleep(0.5)
        except NoSuchElementException:
            logging.info("No cookie banner found")

    def execute(self) -> None:
        """Generate a separate CSV for each week of winter, collecting hotel data by state and city."""
        current_date = WINTER_START_DATE
        while current_date <= WINTER_END_DATE:
            end_date = current_date + datetime.timedelta(days=DAYS_IN_WEEK)
            file_name =  file_name = f'winter_data/book_data_{current_date.strftime("%Y-%m-%d")}_to_{end_date.strftime("%Y-%m-%d")}.csv'
            
            with open(file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["STATE", "CITY", "HOTEL_NAME", "COST", "START_DATE", "END_DATE"])
                
                total_states = len(winter_destinations)
                for idx, state in enumerate(winter_destinations):
                    logging.info(f"Processing state: {state} ({idx+1}/{total_states}) on {current_date}")
                    prices, hotels, cities = self.search_page(
                        winter_destinations[state], 
                        current_date.strftime("%Y-%m-%d"), 
                        end_date.strftime("%Y-%m-%d"), 
                    )
                    
                    for hotel, price, city in zip(hotels, prices, cities):
                        writer.writerow([state, city, hotel, price, current_date, end_date])

            current_date += datetime.timedelta(days=DAYS_IN_WEEK)

    def load_all_content(self, cycle_limit: int) -> BeautifulSoup:
        """Simulate clicking 'Load More' or scrolling down the page."""
        cycle_count = 0
        while cycle_count <= cycle_limit:
            try:
                load_more_button = self.driver.find_element(By.CSS_SELECTOR, ".a83ed08757.c21c56c305.bf0537ecb5.f671049264.af7297d90d.c0e0affd09")
                load_more_button.click()
                logging.info(f"Clicked 'Load More' button ({cycle_count+1}/{cycle_limit})")
            except ElementClickInterceptedException:
                self.close_cookie_banner()
            except NoSuchElementException:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                logging.info(f"Scrolled to the bottom ({cycle_count}/{cycle_limit})")
            time.sleep(0.5)
            cycle_count += 1
        
        reloaded_page = self.driver.page_source
        return BeautifulSoup(reloaded_page, 'html.parser')

    def concatenate(self):
        csv_list = os.listdir("winter_data/")
        csv_data_list = []
        for csv in csv_list:
            csv_path = os.path.join("winter_data", csv)
            csv_data = pd.read_csv(csv_path)
            csv_data_list.append(csv_data)
        big_df = pd.concat(csv_data_list, ignore_index=True)
        big_df.to_csv(os.path.join("winter_data/", "combined_book_data.csv"), index=False)



    def find_hotels_and_prices(self, soup: BeautifulSoup, parent_class: str, stop_class: str) -> Tuple[List[str], List[str]]:
        """Extract hotel names and prices from the page."""
        parent_div = soup.find("div", class_=parent_class)
        hotels, prices = [], []
        
        if parent_div:
            for div in parent_div.find_all("div"):
                if stop_class in div.get("class", []):
                    logging.info("Reached stop class div")
                    break
                if div.has_attr('aria-label'):
                    hotel_name = div.select_one('[data-testid="title"]')
                    price = div.select_one('[data-testid="price-and-discounted-price"]')
                    if hotel_name:
                        hotels.append(hotel_name.text.strip())
                    if price:
                        prices.append(price.text.strip())
        return hotels, prices

    def search_page(self, state: List[str], checkin: str, checkout: str, number_of_rooms: int = 1) -> Tuple[List[str], List[str], List[str]]:
        """Perform search and scrape hotel data for a state."""
        total_prices, total_hotels, total_cities = [], [], []
        for city in state:
            logging.info(f"Searching for hotels in {city}")
            
            # Construct the search URL
            checkin_year, checkin_month, checkin_day = checkin.split("-")
            checkout_year, checkout_month, checkout_day = checkout.split("-")
            url = f"https://www.booking.com/searchresults.html?{urlencode({'ss': city, 'checkin_year': checkin_year, 'checkin_month': checkin_month, 'checkin_monthday': checkin_day, 'checkout_year': checkout_year, 'checkout_month': checkout_month, 'checkout_monthday': checkout_day, 'no_rooms': number_of_rooms})}"
            
            self.driver.get(url)
            logging.info(f"Loading URL: {url}")
            
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="title"]')))
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            h1_tag = soup.find('h1').text
            match = re.search(r"([\d,]+) properties found", h1_tag)
            properties_count = int(match.group(1).replace(",", "")) if match else 0
            logging.info(f"Found {properties_count} properties in {city}")
            
            cycles = properties_count // PROPERTIES_PER_PAGE
            reloaded_page = self.load_all_content(cycles)
            
            hotels, prices = self.find_hotels_and_prices(reloaded_page, parent_class="d4924c9e74", stop_class="b988f50259")
            
            logging.info(f"Scraped {len(hotels)} hotels in {city}")
            
            total_hotels.extend(hotels)
            total_prices.extend(prices)
            total_cities.extend([city] * len(hotels))
        
        return total_prices, total_hotels, total_cities


if __name__ == "__main__":
    scraper = BookingcomScrapper()
    scraper.execute()
    # scraper.concatenate()
    
