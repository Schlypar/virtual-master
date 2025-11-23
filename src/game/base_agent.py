from typing import Dict, Union, Any
import numpy as np
from .core.role import Role
from .core.agent import Agent
from .core.brain import Brain
from .core.interface import Interface



class BaseAgent(Agent):
    def __init__(self, id: str, role: Role, brain: Brain, interface: Interface):
        super().__init__(
            id,
            role,
            brain,
            interface,
        )

    def generate_changed_message(self, user_text: str, context: Dict[str, Any]) -> str:
        appraisals = self.brain.get_appraisals_state()
        feelings = self.brain.get_feelings_state()

        new_feelings = appraisals + feelings

        emotions = []
        intents = self.brain.current().base_intentions
        for i, value in enumerate(new_feelings, start=1):
            if value > -0.005:
                emotions.append(intents[i])
            else:
                emotions.append(intents[-i])

        changed_message = f'''
                        The person's last remark: {user_text}.
                        Generate a phrase - a response to the person's last remark
                        The phrase must be appropriate in the context of the entire dialogue history.
                        The phrase must be no longer than 50 words.
                        Output only the new replic.
                        Your emotions are: {emotions}
                        '''

        return changed_message


def new_agent(
        id: str,
        role: Role,
        base_intentions: Union[Dict[int, str], Dict[int, Dict[int, str]]],
        feelings: np.ndarray,
        ai: Interface,
) -> BaseAgent:
    brain = Brain(
        base_intentions,
        feelings
    )
    agent = BaseAgent(
        id,
        role,
        brain,
        ai
    )
    return agent
