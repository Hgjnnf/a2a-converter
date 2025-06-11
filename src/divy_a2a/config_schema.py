from pydantic import BaseModel, HttpUrl
from typing import List
from enum import Enum

class Frameworks(Enum):
    OPENAI = 'openai'
    CREWAI = 'crewai'
    LANGGRAPH = 'langgraph'

class Skill(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]
    examples: List[str]

class Capabilities(BaseModel):
    streaming: bool
    pushNotifications: bool = False

class CLIConfig(BaseModel):
    agent_export_name: str
    agent_file_name: str
    framework: Frameworks
    name: str
    description: str
    url: HttpUrl
    version: str
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    capabilities: Capabilities
    skills: List[Skill]
