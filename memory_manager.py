"""
Memory Manager for storing and retrieving flight search history.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages persistent storage of flight search data."""
    
    def __init__(self, data_dir: str = "/app/data"):
        """
        Initialize memory manager.
        
        Args:
            data_dir: Directory for storing data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.flights_file = self.data_dir / "flights_history.json"
        self.analysis_file = self.data_dir / "analysis_history.json"
        self.prices_file = self.data_dir / "price_tracking.json"
        
        logger.info(f"Memory manager initialized with data directory: {data_dir}")
    
    def save_flight_data(self, timestamp: str, flights: List[Dict]) -> None:
        """
        Save flight search results.
        
        Args:
            timestamp: ISO format timestamp
            flights: List of flight dictionaries
        """
        try:
            history = self._load_json(self.flights_file, default={})
            history[timestamp] = flights
            self._save_json(self.flights_file, history)
            
            # Update price tracking
            self._update_price_tracking(timestamp, flights)
            
            logger.info(f"Saved {len(flights)} flights for {timestamp}")
        except Exception as e:
            logger.error(f"Error saving flight data: {e}", exc_info=True)
    
    def save_analysis(self, timestamp: str, analysis: Dict) -> None:
        """
        Save Grok analysis results.
        
        Args:
            timestamp: ISO format timestamp
            analysis: Analysis dictionary
        """
        try:
            history = self._load_json(self.analysis_file, default={})
            history[timestamp] = analysis
            self._save_json(self.analysis_file, history)
            logger.info(f"Saved analysis for {timestamp}")
        except Exception as e:
            logger.error(f"Error saving analysis: {e}", exc_info=True)
    
    def get_historical_prices(self, days: int = 30) -> Dict:
        """
        Get historical price data.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary of price history
        """
        try:
            prices = self._load_json(self.prices_file, default={})
            return prices
        except Exception as e:
            logger.error(f"Error loading price history: {e}")
            return {}
    
    def get_latest_flights(self) -> Optional[List[Dict]]:
        """
        Get the most recent flight search results.
        
        Returns:
            List of flight dictionaries or None
        """
        try:
            history = self._load_json(self.flights_file, default={})
            if not history:
                return None
            
            latest_timestamp = max(history.keys())
            return history[latest_timestamp]
        except Exception as e:
            logger.error(f"Error loading latest flights: {e}")
            return None
    
    def get_latest_analysis(self) -> Optional[Dict]:
        """
        Get the most recent analysis.
        
        Returns:
            Analysis dictionary or None
        """
        try:
            history = self._load_json(self.analysis_file, default={})
            if not history:
                return None
            
            latest_timestamp = max(history.keys())
            return history[latest_timestamp]
        except Exception as e:
            logger.error(f"Error loading latest analysis: {e}")
            return None
    
    def _update_price_tracking(self, timestamp: str, flights: List[Dict]) -> None:
        """
        Update price tracking with new flight data.
        
        Args:
            timestamp: ISO format timestamp
            flights: List of flight dictionaries
        """
        try:
            prices = self._load_json(self.prices_file, default={
                "min_price": None,
                "max_price": None,
                "avg_prices": [],
                "history": []
            })
            
            if flights:
                flight_prices = [f.get('price', 0) for f in flights if f.get('price')]
                if flight_prices:
                    min_price = min(flight_prices)
                    max_price = max(flight_prices)
                    avg_price = sum(flight_prices) / len(flight_prices)
                    
                    prices["history"].append({
                        "timestamp": timestamp,
                        "min_price": min_price,
                        "max_price": max_price,
                        "avg_price": avg_price,
                        "num_flights": len(flights)
                    })
                    
                    # Update overall min/max
                    if prices["min_price"] is None or min_price < prices["min_price"]:
                        prices["min_price"] = min_price
                    if prices["max_price"] is None or max_price > prices["max_price"]:
                        prices["max_price"] = max_price
                    
                    prices["avg_prices"].append(avg_price)
                    
                    self._save_json(self.prices_file, prices)
        except Exception as e:
            logger.error(f"Error updating price tracking: {e}")
    
    def _load_json(self, file_path: Path, default=None):
        """Load JSON from file."""
        if not file_path.exists():
            return default
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in {file_path}, returning default")
            return default
    
    def _save_json(self, file_path: Path, data) -> None:
        """Save data to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
