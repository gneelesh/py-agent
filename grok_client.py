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
        self.model = "grok-beta"
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
