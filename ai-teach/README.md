# AI-Teach: Adaptive M&A Learning System

A comprehensive educational platform that provides personalized M&A (Mergers & Acquisitions) education with adaptive learning levels and AI-powered explanations.

## 🎯 Features

### 1. Adaptive Learning Levels
- **Beginner**: Simple explanations, basic concepts, real-world analogies
- **Intermediate**: Moderate technical language, industry examples, strategic context
- **Expert**: Advanced analysis, technical terminology, strategic implications

### 2. Interactive M&A Education
- Comprehensive M&A terminology database
- Real-world case studies (Disney+Pixar, Microsoft+LinkedIn, etc.)
- Industry-specific contexts (Technology, Healthcare, Financial Services)
- Contextual explanations with practical examples

### 3. AI-Powered Explanations
- Uses Anthropic's Claude API for generating educational content
- Natural language processing for understanding user queries
- Personalized responses based on user's background and level
- Integration with live deal data for practical learning scenarios

### 4. Background Assessment System
- Determines user's knowledge level through adaptive questioning
- Assesses finance, business, and M&A experience
- Builds knowledge foundation from identified gaps
- Creates personalized learning paths

### 5. Scenario-Based Learning
- Interactive M&A scenarios with what-if simulations
- Real-world deal structures and outcomes
- Educational feedback on deal implications
- Integration with existing graph visualization system

## 🏗️ Architecture

```
ai-teach/
├── core/
│   ├── adaptive_learning.py     # Main learning engine
│   ├── background_assessment.py # User assessment system
│   ├── ma_education.py         # M&A education module
│   └── scenario_learning.py    # Scenario-based learning
├── models/
│   └── learning_models.py      # Data models and structures
├── services/
│   └── claude_service.py       # Claude API integration
├── main.py                     # Main application entry point
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Anthropic API key

### Installation

1. **Set up environment variables:**
   ```bash
   export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
   ```

2. **Install dependencies:**
   ```bash
   cd ai-teach
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### First Time Setup

1. **Take the Background Assessment** - The system will assess your knowledge level
2. **Start Learning Sessions** - Begin with concepts appropriate to your level
3. **Explore M&A Concepts** - Dive deeper into specific topics
4. **Try Learning Scenarios** - Practice with interactive simulations

## 📚 Learning Flow

### 1. Background Assessment
The system starts by understanding your background:
- Educational and professional experience
- Finance and business knowledge
- Previous M&A exposure
- Adaptive questioning based on responses

### 2. Adaptive Learning Path
Based on your assessment, the system creates a personalized path:

**Beginner Path:**
- Company Fundamentals → Mergers vs Acquisitions → Due Diligence → Financial Statements

**Intermediate Path:**
- M&A Fundamentals → Due Diligence → Financial Analysis → Valuation Methods → Synergies

**Expert Path:**
- Valuation Methods → Synergies → Integration Planning → Accretion/Dilution Analysis

### 3. Interactive Learning
- **Concept Explanations**: AI-powered, level-appropriate explanations
- **Real Examples**: Integration with your existing graph data
- **Q&A Sessions**: Interactive questions to check understanding
- **Case Studies**: Real-world M&A transactions with analysis

### 4. Scenario Simulations
- **Tech Startup Acquisition**: Strategic rationale and integration challenges
- **Healthcare Merger**: Regulatory requirements and cost synergies
- **Cross-Border Deal**: Currency risks and cultural integration
- **Distressed Acquisition**: Turnaround strategies and restructuring

## 🔧 Integration with Existing System

The AI-Teach system integrates seamlessly with your existing project:

### Graph Data Integration
- Automatically loads graph data from your knowledge graph files
- Uses real company relationships for practical examples
- Enhances explanations with actual deal data

### Existing AI Teacher Components
- Can work alongside your existing voice-based AI teacher
- Shares the same educational philosophy and approach
- Extends capabilities with structured learning paths

## 🎓 Educational Philosophy

### Knowledge Tower Approach
The system implements your requested "knowledge tower" approach:

1. **Foundation Assessment**: Determines what the user already knows
2. **Gap Identification**: Finds missing prerequisite concepts
3. **Progressive Building**: Teaches concepts in logical order
4. **Continuous Validation**: Checks understanding before advancing
5. **Adaptive Reinforcement**: Revisits concepts as needed

### Background-Driven Learning
- Always starts with background assessment
- Builds from user's existing knowledge
- Adapts explanations to user's professional context
- Provides relevant examples from user's domain

## 📊 Key Components

### Learning Models
- **UserProfile**: Tracks progress, background, and preferences
- **Concept**: M&A concepts with difficulty levels and prerequisites
- **LearningSession**: Session tracking and progress monitoring
- **ScenarioData**: Interactive learning scenarios

### Core Modules
- **AdaptiveLearningEngine**: Main learning orchestration
- **BackgroundAssessment**: User knowledge evaluation
- **MAEducationModule**: M&A concept explanations and case studies
- **ScenarioLearning**: Interactive simulations and what-if analysis

### AI Services
- **ClaudeService**: Anthropic Claude API integration
- Level-appropriate prompt engineering
- Context-aware explanation generation
- Educational feedback and assessment

## 🎯 Usage Examples

### Starting a Learning Session
```python
from ai_teach import AITeachApp

app = AITeachApp()
await app.start()
```

### Exploring a Concept
```python
# The system will adapt the explanation to user's level
await ma_education.explain_concept("synergy", user_profile)
```

### Running a Scenario
```python
# Interactive simulation with educational feedback
await scenario_learning.present_scenario("tech_startup_acquisition", user_profile)
```

## 🔮 Future Enhancements

- **Voice Integration**: Connect with existing voice interface
- **Progress Analytics**: Detailed learning analytics and insights
- **Collaborative Learning**: Multi-user scenarios and discussions
- **Advanced Simulations**: More sophisticated financial modeling
- **Mobile Interface**: React Native or web-based mobile app

## 🤝 Contributing

The AI-Teach system is designed to be extensible:

1. **Adding Concepts**: Extend the concept database in `learning_models.py`
2. **New Scenarios**: Add scenarios in `scenario_learning.py`
3. **Case Studies**: Expand case studies in `ma_education.py`
4. **Assessment Questions**: Enhance assessment in `background_assessment.py`

## 📝 License

This project is part of your M&A education platform. Please refer to your project's main license.

---

**Ready to start learning M&A? Run `python main.py` and begin your personalized education journey!** 🚀
