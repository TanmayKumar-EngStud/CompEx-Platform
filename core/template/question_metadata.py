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
        template = self._load_template_file(
            "0-questionMetadata/0-generic.txt.template")
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
        template = self._load_template_file(
            "0-questionMetadata/0-passage.txt.template")

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
        template = self._load_template_file(
            "0-questionMetadata/1-graph.txt.template")

        # Apply graph-specific content token replacement
        processed_template = self._apply_content_tokens(
            template, "graph", prompt)

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
        template = self._load_template_file(
            "0-questionMetadata/2-parent_stimulus.txt.template")

        # Apply parent stimulus content token replacement
        processed_template = self._apply_content_tokens(
            template, "parent_stimulus")

        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )

    def multi_sourceInfo(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        customizations: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Load multi-sourceInfo metadata template.

        Handles multi-source reasoning questions with multiple information sources.

        Args:
            exam_type: Target exam type (GMAT/GRE)
            question_type: Question type classification
            customizations: Exam-specific customizations
            prompt: Original prompt for processing

        Returns:
            Processed multi-source metadata template with SourceInfo structures
        """
        template = self._load_template_file(
            "0-questionMetadata/3-multi_source.txt.template")

        # Apply multi-source content token replacement
        processed_template = self._apply_content_tokens(
            template, "multi_source", prompt)

        return self._template_processor.process_template(
            processed_template, exam_type, question_type, customizations, prompt
        )

    def table(
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
        template = self._load_template_file(
            "0-questionMetadata/4-table.txt.template")

        # Apply table-specific content token replacement
        processed_template = self._apply_content_tokens(
            template, "table")

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
            metadata_path = Path(
                "system_instructions/templates/0-questionMetadata/metadata.json")

            if not metadata_path.exists():
                self._logger.warning(
                    f"metadata.json not found at {metadata_path}")
                return template

            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Get content structure based on type
            content_structure = self._get_content_structure(
                metadata, content_type, prompt)

            # Replace {content} tokens in template
            processed_template = template.replace(
                "{content}", content_structure)

            # Handle {graphs_array} token for graph content type
            if content_type == "graph" and "{graphs_array}" in processed_template:
                graphs_array = self._get_graphs_array(metadata, prompt)
                processed_template = processed_template.replace(
                    "{graphs_array}", graphs_array)

            self._logger.debug(f"Applied content tokens for {content_type}")
            return processed_template

        except Exception as e:
            self._logger.error(
                f"Failed to apply content tokens for {content_type}: {e}")
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
                if graph_type and "content_types" in metadata and "graph" in metadata["content_types"]:
                    chart_styles = metadata["content_types"]["graph"].get(
                        "chart_styles", {})
                    if graph_type in chart_styles:
                        chart_format = chart_styles[graph_type].get(
                            "json_format", {})
                        return json.dumps(chart_format, indent=2)

            # Handle multi_source content type by detecting specific content type from prompt
            if content_type == "multi_source" and prompt:
                return self._get_multi_source_content_structure(metadata, prompt)

            # Get default structure for content type
            content_map = {
                "passage": "content_types.passage",
                "graph": "content_types.graph",
                "table": "content_types.table",
                "parent_stimulus": "parent_stimulus"
            }

            category = content_map.get(content_type)
            if category:
                # Navigate nested structure using dot notation
                structures = metadata
                for key in category.split('.'):
                    if isinstance(structures, dict) and key in structures:
                        structures = structures[key]
                    else:
                        return "{}"  # Path not found

                if isinstance(structures, dict) and structures:
                    # Special handling for table structure
                    if content_type == "table":
                        # Navigate to table_styles -> data_table -> json_format
                        if "table_styles" in structures:
                            table_styles = structures["table_styles"]
                            if isinstance(table_styles, dict) and table_styles:
                                first_table_type = list(table_styles.keys())[0]
                                table_format = table_styles[first_table_type].get(
                                    "json_format", {})
                                return json.dumps(table_format, indent=2)

                    # Special handling for graph structure
                    elif content_type == "graph":
                        # Navigate to chart_styles -> first_chart -> json_format
                        if "chart_styles" in structures:
                            chart_styles = structures["chart_styles"]
                            if isinstance(chart_styles, dict) and chart_styles:
                                first_chart_type = list(chart_styles.keys())[0]
                                chart_format = chart_styles[first_chart_type].get(
                                    "json_format", {})
                                return json.dumps(chart_format, indent=2)

                    first_key = list(structures.keys())[0]
                    return json.dumps(structures[first_key], indent=2)
                elif isinstance(structures, list) and structures:
                    return json.dumps(structures[0], indent=2)

            return "{}"  # Empty JSON as fallback

        except Exception as e:
            self._logger.error(
                f"Failed to get content structure for {content_type}: {e}")
            return "{}"

    def _detect_graph_type_from_structure(self, prompt: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Detect specific graph type from prompt using structured parsing.
        
        Expected prompt structure: "GI - <topic> - <skill> - <graph_type> - <difficulty_level: N>"
        
        Args:
            prompt: Original prompt text
            metadata: Loaded metadata.json content for graph type mapping
            
        Returns:
            Detected graph type or None
        """
        try:
            # Split prompt by " - " to get structured parts
            parts = [part.strip() for part in prompt.split(" - ")]
            
            if len(parts) < 4:
                # Fall back to basic detection if structure is unexpected
                return self._detect_graph_type(prompt)
            
            # For GI questions, graph type is typically in the 4th position (index 3)
            # Structure: [question_type, topic, skill, graph_type, difficulty]
            graph_type_part = parts[3].strip()
            
            # Remove angle brackets if present
            if graph_type_part.startswith("<") and graph_type_part.endswith(">"):
                graph_type_part = graph_type_part[1:-1]
            
            # Get graph type mapping from metadata
            graph_mapping = {}
            if ("content_types" in metadata and 
                "graph" in metadata["content_types"] and 
                "graph_type_mapping" in metadata["content_types"]["graph"]):
                graph_mapping = metadata["content_types"]["graph"]["graph_type_mapping"]
            
            # Check if the extracted graph type exists in mapping
            graph_type_lower = graph_type_part.lower()
            if graph_type_lower in graph_mapping:
                return graph_mapping[graph_type_lower]
            
            # Direct match with underscore format
            if graph_type_part.replace(" ", "_").lower() in metadata.get("content_types", {}).get("graph", {}).get("chart_styles", {}):
                return graph_type_part.replace(" ", "_").lower()
            
            # Fall back to basic detection
            return self._detect_graph_type(prompt)
            
        except Exception as e:
            self._logger.error(f"Failed to detect graph type from structure: {e}")
            return self._detect_graph_type(prompt)

    def _detect_graph_type(self, prompt: str) -> Optional[str]:
        """
        Detect specific graph type from prompt content using keyword matching.

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

    def _get_multi_source_content_structure(self, metadata: Dict[str, Any], prompt: str) -> str:
        """
        Get appropriate content structure for multi-source reasoning based on prompt.
        Uses values from customizations.json for MSR configuration dynamically.
        
        Args:
            metadata: Loaded metadata.json content
            prompt: Original prompt containing content type info
            
        Returns:
            JSON structure string for the detected content type
            
        Raises:
            ValueError: If content type cannot be determined or structure not found
        """
        # Load MSR customizations to get the actual types
        customizations_path = Path("system_instructions/gmat/customizations.json")
        if not customizations_path.exists():
            raise ValueError(f"MSR customizations file not found: {customizations_path}")
            
        with open(customizations_path, 'r', encoding='utf-8') as f:
            customizations = json.load(f)
            
        msr_config = customizations.get("integrated reasoning", {}).get("multi source reasoning", {})
        if not msr_config:
            raise ValueError("MSR configuration not found in customizations")
            
        graph_types = msr_config.get("graph_types", [])
        table_types = msr_config.get("table_types", [])
        source_info_types = msr_config.get("source_info", [])
        
        prompt_lower = prompt.lower()
        
        # Determine content type from prompt by checking against configured types
        detected_type = None
        content_category = None
        
        # Check graph types
        for graph_type in graph_types:
            if graph_type.lower() in prompt_lower:
                detected_type = graph_type
                content_category = "graph"
                break
                
        # Check table types if no graph found
        if not detected_type:
            for table_type in table_types:
                if table_type.lower() in prompt_lower:
                    detected_type = table_type
                    content_category = "table"
                    break
                    
        # Check for passage type
        if not detected_type:
            for source_type in source_info_types:
                if "passage" in str(source_type).lower() and "passage" in prompt_lower:
                    detected_type = source_type
                    content_category = "passage"
                    break
        
        if not detected_type or not content_category:
            raise ValueError(f"Could not determine content type from prompt: {prompt}")
            
        # Get the appropriate structure from metadata
        content_types = metadata.get("content_types", {})
        if content_category not in content_types:
            raise ValueError(f"Content category '{content_category}' not found in metadata")
            
        category_config = content_types[content_category]
        
        if content_category == "graph":
            chart_styles = category_config.get("chart_styles", {})
            if detected_type not in chart_styles:
                raise ValueError(f"Graph type '{detected_type}' not found in chart_styles")
            chart_format = chart_styles[detected_type].get("json_format")
            if not chart_format:
                raise ValueError(f"JSON format not found for graph type '{detected_type}'")
            return json.dumps(chart_format, indent=2)
            
        elif content_category == "table":
            table_styles = category_config.get("table_styles", {})
            if detected_type not in table_styles:
                raise ValueError(f"Table type '{detected_type}' not found in table_styles")
            table_format = table_styles[detected_type].get("json_format")
            if not table_format:
                raise ValueError(f"JSON format not found for table type '{detected_type}'")
            return json.dumps(table_format, indent=2)
            
        elif content_category == "passage":
            passage_styles = category_config.get("passage_styles", {})
            if "reading_comprehension" not in passage_styles:
                raise ValueError("Reading comprehension style not found in passage_styles")
            passage_format = passage_styles["reading_comprehension"].get("json_format")
            if not passage_format:
                raise ValueError("JSON format not found for reading comprehension passage")
            return json.dumps(passage_format, indent=2)
            
        raise ValueError(f"Unsupported content category: {content_category}")

    def _get_graphs_array(self, metadata: Dict[str, Any], prompt: Optional[str] = None) -> str:
        """
        Generate graphs array content from metadata.json chart_styles for requested graph type.
        
        Args:
            metadata: Loaded metadata.json content
            prompt: Original prompt to detect specific graph type using structured parsing
            
        Returns:
            JSON string containing array with only the requested graph format object
        """
        try:
            if "content_types" not in metadata or "graph" not in metadata["content_types"]:
                return "[]"
            
            graph_config = metadata["content_types"]["graph"]
            if "chart_styles" not in graph_config:
                return "[]"
                
            chart_styles = graph_config["chart_styles"]
            
            # If prompt is provided, detect specific graph type using structured parsing
            if prompt:
                requested_graph_type = self._detect_graph_type_from_structure(prompt, metadata)
                if requested_graph_type and requested_graph_type in chart_styles:
                    # Return array with only the requested graph type
                    chart_config = chart_styles[requested_graph_type]
                    if "json_format" in chart_config:
                        return json.dumps([chart_config["json_format"]], indent=2)
            
            # Fallback: return first available graph type if no specific type detected
            for chart_type, chart_config in chart_styles.items():
                if "json_format" in chart_config:
                    return json.dumps([chart_config["json_format"]], indent=2)
            
        except Exception as e:
            self._logger.error(f"Failed to generate graphs array: {e}")
            return "[]"

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
