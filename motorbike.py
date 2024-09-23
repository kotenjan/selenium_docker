from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime

class MobileDEScraper:
    def __init__(self):
        # Initialize the Chrome driver
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Run headless Chrome
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        self.driver = webdriver.Chrome(options=chrome_options)

    def accept_cookies(self):
        wait = WebDriverWait(self.driver, 10)
        try:
            # Wait for the accept button to be clickable and click it
            accept_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button.mde-consent-accept-btn')))
            accept_button.click()
            print("Accepted cookies.")
        except Exception as e:
            print("Accept button not found or already accepted.")

    def scrape(self):

        desired_motorbikes = []
        motorbike_name = "cb1000r"
        motorbike_class = "black"

        url = 'https://suchen.mobile.de/fahrzeuge/search.html?fr=2021%3A&isSearchRequest=true&ms=11000%3B%3B%3BCB+1000+R&ref=dsp&s=Motorbike&sb=rel&vc=Motorbike&lang=en'
        self.driver.get(url)

        # Accept cookies before starting to scrape
        self.accept_cookies()

        wait = WebDriverWait(self.driver, 10)

        page_number = 1
        while True:
            print(f"Scraping Page {page_number}")
            # Wait until the adverts are loaded
            wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'a[data-testid^="result-listing"]')))
            adverts = self.driver.find_elements(
                By.CSS_SELECTOR, 'a[data-testid^="result-listing"]')

            for advert in adverts:
                try:
                    title = advert.find_element(By.CSS_SELECTOR, 'h2.QeGRL').text
                    details = advert.find_element(
                        By.CSS_SELECTOR, 'div[data-testid="listing-details-attributes"]').text
                    price = advert.find_element(
                        By.CSS_SELECTOR, 'span[data-testid="price-label"]').text

                    # Extract mileage from details
                    details_list = details.split('•')
                    if len(details_list) > 1:
                        date = details_list[0] if "fr" in details_list[0].lower() else "N/A"
                        mileage = details_list[1] if "km" in details_list[1].lower() else "N/A"
                    else:
                        date = 'N/A'
                        mileage = 'N/A'

                    if motorbike_name in title.replace(" ", "").lower() and motorbike_class in title.replace(" ", "").lower() and date != "N/A" and mileage != "N/A":
                        desired_motorbikes.append({"Title": title, "Date": date, "Mileage": mileage, "Price": price})
                        print(f"Title: {title}")
                        print(f"Date: {date}")
                        print(f"Mileage: {mileage}")
                        print(f"Price: {price}")
                        print('-' * 40)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue

            # Scroll to the bottom of the page to ensure the "Next" button is loaded
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Wait for potential dynamic content to load
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Wait for potential dynamic content to load

            try:
                # Check if the "Next" button is enabled
                next_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[data-testid="pagination:next"]')))
                # Click the "Next" button
                next_button.click()
                page_number += 1
                # Wait for the next page to load
                wait.until(EC.staleness_of(adverts[0]))
                time.sleep(5)
            except Exception as e:
                print("No more pages to scrape.")
                break

        self.driver.quit()
        return desired_motorbikes

if __name__ == '__main__':
    scraper = MobileDEScraper()
    desired_motorbikes = scraper.scrape()

    df_motorbikes = pd.DataFrame(desired_motorbikes)

    # Save to CSV with today's date
    today_date = datetime.now().strftime("%Y-%m-%d")
    csv_filename = f"{today_date}.csv"
    df_motorbikes.to_csv(f"data/{csv_filename}", index=False)
