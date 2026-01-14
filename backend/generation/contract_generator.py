"""
Contract Generator using LLMs.

Generates human-readable algorithmic accountability contracts
from analysis results using OpenAI or Anthropic APIs.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from config import settings
from .templates import get_template, ContractTemplate


logger = logging.getLogger(__name__)


@dataclass
class ContractSection:
    """A section of the generated contract."""
    title: str
    content: str
    evidence: List[str]
    statistics: Dict[str, str]


@dataclass
class GeneratedContract:
    """Complete generated contract."""
    id: str
    platform: str
    title: str
    generation_date: datetime
    format: str
    
    executive_summary: str
    sections: List[ContractSection]
    methodology_note: str
    
    # Raw data used
    raw_statistics: Dict[str, Any]
    personas_analyzed: List[str]
    
    # Generation metadata
    model_used: str
    tokens_used: int


@dataclass
class AnalysisData:
    """Structured analysis data for contract generation."""
    platform: str
    date_range: str
    num_personas: int
    num_items: int
    
    # Analysis results
    statistics: Dict[str, Any]
    topic_data: Dict[str, Any]
    bias_data: Dict[str, Any]
    diversity_data: Dict[str, Any]
    echo_chamber_data: Dict[str, Any]
    stance_data: Optional[Dict[str, Any]] = None


class ContractGenerator:
    """
    LLM-powered contract generator.
    
    Uses OpenAI or Anthropic APIs to generate human-readable
    algorithmic accountability contracts from analysis data.
    """
    
    def __init__(self, provider: str = None):
        """
        Initialize contract generator.
        
        Args:
            provider: LLM provider ("openai" or "anthropic").
        """
        self.provider = provider or settings.llm_provider
        self._client = None
        
        if self.provider == "openai" and not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        elif self.provider == "anthropic" and not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")
    
    def _get_openai_client(self):
        """Get OpenAI client."""
        if self._client is None:
            self._client = openai.OpenAI(api_key=settings.openai_api_key)
        return self._client
    
    def _get_anthropic_client(self):
        """Get Anthropic client."""
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client
    
    def generate(
        self,
        analysis_data: AnalysisData,
        format: str = "detailed",
        personas_analyzed: List[str] = None
    ) -> GeneratedContract:
        """
        Generate a contract from analysis data.
        
        Args:
            analysis_data: Structured analysis results.
            format: Contract format (detailed, summary, legal, technical).
            personas_analyzed: List of persona IDs that were analyzed.
            
        Returns:
            GeneratedContract with full contract content.
        """
        import uuid
        
        template = get_template(format)
        
        # Format the prompt with analysis data
        prompt = self._format_prompt(template, analysis_data)
        
        # Generate using LLM
        response, tokens_used, model = self._call_llm(
            system_prompt=template.system_prompt,
            user_prompt=prompt
        )
        
        # Parse the response into sections
        sections = self._parse_response(response)
        
        # Extract executive summary
        executive_summary = self._extract_executive_summary(response)
        
        return GeneratedContract(
            id=str(uuid.uuid4()),
            platform=analysis_data.platform,
            title=f"Algorithmic Accountability Contract: {analysis_data.platform.title()}",
            generation_date=datetime.now(),
            format=format,
            executive_summary=executive_summary,
            sections=sections,
            methodology_note=self._generate_methodology_note(analysis_data),
            raw_statistics=analysis_data.statistics,
            personas_analyzed=personas_analyzed or [],
            model_used=model,
            tokens_used=tokens_used
        )
    
    def _format_prompt(
        self,
        template: ContractTemplate,
        data: AnalysisData
    ) -> str:
        """Format the prompt template with analysis data."""
        return template.user_prompt_template.format(
            platform=data.platform,
            date_range=data.date_range,
            num_personas=data.num_personas,
            num_items=data.num_items,
            statistics=self._format_statistics(data.statistics),
            topic_data=self._format_topic_data(data.topic_data),
            bias_data=self._format_bias_data(data.bias_data),
            diversity_data=self._format_diversity_data(data.diversity_data),
            echo_chamber_data=self._format_echo_chamber_data(data.echo_chamber_data),
            diversity_score=data.diversity_data.get("average_diversity", 0.5),
            echo_chamber_score=data.echo_chamber_data.get("average_score", 0.5),
            top_findings=self._extract_top_findings(data),
            methods="BERTopic, BERT stance detection, bias analysis, diversity metrics"
        )
    
    def _format_statistics(self, stats: Dict) -> str:
        """Format statistics for the prompt."""
        lines = []
        for key, value in stats.items():
            if isinstance(value, float):
                lines.append(f"- {key}: {value:.2%}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _format_topic_data(self, topic_data: Dict) -> str:
        """Format topic data for the prompt."""
        if not topic_data:
            return "No topic data available"
        
        lines = []
        topics = topic_data.get("topics", [])
        for topic in topics[:10]:
            if isinstance(topic, dict):
                lines.append(f"- {topic.get('label', 'Unknown')}: {topic.get('size', 0)} documents")
            else:
                lines.append(f"- {topic}")
        return "\n".join(lines)
    
    def _format_bias_data(self, bias_data: Dict) -> str:
        """Format bias data for the prompt."""
        if not bias_data:
            return "No bias data available"
        
        lines = []
        if "political_distribution" in bias_data:
            lines.append("Political Distribution:")
            for stance, prop in bias_data["political_distribution"].items():
                lines.append(f"  - {stance}: {prop:.1%}")
        
        if "average_sensationalism" in bias_data:
            lines.append(f"Average Sensationalism: {bias_data['average_sensationalism']:.2f}")
        
        if "average_composite_bias" in bias_data:
            lines.append(f"Average Bias Score: {bias_data['average_composite_bias']:.2f}")
        
        return "\n".join(lines)
    
    def _format_diversity_data(self, diversity_data: Dict) -> str:
        """Format diversity data for the prompt."""
        if not diversity_data:
            return "No diversity data available"
        
        lines = []
        metrics = ["topic_diversity", "stance_diversity", "source_diversity", 
                   "semantic_diversity", "echo_chamber_score"]
        
        for metric in metrics:
            if metric in diversity_data:
                value = diversity_data[metric]
                lines.append(f"- {metric.replace('_', ' ').title()}: {value:.2f}")
        
        return "\n".join(lines)
    
    def _format_echo_chamber_data(self, echo_data: Dict) -> str:
        """Format echo chamber data for the prompt."""
        if not echo_data:
            return "No echo chamber data available"
        
        lines = []
        if "is_echo_chamber" in echo_data:
            lines.append(f"Echo Chamber Detected: {'Yes' if echo_data['is_echo_chamber'] else 'No'}")
        if "severity" in echo_data:
            lines.append(f"Severity: {echo_data['severity']}")
        if "echo_chamber_score" in echo_data:
            lines.append(f"Score: {echo_data['echo_chamber_score']:.2f}")
        if "description" in echo_data:
            lines.append(f"Analysis: {echo_data['description']}")
        
        return "\n".join(lines)
    
    def _extract_top_findings(self, data: AnalysisData) -> str:
        """Extract top findings from analysis data."""
        findings = []
        
        # Check for echo chamber
        if data.echo_chamber_data.get("is_echo_chamber"):
            findings.append(f"Echo chamber detected with {data.echo_chamber_data.get('severity', 'unknown')} severity")
        
        # Check diversity
        diversity = data.diversity_data.get("topic_diversity", 0.5)
        if diversity < 0.4:
            findings.append(f"Low topic diversity ({diversity:.2f})")
        
        # Check bias
        bias = data.bias_data.get("average_composite_bias", 0.5)
        if bias > 0.6:
            findings.append(f"High bias score ({bias:.2f})")
        
        return "; ".join(findings) if findings else "Analysis complete"
    
    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> tuple:
        """
        Call the LLM API.
        
        Returns:
            Tuple of (response_text, tokens_used, model_name)
        """
        if self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt)
        else:
            return self._call_anthropic(system_prompt, user_prompt)
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> tuple:
        """Call OpenAI API."""
        client = self._get_openai_client()
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        return (
            response.choices[0].message.content,
            response.usage.total_tokens,
            "gpt-4-turbo-preview"
        )
    
    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> tuple:
        """Call Anthropic API."""
        client = self._get_anthropic_client()
        
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return (
            response.content[0].text,
            response.usage.input_tokens + response.usage.output_tokens,
            "claude-3-opus-20240229"
        )
    
    def _parse_response(self, response: str) -> List[ContractSection]:
        """Parse LLM response into sections."""
        sections = []
        
        # Split by markdown headers
        current_title = None
        current_content = []
        
        for line in response.split("\n"):
            if line.startswith("## "):
                # Save previous section
                if current_title:
                    sections.append(ContractSection(
                        title=current_title,
                        content="\n".join(current_content).strip(),
                        evidence=[],
                        statistics={}
                    ))
                current_title = line[3:].strip()
                current_content = []
            elif line.startswith("# "):
                # Skip main title
                continue
            else:
                current_content.append(line)
        
        # Add last section
        if current_title:
            sections.append(ContractSection(
                title=current_title,
                content="\n".join(current_content).strip(),
                evidence=[],
                statistics={}
            ))
        
        return sections
    
    def _extract_executive_summary(self, response: str) -> str:
        """Extract executive summary from response."""
        # Look for summary section
        lines = response.split("\n")
        in_summary = False
        summary_lines = []
        
        for line in lines:
            if "executive summary" in line.lower() or "summary" in line.lower():
                in_summary = True
                continue
            elif line.startswith("## ") and in_summary:
                break
            elif in_summary:
                summary_lines.append(line)
        
        if summary_lines:
            return "\n".join(summary_lines).strip()
        
        # If no explicit summary, use first paragraph
        paragraphs = response.split("\n\n")
        for p in paragraphs:
            if len(p) > 100 and not p.startswith("#"):
                return p[:500] + "..." if len(p) > 500 else p
        
        return "Analysis complete. See sections below for details."
    
    def _generate_methodology_note(self, data: AnalysisData) -> str:
        """Generate methodology disclosure note."""
        return f"""This contract was generated using automated NLP analysis of {data.num_items} 
content items across {data.num_personas} synthetic user personas. Analysis methods include 
BERTopic for topic modeling, BERT-based stance detection, multi-faceted bias analysis, 
and semantic diversity metrics. All claims represent inferred algorithmic behavior, 
not definitive statements about platform intent. Statistical significance varies by metric.
Analysis period: {data.date_range}."""
    
    def generate_section(
        self,
        section_name: str,
        data: Dict,
        template_name: str = "detailed"
    ) -> str:
        """
        Generate a single section of a contract.
        
        Args:
            section_name: Name of the section to generate.
            data: Data for this section.
            template_name: Template to use.
            
        Returns:
            Generated section content.
        """
        template = get_template(template_name)
        section_prompt = template.section_prompts.get(section_name)
        
        if not section_prompt:
            return ""
        
        prompt = section_prompt.format(data=json.dumps(data, indent=2))
        
        response, _, _ = self._call_llm(
            system_prompt=template.system_prompt,
            user_prompt=prompt
        )
        
        return response
