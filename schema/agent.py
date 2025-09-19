from typing import TypedDict


class EnhancementAgentState(TypedDict):
    resume_text: str
    enhancement_prompt: str
    enhanced_resume_text: str
