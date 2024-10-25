# Winter Hotels Data Scraper

## Project Overview
This project is designed to gather data on hotel pricing and availability from Booking.com for popular winter destinations. We're specifically targeting **winter hotspots**—destinations where visitors go to experience winter activities like skiing, snowboarding, or winter festivals. Locations like **Aspen**, which is practically the "poster child" for winter vacations, serve as the primary reference point. This focus excludes general vacation spots that happen to see visitors in winter, narrowing our data set to places known specifically for their winter appeal.

**Selenium** is used for scraping because **Booking.com actively works to block automated data extraction**, employing frequent changes to its site structure. Selenium helps overcome these obstacles by simulating real human behavior, making it possible to access the information we need.

## Purpose
The main goal of this scraper is to compile a comprehensive dataset of weekly hotel costs across these winter destinations to analyze pricing trends over the winter season. The dataset is intended to provide valuable insights into how prices fluctuate across the full 12-week winter period, as data from a single point in time would not be sufficient to capture the full picture of seasonal variations.

This scraper collects data for **every single week over the entire winter season**, which lasts for approximately **12 weeks (3 months)**. It loops through every state and city to collect data on a weekly basis, ensuring that we have a clear view of how hotel pricing trends evolve throughout the entire winter. This approach allows us to truly understand price dynamics and availability trends, which would be impossible to capture by scraping just a single day.

## Project Components

1. **Data Collection**  
   - Using Selenium, we navigate and capture hotel information from Booking.com for a range of winter destinations.
   - The data is structured by weekly intervals for each hotel, providing a detailed view of costs over the winter season.

2. **Data Analysis**  
   - The output is saved in an Excel file, where pivot tables and visualizations can be created to analyze trends across destinations.
   - Link to analysis file: **[Excel with Pivot Tables and Analysis](https://docs.google.com/spreadsheets/d/1vfzOI8L17syS7hi3XWGnGuY5GvdLeTPkkiWLoVyReDw/edit?gid=1584220894#gid=1584220894)**

## How to Run the Scraper

### Prerequisites
- Python 3.10
- Firefox (compatible with your Firefo browser version)
- Required libraries: Install with:
  ```bash
  pip install -r requirements.txt
  ```

### Steps to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/luccacastro/bookingcom_scrapper
   cd bookingcom_scrapper
   ```

3. Run the scraper script:
   ```bash
   python scraper.py
   ```

### Output
- The script generates an Excel file containing weekly data for each hotel across the selected winter destinations.
- Use the provided Google Sheets link to view pivot tables and conduct further analysis on cost trends and patterns.

## Notes
- **Booking.com’s Anti-Scraping Measures**: Booking.com frequently updates its site structure to counteract scraping, so the scraper may require adjustments over time.

This scraper provides insights into the winter tourism market, highlighting seasonal pricing and availability trends across high-demand winter destinations.

