from typing import Dict, Any, List
from abc import abstractmethod, ABC
from .brain import Brain
from .interface import Interface
from .constants import EMOTION_SPACE
from .role import Role
import numpy as np


class Agent(ABC):
    """
    Agent является оберткой для Brain.
    Agent отвечает за:
      - формировать запросы к LLM-Interface,
      - обновлять Brain при получении композиции интенций,
      - решать, когда перейти на след. схему.
    """

    def __init__(self, agent_id: str, role: Role, brain: Brain, interface: Interface):
        self.id = agent_id
        self.role = role
        self.brain = brain
        self.interface = interface
        self.messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": f"{self.role.to_string()}. "
            }
        ]
        self.prev_scheme = 0
        self.cur_scheme = 0
        self.schemes_done = [False] * (len(brain.transition_rules) - 1)

    def reset_clear_history_except_last_message(self):
        self.messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": f"{self.role.to_string()}. Your last message will be next message in history of messages."
            },
            self.messages[len(self.messages) - 1],
        ]

    def reset_history_full(self):
        self.messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": f"{self.role.to_string()}."
            },
        ]

    def reset_brain(self):
        self.reset_history_full()
        self.prev_scheme = 0
        self.cur_scheme = 0
        self.schemes_done = [False] * len(self.schemes_done)

    async def analyze_intentions(self, user_text: str) -> List[float]:
        return await self.interface.get_composition(self.brain.base_intentions, user_text)

    async def analyze_emotions(self, user_text: str) -> List[float]:
        return await self.interface.get_composition(EMOTION_SPACE, user_text)

    @abstractmethod
    def generate_changed_message(self, user_text: str, intentions: str) -> str:
        pass

    async def generate_reply(self, user_text: str) -> Dict[str, Any]:
        """Главный цикл обработки входного текста."""

        intents = await self.analyze_intentions(user_text)
        emotions = await self.analyze_emotions(user_text)

        self.brain.update_vectors(np.array(intents))

        context = {
            "last_message": user_text,
            "intents": intents,
            "emotions": emotions,
        }
        cur_idx = self.brain.active_scheme or self.cur_scheme
        if self.brain.check_transition(cur_idx, context):
            self.schemes_done[cur_idx] = True
            next_idx = cur_idx + 1
            self.brain.switch_to(next_idx)
            self.cur_scheme = next_idx

        # 4) Формируем ответ для LLM
        intentions = ", ".join(self.brain.current().base_intentions.values())
        changed_message = self.generate_changed_message(user_text, intentions)

        messages = list(self.messages)
        messages.append({"role": "user", "content": changed_message})
        reply_text = await self.interface.extract_text(messages)

        self.messages.append({"role": "user", "content": user_text})
        self.messages.append({"role": "assistant", "content": reply_text})
        self.prev_scheme = self.cur_scheme

        return {
            "Reply": reply_text,
            "Emotions": emotions,
        }
