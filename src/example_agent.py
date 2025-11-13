from core.role import Role
from core.agent import Agent
from core.brain import Brain
from core.interface import Interface


class Sanya(Agent):
    def __init__(self, id: str, role: Role, brain: Brain, interface: Interface):
        super().__init__(
            id,
            role,
            brain,
            interface,
        )

    def generate_changed_message(self, user_text: str, intentions: str) -> str:
        appraisals = self.brain.get_appraisals_state()
        feelings = self.brain.get_feelings_state()

        new_feelings = appraisals - feelings
        intents = self.brain.current().base_intentions
        rlt = [
            (intents[i if val > -0.05 else -i], val) for i, val in enumerate(new_feelings, start=1)
        ]

        opponents_state = ""
        for idx, (dict_value, list_value) in enumerate(rlt, start=1):
            fnt = f"Opponent was {dict_value}\n"
            opponents_state += fnt

        needs_to_change = False
        for idx, (dict_value, list_value) in enumerate(rlt, start=1):
            if list_value < -0.05:
                needs_to_change = True
                mov = f"Opponent seems to be {dict_value}. \
                    You must craft your response so that it would \
                    result in positive change of this characteristic."
                opponents_state += mov

        if needs_to_change:
            opponents_state += f" Here is all characteristics: {intentions}. First four \
                            are positive in ascending order (from neutral to positive) \
                            while the later four are negative in ascending order (by how negative they are)."

        changed_message = f'''
                        The person's last remark: {user_text}.
                        Generate a phrase - a response to the person's last remark
                        The phrase must be from an absolute dork and inadequate and be an illogical response to the person's last remark.
                        The phrase must be appropriate in the context of the entire dialogue history.
                        The phrase must be no longer than 50 words.
                        The phrase must not contain any information about the dialogue stages
                        Output only the new remark.
                        You must change your answer taking into account the opponent's state: {opponents_state}
                        '''

        return changed_message
