"""
Email Client for sending flight analysis notifications.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailClient:
    """Client for sending email notifications via SMTP."""
    
    def __init__(self):
        """Initialize email client with SMTP configuration."""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.zoho.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '465'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.email_to = os.getenv('EMAIL_TO')
        
        if not all([self.smtp_user, self.smtp_password, self.email_to]):
            logger.warning("Email configuration incomplete. Email notifications will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"Email client initialized. Will send to: {self.email_to}")
    
    def send_flight_analysis(self, flights: List[Dict], analysis: Dict, search_params: Dict) -> bool:
        """
        Send flight analysis results via email.
        
        Args:
            flights: List of flight data
            analysis: Analysis results from Grok AI
            search_params: Search parameters used
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email client not enabled. Skipping email notification.")
            return False
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Flight Search Results: {search_params['departure_airport']} → {search_params['destination_airport']}"
            msg['From'] = self.smtp_user
            msg['To'] = self.email_to
            
            # Create email body
            html_body = self._create_html_body(flights, analysis, search_params)
            text_body = self._create_text_body(flights, analysis, search_params)
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email via SMTP
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {self.email_to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False
    
    def _create_text_body(self, flights: List[Dict], analysis: Dict, search_params: Dict) -> str:
        """Create plain text email body."""
        body = f"""
Flight Search Results
======================

Search Parameters:
- Route: {search_params['departure_airport']} → {search_params['destination_airport']}
- Departure: {search_params['departure_date_start']} to {search_params['departure_date_end']}
- Return: {search_params['return_date_start']} to {search_params['return_date_end']}
- Passengers: {search_params['passengers']}
- Class: {search_params['travel_class']}

Found {len(flights)} flight options.

AI Analysis:
{self._format_analysis_text(analysis)}

Flight Details:
{self._format_flights_text(flights)}

---
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return body
    
    def _create_html_body(self, flights: List[Dict], analysis: Dict, search_params: Dict) -> str:
        """Create HTML email body."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .params {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .param-item {{ margin: 5px 0; }}
        .analysis {{ background: #e8f5e9; padding: 15px; border-left: 4px solid #4caf50; margin: 20px 0; }}
        .flight {{ background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .flight-header {{ font-weight: bold; color: #2980b9; margin-bottom: 10px; }}
        .price {{ color: #27ae60; font-size: 1.2em; font-weight: bold; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✈️ Flight Search Results</h1>
        
        <div class="params">
            <h2>Search Parameters</h2>
            <div class="param-item"><strong>Route:</strong> {search_params['departure_airport']} → {search_params['destination_airport']}</div>
            <div class="param-item"><strong>Departure:</strong> {search_params['departure_date_start']} to {search_params['departure_date_end']}</div>
            <div class="param-item"><strong>Return:</strong> {search_params['return_date_start']} to {search_params['return_date_end']}</div>
            <div class="param-item"><strong>Passengers:</strong> {search_params['passengers']}</div>
            <div class="param-item"><strong>Class:</strong> {search_params['travel_class'].title()}</div>
        </div>
        
        <h2>📊 Found {len(flights)} Flight Options</h2>
        
        <div class="analysis">
            <h2>🤖 AI Analysis</h2>
            {self._format_analysis_html(analysis)}
        </div>
        
        <h2>Flight Details</h2>
        {self._format_flights_html(flights)}
        
        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _format_analysis_text(self, analysis: Dict) -> str:
        """Format analysis for plain text."""
        if not analysis:
            return "No analysis available."
        
        if isinstance(analysis, dict):
            if 'recommendation' in analysis:
                return analysis['recommendation']
            return str(analysis)
        return str(analysis)
    
    def _format_analysis_html(self, analysis: Dict) -> str:
        """Format analysis for HTML."""
        if not analysis:
            return "<p>No analysis available.</p>"
        
        if isinstance(analysis, dict):
            if 'recommendation' in analysis:
                # Convert newlines to <br> for HTML
                recommendation = analysis['recommendation'].replace('\n', '<br>')
                return f"<p>{recommendation}</p>"
            
            # Format dict as HTML list
            items = []
            for key, value in analysis.items():
                items.append(f"<li><strong>{key}:</strong> {value}</li>")
            return f"<ul>{''.join(items)}</ul>"
        
        return f"<p>{str(analysis)}</p>"
    
    def _format_flights_text(self, flights: List[Dict]) -> str:
        """Format flights for plain text."""
        if not flights:
            return "No flights found."
        
        result = []
        for i, flight in enumerate(flights[:10], 1):  # Limit to 10 flights
            result.append(f"\n{i}. {flight.get('source', 'Unknown')}")
            result.append(f"   Date: {flight.get('date', 'N/A')}")
            result.append(f"   Price: {flight.get('price', 'N/A')}")
            if 'departure_time' in flight:
                result.append(f"   Departure: {flight.get('departure_time', 'N/A')}")
            if 'arrival_time' in flight:
                result.append(f"   Arrival: {flight.get('arrival_time', 'N/A')}")
        
        if len(flights) > 10:
            result.append(f"\n... and {len(flights) - 10} more flights")
        
        return '\n'.join(result)
    
    def send_grok_recommendations(self, recommendations: str, search_params: Dict) -> bool:
        """
        Send Grok AI flight recommendations via email.
        
        Args:
            recommendations: Grok's flight search recommendations (text)
            search_params: Search parameters used
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email client not enabled. Skipping email notification.")
            return False
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Flight Recommendations: {search_params['departure_airport']} → {search_params['destination_airport']}"
            msg['From'] = self.smtp_user
            msg['To'] = self.email_to
            
            # Create email body
            html_body = self._create_grok_html_body(recommendations, search_params)
            text_body = self._create_grok_text_body(recommendations, search_params)
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email via SMTP
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {self.email_to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False
    
    def _create_grok_text_body(self, recommendations: str, search_params: Dict) -> str:
        """Create plain text email body for Grok recommendations."""
        body = f"""
Flight Search Results - Powered by Grok AI
==========================================

Search Parameters:
- Route: {search_params['departure_airport']} → {search_params['destination_airport']}
- Departure: {search_params['departure_date_start']} to {search_params['departure_date_end']}
- Return: {search_params['return_date_start']} to {search_params['return_date_end']}
- Passengers: {search_params['passengers']}
- Class: {search_params['travel_class']}

{recommendations}

---
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Powered by Grok AI
"""
        return body
    
    def _create_grok_html_body(self, recommendations: str, search_params: Dict) -> str:
        """Create HTML email body for Grok recommendations."""
        # Convert newlines to <br> and preserve formatting
        formatted_recommendations = recommendations.replace('\n', '<br>')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .params {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .param-item {{ margin: 5px 0; }}
        .recommendations {{ background: #fff; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0; white-space: pre-wrap; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 0.9em; }}
        .badge {{ background: #3498db; color: white; padding: 5px 10px; border-radius: 3px; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✈️ Flight Recommendations <span class="badge">Powered by Grok AI</span></h1>
        
        <div class="params">
            <h2>Search Parameters</h2>
            <div class="param-item"><strong>Route:</strong> {search_params['departure_airport']} → {search_params['destination_airport']}</div>
            <div class="param-item"><strong>Departure:</strong> {search_params['departure_date_start']} to {search_params['departure_date_end']}</div>
            <div class="param-item"><strong>Return:</strong> {search_params['return_date_start']} to {search_params['return_date_end']}</div>
            <div class="param-item"><strong>Passengers:</strong> {search_params['passengers']}</div>
            <div class="param-item"><strong>Class:</strong> {search_params['travel_class'].title()}</div>
        </div>
        
        <div class="recommendations">
            {formatted_recommendations}
        </div>
        
        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Powered by Grok AI
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _format_flights_html(self, flights: List[Dict]) -> str:
        """Format flights for HTML."""
        if not flights:
            return "<p>No flights found.</p>"
        
        result = []
        for i, flight in enumerate(flights[:10], 1):  # Limit to 10 flights
            result.append(f"""
            <div class="flight">
                <div class="flight-header">Flight {i} - {flight.get('source', 'Unknown')}</div>
                <div><strong>Date:</strong> {flight.get('date', 'N/A')}</div>
                <div class="price">Price: {flight.get('price', 'N/A')}</div>
                {'<div><strong>Departure:</strong> ' + flight.get('departure_time', 'N/A') + '</div>' if 'departure_time' in flight else ''}
                {'<div><strong>Arrival:</strong> ' + flight.get('arrival_time', 'N/A') + '</div>' if 'arrival_time' in flight else ''}
            </div>
            """)
        
        if len(flights) > 10:
            result.append(f"<p><em>... and {len(flights) - 10} more flights</em></p>")
        
        return ''.join(result)

