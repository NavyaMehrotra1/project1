# Voice-Based AI Teacher

An adaptive AI teaching system that uses Whisper for speech recognition and Claude for conversational teaching. The system can access knowledge graphs and adaptively teach by going backward to prerequisites when students don't understand concepts.

## Features

- **Voice Interaction**: Real-time speech-to-text using OpenAI Whisper
- **Adaptive Teaching**: Uses Claude API for intelligent, conversational teaching
- **Knowledge Graph**: Tracks concept relationships and prerequisites
- **Backward Chaining**: Automatically teaches prerequisites when knowledge gaps are detected
- **Session Management**: Saves learning progress and conversation history
- **Multiple Modes**: Voice mode for natural conversation, text mode for testing

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # ANTHROPIC_API_KEY=your_key_here
   # OPENAI_API_KEY=your_key_here (optional, for future TTS features)
   ```

3. **Audio Setup** (macOS):
   - Ensure microphone permissions are granted
   - Install PortAudio if needed: `brew install portaudio`

## Usage

### Voice Mode (Interactive)
```bash
python main.py voice
```
- Speak naturally to ask questions
- The AI will respond with voice
- Say "quit" or press Ctrl+C to exit

### Text Mode (Testing)
```bash
python main.py text
```
- Type questions instead of speaking
- Useful for development and testing
- All teaching logic works the same

### Demo Mode
```bash
python main.py demo
```
- Shows the knowledge graph structure
- Demonstrates learning path generation
- Useful for understanding the system

## How It Works

### 1. Knowledge Graph
- Stores concepts with prerequisites and relationships
- Default concepts include math, programming, and science topics
- Automatically generates learning paths based on student's known concepts

### 2. Adaptive Teaching
- Assesses student knowledge from their responses
- Identifies gaps in understanding
- Uses backward chaining to teach prerequisites first
- Adapts explanations to student's level

### 3. Voice Interface
- Continuous listening with voice activity detection
- Whisper transcription for high accuracy
- Text-to-speech responses (macOS `say` command)

### 4. Session Management
- Tracks what concepts the student knows
- Saves conversation history
- Resumes learning from where you left off

## Example Conversation

```
🤖 AI Teacher: Hello! What would you like to learn about today?

👤 Student: "I want to learn calculus"

🤖 AI Teacher: Great choice! Before we dive into calculus, let me check - 
are you comfortable with algebra? Calculus builds heavily on algebraic 
concepts like solving equations and working with variables.

👤 Student: "Not really, I'm not good with algebra"

🤖 AI Teacher: No problem! Let's start with algebra fundamentals. 
Algebra is like arithmetic, but instead of just numbers, we use letters 
to represent unknown values. For example, if I say x + 5 = 10, 
what do you think x equals?
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Voice Interface │    │ Adaptive Teacher │    │ Knowledge Graph │
│                 │    │                  │    │                 │
│ • Whisper STT   │◄──►│ • Claude API     │◄──►│ • Concepts      │
│ • Voice Activity│    │ • Session Mgmt   │    │ • Prerequisites │
│ • TTS Output    │    │ • Assessment     │    │ • Learning Paths│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Customization

### Adding New Concepts
Edit `knowledge_graph.py` to add new concepts:

```python
new_concept = Concept(
    id="machine_learning",
    name="Machine Learning",
    description="Algorithms that learn from data",
    difficulty_level=8,
    prerequisites=["programming_basics", "statistics"],
    examples=["Linear regression", "Neural networks"],
    related_concepts=["data_science", "ai"],
    learning_objectives=["Understand ML algorithms", "Apply ML to problems"]
)
```

### Modifying Teaching Style
Adjust the `system_prompt` in `adaptive_teacher.py` to change how the AI teaches.

### Voice Settings
Modify voice detection sensitivity and other audio parameters in `voice_interface.py`.

## Troubleshooting

### Audio Issues
- **No microphone detected**: Check system permissions
- **Poor transcription**: Ensure quiet environment, speak clearly
- **Audio errors**: Try `brew install portaudio` on macOS

### API Issues
- **Claude API errors**: Verify ANTHROPIC_API_KEY is correct
- **Rate limiting**: Add delays between requests if needed

### Dependencies
- **PyAudio installation**: May require system audio libraries
- **Whisper model**: First run downloads the model (can be slow)

## Future Enhancements

- [ ] Web interface for visual learning
- [ ] Integration with external knowledge sources
- [ ] Multi-language support
- [ ] Advanced TTS with emotional expression
- [ ] Learning analytics and progress tracking
- [ ] Collaborative learning sessions
