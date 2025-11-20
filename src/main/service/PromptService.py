"""
PromptService.py
Service for loading and managing pedagogy mode-specific prompts.
"""
import os
import logging
from typing import Optional
from pathlib import Path
from src.main.dtos.PedagogyMode import PedagogyMode

logger = logging.getLogger(__name__)


class PromptService:
    """
    Service for loading and managing different pedagogy mode prompts.
    
    Loads mode-specific prompts from the prompts/ directory and provides
    methods to retrieve them based on the selected pedagogy mode.
    """
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize the PromptService.
        
        Args:
            prompts_dir: Directory containing prompt files (defaults to project prompts/ folder)
        """
        if prompts_dir is None:
            # Default to prompts/ directory relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            prompts_dir = project_root / "prompts"
        
        self.prompts_dir = Path(prompts_dir)
        self._prompt_cache: dict[str, str] = {}
        
        logger.info(f"PromptService initialized with prompts_dir={self.prompts_dir}")
    
    def get_mode_prompt(self, mode: PedagogyMode) -> str:
        """
        Get the prompt content for a specific pedagogy mode.
        
        Args:
            mode: PedagogyMode enum value
        
        Returns:
            Prompt content as string
        
        Raises:
            FileNotFoundError: If prompt file doesn't exist
            ValueError: If mode is invalid
        """
        if isinstance(mode, str):
            mode = PedagogyMode.from_string(mode)
        
        # Check cache first
        cache_key = mode.value
        if cache_key in self._prompt_cache:
            logger.debug(f"Returning cached prompt for mode '{mode.value}'")
            return self._prompt_cache[cache_key]
        
        # Load from file
        filename = mode.get_prompt_filename()
        filepath = self.prompts_dir / filename
        
        if not filepath.exists():
            error_msg = f"Prompt file not found: {filepath}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            # Cache the prompt
            self._prompt_cache[cache_key] = prompt_content
            logger.info(f"Loaded and cached prompt for mode '{mode.value}' from {filename}")
            
            return prompt_content
        
        except Exception as e:
            logger.error(f"Error loading prompt file {filepath}: {e}")
            raise
    
    def get_combined_prompt(
        self, 
        base_prompt: str, 
        mode: PedagogyMode,
        separator: str = "\n\n---\n\n"
    ) -> str:
        """
        Combine a base prompt with a mode-specific prompt.
        
        Args:
            base_prompt: Base system prompt (e.g., role definition, general instructions)
            mode: Pedagogy mode
            separator: String to separate base and mode prompts
        
        Returns:
            Combined prompt string
        """
        mode_prompt = self.get_mode_prompt(mode)
        combined = f"{base_prompt}{separator}{mode_prompt}"
        
        logger.debug(f"Combined base prompt with {mode.value} mode prompt ({len(combined)} chars)")
        return combined
    
    def validate_mode(self, mode_str: Optional[str]) -> PedagogyMode:
        """
        Validate and convert a mode string to PedagogyMode enum.
        
        Args:
            mode_str: Mode string to validate (None returns default)
        
        Returns:
            Validated PedagogyMode enum value
        
        Raises:
            ValueError: If mode string is invalid
        """
        try:
            mode = PedagogyMode.from_string(mode_str)
            logger.debug(f"Validated mode: '{mode.value}'")
            return mode
        except ValueError as e:
            logger.error(f"Invalid pedagogy mode: {mode_str}")
            raise
    
    def get_mode_description(self, mode: PedagogyMode) -> str:
        """
        Get a human-readable description of a pedagogy mode.
        
        Args:
            mode: Pedagogy mode
        
        Returns:
            Description string
        """
        if isinstance(mode, str):
            mode = PedagogyMode.from_string(mode)
        
        return mode.get_description()
    
    def list_available_modes(self) -> list[dict]:
        """
        List all available pedagogy modes with their descriptions.
        
        Returns:
            List of dicts with 'mode' and 'description' keys
        """
        modes = []
        for mode in PedagogyMode:
            modes.append({
                "mode": mode.value,
                "description": mode.get_description(),
                "prompt_file": mode.get_prompt_filename()
            })
        
        return modes
    
    def clear_cache(self):
        """Clear the prompt cache (useful for testing or hot-reloading)."""
        self._prompt_cache.clear()
        logger.info("Cleared prompt cache")
    
    def preload_all_prompts(self):
        """
        Preload all pedagogy mode prompts into cache.
        
        Useful for application startup to catch any missing files early.
        """
        logger.info("Preloading all pedagogy mode prompts...")
        
        for mode in PedagogyMode:
            try:
                self.get_mode_prompt(mode)
                logger.debug(f"  ✓ Loaded {mode.value} mode prompt")
            except Exception as e:
                logger.error(f"  ✗ Failed to load {mode.value} mode prompt: {e}")
                raise
        
        logger.info(f"Successfully preloaded {len(PedagogyMode)} mode prompts")


# Singleton instance for easy access
_prompt_service_instance: Optional[PromptService] = None


def get_prompt_service() -> PromptService:
    """
    Get the singleton PromptService instance.
    
    Returns:
        PromptService instance
    """
    global _prompt_service_instance
    
    if _prompt_service_instance is None:
        _prompt_service_instance = PromptService()
        # Preload prompts at initialization
        try:
            _prompt_service_instance.preload_all_prompts()
        except Exception as e:
            logger.warning(f"Failed to preload prompts (will load on-demand): {e}")
    
    return _prompt_service_instance
