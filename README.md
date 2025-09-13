# DealFlow - AI-Native M&A Intelligence Platform

> **"In 2008, nobody saw Lehman Brothers coming. In 2024, FTX shocked everyone. What if you could predict these events months in advance?"**

DealFlow is the AI-native successor to Crunchbase, built for the modern era of predictive M&A intelligence. It combines real-time data ingestion, network graph visualization, and LLM-powered predictions to help users understand, analyze, and forecast corporate deals.

## 🚀 Features

### Core MVP Features
- **📊 Network Graph Visualization**: Interactive D3.js-powered graph showing companies as nodes and deals as edges
- **🤖 AI Prediction Layer**: Claude API integration for forecasting future M&A deals
- **⚡ What-If Simulator**: Simulate hypothetical scenarios and analyze market impact
- **🎓 Education Mode**: AI tutor for learning about M&A concepts at different expertise levels
- **📈 Data Ingestion**: Real-time news parsing from NewsAPI and Yahoo Finance

### Advanced Features
- **🌟 Extraordinary Company Detection**: Highlight standout companies with larger nodes
- **📱 Responsive Design**: Modern, mobile-friendly interface
- **🔍 Smart Search**: Find companies and deals instantly
- **📊 Financial Metrics**: Company profiles with market data and sentiment analysis

## 🏗️ Architecture

### Frontend (Next.js + TypeScript)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom components
- **Visualization**: D3.js for network graphs
- **State Management**: React hooks and context
- **UI Components**: Custom component library with Lucide icons

### Backend (Python + FastAPI)
- **API Framework**: FastAPI with async support
- **Data Sources**: NewsAPI, Yahoo Finance, synthetic data
- **LLM Integration**: Anthropic Claude API
- **Graph Processing**: NetworkX for network analysis
- **Data Models**: Pydantic schemas

## 🛠️ Installation & Setup

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.8+
- API Keys: NewsAPI, Anthropic Claude

### Quick Start

1. **Clone and Install Dependencies**
```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

2. **Environment Setup**
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Add your API keys to backend/.env
ANTHROPIC_API_KEY=your_anthropic_key_here
NEWSAPI_KEY=your_newsapi_key_here
```

3. **Run Development Servers**
```bash
# Terminal 1: Start backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
npm run dev
```

4. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📱 Usage Guide

### 1. Network Graph View
- **Explore**: Pan, zoom, and click on companies to view profiles
- **Predictions**: Toggle AI predictions to see forecasted deals (dashed lines)
- **Legend**: Color-coded by industry, size by market cap and extraordinary score

### 2. What-If Simulator
- Enter hypothetical scenarios (e.g., "Microsoft acquires OpenAI")
- Analyze market impact and affected companies
- View confidence scores and timelines

### 3. Education Mode
- Ask questions about M&A concepts
- Adjust expertise level (beginner/intermediate/expert)
- Get contextual explanations with examples

### 4. Data Ingestion
- Import news data with custom search queries
- Upload CSV files with deal data
- Configure API keys for real-time updates

## 🎯 Hackathon Tracks

### YC Track: FundersClub 2.0
- **Problem**: Crunchbase was built for Web 2.0 with static listings
- **Solution**: AI-native platform with live, predictive, and educational features
- **Impact**: Transform how investors and analysts understand deal flow

### Extraordinary Track
- Highlight standout companies with exceptional metrics
- Larger nodes for extraordinary companies
- Detailed profiles with unique factors

## 🚀 Deployment

### Vercel (Frontend)
```bash
# Deploy to Vercel
npm run build
vercel --prod
```

### Backend Deployment Options
- **Heroku**: `git push heroku main`
- **Railway**: Connect GitHub repo
- **DigitalOcean**: Docker deployment

### Environment Variables
```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://your-backend-url.com

# Backend (.env)
ANTHROPIC_API_KEY=your_key
NEWSAPI_KEY=your_key
DATABASE_URL=your_db_url  # For production
```

## 📊 Demo Data

The application includes sample data featuring:
- **Companies**: OpenAI, Microsoft, Google, Meta, Anthropic
- **Deals**: Microsoft-OpenAI investment, Google-Anthropic partnership
- **Industries**: AI, Technology, Social Media
- **Predictions**: AI-generated future deal scenarios

## 🔧 API Endpoints

### Core Endpoints
- `GET /api/graph-data` - Network graph data
- `POST /api/predict-deals` - Generate AI predictions
- `POST /api/what-if` - Scenario simulation
- `POST /api/education` - Educational explanations
- `POST /api/ingest-news` - Data ingestion

### Graph Operations
- `POST /api/graph/add-node` - Add company
- `DELETE /api/graph/remove-node/{id}` - Remove company
- `POST /api/graph/add-edge` - Add deal
- `DELETE /api/graph/remove-edge/{id}` - Remove deal

## 🎨 Design System

### Color Palette
- **Primary**: Blue (#3b82f6) - Technology companies
- **Secondary**: Purple (#8b5cf6) - AI companies  
- **Accent**: Yellow (#fbbf24) - Predictions
- **Success**: Green (#10b981) - Partnerships
- **Warning**: Red (#ef4444) - Acquisitions

### Typography
- **Headings**: Inter font family
- **Body**: System font stack
- **Code**: Monospace

## 🧪 Testing

```bash
# Frontend tests
npm run test

# Backend tests
cd backend
pytest

# E2E tests
npm run test:e2e
```

## 📈 Performance

- **Frontend**: Optimized with Next.js SSR and code splitting
- **Backend**: Async FastAPI with efficient data processing
- **Graph**: D3.js with virtualization for large datasets
- **Caching**: Redis for API responses (production)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Sponsors**: Anthropic (Claude API), NewsAPI, Vercel
- **Inspiration**: Crunchbase, FundersClub, modern AI tools
- **Team**: Built for AI hackathon with focus on practical M&A intelligence

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: team@dealflow.ai

---

**Built with ❤️ for the AI Hackathon**

*Transforming M&A intelligence from reactive to predictive*
