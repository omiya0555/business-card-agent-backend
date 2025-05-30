from strands import Agent
from strands.models import BedrockModel
import os

def load_agent():
    model = BedrockModel(
        model_id="apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="ap-northeast-1"
    )
    agent = Agent(model=model)
    return agent
