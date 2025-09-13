"""
Knowledge Graph System for Adaptive Teaching
Manages concept relationships and prerequisite chains
"""

import json
import networkx as nx
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Concept:
    """Represents a learning concept with metadata"""
    id: str
    name: str
    description: str
    difficulty_level: int  # 1-10 scale
    prerequisites: List[str]  # List of concept IDs
    examples: List[str]
    related_concepts: List[str]
    learning_objectives: List[str]

class KnowledgeGraph:
    """Manages the knowledge graph for adaptive teaching"""
    
    def __init__(self, graph_file: str = "knowledge_graph.json"):
        self.graph = nx.DiGraph()
        self.concepts: Dict[str, Concept] = {}
        self.graph_file = Path(graph_file)
        self.load_graph()
    
    def load_graph(self):
        """Load knowledge graph from JSON file"""
        if self.graph_file.exists():
            with open(self.graph_file, 'r') as f:
                data = json.load(f)
                self._build_graph_from_data(data)
        else:
            self._create_default_graph()
    
    def _create_default_graph(self):
        """Create a default knowledge graph with basic concepts"""
        default_concepts = [
            {
                "id": "basic_math",
                "name": "Basic Mathematics",
                "description": "Fundamental arithmetic operations",
                "difficulty_level": 1,
                "prerequisites": [],
                "examples": ["2 + 2 = 4", "5 × 3 = 15"],
                "related_concepts": ["algebra"],
                "learning_objectives": ["Perform basic arithmetic", "Understand number relationships"]
            },
            {
                "id": "algebra",
                "name": "Algebra",
                "description": "Mathematical operations with variables",
                "difficulty_level": 3,
                "prerequisites": ["basic_math"],
                "examples": ["x + 5 = 10", "2y = 8"],
                "related_concepts": ["calculus", "geometry"],
                "learning_objectives": ["Solve for variables", "Manipulate equations"]
            },
            {
                "id": "calculus",
                "name": "Calculus",
                "description": "Study of rates of change and accumulation",
                "difficulty_level": 7,
                "prerequisites": ["algebra", "geometry"],
                "examples": ["d/dx(x²) = 2x", "∫x dx = x²/2 + C"],
                "related_concepts": ["differential_equations"],
                "learning_objectives": ["Understand derivatives", "Compute integrals"]
            },
            {
                "id": "geometry",
                "name": "Geometry",
                "description": "Study of shapes, sizes, and spatial relationships",
                "difficulty_level": 4,
                "prerequisites": ["basic_math"],
                "examples": ["Area of circle = πr²", "Pythagorean theorem: a² + b² = c²"],
                "related_concepts": ["trigonometry", "calculus"],
                "learning_objectives": ["Calculate areas and volumes", "Understand spatial relationships"]
            },
            {
                "id": "programming_basics",
                "name": "Programming Fundamentals",
                "description": "Basic programming concepts and logic",
                "difficulty_level": 2,
                "prerequisites": [],
                "examples": ["Variables", "Loops", "Functions"],
                "related_concepts": ["data_structures", "algorithms"],
                "learning_objectives": ["Write simple programs", "Understand control flow"]
            },
            {
                "id": "data_structures",
                "name": "Data Structures",
                "description": "Ways to organize and store data efficiently",
                "difficulty_level": 5,
                "prerequisites": ["programming_basics"],
                "examples": ["Arrays", "Linked Lists", "Trees", "Hash Tables"],
                "related_concepts": ["algorithms", "databases"],
                "learning_objectives": ["Choose appropriate data structures", "Implement basic structures"]
            },
            {
                "id": "algorithms",
                "name": "Algorithms",
                "description": "Step-by-step procedures for solving problems",
                "difficulty_level": 6,
                "prerequisites": ["programming_basics", "data_structures"],
                "examples": ["Binary Search", "Merge Sort", "Dijkstra's Algorithm"],
                "related_concepts": ["complexity_analysis"],
                "learning_objectives": ["Design efficient algorithms", "Analyze algorithm performance"]
            }
        ]
        
        for concept_data in default_concepts:
            concept = Concept(**concept_data)
            self.add_concept(concept)
        
        self.save_graph()
    
    def _build_graph_from_data(self, data: Dict):
        """Build graph from loaded JSON data"""
        for concept_data in data.get("concepts", []):
            concept = Concept(**concept_data)
            self.add_concept(concept)
    
    def add_concept(self, concept: Concept):
        """Add a concept to the knowledge graph"""
        self.concepts[concept.id] = concept
        self.graph.add_node(concept.id, **concept.__dict__)
        
        # Add prerequisite edges
        for prereq in concept.prerequisites:
            self.graph.add_edge(prereq, concept.id, relationship="prerequisite")
        
        # Add related concept edges
        for related in concept.related_concepts:
            if related in self.concepts:
                self.graph.add_edge(concept.id, related, relationship="related")
    
    def get_prerequisites_chain(self, concept_id: str) -> List[str]:
        """Get the full chain of prerequisites for a concept"""
        if concept_id not in self.concepts:
            return []
        
        prerequisites = []
        visited = set()
        
        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            
            concept = self.concepts.get(node_id)
            if concept:
                for prereq in concept.prerequisites:
                    if prereq not in visited:
                        dfs(prereq)
                        prerequisites.append(prereq)
        
        dfs(concept_id)
        return prerequisites
    
    def find_learning_path(self, target_concept: str, known_concepts: Set[str]) -> List[str]:
        """Find the optimal learning path to reach target concept"""
        if target_concept not in self.concepts:
            return []
        
        # Get all prerequisites
        all_prereqs = self.get_prerequisites_chain(target_concept)
        
        # Filter out already known concepts
        learning_path = [concept for concept in all_prereqs if concept not in known_concepts]
        
        # Sort by difficulty level
        learning_path.sort(key=lambda x: self.concepts[x].difficulty_level)
        
        # Add target concept at the end
        learning_path.append(target_concept)
        
        return learning_path
    
    def get_concept_by_name(self, name: str) -> Optional[Concept]:
        """Find concept by name (case-insensitive)"""
        name_lower = name.lower()
        for concept in self.concepts.values():
            if concept.name.lower() == name_lower:
                return concept
        return None
    
    def find_related_concepts(self, concept_id: str, max_distance: int = 2) -> List[str]:
        """Find concepts related to the given concept within max_distance"""
        if concept_id not in self.concepts:
            return []
        
        related = []
        for node in nx.single_source_shortest_path_length(
            self.graph.to_undirected(), concept_id, cutoff=max_distance
        ):
            if node != concept_id:
                related.append(node)
        
        return related
    
    def get_concept_difficulty(self, concept_id: str) -> int:
        """Get difficulty level of a concept"""
        concept = self.concepts.get(concept_id)
        return concept.difficulty_level if concept else 0
    
    def save_graph(self):
        """Save knowledge graph to JSON file"""
        data = {
            "concepts": [concept.__dict__ for concept in self.concepts.values()]
        }
        
        with open(self.graph_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_concept_info(self, concept_id: str) -> Optional[Dict]:
        """Get detailed information about a concept"""
        concept = self.concepts.get(concept_id)
        if not concept:
            return None
        
        return {
            "concept": concept,
            "prerequisites": [self.concepts[pid] for pid in concept.prerequisites if pid in self.concepts],
            "related": [self.concepts[rid] for rid in concept.related_concepts if rid in self.concepts],
            "difficulty": concept.difficulty_level
        }
