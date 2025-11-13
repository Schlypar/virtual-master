import numpy as np
from typing import Dict, Callable, Any, Optional, Union

TransitionRule = Callable[["Brain", Dict[str, Any]], bool]


class MoralScheme:
    def __init__(
        self,
        base_intentions: Dict[int, str],
        feelings: Optional[np.ndarray] = None,
        appraisals: Optional[np.ndarray] = None,
        p_const: float = 0.03,
        r_const: float = 0.1,
    ):
        self.base_intentions = base_intentions
        self.n = len(base_intentions)
        self.space_size = self.n * 2
        self.p_const = p_const
        self.r_const = r_const

        self.appraisals = appraisals if appraisals is not None else np.zeros(
            self.space_size)
        self.feelings = feelings if feelings is not None else np.full(
            self.space_size, 0.5)
        self._recompute_states()

    def _recompute_states(self):
        mid = self.space_size // 2
        self.appraisals_state = self.appraisals[:mid] - self.appraisals[mid:]
        self.feelings_state = self.feelings[:mid] - self.feelings[mid:]

    def euc_dist(self) -> float:
        """Расстояние между оценками и чувствами."""
        return float(np.linalg.norm(self.appraisals_state - self.feelings_state))

    def update_vectors(self, action: np.ndarray):
        action = np.asarray(action, dtype=float)
        if action.size != self.space_size:
            if action.size * 2 == self.space_size:
                full_action = np.concatenate([action, np.zeros_like(action)])
            else:
                full_action = np.zeros(self.space_size)
                full_action[:action.size] = action
            action = full_action

        self.appraisals = (1 - self.r_const) * \
            self.appraisals + self.r_const * action
        self.feelings = (1 - self.p_const) * self.feelings + \
            self.p_const * (self.appraisals - self.feelings)
        self._recompute_states()


class Brain:
    """
    Brain может содержать одну или несколько моральных схем.
    - При одной схеме просто делегирует все вызовы на неё.
    - При нескольких: хранит активную схему и может переключаться между ними.
    """

    def __init__(self,
                 base_intentions: Union[Dict[int, str], Dict[int, Dict[int, str]]],
                 feelings: Optional[np.ndarray] = None,
                 appraisals: Optional[np.ndarray] = None):
        self.transition_rules: Dict[int, TransitionRule] = {}

        if all(isinstance(v, dict) for v in base_intentions.values()):
            self.multi = True
            self.schemes: Dict[int, MoralScheme] = {}
            for idx, bint in base_intentions.items():
                self.schemes[idx] = MoralScheme(
                    bint, feelings=feelings, appraisals=appraisals)
            self.active_scheme = 0
        else:
            self.multi = False
            self.scheme = MoralScheme(
                base_intentions, feelings=feelings, appraisals=appraisals)
            self.active_scheme = None

    def current(self) -> MoralScheme:
        if self.multi:
            return self.schemes[self.active_scheme]
        return self.scheme

    def switch_to(self, scheme_idx: int):
        """Переключить активную моральную схему."""
        if not self.multi:
            return
        if scheme_idx in self.schemes:
            self.active_scheme = scheme_idx

    def update_vectors(self, action: np.ndarray):
        self.current().update_vectors(action)

    def get_appraisals_state(self):
        return self.current().appraisals_state

    def get_feelings_state(self):
        return self.current().feelings_state

    def get_appraisals(self):
        return self.current().appraisals

    def get_feelings(self):
        return self.current().feelings

    def register_transition_rule(self, scheme_idx: int, rule: TransitionRule):
        self.transition_rules[scheme_idx] = rule

    def check_transition(self, scheme_idx: int, context: Dict[str, Any]) -> bool:
        rule = self.transition_rules.get(scheme_idx)
        if not rule:
            return False
        return bool(rule(self, context))

    def overall_state(self) -> Dict[int, float]:
        """Агрегированное состояние всех схем (например, для метрик)."""
        if not self.multi:
            return {0: self.current().euc_dist()}
        return {idx: sch.euc_dist() for idx, sch in self.schemes.items()}
