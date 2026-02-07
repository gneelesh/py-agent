# Flight Search Agent - Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed on your system
- Grok API key from X.AI (https://x.ai/)

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/gneelesh/py-agent.git
cd py-agent
```

### Step 2: Set Up Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Grok API key
nano .env  # or use your preferred editor
```

Required: Set `GROK_API_KEY=your_actual_api_key_here`

### Step 3: Run the Agent

#### Option A: Use the Quick Start Script
```bash
./run.sh
```

#### Option B: Manual Docker Commands
```bash
# Build the Docker image
docker-compose build

# Start the agent
docker-compose up -d

# View logs
docker-compose logs -f
```

## Usage

### View Logs
```bash
docker-compose logs -f
```

### Stop the Agent
```bash
docker-compose down
```

### Restart the Agent
```bash
docker-compose restart
```

### Check Status
```bash
docker-compose ps
```

## Data Storage

All data is stored in local directories that persist between runs:

- `./data/` - Flight search results and price history
  - `flights_history.json` - Complete history of all searches
  - `analysis_history.json` - AI analysis for each search
  - `price_tracking.json` - Price trends and statistics

- `./logs/` - Application logs
  - `agent.log` - Detailed application logs

## Configuration

Edit `.env` to customize:

```env
# Search Parameters
DEPARTURE_AIRPORT=IAD          # Origin airport code
DESTINATION_AIRPORT=IDR        # Destination airport code
DEPARTURE_DATE_START=2026-06-13
DEPARTURE_DATE_END=2026-06-17
RETURN_DATE_START=2026-06-30
RETURN_DATE_END=2026-07-05
PASSENGERS=1
TRAVEL_CLASS=economy

# Schedule
RUN_TIME=09:00                 # Daily run time (24-hour format)
```

## How It Works

1. **Scheduled Execution**: Agent runs daily at the configured time
2. **Flight Search**: Searches Google Flights and Expedia for your route
3. **Data Collection**: Saves all flight information to local storage
4. **AI Analysis**: Uses Grok AI to analyze prices and trends
5. **Recommendations**: Provides intelligent booking recommendations

## Checking Results

### View Latest Analysis
```bash
cat ./data/analysis_history.json | tail -50
```

### View Price Trends
```bash
cat ./data/price_tracking.json
```

### View Recent Logs
```bash
tail -50 ./logs/agent.log
```

## Troubleshooting

### Agent Won't Start
- Verify Docker is running: `docker ps`
- Check you've set GROK_API_KEY in .env
- View logs: `docker-compose logs`

### No Flights Found
- Web scraping is challenging due to anti-bot measures
- Check logs for specific errors
- Sites may have changed their structure

### API Errors
- Verify your Grok API key is valid
- Check you have API credits remaining
- Ensure internet connectivity

## Advanced Usage

### Run Tests
```bash
python3 test_agent.py
```

### Manual Run (Without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROK_API_KEY=your_key_here

# Run agent
python agent.py
```

### Customize Search
Edit the search parameters in `.env` to search for different:
- Routes (change airport codes)
- Dates (update date ranges)
- Number of passengers
- Travel class

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Review README.md for detailed documentation
3. Open an issue on GitHub

## Important Notes

⚠️ **Web Scraping**: Flight booking sites actively prevent automated access. The scraping functionality provides a framework but may require adjustments.

⚠️ **Rate Limiting**: The agent includes delays to be respectful of target sites. Don't reduce these delays.

⚠️ **Legal**: Ensure compliance with the terms of service of flight search platforms.
