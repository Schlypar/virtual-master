from typing import Dict, Any, List
from .brain import Brain
from .interface import Interface
from .prompts import FROM1TO2, FROM2TO3
import numpy as np


class Agent:
    """
    Agent является оберткой для Brain.
    Agent отвечает за:
      - формировать запросы к LLM-Interface,
      - обновлять Brain при получении композиции интенций,
      - решать, когда перейти на след. схему.
    """

    def __init__(self, agent_id: str, role: str, brain: Brain, interface: Interface):
        self.id = agent_id
        self.role = role
        self.brain = brain
        self.interface = interface
        # история диалога
        self.messages: List[Dict[str, str]] = []
        self.prev_scheme = 0
        self.cur_scheme = 0
        self.schemes_done = [False] * (len(brain.transition_rules) - 1)

    async def analyze_intentions(self, user_text: str) -> List[float]:
        return await self.interface.get_composition(self.brain.base_intentions, user_text)

    async def analyze_emotions(self, user_text: str) -> List[float]:
        from .constants import EMOTION_SPACE
        return await self.interface.get_composition(EMOTION_SPACE, user_text)

    async def check_stage_transition_by_llm(self, last_message: str) -> bool:
        """
        Проверяет, был ли переход между состояниями (моральными схемами).
        Возвращает True/False.
        """
        if self.cur_scheme == 0:
            check = f"Последняя реплика человека:{
                last_message}. Нужно ответить только 'да' или 'нет': получил ли преподаватель формальное согласие начать занятие?"
        elif self.cur_scheme == 1:
            check = f"Последняя реплика человека:{
                last_message}. Нужно ответить 'да' если это outline, иначе 'нет'"
        elif self.cur_scheme == 2:
            check = f"Последняя реплика человека:{
                last_message}. Нужно ответить 'да' если эссе полностью написано иначе 'нет'"
        else:
            return False

        messages = [{"role": "user", "content": check}]
        text = await self.interface.extract_text(messages)
        return "да" in text.lower()

    async def generate_reply(self, user_text: str) -> Dict[str, Any]:
        # 1) анализ интенций
        intents = await self.analyze_intentions(user_text)
        emotions = await self.analyze_emotions(user_text)

        # 2) обновляем brain
        self.brain.update_vectors(np.array(intents))

        # 3) проверка перехода
        context = {
            "last_message": user_text,
            "intents": intents,
            "emotions": emotions
        }
        if self.brain.check_transition(self.cur_scheme, context):
            self.cur_scheme = min(self.cur_scheme + 1,
                                  len(self.schemes_done)-1)
        else:
            # fallbacka and hardcode. thinking removing this else if
            try:
                progressed = await self.check_stage_transition_by_llm(user_text)
            except Exception:
                progressed = False
            if progressed:
                self.cur_scheme = min(
                    self.cur_scheme + 1, len(self.schemes_done)-1)

        # 4) запрашиваем у LLM ответ
        profile = "Student profile: " + \
            ", ".join(self.brain.base_intentions.values())
        changed_message = f"The person's last remark: {
            user_text}. Generate a short reply (<=50 words). Consider student profile: {profile}"

        # прикладываем сигнал о переходе (пример)
        if self.cur_scheme - self.prev_scheme == 1:
            if self.cur_scheme == 2:
                changed_message += "\n" + FROM1TO2
            elif self.cur_scheme == 3:
                changed_message += "\n" + FROM2TO3

        messages = list(self.messages)
        messages.append({"role": "user", "content": changed_message})

        reply_text = await self.interface.extract_text(messages)
        # обновляем историю
        self.messages.append({"role": "user", "content": user_text})
        self.messages.append({"role": "assistant", "content": reply_text})
        self.prev_scheme = self.cur_scheme

        return {"Reply": reply_text, "Emotions": emotions}
