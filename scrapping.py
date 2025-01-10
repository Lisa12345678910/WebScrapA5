from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,StaleElementReferenceException,ElementClickInterceptedException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import re

# Initialize the WebDriver
service = Service(r'C:\Users\deslo\.wdm\drivers\chromedriver\win64\131.0.6778.108\chromedriver-win32\chromedriver.exe')
driver = webdriver.Chrome(service=service)

#part to scrap data from google flights :
def input_search_criteria(origin, destination, travel_departure):
    service = Service(r'C:\Users\deslo\.wdm\drivers\chromedriver\win64\131.0.6778.108\chromedriver-win32\chromedriver.exe')
   

    # Open Google Flights
    driver.get('https://www.google.com/travel/flights?hl=en')
    date_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Departure"]'))
    )
    date_input.clear()
    date_input.send_keys(travel_departure)
    time.sleep(1)
    date_input.send_keys(Keys.ENTER)


    origin_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Where from?"]'))
    )
    origin_input.clear()
    origin_input.send_keys(origin)
    origin_input.send_keys(Keys.ENTER)

    time.sleep(1)
    destination_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Where to?"]'))
    )
    destination_input.clear()
    destination_input.send_keys(destination)
    time.sleep(1)
    #click on the first suggestion
    click_first_suggestion = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[class="zsRT0d"]'))
    )
    click_first_suggestion.click()
    time.sleep(3)

    all_flights_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="View flights"]'))
    )
    driver.execute_script("arguments[0].target='_self';", all_flights_button)
    all_flights_button.click()

    # Attendre que la page des vols se charge
    WebDriverWait(driver, 20).until(
        lambda d: "/flights" in d.current_url
    )
    print(f"URL actuelle : {driver.current_url}")

    # Charger le contenu de la page avec BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Utiliser WebDriverWait pour attendre que le bouton soit cliquable
    sorted_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Sorted by top flights, Change sort order."]'))
    )
    sorted_button.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-menu-uid]'))
    )

    # Cliquer sur l'option "Emissions"
    emissions_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div/ul/li[6]/span[4]'))
    )
    emissions_option.click()
    time.sleep(3)


def scrape_flight_data():
    flight_data = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    current_url = driver.current_url
    print(f"Current URL1: {current_url}")
    liste_vols = soup.find_all('li', {'class': 'pIav2d'})

    print(f"Nombre de vols trouvés : {len(liste_vols)}")
    

    for flight in liste_vols:
        try:
            button_vol = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[3]/ul/li[{liste_vols.index(flight) + 1}]/div/div[3]/div/div/button'))
            )
            button_vol.click()
            time.sleep(1)# Heure de départ
            # Try to get flight number from span[10]
            flight_number = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[3]/ul/li[{liste_vols.index(flight) + 1}]/div/div[4]/div/div[1]/div[12]/span[8]'))
            ).text
            

            if len(flight_number) > 8:
               flight_number = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[3]/ul/li[{liste_vols.index(flight) + 1}]/div/div[4]/div/div[1]/div[12]/span[10]'))
                ).text
               airline=WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[3]/ul/li[{liste_vols.index(flight) + 1}]/div/div[4]/div/div[1]/div[12]/span[2]'))
            ).text
               
               plane= WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[3]/ul/li[{liste_vols.index(flight) + 1}]/div/div[4]/div/div[1]/div[12]/span[8]'))
            ).text
               class_category=WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[3]/ul/li[{liste_vols.index(flight) + 1}]/div/div[4]/div/div[1]/div[12]/span[6]'))
            ).text

            else:
                flight_number = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[3]/ul/li[{liste_vols.index(flight) + 1}]/div/div[4]/div/div[1]/div[12]/span[8]'))
            ).text
                airline=WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[3]/ul/li[{liste_vols.index(flight) + 1}]/div/div[4]/div/div[2]/div[11]/span[2]'))
            ).text
                plane= "Non Renseigné"
                class_category=WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/c-wiz[4]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]/div[3]/ul/li[{liste_vols.index(flight) + 1}]/div/div[4]/div/div[2]/div[11]/span[6]'))
            ).text

            
            departure_time_span = flight.find('span', {'aria-label': lambda x: x and 'Departure time' in x})
            departure_time = departure_time_span.get_text(strip=True) if departure_time_span else None

            arrival_time_span = flight.find('span', {'aria-label': lambda x: x and 'Arrival time' in x})
            arrival_time = arrival_time_span.get_text(strip=True) if arrival_time_span else None

            price_span = flight.find('span', {'aria-label': lambda x: x and 'euros' in x})
            price = price_span.get_text(strip=True) if price_span else None

            emissions = flight.find('div', {'class': 'O7CXue'}).get_text(strip=True) if flight.find('div', {'class': 'O7CXue'}) else None      

            flight_data.append({
                'Flight': flight_number,
                'Departure Time': departure_time,
                'Arrival Time': arrival_time,
                'Airline':airline,
                'Price (€)': price,
                'Emission (kg CO2)': emissions,
                'Class Category': class_category,
                'Plane': plane
            })
        except TimeoutException as e:
            return flight_data
            continue

        #stocke sur un fichier csv
        df = pd.DataFrame(flight_data)
        df.to_csv('flight_data.csv', index=False)

    return flight_data



