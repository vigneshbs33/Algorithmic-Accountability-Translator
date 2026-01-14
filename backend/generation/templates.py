"""
Contract Generation Templates.

Defines prompt templates for generating algorithmic accountability contracts.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class ContractFormat(Enum):
    """Contract format types."""
    DETAILED = "detailed"
    SUMMARY = "summary"
    LEGAL = "legal"
    TECHNICAL = "technical"


@dataclass
class ContractTemplate:
    """Template for contract generation."""
    name: str
    format: ContractFormat
    system_prompt: str
    user_prompt_template: str
    section_prompts: Dict[str, str]


# ===================
# System Prompts
# ===================

SYSTEM_PROMPT_DETAILED = """You are an expert at analyzing algorithmic systems and translating 
their behavior into clear, accessible language. Your task is to generate accountability 
contracts that explain how recommendation algorithms work in plain language.

Your contracts should:
1. Be accessible to non-technical readers
2. Use specific percentages and statistics
3. Provide concrete examples
4. Clearly state what the algorithm optimizes for
5. Explain the real-world impact on users
6. Include evidence for every claim

Write in a professional but approachable tone. Use bullet points and numbered lists 
for clarity. Always back up claims with data from the analysis."""


SYSTEM_PROMPT_LEGAL = """You are a legal technology expert specializing in algorithmic 
accountability and digital rights. Your task is to generate formal accountability 
documents that could serve as the basis for transparency requirements.

Your contracts should:
1. Use precise, legally-informed language
2. Define all technical terms clearly
3. Structure content with formal sections and subsections
4. Include methodology disclosures
5. Note limitations and confidence levels
6. Be suitable for regulatory filing

Write in formal legal style with clear definitions and structured arguments."""


SYSTEM_PROMPT_TECHNICAL = """You are a machine learning researcher specializing in 
recommendation systems and algorithmic fairness. Your task is to generate technical 
reports on algorithmic behavior.

Your reports should:
1. Include statistical methodology
2. Reference relevant metrics and formulas
3. Discuss model architecture considerations
4. Analyze feature importance
5. Note statistical significance levels
6. Suggest algorithmic interventions

Write in academic style with proper statistical terminology."""


# ===================
# User Prompt Templates
# ===================

USER_PROMPT_DETAILED = """Generate an algorithmic accountability contract based on the 
following analysis:

## Platform Information
- Platform: {platform}
- Analysis Period: {date_range}
- User Personas Tested: {num_personas}
- Total Content Analyzed: {num_items}

## Statistical Findings
{statistics}

## Topic Distribution Analysis
{topic_data}

## Bias Measurements
{bias_data}

## Diversity Metrics
{diversity_data}

## Echo Chamber Analysis
{echo_chamber_data}

Generate a comprehensive contract with the following sections:
1. Executive Summary
2. Algorithmic Optimization Objectives
3. Filter Bubble Analysis
4. Bias Quantification
5. Concrete Examples
6. Impact Assessment
7. Recommendations for Users

For each section, include:
- Clear explanations
- Specific percentages from the data
- Concrete examples
- Evidence citations

Format the output as markdown."""


USER_PROMPT_SUMMARY = """Based on the following algorithmic analysis, generate a concise 
executive summary (max 500 words):

Platform: {platform}
Analysis Period: {date_range}
Key Statistics: {statistics}
Diversity Score: {diversity_score}
Echo Chamber Score: {echo_chamber_score}
Top Findings: {top_findings}

Include:
1. One-paragraph overview
2. 5 key bullet points
3. One concrete example
4. Overall assessment (low/medium/high concern)

Format as markdown."""


USER_PROMPT_LEGAL = """Generate a formal Algorithmic Transparency Disclosure based on:

## Subject Platform
{platform}

## Analysis Methodology
- Period: {date_range}
- Sample Size: {num_items} content items
- Personas: {num_personas} synthetic user profiles
- Analysis Methods: {methods}

## Quantitative Findings
{statistics}

## Bias Assessment
{bias_data}

## Diversity Assessment
{diversity_data}

Generate a formal disclosure document with:
1. Definitions
2. Scope and Methodology
3. Findings of Fact
4. Analysis and Conclusions
5. Limitations
6. Certification

Use formal legal language suitable for regulatory purposes."""


# ===================
# Section Templates
# ===================

SECTION_TEMPLATES = {
    "executive_summary": """Summarize this algorithmic analysis in 2-3 paragraphs:
{data}
Focus on the most important findings and their implications for users.""",

    "optimization_objectives": """Analyze what this algorithm optimizes for based on:
{data}
List the optimization objectives in order of priority with evidence.""",

    "filter_bubble": """Explain the filter bubble effects based on:
{data}
Include specific metrics and what they mean for information diversity.""",

    "bias_quantification": """Quantify the biases found in recommendations:
{data}
Include percentages and comparisons across user personas.""",

    "examples": """Generate 3 concrete examples illustrating algorithmic behavior:
{data}
Make examples specific and relatable.""",

    "recommendations": """Based on these findings:
{data}
Provide actionable recommendations for users to mitigate filter bubble effects."""
}


# ===================
# Template Instances
# ===================

DETAILED_TEMPLATE = ContractTemplate(
    name="detailed",
    format=ContractFormat.DETAILED,
    system_prompt=SYSTEM_PROMPT_DETAILED,
    user_prompt_template=USER_PROMPT_DETAILED,
    section_prompts=SECTION_TEMPLATES
)

SUMMARY_TEMPLATE = ContractTemplate(
    name="summary",
    format=ContractFormat.SUMMARY,
    system_prompt=SYSTEM_PROMPT_DETAILED,
    user_prompt_template=USER_PROMPT_SUMMARY,
    section_prompts={}
)

LEGAL_TEMPLATE = ContractTemplate(
    name="legal",
    format=ContractFormat.LEGAL,
    system_prompt=SYSTEM_PROMPT_LEGAL,
    user_prompt_template=USER_PROMPT_LEGAL,
    section_prompts=SECTION_TEMPLATES
)

TECHNICAL_TEMPLATE = ContractTemplate(
    name="technical",
    format=ContractFormat.TECHNICAL,
    system_prompt=SYSTEM_PROMPT_TECHNICAL,
    user_prompt_template=USER_PROMPT_DETAILED,
    section_prompts=SECTION_TEMPLATES
)


TEMPLATES = {
    "detailed": DETAILED_TEMPLATE,
    "summary": SUMMARY_TEMPLATE,
    "legal": LEGAL_TEMPLATE,
    "technical": TECHNICAL_TEMPLATE
}


def get_template(name: str = "detailed") -> ContractTemplate:
    """
    Get a contract template by name.
    
    Args:
        name: Template name (detailed, summary, legal, technical).
        
    Returns:
        ContractTemplate instance.
    """
    return TEMPLATES.get(name, DETAILED_TEMPLATE)
