"""
Flight Search AI Agent - Simplified Version
This agent uses Grok AI to search for flights and provide recommendations.
"""

import os
import json
import time
import schedule
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict
from dotenv import load_dotenv

from grok_client import GrokClient
from email_client import EmailClient

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
    """AI Agent that uses Grok to search for flights and find the best deals."""
    
    def __init__(self):
        """Initialize the flight agent."""
        self.grok_client = GrokClient(
            api_key=os.getenv('GROK_API_KEY'),
            api_base=os.getenv('GROK_API_BASE', 'https://api.x.ai/v1')
        )
        self.email_client = EmailClient()
        
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
    
    def run_daily_search(self):
        """Main function to run the daily search routine."""
        logger.info("=" * 50)
        logger.info("Starting daily flight search routine")
        logger.info("=" * 50)
        
        try:
            # Ask Grok to search for flights
            logger.info("Requesting Grok AI to search for flights...")
            flight_recommendations = self.grok_client.search_flights(self.search_params)
            
            # Log the recommendations
            logger.info("=" * 50)
            logger.info("GROK FLIGHT RECOMMENDATIONS")
            logger.info("=" * 50)
            logger.info(flight_recommendations)
            
            # Send email notification
            logger.info("Sending email notification...")
            self.email_client.send_grok_recommendations(
                flight_recommendations, 
                self.search_params
            )
            
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
