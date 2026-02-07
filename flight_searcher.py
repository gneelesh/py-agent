"""
Flight Searcher for querying flight information from various platforms.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class FlightSearcher:
    """Searches for flights on various platforms."""
    
    def __init__(self):
        """Initialize the flight searcher."""
        self.driver = None
        logger.info("Flight searcher initialized")
    
    def _get_driver(self) -> webdriver.Chrome:
        """Get a configured Chrome WebDriver."""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome WebDriver initialized")
        
        return self.driver
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("WebDriver closed")
    
    def search_google_flights(self, params: Dict) -> List[Dict]:
        """
        Search for flights on Google Flights.
        
        Args:
            params: Search parameters dictionary
            
        Returns:
            List of flight dictionaries
        """
        flights = []
        
        try:
            driver = self._get_driver()
            
            # Generate date range for departure
            dep_start = datetime.strptime(params['departure_date_start'], '%Y-%m-%d')
            dep_end = datetime.strptime(params['departure_date_end'], '%Y-%m-%d')
            
            # Search for each departure date
            current_date = dep_start
            while current_date <= dep_end:
                dep_date = current_date.strftime('%Y-%m-%d')
                
                # Calculate return dates
                ret_start = datetime.strptime(params['return_date_start'], '%Y-%m-%d')
                ret_end = datetime.strptime(params['return_date_end'], '%Y-%m-%d')
                
                # Use middle return date for simplicity
                ret_date = (ret_start + (ret_end - ret_start) / 2).strftime('%Y-%m-%d')
                
                logger.info(f"Searching Google Flights: {params['departure_airport']} -> {params['destination_airport']} on {dep_date}")
                
                # Construct Google Flights URL
                url = self._build_google_flights_url(
                    params['departure_airport'],
                    params['destination_airport'],
                    dep_date,
                    ret_date,
                    params['passengers']
                )
                
                try:
                    driver.get(url)
                    time.sleep(5)  # Wait for page load
                    
                    # Try to extract flight information
                    flight_data = self._extract_google_flights_data(driver, dep_date, ret_date)
                    flights.extend(flight_data)
                    
                except Exception as e:
                    logger.error(f"Error searching Google Flights for {dep_date}: {e}")
                
                current_date += timedelta(days=1)
                time.sleep(2)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error in Google Flights search: {e}", exc_info=True)
        
        return flights
    
    def search_expedia(self, params: Dict) -> List[Dict]:
        """
        Search for flights on Expedia.
        
        Args:
            params: Search parameters dictionary
            
        Returns:
            List of flight dictionaries
        """
        flights = []
        
        try:
            driver = self._get_driver()
            
            # Generate date range for departure
            dep_start = datetime.strptime(params['departure_date_start'], '%Y-%m-%d')
            dep_end = datetime.strptime(params['departure_date_end'], '%Y-%m-%d')
            
            # Search for each departure date
            current_date = dep_start
            while current_date <= dep_end:
                dep_date = current_date.strftime('%Y-%m-%d')
                
                # Calculate return dates
                ret_start = datetime.strptime(params['return_date_start'], '%Y-%m-%d')
                ret_end = datetime.strptime(params['return_date_end'], '%Y-%m-%d')
                
                # Use middle return date for simplicity
                ret_date = (ret_start + (ret_end - ret_start) / 2).strftime('%Y-%m-%d')
                
                logger.info(f"Searching Expedia: {params['departure_airport']} -> {params['destination_airport']} on {dep_date}")
                
                # Construct Expedia URL
                url = self._build_expedia_url(
                    params['departure_airport'],
                    params['destination_airport'],
                    dep_date,
                    ret_date,
                    params['passengers']
                )
                
                try:
                    driver.get(url)
                    time.sleep(5)  # Wait for page load
                    
                    # Try to extract flight information
                    flight_data = self._extract_expedia_data(driver, dep_date, ret_date)
                    flights.extend(flight_data)
                    
                except Exception as e:
                    logger.error(f"Error searching Expedia for {dep_date}: {e}")
                
                current_date += timedelta(days=1)
                time.sleep(2)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error in Expedia search: {e}", exc_info=True)
        
        return flights
    
    def _build_google_flights_url(self, origin: str, dest: str, dep_date: str, ret_date: str, passengers: int) -> str:
        """Build Google Flights search URL."""
        return f"https://www.google.com/travel/flights?q=flights%20from%20{origin}%20to%20{dest}%20on%20{dep_date}%20return%20{ret_date}%20{passengers}%20passenger"
    
    def _build_expedia_url(self, origin: str, dest: str, dep_date: str, ret_date: str, passengers: int) -> str:
        """Build Expedia search URL."""
        # Convert date format for Expedia
        dep = datetime.strptime(dep_date, '%Y-%m-%d').strftime('%m/%d/%Y')
        ret = datetime.strptime(ret_date, '%Y-%m-%d').strftime('%m/%d/%Y')
        return f"https://www.expedia.com/Flights-Search?trip=roundtrip&leg1=from:{origin},to:{dest},departure:{dep}&leg2=from:{dest},to:{origin},departure:{ret}&passengers=adults:{passengers}"
    
    def _extract_google_flights_data(self, driver, dep_date: str, ret_date: str) -> List[Dict]:
        """Extract flight data from Google Flights page."""
        flights = []
        
        try:
            # Wait for results to load
            wait = WebDriverWait(driver, 10)
            
            # This is a simplified extraction - actual selectors may vary
            # Google Flights uses dynamic content, so this is a basic approach
            
            # Try to find price elements (these selectors are examples and may need adjustment)
            price_elements = driver.find_elements(By.CSS_SELECTOR, "[role='listitem']")
            
            for idx, element in enumerate(price_elements[:5]):  # Limit to first 5
                try:
                    # Extract basic information - actual implementation would need proper selectors
                    text = element.text
                    
                    # Create a flight entry (this is simplified)
                    flights.append({
                        'source': 'google_flights',
                        'departure_date': dep_date,
                        'return_date': ret_date,
                        'price': None,  # Would extract from text
                        'airline': 'Various',  # Would extract from elements
                        'duration': 'Unknown',  # Would extract from elements
                        'stops': 'Unknown',  # Would extract from elements
                        'raw_data': text[:200] if text else '',
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.debug(f"Error extracting flight {idx}: {e}")
            
            if not flights:
                # If no structured data found, create a placeholder entry
                flights.append({
                    'source': 'google_flights',
                    'departure_date': dep_date,
                    'return_date': ret_date,
                    'price': None,
                    'airline': 'Search completed',
                    'note': 'Manual verification needed - automated extraction requires further development',
                    'timestamp': datetime.now().isoformat()
                })
                
        except TimeoutException:
            logger.warning("Timeout waiting for Google Flights results")
        except Exception as e:
            logger.error(f"Error extracting Google Flights data: {e}")
        
        return flights
    
    def _extract_expedia_data(self, driver, dep_date: str, ret_date: str) -> List[Dict]:
        """Extract flight data from Expedia page."""
        flights = []
        
        try:
            # Wait for results to load
            wait = WebDriverWait(driver, 10)
            
            # This is a simplified extraction - actual selectors may vary
            # Expedia structure changes frequently, so this is a basic approach
            
            # Try to find flight listings
            flight_elements = driver.find_elements(By.CSS_SELECTOR, "[data-test-id*='offer']")
            
            for idx, element in enumerate(flight_elements[:5]):  # Limit to first 5
                try:
                    text = element.text
                    
                    # Create a flight entry (this is simplified)
                    flights.append({
                        'source': 'expedia',
                        'departure_date': dep_date,
                        'return_date': ret_date,
                        'price': None,  # Would extract from text
                        'airline': 'Various',  # Would extract from elements
                        'duration': 'Unknown',  # Would extract from elements
                        'stops': 'Unknown',  # Would extract from elements
                        'raw_data': text[:200] if text else '',
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.debug(f"Error extracting flight {idx}: {e}")
            
            if not flights:
                # If no structured data found, create a placeholder entry
                flights.append({
                    'source': 'expedia',
                    'departure_date': dep_date,
                    'return_date': ret_date,
                    'price': None,
                    'airline': 'Search completed',
                    'note': 'Manual verification needed - automated extraction requires further development',
                    'timestamp': datetime.now().isoformat()
                })
                
        except TimeoutException:
            logger.warning("Timeout waiting for Expedia results")
        except Exception as e:
            logger.error(f"Error extracting Expedia data: {e}")
        
        return flights
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()
