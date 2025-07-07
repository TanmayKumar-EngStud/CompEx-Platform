"""
Graph style management system for GMAT/GRE question generation.

This module handles loading, selecting, and injecting graph styles
based on the graph type specified in question prompts.
"""

import json
import re
from typing import Dict, Optional, Any, List
from pathlib import Path

from core.utilities.logging_utils import StructuredLogger
from core.utilities.file_utils import load_json_file


class GraphStyleManager:
    """
    Manages graph styles and provides style injection for question generation.
    
    This class handles loading graph configurations, parsing graph types from prompts,
    and providing the appropriate style information for instruction templates.
    
    Attributes:
        _styles: Dictionary containing all graph style configurations
        _logger: Structured logger instance
        _graph_type_mapping: Mapping of common graph names to style keys
        
    Example:
        manager = GraphStyleManager()
        style = manager.get_graph_style("bar chart")
        instruction = manager.inject_graph_style(template, "pie chart")
    """
    
    def __init__(self, styles_file: str = "system_instructions/graph_styles.json"):
        """
        Initialize the graph style manager.
        
        Args:
            styles_file: Path to the graph styles configuration file
        """
        self._logger = StructuredLogger(__name__)
        self._styles = {}
        self._graph_type_mapping = {}
        self._default_colors = {}
        
        # Load graph styles configuration
        self._load_styles_config(styles_file)
    
    def _load_styles_config(self, styles_file: str) -> None:
        """
        Load graph styles configuration from JSON file.
        
        Args:
            styles_file: Path to the styles configuration file
            
        Raises:
            FileNotFoundError: If the styles file doesn't exist
            ValueError: If the styles file is invalid
        """
        try:
            styles_path = Path(styles_file)
            if not styles_path.exists():
                raise FileNotFoundError(f"Graph styles file not found: {styles_file}")
            
            config = load_json_file(str(styles_path))
            
            # Load main configuration sections
            self._styles = config.get("chart_styles", {})
            self._graph_type_mapping = config.get("graph_type_mapping", {})
            self._default_colors = config.get("default_colors", {})
            
            self._logger.log_graph_styles_loaded(len(self._styles))
            
        except Exception as e:
            self._logger.log_graph_styles_error(e, styles_file)
            raise ValueError(f"Failed to load graph styles configuration: {e}")
    
    def parse_graph_type_from_prompt(self, prompt: str) -> Optional[str]:
        """
        Parse graph type from a question generation prompt.
        
        Args:
            prompt: The question generation prompt
            
        Returns:
            Graph type key if found, None otherwise
        """
        if not prompt:
            return None
        
        # Common patterns for graph type identification
        graph_patterns = [
            r'<([^>]*(?:chart|graph|plot)[^>]*)>',  # Within angle brackets
            r'(?:create|generate|show|display)\s+(?:a|an)?\s*([^.]*(?:chart|graph|plot)[^.]*)',  # Action + graph type
            r'(?:bar|pie|line|scatter|area|donut|stacked)\s+(?:chart|graph|plot)',  # Direct graph type
            r'(?:chart|graph|plot)\s+(?:type|showing|of|with)\s+([^.]*)',  # Graph type with description
        ]
        
        for pattern in graph_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    # Clean and normalize the match
                    normalized = match.strip().lower()
                    
                    # Check if it matches any known graph type
                    graph_type = self._normalize_graph_type(normalized)
                    if graph_type:
                        self._logger.log_graph_type_parsed(graph_type, normalized)
                        return graph_type
        
        # Default fallback for common question types
        if "gi" in prompt.lower() or "graphic interpretation" in prompt.lower():
            return "bar_chart"  # Default for GI questions
        
        return None
    
    def _normalize_graph_type(self, graph_description: str) -> Optional[str]:
        """
        Normalize graph description to a standard graph type key.
        
        Args:
            graph_description: Raw graph description from prompt
            
        Returns:
            Normalized graph type key if found, None otherwise
        """
        # Direct mapping check
        if graph_description in self._graph_type_mapping:
            return self._graph_type_mapping[graph_description]
        
        # Fuzzy matching for common variations
        for mapped_name, graph_type in self._graph_type_mapping.items():
            if mapped_name in graph_description or graph_description in mapped_name:
                return graph_type
        
        # Pattern-based matching
        if "bar" in graph_description:
            if "horizontal" in graph_description:
                return "horizontal_bar_chart"
            elif "stacked" in graph_description:
                return "stacked_bar_chart"
            else:
                return "bar_chart"
        elif "pie" in graph_description:
            return "pie_chart"
        elif "line" in graph_description:
            return "line_chart"
        elif "scatter" in graph_description:
            return "scatter_plot"
        elif "area" in graph_description:
            return "area_chart"
        elif "donut" in graph_description:
            return "donut_chart"
        
        return None
    
    def get_graph_style(self, graph_type: str) -> Optional[Dict[str, Any]]:
        """
        Get complete style configuration for a specific graph type.
        
        Args:
            graph_type: Graph type key or description
            
        Returns:
            Dictionary containing style configuration, None if not found
        """
        # Normalize the graph type
        normalized_type = self._normalize_graph_type(graph_type.lower())
        
        if normalized_type and normalized_type in self._styles:
            return self._styles[normalized_type]
        
        # Direct lookup if normalization failed
        if graph_type in self._styles:
            return self._styles[graph_type]
        
        return None
    
    def get_display_instructions(self, graph_type: str) -> str:
        """
        Get display instructions for a specific graph type.
        
        Args:
            graph_type: Graph type key or description
            
        Returns:
            Display instructions string, empty if not found
        """
        style = self.get_graph_style(graph_type)
        return style.get("display_instructions", "") if style else ""
    
    def get_json_format(self, graph_type: str) -> Dict[str, Any]:
        """
        Get JSON format specification for a specific graph type.
        
        Args:
            graph_type: Graph type key or description
            
        Returns:
            JSON format dictionary, empty if not found
        """
        style = self.get_graph_style(graph_type)
        return style.get("json_format", {}) if style else {}
    
    def get_structure_example(self, graph_type: str) -> Dict[str, Any]:
        """
        Get structure example for a specific graph type.
        
        Args:
            graph_type: Graph type key or description
            
        Returns:
            Structure example dictionary, empty if not found
        """
        style = self.get_graph_style(graph_type)
        return style.get("structure", {}) if style else {}
    
    def inject_graph_style(self, template: str, prompt: str) -> str:
        """
        Inject graph style information into an instruction template.
        
        Args:
            template: Instruction template string
            prompt: Question generation prompt
            
        Returns:
            Template with graph style information injected
        """
        # Parse graph type from prompt
        graph_type = self.parse_graph_type_from_prompt(prompt)
        
        if not graph_type:
            # If no graph type found, return template as-is
            return template
        
        # Get style configuration
        style = self.get_graph_style(graph_type)
        if not style:
            return template
        
        # Prepare replacement variables
        replacements = {
            "GRAPH_TYPE": graph_type,
            "GRAPH_DISPLAY_INSTRUCTIONS": self.get_display_instructions(graph_type),
            "GRAPH_JSON_FORMAT": json.dumps(self.get_json_format(graph_type), indent=2),
            "GRAPH_STRUCTURE_EXAMPLE": json.dumps(self.get_structure_example(graph_type), indent=2),
            "GRAPH_DESCRIPTION": style.get("description", ""),
        }
        
        # Inject style information into template
        result = template
        for key, value in replacements.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        
        self._logger.log_graph_style_injected(graph_type, len(replacements))
        return result
    
    def get_available_graph_types(self) -> List[str]:
        """
        Get list of all available graph types.
        
        Returns:
            List of available graph type keys
        """
        return list(self._styles.keys())
    
    def get_graph_type_mappings(self) -> Dict[str, str]:
        """
        Get all graph type mappings.
        
        Returns:
            Dictionary mapping common names to graph type keys
        """
        return self._graph_type_mapping.copy()
    
    def validate_graph_type(self, graph_type: str) -> bool:
        """
        Validate if a graph type is supported.
        
        Args:
            graph_type: Graph type to validate
            
        Returns:
            True if supported, False otherwise
        """
        return self.get_graph_style(graph_type) is not None
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information about the graph style manager.
        
        Returns:
            Dictionary containing system status and statistics
        """
        return {
            "total_graph_types": len(self._styles),
            "total_mappings": len(self._graph_type_mapping),
            "available_graph_types": self.get_available_graph_types(),
            "default_colors": len(self._default_colors),
            "loaded_successfully": len(self._styles) > 0
        }


# Helper functions for convenience
def get_graph_style_manager() -> GraphStyleManager:
    """
    Get a singleton instance of GraphStyleManager.
    
    Returns:
        GraphStyleManager instance
    """
    if not hasattr(get_graph_style_manager, '_instance'):
        get_graph_style_manager._instance = GraphStyleManager()
    return get_graph_style_manager._instance


def parse_graph_type(prompt: str) -> Optional[str]:
    """
    Convenience function to parse graph type from prompt.
    
    Args:
        prompt: Question generation prompt
        
    Returns:
        Graph type if found, None otherwise
    """
    manager = get_graph_style_manager()
    return manager.parse_graph_type_from_prompt(prompt)


def get_graph_instructions(graph_type: str) -> str:
    """
    Convenience function to get display instructions for a graph type.
    
    Args:
        graph_type: Graph type key or description
        
    Returns:
        Display instructions string
    """
    manager = get_graph_style_manager()
    return manager.get_display_instructions(graph_type)


def get_graph_json_format(graph_type: str) -> Dict[str, Any]:
    """
    Convenience function to get JSON format for a graph type.
    
    Args:
        graph_type: Graph type key or description
        
    Returns:
        JSON format dictionary
    """
    manager = get_graph_style_manager()
    return manager.get_json_format(graph_type)