"""
PedagogyMode.py
Enum defining available teaching modes for the AI tutor.
Each mode represents a different pedagogical approach.
"""
from enum import Enum


class PedagogyMode(str, Enum):
    """
    Enumeration of available pedagogy modes for the AI tutor.
    
    Each mode corresponds to a different teaching approach and has an
    associated prompt file in the prompts/ directory.
    """
    
    SOCRATIC = "socratic"
    """
    Socratic Mode - Discovery Through Questioning
    
    Uses the Socratic method to guide students toward discovering answers
    themselves through thoughtful questioning. Focuses on developing
    critical thinking and problem-solving skills.
    
    Best for: Concept exploration, problem-solving, critical thinking
    """
    
    EXPLANATORY = "explanatory"
    """
    Explanatory Mode - Direct Instruction (Default)
    
    Provides clear, comprehensive explanations with examples and code.
    Direct teaching approach with step-by-step breakdowns.
    
    Best for: Learning new concepts, reference material, clear answers
    """
    
    DEBUGGING = "debugging"
    """
    Debugging Mode - Guided Problem-Solving with Hints
    
    Helps students fix code and solve problems without giving away solutions.
    Provides hints and guides them to find and fix issues themselves.
    
    Best for: Homework help, debugging assistance, avoiding giving solutions
    """
    
    ASSESSMENT = "assessment"
    """
    Assessment Mode - Testing Understanding
    
    Tests and evaluates student understanding through questions and problems.
    Provides feedback on answers without teaching directly.
    
    Best for: Self-assessment, practice problems, exam preparation
    """
    
    REVIEW = "review"
    """
    Review Mode - Reinforcement and Consolidation
    
    Helps students reinforce and consolidate previously learned material.
    Summarizes concepts, makes connections, and fills knowledge gaps.
    
    Best for: Exam prep, refreshing concepts, building retention
    """
    
    @classmethod
    def get_default(cls) -> "PedagogyMode":
        """
        Get the default pedagogy mode.
        
        Returns:
            PedagogyMode.EXPLANATORY - The default teaching mode
        """
        return cls.EXPLANATORY
    
    @classmethod
    def from_string(cls, mode_str: str) -> "PedagogyMode":
        """
        Convert a string to a PedagogyMode enum value.
        
        Args:
            mode_str: String representation of the mode (case-insensitive)
        
        Returns:
            Corresponding PedagogyMode enum value
        
        Raises:
            ValueError: If the mode string is not valid
        """
        if mode_str is None:
            return cls.get_default()
        
        try:
            return cls(mode_str.lower())
        except ValueError:
            valid_modes = ", ".join([mode.value for mode in cls])
            raise ValueError(
                f"Invalid pedagogy mode: '{mode_str}'. "
                f"Valid modes are: {valid_modes}"
            )
    
    def get_prompt_filename(self) -> str:
        """
        Get the filename of the prompt file for this mode.
        
        Returns:
            Filename in the prompts/ directory
        """
        return f"{self.value}_mode_prompt.md"
    
    def get_description(self) -> str:
        """
        Get a human-readable description of this pedagogy mode.
        
        Returns:
            Description string
        """
        descriptions = {
            self.SOCRATIC: "Discovery through questioning - guides students to find answers",
            self.EXPLANATORY: "Direct instruction with clear explanations and examples",
            self.DEBUGGING: "Hint-based problem solving without giving away solutions",
            self.ASSESSMENT: "Tests understanding through questions and feedback",
            self.REVIEW: "Reinforces and consolidates previously learned material"
        }
        return descriptions.get(self, "Unknown mode")
