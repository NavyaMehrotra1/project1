# 🤖 M&A Intelligence Agent Setup Guide

## Overview
The M&A Intelligence Agent continuously monitors the web using Exa API to discover:
- **Mergers & Acquisitions**
- **Business Partnerships** 
- **Consolidations**
- **Joint Ventures**
- **Strategic Alliances**

The agent runs every **1 minute** and provides real-time notifications when new deals are discovered.

## Quick Start

### 1. Set Up Exa API Key
```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Edit the .env file and add your Exa API key
# EXA_API_KEY=your_exa_api_key_here
```

### 2. Start the Backend Server
```bash
cd backend
python main.py
```
The server will run on `http://localhost:8000`

### 3. Start the Frontend (Optional)
```bash
npm run dev
```
Visit `http://localhost:3000/ma-agent` to see the dashboard

### 4. Start the Agent via API
```bash
# Start the agent
curl -X POST http://localhost:8000/ma-agent/start

# Check status
curl http://localhost:8000/ma-agent/status

# Stop the agent
curl -X POST http://localhost:8000/ma-agent/stop
```

### 5. Or Run Standalone Agent
```bash
cd backend
python run_ma_agent.py
```

## API Endpoints

### Agent Control
- `POST /ma-agent/start` - Start monitoring
- `POST /ma-agent/stop` - Stop monitoring  
- `GET /ma-agent/status` - Get agent status

### Data Access
- `GET /ma-agent/events?hours=24` - Get recent M&A events
- `GET /ma-agent/notifications` - Get notifications
- `GET /ma-agent/activities` - Get agent activity log
- `GET /ma-agent/dashboard` - Complete dashboard data

### Event Details
- `GET /ma-agent/events/{event_id}` - Get specific event details
- `POST /ma-agent/notifications/{id}/read` - Mark notification as read

## Dashboard Features

### 📊 Real-time Statistics
- Total events discovered
- Events found today
- High confidence events
- Unread notifications

### 🔔 Notification System
- New event alerts
- Ecosystem impact notifications  
- Priority-based filtering
- Mark as read functionality

### 📈 Agent Activity Log
- Search operations
- Events found per cycle
- Execution times
- Success/failure status

### 🏢 Recent M&A Events
- Event classification
- Company names involved
- Deal values (when available)
- Confidence scores
- Source links

## Event Types Monitored

1. **Merger & Acquisition** - Company buyouts, acquisitions, mergers
2. **Business Partnership** - Strategic partnerships, collaborations
3. **Consolidation** - Market consolidation, combining operations
4. **Joint Venture** - New joint ventures, consortium formations
5. **Strategic Alliance** - Strategic agreements, alliances

## Data Storage

The agent stores data in JSON files:
- `backend/data/ma_events.json` - All discovered events
- `backend/data/notifications.json` - Notification history
- `backend/data/agent_activities.json` - Activity logs
- `backend/data/ecosystem_impacts.json` - Impact analysis

## Ecosystem Impact Analysis

The agent analyzes how new M&A events affect your existing company graph:
- Identifies affected companies by industry
- Calculates impact scores
- Generates impact descriptions
- Creates notifications for significant impacts

## Monitoring Frequency

- **Search Interval**: 1 minute (configurable)
- **API Rate Limiting**: Built-in delays between requests
- **Data Retention**: 7 days for activities, permanent for events
- **Batch Processing**: Processes multiple queries per cycle

## Troubleshooting

### Agent Won't Start
1. Check Exa API key is set in `.env`
2. Verify backend dependencies are installed
3. Check logs in `backend/ma_agent.log`

### No Events Found
1. Exa API may have rate limits
2. Check API key validity
3. Review search queries in logs
4. Verify internet connection

### Dashboard Not Loading
1. Ensure backend is running on port 8000
2. Check CORS settings in `main.py`
3. Verify frontend is running on port 3000

## Cost Management

With $50 Exa API credits:
- Each search costs ~$0.01-0.05
- Agent makes ~8-10 searches per minute
- Estimated runtime: 100-500 hours depending on usage
- Monitor usage via Exa dashboard

## Integration with Graph Visualization

The M&A events can be integrated with your graph visualization:

```javascript
// Fetch recent events
const response = await fetch('/api/ma-agent/events?hours=24');
const events = await response.json();

// Update graph with new connections
events.forEach(event => {
  if (event.event_type === 'merger_acquisition') {
    // Add acquisition edge to graph
    addAcquisitionEdge(event.primary_company.name, event.secondary_company.name);
  }
});
```

## Next Steps

1. **Set up your Exa API key** in the `.env` file
2. **Start the backend server** 
3. **Visit the dashboard** at `/ma-agent`
4. **Start the agent** and watch for real-time M&A events
5. **Integrate events** with your graph visualization

The agent will continuously discover new M&A activity and notify you of changes that could impact the startup ecosystem!
