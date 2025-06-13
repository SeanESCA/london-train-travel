from datetime import datetime
import numpy as np
import re
from selenium import webdriver
from selenium.webdriver.common.by import By


def get_undergound_stations(driver):
    
    driver.get("https://en.wikipedia.org/wiki/List_of_London_Underground_stations")
    stations: list = [station.text for station in driver.find_elements(By.CSS_SELECTOR, ".wikitable tbody tr th:first-child a")]
    areas: list = [area.text for area in driver.find_elements(By.CSS_SELECTOR, ".wikitable tbody tr td:last-child a")]

    lines = []
    for entry in driver.find_elements(By.CSS_SELECTOR, ".wikitable tbody tr td:nth-child(3)"):
        lines_str: str = re.sub(r"\[.\]","",entry.text)
        lines.append(lines_str.split("\n"))

    assert len(stations) == len(lines)
    assert len(stations) == len(areas)

    unique_stations, counts = np.unique(stations, 
                                        return_counts=True)
    for station in unique_stations[counts > 1]:
        i = stations.index(station)
        stations.pop(i+1)
        lines[i] = lines[i] + lines[i+1]
        areas.pop(i+1)

    return {
        "stations": stations,
        "lines": lines,
        "areas": areas
    }

def get_journey(driver):
    # Open journey details.
    for element in driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Toggle details"]'):
        if element.is_displayed():
            element.click()
    
    # Collect stations.
    journey = []
    for entry in driver.find_elements(By.CSS_SELECTOR, 'span[id^=transit_group] h2'):
        # Remove '.' from abbreviations in the station name.
        station: str = re.sub(r"\.", "", entry.text)
        # Remove 'Station' from the station name unless it refers to Battersea Power Station.
        station = re.sub(r"(?<!Battersea Power) Station", r"", station)
        # Correct for Harrow-on-the-Hill.
        if station == "Harrow on the Hill":
            station = "Harrow-on-the-Hill"
        if len(station) > 0:
            journey.append(station)

    # Collect timestamps.
    timestamps = []
    for entry in driver.find_elements(By.CSS_SELECTOR, 'span[id^=transit_group] div:has(~ h2), span[id^=transit_group] > div > div:first-child'):
        timestamp_str: str = re.sub(r"\u202f", "", entry.text)
        if len(timestamp_str) > 0:
            timestamp = datetime.strptime(timestamp_str, "%I:%M%p")
            timestamps.append(timestamp)

    # Check extraction.
    assert len(journey) == len(timestamps)
    print(f'Number of stations: {len(journey)}')

    return {
        "journey": journey,
        "timestamps": timestamps
    }

def find_stations_in_range(mat: np.array, start_ind: int, travel_time: float, stations_ind: list) -> None:
    '''
    Find stations within the travel time using recursion.
    '''
    if travel_time > 0:
        stations_ind.append(start_ind)
        for i in np.where(mat[start_ind] > 0)[0]:
            # Travel time from the current station to the neighbouring station.
            g_val: float = mat[start_ind, i]
            # Only check stations within the travel time and that have not been visited.
            if (g_val < travel_time) and (i not in stations_ind):
                find_stations_in_range(mat, i, travel_time - g_val, stations_ind)