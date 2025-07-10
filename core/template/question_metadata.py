"""
QuestionMetadata template class for handling metadata generation templates.

This class encapsulates all logic related to question metadata template loading
and processing, including graph structures, passage metadata, and multi-source content.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.utilities.logging_utils import StructuredLogger
from core.instructions.template_processor import TemplateProcessor
from core.instructions.instruction_loader import InstructionLoader


class QuestionMetadata:
    """
    Handles question metadata template loading and processing.
    
    This class provides clean methods for each metadata template type,
    handling content token replacement and exam-specific customizations.
    """
    
    def __init__(self):
        """Initialize the QuestionMetadata handler."""
        self._logger = StructuredLogger(__name__)
        self._template_processor = TemplateProcessor()
        self._instruction_loader = InstructionLoader()
        
    def generic(
        self, 
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load generic metadata template from 0-questionMetadata/0-generic.txt.template
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed generic metadata template
        """
        template = self._load_template_file("0-questionMetadata/0-generic.txt.template")
        return self._template_processor.process_template(
            template, exam_type, question_type, customizations, prompt
        )
    
    def passage(
        self,
        exam_type: ExamType, 
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load passage metadata template from 0-questionMetadata/0-passage.txt.template
        
        Handles reading comprehension passages and content structures.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed passage metadata template with content structures
        """
        template = self._load_template_file("0-questionMetadata/0-passage.txt.template")
        
        # Apply passage-specific content token replacement
        processed_template = self._apply_content_tokens(template, "passage")
        
        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )
    
    def graph(
        self,
        exam_type: ExamType,
        question_type: QuestionType, 
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load graph metadata template.
        
        Handles graph-based questions including line charts, bar charts, etc.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed graph metadata template with graph structures
        """
        template = self._load_template_file("0-questionMetadata/1-graph.txt.template")
        
        # Apply graph-specific content token replacement
        processed_template = self._apply_content_tokens(template, "graph", prompt)
        
        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )
    
    def parent_stimulus(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load parent stimulus metadata template.
        
        Handles parent-child question structures with shared stimuli.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed parent stimulus metadata template
        """
        template = self._load_template_file("0-questionMetadata/2-parent_stimulus.txt.template")
        
        # Apply parent stimulus content token replacement
        processed_template = self._apply_content_tokens(template, "parent_stimulus")
        
        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )
    
    def multi_source(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load multi-source metadata template.
        
        Handles multi-source reasoning questions with multiple information sources.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed multi-source metadata template with SourceInfo structures
        """
        template = self._load_template_file("0-questionMetadata/3-multi_source.txt.template")
        
        # Apply multi-source content token replacement
        processed_template = self._apply_content_tokens(template, "multi_source")
        
        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )
    
    def specialized_table(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load specialized table metadata template.
        
        Handles table analysis questions with structured tabular data.
        
        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing
            
        Returns:
            Processed specialized table metadata template
        """
        template = self._load_template_file("0-questionMetadata/4-specialized_table.txt.template")
        
        # Apply table-specific content token replacement
        processed_template = self._apply_content_tokens(template, "specialized_table")
        
        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )
    
    def _apply_content_tokens(
        self, 
        template: str, 
        content_type: str,
        prompt: Optional[str] = None
    ) -> str:
        """
        Apply content-specific token replacement using metadata.json.
        
        Args:
            template: Raw template content
            content_type: Type of content (passage, graph, table, etc.)
            prompt: Original prompt for content type detection
            
        Returns:
            Template with {content} tokens replaced by appropriate structures
        """
        try:
            # Load metadata.json for content type definitions
            metadata_path = Path("system_instructions/templates/0-questionMetadata/metadata.json")
            
            if not metadata_path.exists():
                self._logger.warning(f"metadata.json not found at {metadata_path}")
                return template
                
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Get content structure based on type
            content_structure = self._get_content_structure(metadata, content_type, prompt)
            
            # Replace {content} tokens in template
            processed_template = template.replace("{content}", content_structure)
            
            self._logger.debug(f"Applied content tokens for {content_type}")
            return processed_template
            
        except Exception as e:
            self._logger.error(f"Failed to apply content tokens for {content_type}: {e}")
            return template
    
    def _get_content_structure(
        self, 
        metadata: Dict[str, Any], 
        content_type: str,
        prompt: Optional[str] = None
    ) -> str:
        """
        Get appropriate content structure from metadata.json.
        
        Args:
            metadata: Loaded metadata.json content
            content_type: Type of content to structure
            prompt: Original prompt for specific type detection
            
        Returns:
            JSON structure string for the content type
        """
        try:
            if content_type == "graph" and prompt:
                # Detect specific graph type from prompt
                graph_type = self._detect_graph_type(prompt)
                if graph_type and graph_type in metadata.get("graphs", {}):
                    return json.dumps(metadata["graphs"][graph_type], indent=2)
                
            # Get default structure for content type
            content_map = {
                "passage": "passages",
                "graph": "graphs",
                "specialized_table": "tables",
                "multi_source": "multi_source",
                "parent_stimulus": "parent_stimulus"
            }
            
            category = content_map.get(content_type)
            if category and category in metadata:
                # Return first available structure as default
                structures = metadata[category]
                if isinstance(structures, dict) and structures:
                    first_key = list(structures.keys())[0]
                    return json.dumps(structures[first_key], indent=2)
                elif isinstance(structures, list) and structures:
                    return json.dumps(structures[0], indent=2)
                    
            return "{}"  # Empty JSON as fallback
            
        except Exception as e:
            self._logger.error(f"Failed to get content structure for {content_type}: {e}")
            return "{}"
    
    def _detect_graph_type(self, prompt: str) -> Optional[str]:
        """
        Detect specific graph type from prompt content.
        
        Args:
            prompt: Original prompt text
            
        Returns:
            Detected graph type or None
        """
        prompt_lower = prompt.lower()
        
        # Map prompt keywords to graph types
        graph_keywords = {
            "line chart": "line_chart",
            "bar chart": "bar_chart", 
            "pie chart": "pie_chart",
            "scatter plot": "scatter_plot",
            "histogram": "histogram",
            "graph": "line_chart"  # Default fallback
        }
        
        for keyword, graph_type in graph_keywords.items():
            if keyword in prompt_lower:
                return graph_type
                
        return None
    
    def _load_template_file(self, template_path: str) -> str:
        """
        Load template file from system_instructions/templates directory.
        
        Args:
            template_path: Relative path to template file
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If template file can't be read
        """
        full_path = Path("system_instructions/templates") / template_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Template file not found: {full_path}")
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._logger.debug(f"Loaded template: {template_path}")
            return content
        except Exception as e:
            raise IOError(f"Failed to load template {template_path}: {e}")