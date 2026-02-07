# Flight Search AI Agent - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Flight Search AI Agent                      │
│                        (Docker Container)                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          agent.py                                │
│                    (Main Orchestrator)                           │
│  • Schedules daily runs                                          │
│  • Coordinates all components                                    │
│  • Manages workflow                                              │
└───────────┬─────────────────────┬──────────────────┬────────────┘
            │                     │                  │
            ▼                     ▼                  ▼
┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│ flight_searcher  │  │   grok_client    │  │ memory_manager  │
│      .py         │  │      .py         │  │     .py         │
├──────────────────┤  ├──────────────────┤  ├─────────────────┤
│ • Web Scraping   │  │ • Grok AI API    │  │ • JSON Storage  │
│ • Google Flights │  │ • Flight Analysis│  │ • History       │
│ • Expedia        │  │ • Recommendations│  │ • Price Track   │
│ • Selenium       │  │ • Decision Making│  │ • Data Persist  │
└────────┬─────────┘  └────────┬─────────┘  └────────┬────────┘
         │                     │                      │
         ▼                     ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  External Sites  │  │   Grok AI API    │  │  Local Storage  │
│ • Google Flights │  │  (X.AI Service)  │  │   /app/data/    │
│ • Expedia.com    │  │                  │  │   /app/logs/    │
└──────────────────┘  └──────────────────┘  └─────────────────┘
```

## Component Details

### 1. agent.py (Main Orchestrator)
**Responsibilities:**
- Initialize all components
- Schedule daily execution
- Coordinate flight search workflow
- Manage error handling and logging

**Key Functions:**
- `__init__()` - Initialize components
- `search_flights()` - Trigger flight searches
- `analyze_flights()` - Send data to Grok AI
- `run_daily_search()` - Main execution routine
- `start()` - Start scheduler loop

### 2. flight_searcher.py (Web Scraping)
**Responsibilities:**
- Search flight booking websites
- Extract flight information
- Handle web automation
- Manage rate limiting

**Key Functions:**
- `search_google_flights()` - Search Google Flights
- `search_expedia()` - Search Expedia
- `_get_driver()` - Configure Selenium WebDriver
- `_extract_*_data()` - Parse search results

**Technologies:**
- Selenium WebDriver (Chrome headless)
- BeautifulSoup (HTML parsing)
- Chrome/Chromium browser

### 3. grok_client.py (AI Integration)
**Responsibilities:**
- Interface with Grok AI API
- Format analysis prompts
- Parse AI responses
- Handle API errors

**Key Functions:**
- `analyze()` - Send analysis request
- `summarize_flights()` - Get flight summary

**API Details:**
- Endpoint: https://api.x.ai/v1
- Model: grok-beta
- Uses OpenAI-compatible client

### 4. memory_manager.py (Data Persistence)
**Responsibilities:**
- Save search results
- Store AI analysis
- Track price history
- Manage JSON files

**Key Functions:**
- `save_flight_data()` - Store search results
- `save_analysis()` - Store AI analysis
- `get_historical_prices()` - Retrieve price data
- `get_latest_*()` - Get most recent data

**Storage Structure:**
```
/app/data/
├── flights_history.json    # All search results
├── analysis_history.json   # AI analysis results
└── price_tracking.json     # Price trends & stats
```

## Data Flow

```
1. SCHEDULE TRIGGER
   ↓
2. START SEARCH
   ↓
3. SEARCH GOOGLE FLIGHTS (flight_searcher.py)
   ├─→ Extract results
   └─→ Store in memory
   ↓
4. SEARCH EXPEDIA (flight_searcher.py)
   ├─→ Extract results
   └─→ Store in memory
   ↓
5. SAVE RESULTS (memory_manager.py)
   ├─→ flights_history.json
   └─→ price_tracking.json
   ↓
6. ANALYZE WITH GROK (grok_client.py)
   ├─→ Send flight data + history
   ├─→ Get recommendations
   └─→ Parse response
   ↓
7. SAVE ANALYSIS (memory_manager.py)
   └─→ analysis_history.json
   ↓
8. LOG RESULTS
   └─→ logs/agent.log
   ↓
9. WAIT FOR NEXT SCHEDULE
```

## Execution Flow

```
┌──────────────────────────────────────────────────────────┐
│ Container Starts                                         │
│ ↓                                                        │
│ Load Configuration (.env)                               │
│ ↓                                                        │
│ Initialize Components                                   │
│ ├─ FlightSearcher (Selenium)                           │
│ ├─ GrokClient (API)                                    │
│ └─ MemoryManager (Storage)                             │
│ ↓                                                        │
│ Run Initial Search (immediate)                          │
│ ↓                                                        │
│ Schedule Daily Job (default: 09:00)                     │
│ ↓                                                        │
│ Wait Loop (check every minute)                          │
│ ↓                                                        │
│ Execute Scheduled Job                                   │
│ └─ Search → Store → Analyze → Report                   │
│ ↓                                                        │
│ Repeat Daily...                                         │
└──────────────────────────────────────────────────────────┘
```

## Environment Configuration

```
┌─────────────────────────────────────────────────────────┐
│ Docker Container                                        │
│                                                         │
│ Environment Variables (.env)                            │
│ ├─ GROK_API_KEY          → Grok authentication        │
│ ├─ DEPARTURE_AIRPORT     → Search origin (IAD)        │
│ ├─ DESTINATION_AIRPORT   → Search destination (IDR)   │
│ ├─ DEPARTURE_DATE_*      → Departure date range       │
│ ├─ RETURN_DATE_*         → Return date range          │
│ ├─ PASSENGERS            → Number of passengers       │
│ └─ RUN_TIME              → Schedule time              │
│                                                         │
│ Volumes (Persistent)                                    │
│ ├─ ./data → /app/data    → Search history            │
│ └─ ./logs → /app/logs    → Application logs           │
└─────────────────────────────────────────────────────────┘
```

## Error Handling

- **Web Scraping Failures**: Logged, continues with other sources
- **API Errors**: Logged, analysis skipped for that run
- **Storage Errors**: Logged, data may be lost for that run
- **Network Issues**: Retry with exponential backoff (not implemented yet)

## Security Considerations

- API keys stored in environment variables
- No hardcoded credentials
- .gitignore prevents committing secrets
- Container isolation
- Minimal external dependencies

## Scalability

Current Implementation:
- Single container
- Sequential searches
- Local storage only

Potential Enhancements:
- Multiple containers for parallel searches
- Database backend (PostgreSQL, MongoDB)
- Message queue for job distribution
- Microservices architecture
- Cloud storage integration

## Dependencies

### Python Packages:
- `selenium` - Web automation
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `schedule` - Job scheduling
- `openai` - Grok API client
- `python-dotenv` - Environment management

### System Dependencies:
- Chromium browser
- ChromeDriver
- Python 3.11+
