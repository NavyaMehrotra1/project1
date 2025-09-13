"""
Main Voice-Based AI Teacher Application
Combines Whisper, Claude, and Knowledge Graph for adaptive teaching
"""

import os
import sys
import asyncio
import signal
from dotenv import load_dotenv
from voice_interface import VoiceInterface
from adaptive_teacher import AdaptiveTeacher
from knowledge_graph import KnowledgeGraph

class VoiceTeacher:
    """Main application class for voice-based AI teacher"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.anthropic_key:
            print("❌ ANTHROPIC_API_KEY not found in environment variables")
            print("Please copy .env.example to .env and add your API keys")
            sys.exit(1)
        
        # Initialize components
        print("🧠 Initializing knowledge graph...")
        self.knowledge_graph = KnowledgeGraph()
        
        print("🤖 Initializing AI teacher...")
        self.teacher = AdaptiveTeacher(self.anthropic_key, self.knowledge_graph)
        
        print("🎤 Initializing voice interface...")
        self.voice = VoiceInterface()
        
        # Set up voice callbacks
        self.voice.on_speech_detected = self.handle_speech
        self.voice.on_silence_detected = self.handle_silence
        
        self.is_running = False
        self.waiting_for_response = False
        
    def handle_speech(self, text: str):
        """Handle detected speech from user"""
        if self.waiting_for_response:
            return
            
        self.waiting_for_response = True
        
        try:
            # Get AI teacher response
            response = self.teacher.generate_teaching_response(text)
            
            # Speak the response
            self.voice.speak_text(response)
            
        except Exception as e:
            print(f"Error processing speech: {e}")
            self.voice.speak_text("I'm sorry, I had trouble understanding that. Could you try again?")
        
        finally:
            self.waiting_for_response = False
    
    def handle_silence(self):
        """Handle silence detection"""
        pass  # Could be used for prompting user or other actions
    
    def start_interactive_mode(self):
        """Start interactive voice conversation"""
        print("\n" + "="*60)
        print("🎓 VOICE-BASED AI TEACHER")
        print("="*60)
        print("Commands:")
        print("  - Just speak naturally to ask questions")
        print("  - Say 'quit' or 'exit' to stop")
        print("  - Press Ctrl+C to force quit")
        print("="*60)
        
        # Start a new learning session
        session_id = self.teacher.start_session()
        print(f"📚 Started learning session: {session_id}")
        
        self.voice.speak_text("Hello! I'm your AI teacher. What would you like to learn about today?")
        
        # Start voice listening
        self.voice.start_listening()
        self.is_running = True
        
        try:
            # Keep the main thread alive
            while self.is_running:
                asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            self.cleanup()
    
    def start_text_mode(self):
        """Start text-based conversation for testing"""
        print("\n" + "="*60)
        print("🎓 TEXT-BASED AI TEACHER (Testing Mode)")
        print("="*60)
        print("Type your questions. Type 'quit' to exit.")
        print("="*60)
        
        # Start a new learning session
        session_id = self.teacher.start_session()
        print(f"📚 Started learning session: {session_id}")
        
        print("\n🤖 AI Teacher: Hello! I'm your AI teacher. What would you like to learn about today?")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("🤖 AI Teacher: Goodbye! Keep learning!")
                    break
                
                if not user_input:
                    continue
                
                # Get AI teacher response
                response = self.teacher.generate_teaching_response(user_input)
                print(f"\n🤖 AI Teacher: {response}")
                
                # Check understanding
                understanding_check = input("\n❓ Did that make sense? (yes/no/partially): ").strip().lower()
                if understanding_check:
                    check_result = self.teacher.check_understanding(understanding_check)
                    
                    if not check_result.get("understood", False):
                        print(f"\n🤖 AI Teacher: {check_result.get('feedback', 'Let me explain differently...')}")
                
            except KeyboardInterrupt:
                print("\n🛑 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Save session
        self.teacher.save_session()
        print("💾 Session saved!")
    
    def demo_knowledge_graph(self):
        """Demonstrate knowledge graph functionality"""
        print("\n" + "="*60)
        print("🧠 KNOWLEDGE GRAPH DEMO")
        print("="*60)
        
        # Show all concepts
        print("Available concepts:")
        for concept_id, concept in self.knowledge_graph.concepts.items():
            prereqs = [self.knowledge_graph.concepts[p].name for p in concept.prerequisites]
            print(f"  • {concept.name} (Level {concept.difficulty_level}) - Prerequisites: {prereqs}")
        
        print("\n" + "-"*40)
        
        # Demonstrate learning path
        target = "calculus"
        known = {"basic_math"}
        
        print(f"Learning path to '{target}' with known concepts {known}:")
        path = self.knowledge_graph.find_learning_path(target, known)
        for i, concept_id in enumerate(path, 1):
            concept = self.knowledge_graph.concepts[concept_id]
            print(f"  {i}. {concept.name} (Level {concept.difficulty_level})")
        
        print("\n" + "-"*40)
        
        # Show concept details
        concept_info = self.knowledge_graph.get_concept_info("algebra")
        if concept_info:
            concept = concept_info["concept"]
            print(f"Concept Details: {concept.name}")
            print(f"  Description: {concept.description}")
            print(f"  Examples: {concept.examples}")
            print(f"  Learning Objectives: {concept.learning_objectives}")
    
    def cleanup(self):
        """Clean up resources"""
        self.is_running = False
        if hasattr(self, 'voice'):
            self.voice.cleanup()
        if hasattr(self, 'teacher') and self.teacher.current_session:
            self.teacher.save_session()
            print("💾 Session saved!")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        print("Select mode:")
        print("1. Voice mode (requires microphone)")
        print("2. Text mode (for testing)")
        print("3. Demo knowledge graph")
        choice = input("Enter choice (1/2/3): ").strip()
        
        mode_map = {"1": "voice", "2": "text", "3": "demo"}
        mode = mode_map.get(choice, "text")
    
    app = VoiceTeacher()
    
    # Set up signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal...")
        app.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        if mode == "voice":
            app.start_interactive_mode()
        elif mode == "demo":
            app.demo_knowledge_graph()
        else:
            app.start_text_mode()
    except Exception as e:
        print(f"❌ Application error: {e}")
        app.cleanup()

if __name__ == "__main__":
    main()
