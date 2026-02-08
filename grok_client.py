"""
Grok API Client for interacting with Grok AI.
"""

import json
import logging
from typing import Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class GrokClient:
    """Client for interacting with Grok AI API."""
    
    def __init__(self, api_key: str, api_base: str = "https://api.x.ai/v1"):
        """
        Initialize Grok client.
        
        Args:
            api_key: Grok API key
            api_base: API base URL
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        self.model = "grok-3"
        logger.info("Grok client initialized")
    
    def analyze(self, prompt: str, temperature: float = 0.7) -> Dict:
        """
        Analyze data using Grok AI.
        
        Args:
            prompt: The prompt to send to Grok
            temperature: Sampling temperature (0-1)
            
        Returns:
            Dict containing the analysis results
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant specializing in flight search and travel optimization. Provide clear, actionable recommendations based on the data provided."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature
            )
            
            result = response.choices[0].message.content
            
            # Try to parse as JSON if possible, otherwise return as text
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {
                    "recommendation": result,
                    "raw_response": result
                }
                
        except Exception as e:
            logger.error(f"Error calling Grok API: {e}", exc_info=True)
            raise
    
    def search_flights(self, search_params: Dict) -> str:
        """
        Ask Grok AI to search for flights and provide recommendations.
        
        Args:
            search_params: Dictionary containing search parameters
            
        Returns:
            Grok's flight search results and recommendations
        """
        prompt = f"""
You are a flight search assistant. Please search for flights with the following criteria:

Route: {search_params['departure_airport']} to {search_params['destination_airport']}
Departure Date Range: {search_params['departure_date_start']} to {search_params['departure_date_end']}
Return Date Range: {search_params['return_date_start']} to {search_params['return_date_end']}
Passengers: {search_params['passengers']}
Class: {search_params['travel_class']}

Please:
1. Search for flights on Google Flights and Expedia for all dates in the departure range
2. Compare the available options
3. Find the best flight that offers the optimal combination of:
   - Price (lower is better)
   - Flight duration (shorter is better)
   - Number of stops (fewer is better)
4. Provide specific recommendations with:
   - Exact flight details (airline, flight number, times)
   - Price comparison across dates
   - Why this is the best option
   - Alternative options if available

Format your response clearly with sections for:
- Best Recommended Flight
- Price Analysis
- Alternative Options
- Booking Recommendation (should we book now or wait?)
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful flight search assistant with access to real-time flight data. Provide detailed, accurate flight recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            logger.info("Grok flight search completed")
            return result
            
        except Exception as e:
            logger.error(f"Error searching flights with Grok: {e}", exc_info=True)
            return f"Error searching for flights: {str(e)}"
    
    def summarize_flights(self, flights: list) -> str:
        """
        Get a summary of flight options.
        
        Args:
            flights: List of flight dictionaries
            
        Returns:
            Summary text
        """
        prompt = f"""
Summarize these flight options concisely:
{json.dumps(flights, indent=2)}

Provide a brief summary highlighting:
- Number of options
- Price range
- Best value option
"""
        try:
            response = self.analyze(prompt)
            return response.get("recommendation", "")
        except Exception as e:
            logger.error(f"Error summarizing flights: {e}")
            return "Unable to generate summary"

