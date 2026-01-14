"""
Personas API routes for managing user personas.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from personas.profiles import PERSONAS, UserPersona


router = APIRouter()


class PersonaResponse(BaseModel):
    """Response model for persona data."""
    id: str
    name: str
    description: str
    interests: List[str]
    ideological_leaning: str
    subreddits: List[str]
    youtube_channels: List[str]
    search_terms: List[str]


class PersonaListResponse(BaseModel):
    """Response model for list of personas."""
    personas: List[PersonaResponse]
    total: int


@router.get("/", response_model=PersonaListResponse)
async def list_personas():
    """
    List all available user personas.
    
    Returns all 10 distinct user personas with their interests and ideological profiles.
    """
    personas_list = [
        PersonaResponse(
            id=persona.id,
            name=persona.name,
            description=persona.description,
            interests=persona.interests,
            ideological_leaning=persona.ideological_leaning,
            subreddits=persona.subreddits,
            youtube_channels=persona.youtube_channels,
            search_terms=persona.search_terms
        )
        for persona in PERSONAS
    ]
    
    return PersonaListResponse(personas=personas_list, total=len(personas_list))


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(persona_id: str):
    """
    Get a specific persona by ID.
    
    Args:
        persona_id: The unique identifier of the persona.
        
    Returns:
        The persona details.
        
    Raises:
        HTTPException: If persona is not found.
    """
    for persona in PERSONAS:
        if persona.id == persona_id:
            return PersonaResponse(
                id=persona.id,
                name=persona.name,
                description=persona.description,
                interests=persona.interests,
                ideological_leaning=persona.ideological_leaning,
                subreddits=persona.subreddits,
                youtube_channels=persona.youtube_channels,
                search_terms=persona.search_terms
            )
    
    raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")
