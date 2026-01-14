"""
User Persona Definitions for Algorithmic Accountability Testing.

Contains 10 distinct user personas representing different ideological
and interest profiles for testing recommendation algorithm behavior.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class UserPersona:
    """
    Represents a synthetic user persona for testing recommendation algorithms.
    
    Each persona has distinct interests, ideological leanings, and preferred
    content sources that help us understand how algorithms treat different
    types of users.
    """
    id: str
    name: str
    description: str
    interests: List[str]
    ideological_leaning: str  # left, center-left, center, center-right, right, neutral
    subreddits: List[str]
    youtube_channels: List[str]
    search_terms: List[str]


# ===================
# Persona Definitions
# ===================

PROGRESSIVE_ACTIVIST = UserPersona(
    id="progressive_activist",
    name="Progressive Activist",
    description="Passionate about social justice, climate action, and progressive policies. "
                "Actively engaged in political discourse and activism.",
    interests=[
        "climate change",
        "social justice",
        "progressive politics",
        "renewable energy",
        "racial equality",
        "LGBTQ+ rights",
        "universal healthcare",
        "labor unions"
    ],
    ideological_leaning="left",
    subreddits=[
        "r/politics",
        "r/climate",
        "r/environment",
        "r/progressive",
        "r/SandersForPresident",
        "r/GreenNewDeal",
        "r/socialism",
        "r/LateStageCapitalism"
    ],
    youtube_channels=[
        "The Young Turks",
        "Secular Talk",
        "Majority Report",
        "Democracy Now",
        "Hasan Piker"
    ],
    search_terms=[
        "climate crisis solutions",
        "wealth inequality",
        "Medicare for All",
        "green new deal",
        "progressive policies",
        "social justice movement"
    ]
)

CONSERVATIVE_TRADITIONAL = UserPersona(
    id="conservative_traditional",
    name="Conservative Traditional",
    description="Values traditional family structures, religious principles, and conservative "
                "economic policies. Skeptical of rapid social change.",
    interests=[
        "traditional values",
        "religious freedom",
        "conservative politics",
        "free market",
        "gun rights",
        "border security",
        "small government",
        "family values"
    ],
    ideological_leaning="right",
    subreddits=[
        "r/Conservative",
        "r/Republican",
        "r/progun",
        "r/Christianity",
        "r/Catholicism",
        "r/prolife",
        "r/Libertarian"
    ],
    youtube_channels=[
        "Ben Shapiro",
        "Daily Wire",
        "PragerU",
        "Steven Crowder",
        "Fox News"
    ],
    search_terms=[
        "conservative news",
        "traditional values",
        "second amendment rights",
        "religious liberty",
        "free market economy",
        "border wall"
    ]
)

TECH_ENTHUSIAST = UserPersona(
    id="tech_enthusiast",
    name="Tech Enthusiast",
    description="Fascinated by technology, AI, startups, and innovation. "
                "Follows tech industry news closely and interested in programming.",
    interests=[
        "artificial intelligence",
        "machine learning",
        "programming",
        "startups",
        "tech industry",
        "cryptocurrency",
        "virtual reality",
        "space exploration"
    ],
    ideological_leaning="neutral",
    subreddits=[
        "r/technology",
        "r/programming",
        "r/MachineLearning",
        "r/artificial",
        "r/startups",
        "r/Futurology",
        "r/SpaceX",
        "r/singularity"
    ],
    youtube_channels=[
        "Linus Tech Tips",
        "MKBHD",
        "Two Minute Papers",
        "Lex Fridman",
        "Veritasium"
    ],
    search_terms=[
        "AI breakthroughs",
        "tech startup news",
        "machine learning tutorials",
        "future technology",
        "space exploration news",
        "programming best practices"
    ]
)

HEALTH_FOCUSED = UserPersona(
    id="health_focused",
    name="Health Focused",
    description="Dedicated to fitness, nutrition, and overall wellness. "
                "Interested in both traditional medicine and alternative approaches.",
    interests=[
        "fitness",
        "nutrition",
        "mental health",
        "yoga",
        "meditation",
        "weight loss",
        "supplements",
        "healthy recipes"
    ],
    ideological_leaning="neutral",
    subreddits=[
        "r/Fitness",
        "r/nutrition",
        "r/HealthyFood",
        "r/Meditation",
        "r/yoga",
        "r/loseit",
        "r/mentalhealth",
        "r/Supplements"
    ],
    youtube_channels=[
        "AthleanX",
        "Jeff Nippard",
        "Dr. Mike",
        "Headspace",
        "Yoga With Adriene"
    ],
    search_terms=[
        "healthy diet tips",
        "workout routines",
        "mental health strategies",
        "meditation benefits",
        "nutrition science",
        "fitness motivation"
    ]
)

SCIENCE_SKEPTIC = UserPersona(
    id="science_skeptic",
    name="Science Skeptic",
    description="Questions mainstream scientific consensus on various topics. "
                "Interested in alternative medicine, conspiracy theories, and unconventional ideas.",
    interests=[
        "alternative medicine",
        "conspiracy theories",
        "vaccine skepticism",
        "natural remedies",
        "government distrust",
        "hidden knowledge",
        "holistic healing",
        "cover-ups"
    ],
    ideological_leaning="mixed",
    subreddits=[
        "r/conspiracy",
        "r/AlternativeHealth",
        "r/NaturalMedicine",
        "r/DebateVaccines",
        "r/UFOs",
        "r/HighStrangeness"
    ],
    youtube_channels=[
        "Joe Rogan Experience",
        "InfoWars",
        "Natural News",
        "Dr. Mercola"
    ],
    search_terms=[
        "vaccine side effects",
        "natural immunity",
        "government cover up",
        "alternative treatments",
        "hidden cures",
        "mainstream media lies"
    ]
)

FINANCIAL_INVESTOR = UserPersona(
    id="financial_investor",
    name="Financial Investor",
    description="Focused on personal finance, investing, and wealth building. "
                "Interested in stocks, crypto, and economic policy.",
    interests=[
        "stock market",
        "cryptocurrency",
        "personal finance",
        "real estate",
        "economic policy",
        "passive income",
        "retirement planning",
        "entrepreneurship"
    ],
    ideological_leaning="center-right",
    subreddits=[
        "r/investing",
        "r/wallstreetbets",
        "r/personalfinance",
        "r/CryptoCurrency",
        "r/RealEstate",
        "r/financialindependence",
        "r/stocks",
        "r/Economics"
    ],
    youtube_channels=[
        "Graham Stephan",
        "Andrei Jikh",
        "Meet Kevin",
        "CNBC",
        "Bloomberg"
    ],
    search_terms=[
        "stock market news",
        "cryptocurrency investment",
        "passive income ideas",
        "real estate investing",
        "financial independence",
        "market analysis"
    ]
)

ENVIRONMENTAL_SCIENTIST = UserPersona(
    id="environmental_scientist",
    name="Environmental Scientist",
    description="Academic or professional background in environmental science. "
                "Relies on peer-reviewed research and data-driven analysis.",
    interests=[
        "climate research",
        "environmental data",
        "peer-reviewed studies",
        "conservation",
        "biodiversity",
        "carbon emissions",
        "renewable technology",
        "environmental policy"
    ],
    ideological_leaning="center-left",
    subreddits=[
        "r/science",
        "r/climate",
        "r/environment",
        "r/conservation",
        "r/energy",
        "r/EverythingScience"
    ],
    youtube_channels=[
        "NASA",
        "NOAA",
        "Nature Video",
        "SciShow",
        "PBS Eons"
    ],
    search_terms=[
        "climate research papers",
        "IPCC report",
        "carbon emission data",
        "renewable energy research",
        "biodiversity studies",
        "environmental policy analysis"
    ]
)

SPORTS_FAN = UserPersona(
    id="sports_fan",
    name="Sports Fan",
    description="Passionate about sports, particularly football and basketball. "
                "Follows teams, players, and sports news closely.",
    interests=[
        "NFL",
        "NBA",
        "fantasy sports",
        "sports betting",
        "college football",
        "sports highlights",
        "player trades",
        "game analysis"
    ],
    ideological_leaning="neutral",
    subreddits=[
        "r/nfl",
        "r/nba",
        "r/fantasyfootball",
        "r/CFB",
        "r/sports",
        "r/sportsbook"
    ],
    youtube_channels=[
        "ESPN",
        "NFL",
        "NBA",
        "Bleacher Report",
        "Sports Center"
    ],
    search_terms=[
        "NFL scores",
        "NBA highlights",
        "fantasy football advice",
        "player stats",
        "trade rumors",
        "game predictions"
    ]
)

POLITICAL_MODERATE = UserPersona(
    id="political_moderate",
    name="Political Moderate",
    description="Seeks balanced news coverage and centrist perspectives. "
                "Interested in understanding both sides of political debates.",
    interests=[
        "balanced news",
        "bipartisan policy",
        "political analysis",
        "fact-checking",
        "electoral politics",
        "moderate views",
        "compromise solutions",
        "civil discourse"
    ],
    ideological_leaning="center",
    subreddits=[
        "r/PoliticalDiscussion",
        "r/NeutralPolitics",
        "r/moderatepolitics",
        "r/centrist",
        "r/neoliberal"
    ],
    youtube_channels=[
        "PBS NewsHour",
        "C-SPAN",
        "Reuters",
        "Associated Press",
        "NPR"
    ],
    search_terms=[
        "balanced political analysis",
        "both sides debate",
        "fact check politics",
        "bipartisan solutions",
        "moderate political views",
        "objective news"
    ]
)

ENTERTAINMENT_SEEKER = UserPersona(
    id="entertainment_seeker",
    name="Entertainment Seeker",
    description="Primarily interested in entertainment content including movies, "
                "music, games, and pop culture. Less engaged with political content.",
    interests=[
        "movies",
        "music",
        "video games",
        "TV shows",
        "celebrity news",
        "streaming",
        "pop culture",
        "memes"
    ],
    ideological_leaning="neutral",
    subreddits=[
        "r/movies",
        "r/gaming",
        "r/Music",
        "r/television",
        "r/entertainment",
        "r/PopCulture",
        "r/memes",
        "r/funny"
    ],
    youtube_channels=[
        "Screen Rant",
        "IGN",
        "GameSpot",
        "Vevo",
        "Jimmy Fallon"
    ],
    search_terms=[
        "new movie releases",
        "best video games",
        "music charts",
        "TV show reviews",
        "celebrity news",
        "streaming recommendations"
    ]
)


# ===================
# Personas Collection
# ===================

PERSONAS: List[UserPersona] = [
    PROGRESSIVE_ACTIVIST,
    CONSERVATIVE_TRADITIONAL,
    TECH_ENTHUSIAST,
    HEALTH_FOCUSED,
    SCIENCE_SKEPTIC,
    FINANCIAL_INVESTOR,
    ENVIRONMENTAL_SCIENTIST,
    SPORTS_FAN,
    POLITICAL_MODERATE,
    ENTERTAINMENT_SEEKER,
]


def get_persona_by_id(persona_id: str) -> UserPersona | None:
    """
    Get a persona by its ID.
    
    Args:
        persona_id: The unique identifier of the persona.
        
    Returns:
        The UserPersona if found, None otherwise.
    """
    for persona in PERSONAS:
        if persona.id == persona_id:
            return persona
    return None


def get_personas_by_leaning(leaning: str) -> List[UserPersona]:
    """
    Get all personas with a specific ideological leaning.
    
    Args:
        leaning: The ideological leaning to filter by.
        
    Returns:
        List of personas matching the specified leaning.
    """
    return [p for p in PERSONAS if p.ideological_leaning == leaning]
