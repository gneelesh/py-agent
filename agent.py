"""
Flight Search AI Agent
This agent searches for flights on Expedia and Google Flights daily,
tracks prices, and finds the best deals using Grok AI.
"""

import os
import json
import time
import schedule
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

from flight_searcher import FlightSearcher
from grok_client import GrokClient
from memory_manager import MemoryManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FlightAgent:
    """AI Agent that searches for flights and finds the best deals."""
    
    def __init__(self):
        """Initialize the flight agent."""
        self.grok_client = GrokClient(
            api_key=os.getenv('GROK_API_KEY'),
            api_base=os.getenv('GROK_API_BASE', 'https://api.x.ai/v1')
        )
        self.memory_manager = MemoryManager('/app/data')
        self.flight_searcher = FlightSearcher()
        
        # Load search parameters from environment
        self.search_params = {
            'departure_airport': os.getenv('DEPARTURE_AIRPORT', 'IAD'),
            'destination_airport': os.getenv('DESTINATION_AIRPORT', 'IDR'),
            'departure_date_start': os.getenv('DEPARTURE_DATE_START', '2026-06-13'),
            'departure_date_end': os.getenv('DEPARTURE_DATE_END', '2026-06-17'),
            'return_date_start': os.getenv('RETURN_DATE_START', '2026-06-30'),
            'return_date_end': os.getenv('RETURN_DATE_END', '2026-07-05'),
            'passengers': int(os.getenv('PASSENGERS', '1')),
            'travel_class': os.getenv('TRAVEL_CLASS', 'economy')
        }
        
        logger.info("Flight Agent initialized with parameters: %s", self.search_params)
    
    def search_flights(self) -> List[Dict]:
        """Search for flights on multiple platforms."""
        logger.info("Starting flight search...")
        all_flights = []
        
        try:
            # Search on Google Flights
            logger.info("Searching Google Flights...")
            google_flights = self.flight_searcher.search_google_flights(self.search_params)
            all_flights.extend(google_flights)
            logger.info(f"Found {len(google_flights)} flights on Google Flights")
            
            # Search on Expedia
            logger.info("Searching Expedia...")
            expedia_flights = self.flight_searcher.search_expedia(self.search_params)
            all_flights.extend(expedia_flights)
            logger.info(f"Found {len(expedia_flights)} flights on Expedia")
            
        except Exception as e:
            logger.error(f"Error searching flights: {e}", exc_info=True)
        
        return all_flights
    
    def analyze_flights(self, flights: List[Dict]) -> Dict:
        """Analyze flights using Grok AI to find the best options."""
        if not flights:
            logger.warning("No flights to analyze")
            return {}
        
        logger.info(f"Analyzing {len(flights)} flights with Grok AI...")
        
        # Get historical data for comparison
        historical_data = self.memory_manager.get_historical_prices()
        
        # Prepare prompt for Grok
        prompt = self._create_analysis_prompt(flights, historical_data)
        
        try:
            analysis = self.grok_client.analyze(prompt)
            logger.info("Grok analysis completed")
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing flights with Grok: {e}", exc_info=True)
            return {}
    
    def _create_analysis_prompt(self, flights: List[Dict], historical_data: Dict) -> str:
        """Create a prompt for Grok AI analysis."""
        prompt = f"""
Analyze the following flight options from {self.search_params['departure_airport']} to {self.search_params['destination_airport']}:

Current Flight Options:
{json.dumps(flights, indent=2)}

Historical Price Data:
{json.dumps(historical_data, indent=2)}

Please analyze:
1. Which flight offers the best value for money?
2. Are prices trending up or down?
3. What is the best departure date considering price and convenience?
4. Should we book now or wait for better prices?

Provide a structured recommendation with reasoning.
"""
        return prompt
    
    def run_daily_search(self):
        """Main function to run the daily search routine."""
        logger.info("=" * 50)
        logger.info("Starting daily flight search routine")
        logger.info("=" * 50)
        
        try:
            # Search for flights
            flights = self.search_flights()
            
            # Store the results
            timestamp = datetime.now().isoformat()
            self.memory_manager.save_flight_data(timestamp, flights)
            
            # Analyze flights with Grok
            if flights:
                analysis = self.analyze_flights(flights)
                self.memory_manager.save_analysis(timestamp, analysis)
                
                # Log the best recommendations
                logger.info("=" * 50)
                logger.info("ANALYSIS RESULTS")
                logger.info("=" * 50)
                logger.info(json.dumps(analysis, indent=2))
            else:
                logger.warning("No flights found in this search")
            
            logger.info("Daily search routine completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily search routine: {e}", exc_info=True)
    
    def start(self):
        """Start the agent with scheduled daily runs."""
        run_time = os.getenv('RUN_TIME', '09:00')
        logger.info(f"Agent starting. Scheduled to run daily at {run_time}")
        
        # Schedule the daily job
        schedule.every().day.at(run_time).do(self.run_daily_search)
        
        # Run immediately on startup
        logger.info("Running initial search...")
        self.run_daily_search()
        
        # Keep running
        logger.info("Agent is now running. Waiting for next scheduled run...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Main entry point."""
    logger.info("Initializing Flight Search AI Agent...")
    
    # Verify required environment variables
    if not os.getenv('GROK_API_KEY'):
        logger.error("GROK_API_KEY environment variable not set!")
        return
    
    try:
        agent = FlightAgent()
        agent.start()
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
