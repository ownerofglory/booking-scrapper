import os
import time
import boto3
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from botocore.exceptions import BotoCoreError, ClientError

START_PAGE = "https://www.booking.com/"
LOCATION = "Innsbruck"
START_DATE = "2025-06-22"
END_DATE = "2025-06-25"
AMOUNT_PEOPLE = 4

# Init Selenium web driver
driver = webdriver.Chrome()

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

if __name__ == "__main__":
    try:
        logging.info("Init environment")

        load_dotenv()
        AWS_KEY = os.getenv("AWS_KEY")
        AWS_SECRET = os.getenv("AWS_SECRET")
        AWS_REGION = os.getenv("AWS_REGION")
        PHONE_NUMBER = os.getenv("PHONE_NUMBER")

        logging.info("Init SNS client")
        # Create SNS client
        sns = boto3.client('sns',
                           region_name=AWS_REGION,
                           aws_access_key_id=AWS_KEY,
                           aws_secret_access_key=AWS_SECRET)


        logging.info(f"Navigate to the start page {START_PAGE}")
        # Navigate to a website
        driver.get(START_PAGE)

        # Wait for the page to load
        time.sleep(4)

        # Find the location input element
        location_input = driver.find_element(By.NAME, 'ss')
        logging.info(f"Found hotel: {location_input.text}")

        # Enter location
        location_input.click()
        location_input.send_keys(LOCATION)
        time.sleep(2)

        # Find the data picker
        dates_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='searchbox-dates-container']")
        dates_button.click()
        time.sleep(0.5)

        # Enter start and end dates
        start_date_cell = driver.find_element(By.CSS_SELECTOR, f"[data-date='{START_DATE}']")
        end_date_cell = driver.find_element(By.CSS_SELECTOR, f"[data-date='{END_DATE}']")

        start_date_cell.click()
        time.sleep(0.5)
        end_date_cell.click()
        time.sleep(0.5)

        # Find the occupancy configurator
        occupancy_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='occupancy-config']")
        occupancy_button.click()
        time.sleep(0.5)

        amount_people_section = driver.find_element(By.CLASS_NAME, 'e484bb5b7a')
        amount_buttons = amount_people_section.find_elements(By.TAG_NAME, 'button')
        amount_minus_button = amount_buttons[0]
        amount_plus_button = amount_buttons[1]
        amount_val = amount_people_section.find_element(By.CLASS_NAME, 'e32aa465fd')

        # Enter the amount of people
        logging.info(f"Current amount of people: {amount_val.text}; desired: {AMOUNT_PEOPLE}")
        while amount_val.text != f"{AMOUNT_PEOPLE}":
            amount = int(amount_val.text)
            if amount < AMOUNT_PEOPLE:
                amount_plus_button.click()
                time.sleep(0.5)
            elif amount > AMOUNT_PEOPLE:
                amount_minus_button.click()
                time.sleep(0.5)
            else:
                break


        # Hit search
        search_button = driver.find_element(By.CSS_SELECTOR, '.de576f5064.b46cd7aad7.ced67027e5.dda427e6b5.e4f9ca4b0c.ca8e0b9533.cfd71fb584.a9d40b8d51')
        search_button.click()
        time.sleep(4)

        # Get the top suggestion
        top_suggestion = driver.find_element(By.CSS_SELECTOR, "[data-testid='property-card']")
        hotel_title = top_suggestion.find_element(By.CSS_SELECTOR, "[data-testid='title']")
        hotel_price = top_suggestion.find_element(By.CSS_SELECTOR, "[data-testid='price-and-discounted-price']")
        hotel_config = top_suggestion.find_element(By.CSS_SELECTOR, "[data-testid='property-card-unit-configuration']")
        hotel_address = top_suggestion.find_element(By.CSS_SELECTOR, "[data-testid='address']")

        logging.info(f"Property found. Name '{hotel_title.text}'; price {hotel_price.text}; config: '{hotel_config.text}', address '{hotel_address.text}'")

        #Send an SMS
        sms_message = f"{hotel_address.text}\n{START_DATE} - {END_DATE}\n{hotel_title.text}: {hotel_price.text} Euro\n{hotel_config.text}"
        response = sns.publish(PhoneNumber=PHONE_NUMBER, Message=sms_message)
        logging.info(f"Message sent. Message ID: {response['MessageId']}")
    except (BotoCoreError, ClientError) as error:
        logging.error(f"Failed to send SMS: {error}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
    finally:
        logging.info("Closing browser")
        # Close the browser
        driver.quit()
