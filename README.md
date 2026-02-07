# Flight Search AI Agent

An intelligent AI agent that automatically searches for flights daily on Google Flights and Expedia, analyzes prices using Grok AI, and helps you find the best deals.

## Features

- 🤖 **AI-Powered Analysis**: Uses Grok AI to analyze flight options and provide intelligent recommendations
- 🔍 **Multi-Platform Search**: Searches both Google Flights and Expedia
- 📊 **Price Tracking**: Maintains historical price data to identify trends
- ⏰ **Automated Daily Runs**: Runs automatically every day at a configured time
- 💾 **Persistent Memory**: Stores all search results and analysis in local storage
- 🐳 **Docker Support**: Fully containerized for easy deployment

## Search Configuration

The agent is configured to search for:
- **Route**: Washington Dulles (IAD) → Indore, India (IDR) → Washington Dulles (IAD)
- **Departure Dates**: June 13-17, 2026 (flexible)
- **Return Dates**: June 30 - July 5, 2026 (flexible)
- **Class**: Economy
- **Passengers**: 1

## Prerequisites

- Docker and Docker Compose installed
- Grok API key from X.AI

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/gneelesh/py-agent.git
   cd py-agent
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your Grok API key:
   ```
   GROK_API_KEY=your_actual_grok_api_key_here
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

## Configuration

You can customize the search parameters by editing the `.env` file:

```env
# Grok API Configuration
GROK_API_KEY=your_grok_api_key_here
GROK_API_BASE=https://api.x.ai/v1

# Flight Search Parameters
DEPARTURE_AIRPORT=IAD
DESTINATION_AIRPORT=IDR
DEPARTURE_DATE_START=2026-06-13
DEPARTURE_DATE_END=2026-06-17
RETURN_DATE_START=2026-06-30
RETURN_DATE_END=2026-07-05
PASSENGERS=1
TRAVEL_CLASS=economy

# Schedule Configuration
RUN_TIME=09:00
```

## Architecture

The agent consists of several modules:

- **agent.py**: Main orchestrator that coordinates the search and analysis
- **flight_searcher.py**: Handles web scraping of Google Flights and Expedia
- **grok_client.py**: Interfaces with Grok AI for intelligent analysis
- **memory_manager.py**: Manages persistent storage of search results and history

## Data Storage

All data is stored in the `data/` directory:
- `flights_history.json`: Complete history of all flight searches
- `analysis_history.json`: AI analysis results for each search
- `price_tracking.json`: Aggregated price trends and statistics

Logs are stored in the `logs/` directory:
- `agent.log`: Application logs

## Manual Run (Without Docker)

If you prefer to run without Docker:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export GROK_API_KEY=your_key_here
   # Set other variables as needed
   ```

3. **Run the agent**
   ```bash
   python agent.py
   ```

## How It Works

1. **Daily Schedule**: The agent runs at the configured time each day (default: 9:00 AM)
2. **Flight Search**: Searches Google Flights and Expedia for flights matching your criteria
3. **Data Storage**: Saves all flight results to local JSON files
4. **AI Analysis**: Sends flight data to Grok AI for analysis
5. **Recommendations**: Grok analyzes prices, trends, and provides booking recommendations
6. **Historical Tracking**: Maintains price history to identify trends

## Development

### Project Structure

```
py-agent/
├── agent.py              # Main agent orchestrator
├── flight_searcher.py    # Flight search functionality
├── grok_client.py        # Grok AI client
├── memory_manager.py     # Data persistence
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Docker Compose configuration
├── .env.example          # Example environment variables
├── data/                 # Persistent data storage
└── logs/                 # Application logs
```

### Docker Commands

- Start the agent: `docker-compose up -d`
- Stop the agent: `docker-compose down`
- View logs: `docker-compose logs -f`
- Rebuild: `docker-compose up -d --build`

## Troubleshooting

### Agent not starting
- Check that `GROK_API_KEY` is set correctly in `.env`
- Verify Docker is running: `docker ps`
- Check logs: `docker-compose logs`

### No flights found
- Flight booking sites frequently change their structure
- The web scraping may need updates for current site layouts
- Check logs for specific errors

### API errors
- Verify your Grok API key is valid
- Check API rate limits
- Ensure you have internet connectivity

## Notes

- **Web Scraping**: Flight booking sites actively prevent automated access. The current implementation provides a framework but may require adjustments based on site changes and anti-bot measures.
- **Rate Limiting**: The agent includes delays between searches to be respectful of the target sites.
- **Legal**: Ensure compliance with the terms of service of the flight search platforms.

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
