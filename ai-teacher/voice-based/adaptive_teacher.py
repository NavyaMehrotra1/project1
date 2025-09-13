"""
Adaptive AI Teacher using Claude API
Provides conversational teaching with backward chaining for unknown concepts
"""

import anthropic
import json
import os
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from knowledge_graph import KnowledgeGraph, Concept

@dataclass
class LearningSession:
    """Tracks a learning session with the student"""
    session_id: str
    start_time: datetime
    known_concepts: Set[str]
    current_topic: Optional[str]
    conversation_history: List[Dict[str, str]]
    learning_goals: List[str]
    difficulty_preference: int  # 1-10 scale

class AdaptiveTeacher:
    """AI Teacher that adapts to student's knowledge level"""
    
    def __init__(self, api_key: str, knowledge_graph: KnowledgeGraph):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.knowledge_graph = knowledge_graph
        self.current_session: Optional[LearningSession] = None
        
        # Teaching prompts
        self.system_prompt = """You are an adaptive AI teacher. Your role is to:

1. Assess the student's current knowledge level
2. Identify gaps in understanding 
3. Teach concepts by building from what they already know
4. Use backward chaining - if they don't understand something, go back to prerequisites
5. Provide clear explanations with examples
6. Ask questions to check understanding
7. Adapt your teaching style to their level

Key principles:
- Always build on existing knowledge
- Use analogies and real-world examples
- Break complex topics into smaller parts
- Check understanding frequently
- Be encouraging and patient
- If they're confused, step back to simpler concepts

You have access to a knowledge graph that shows concept relationships and prerequisites."""

    def start_session(self, session_id: str = None) -> str:
        """Start a new learning session"""
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = LearningSession(
            session_id=session_id,
            start_time=datetime.now(),
            known_concepts=set(),
            current_topic=None,
            conversation_history=[],
            learning_goals=[],
            difficulty_preference=5
        )
        
        return session_id
    
    def assess_knowledge(self, student_response: str, topic: str) -> Dict[str, any]:
        """Assess student's knowledge level on a topic"""
        concept = self.knowledge_graph.get_concept_by_name(topic)
        if not concept:
            return {"error": f"Topic '{topic}' not found in knowledge graph"}
        
        # Get related concepts and prerequisites
        prereqs = self.knowledge_graph.get_prerequisites_chain(concept.id)
        related = self.knowledge_graph.find_related_concepts(concept.id)
        
        assessment_prompt = f"""
        Based on the student's response: "{student_response}"
        
        Assess their knowledge of: {concept.name}
        Description: {concept.description}
        Prerequisites: {[self.knowledge_graph.concepts[p].name for p in prereqs]}
        
        Determine:
        1. Do they understand this concept? (yes/no/partial)
        2. Which prerequisites do they seem to know?
        3. What specific gaps exist?
        4. What should we teach next?
        
        Respond in JSON format:
        {{
            "understands_concept": "yes/no/partial",
            "known_prerequisites": ["list", "of", "prerequisite", "names"],
            "knowledge_gaps": ["list", "of", "gaps"],
            "next_teaching_step": "what to teach next",
            "confidence_level": 0.8
        }}
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=self.system_prompt,
                messages=[{"role": "user", "content": assessment_prompt}]
            )
            
            assessment = json.loads(response.content[0].text)
            
            # Update session with known concepts
            if self.current_session:
                for prereq_name in assessment.get("known_prerequisites", []):
                    prereq_concept = self.knowledge_graph.get_concept_by_name(prereq_name)
                    if prereq_concept:
                        self.current_session.known_concepts.add(prereq_concept.id)
            
            return assessment
            
        except Exception as e:
            return {"error": f"Assessment failed: {str(e)}"}
    
    def generate_teaching_response(self, student_input: str) -> str:
        """Generate an adaptive teaching response"""
        if not self.current_session:
            self.start_session()
        
        # Add to conversation history
        self.current_session.conversation_history.append({
            "role": "student",
            "content": student_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Determine current topic from input
        topic = self._extract_topic_from_input(student_input)
        
        if topic:
            self.current_session.current_topic = topic
            
            # Get concept information
            concept = self.knowledge_graph.get_concept_by_name(topic)
            if concept:
                concept_info = self.knowledge_graph.get_concept_info(concept.id)
                
                # Find learning path
                learning_path = self.knowledge_graph.find_learning_path(
                    concept.id, 
                    self.current_session.known_concepts
                )
                
                # Create teaching prompt
                teaching_prompt = self._create_teaching_prompt(
                    student_input, concept_info, learning_path
                )
                
                try:
                    response = self.client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=1500,
                        system=self.system_prompt,
                        messages=self._get_conversation_context() + [
                            {"role": "user", "content": teaching_prompt}
                        ]
                    )
                    
                    ai_response = response.content[0].text
                    
                    # Add to conversation history
                    self.current_session.conversation_history.append({
                        "role": "teacher",
                        "content": ai_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return ai_response
                    
                except Exception as e:
                    return f"I'm having trouble processing that. Could you rephrase your question? (Error: {str(e)})"
        
        # General conversation response
        return self._generate_general_response(student_input)
    
    def _extract_topic_from_input(self, input_text: str) -> Optional[str]:
        """Extract the main topic from student input"""
        input_lower = input_text.lower()
        
        # Check for exact concept matches
        for concept in self.knowledge_graph.concepts.values():
            if concept.name.lower() in input_lower:
                return concept.name
        
        # Check for partial matches
        for concept in self.knowledge_graph.concepts.values():
            concept_words = concept.name.lower().split()
            if any(word in input_lower for word in concept_words):
                return concept.name
        
        return None
    
    def _create_teaching_prompt(self, student_input: str, concept_info: Dict, learning_path: List[str]) -> str:
        """Create a detailed teaching prompt"""
        concept = concept_info["concept"]
        prerequisites = concept_info["prerequisites"]
        
        # Identify missing prerequisites
        missing_prereqs = []
        for prereq in prerequisites:
            if prereq.id not in self.current_session.known_concepts:
                missing_prereqs.append(prereq)
        
        prompt = f"""
        Student asked: "{student_input}"
        
        Topic: {concept.name}
        Description: {concept.description}
        Difficulty Level: {concept.difficulty_level}/10
        
        Learning Context:
        - Known concepts: {[self.knowledge_graph.concepts[cid].name for cid in self.current_session.known_concepts]}
        - Missing prerequisites: {[p.name for p in missing_prereqs]}
        - Learning path: {[self.knowledge_graph.concepts[cid].name for cid in learning_path]}
        
        Examples to use: {concept.examples}
        Learning objectives: {concept.learning_objectives}
        
        Instructions:
        1. If they're missing prerequisites, start with the most basic missing concept
        2. Use analogies and examples they can relate to
        3. Build understanding step by step
        4. Ask a question to check their understanding
        5. Be encouraging and conversational
        
        Provide a helpful, adaptive response that meets them at their level.
        """
        
        return prompt
    
    def _generate_general_response(self, student_input: str) -> str:
        """Generate a general conversational response"""
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=self.system_prompt + "\n\nThe student is asking a general question. Be helpful and try to guide them toward specific learning topics.",
                messages=[{"role": "user", "content": student_input}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return "I'm here to help you learn! What topic would you like to explore today?"
    
    def _get_conversation_context(self) -> List[Dict[str, str]]:
        """Get recent conversation context for Claude"""
        if not self.current_session:
            return []
        
        # Get last 6 messages for context
        recent_history = self.current_session.conversation_history[-6:]
        
        context = []
        for msg in recent_history:
            role = "user" if msg["role"] == "student" else "assistant"
            context.append({"role": role, "content": msg["content"]})
        
        return context
    
    def check_understanding(self, student_response: str) -> Dict[str, any]:
        """Check if student understood the explanation"""
        if not self.current_session or not self.current_session.current_topic:
            return {"understood": False, "feedback": "No active topic"}
        
        concept = self.knowledge_graph.get_concept_by_name(self.current_session.current_topic)
        if not concept:
            return {"understood": False, "feedback": "Topic not found"}
        
        check_prompt = f"""
        Topic: {concept.name}
        Student response: "{student_response}"
        
        Assess if the student understood the concept based on their response.
        
        Respond in JSON format:
        {{
            "understood": true/false,
            "confidence": 0.8,
            "feedback": "specific feedback",
            "next_action": "continue/review/move_to_prerequisite"
        }}
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                system=self.system_prompt,
                messages=[{"role": "user", "content": check_prompt}]
            )
            
            result = json.loads(response.content[0].text)
            
            # Update known concepts if they understood
            if result.get("understood") and result.get("confidence", 0) > 0.7:
                self.current_session.known_concepts.add(concept.id)
            
            return result
            
        except Exception as e:
            return {"understood": False, "feedback": f"Error checking understanding: {str(e)}"}
    
    def suggest_next_topic(self) -> Optional[str]:
        """Suggest the next topic to learn"""
        if not self.current_session:
            return None
        
        # Find concepts that are now learnable (prerequisites met)
        learnable_concepts = []
        
        for concept_id, concept in self.knowledge_graph.concepts.items():
            if concept_id not in self.current_session.known_concepts:
                # Check if all prerequisites are known
                prereqs_known = all(
                    prereq in self.current_session.known_concepts 
                    for prereq in concept.prerequisites
                )
                
                if prereqs_known:
                    learnable_concepts.append(concept)
        
        # Sort by difficulty and return the easiest
        if learnable_concepts:
            learnable_concepts.sort(key=lambda c: c.difficulty_level)
            return learnable_concepts[0].name
        
        return None
    
    def save_session(self, filename: str = None):
        """Save current session to file"""
        if not self.current_session:
            return
        
        if not filename:
            filename = f"session_{self.current_session.session_id}.json"
        
        session_data = {
            "session_id": self.current_session.session_id,
            "start_time": self.current_session.start_time.isoformat(),
            "known_concepts": list(self.current_session.known_concepts),
            "current_topic": self.current_session.current_topic,
            "conversation_history": self.current_session.conversation_history,
            "learning_goals": self.current_session.learning_goals,
            "difficulty_preference": self.current_session.difficulty_preference
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def load_session(self, filename: str):
        """Load session from file"""
        try:
            with open(filename, 'r') as f:
                session_data = json.load(f)
            
            self.current_session = LearningSession(
                session_id=session_data["session_id"],
                start_time=datetime.fromisoformat(session_data["start_time"]),
                known_concepts=set(session_data["known_concepts"]),
                current_topic=session_data["current_topic"],
                conversation_history=session_data["conversation_history"],
                learning_goals=session_data["learning_goals"],
                difficulty_preference=session_data["difficulty_preference"]
            )
            
        except Exception as e:
            print(f"Error loading session: {e}")
            self.start_session()
