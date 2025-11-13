import numpy as np
from typing import Dict, Callable, Any, Optional

TransitionRule = Callable[["Brain", Dict[str, Any]], bool]


class Brain:
    """
    Brain хранит:
      - base_intentions: mapping int->label
      - appraisals и feelings (вектора)
      - регистрируемые правила перехода (transition rules)
    Brain НЕ вызывает LLM.
    """

    def __init__(self,
                 base_intentions: Dict[int, str],
                 feelings: Optional[np.ndarray] = None,
                 appraisals: Optional[np.ndarray] = None,
                 p_const: float = 0.03,
                 r_const: float = 0.1):
        self.base_intentions = base_intentions
        # Для совместимости с вашим старым кодом храним векторы длины 2*N
        n = len(base_intentions)
        self.space_size = n * 2
        self.p_const = p_const
        self.r_const = r_const

        self.appraisals = appraisals if appraisals is not None else np.zeros(
            self.space_size)
        self.feelings = feelings if feelings is not None else np.full(
            self.space_size, 0.5)

        self.appraisals_state = np.zeros(n)
        self.feelings_state = np.zeros(n)

        self._recompute_states()
        self.transition_rules: Dict[int, TransitionRule] = {}

    def _recompute_states(self):
        mid = self.space_size // 2
        self.appraisals_state = self.appraisals[:mid] - self.appraisals[mid:]
        self.feelings_state = self.feelings[:mid] - self.feelings[mid:]

    def euc_dist(self, a: np.ndarray, b: np.ndarray) -> float:
        if a.shape != b.shape:
            raise ValueError("Shapes must match")
        return float(np.linalg.norm(a - b))

    def update_vectors(self, action: np.ndarray):
        """
        action: длина равна mid (кол-во базисов) или full length.
        Если предоставлен вектор меньшей длины, расширяем его в формат space_size.
        """
        action = np.asarray(action, dtype=float)
        # приводим action к длине space_size (повторяем/дополняем нулями)
        if action.size != self.space_size:
            if action.size * 2 == self.space_size:
                # предположим, что action задан для половины пространства
                full_action = np.concatenate([action, np.zeros_like(action)])
            else:
                # расширяем нулями
                full_action = np.zeros(self.space_size)
                full_action[:action.size] = action
            action = full_action

        self.appraisals = (1 - self.r_const) * \
            self.appraisals + self.r_const * action
        self.feelings = (1 - self.p_const) * self.feelings + \
            self.p_const * (self.appraisals - self.feelings)
        self._recompute_states()

    def register_transition_rule(self, scheme_idx: int, rule: TransitionRule):
        self.transition_rules[scheme_idx] = rule

    def check_transition(self, scheme_idx: int, context: Dict[str, Any]) -> bool:
        rule = self.transition_rules.get(scheme_idx)
        if not rule:
            return False
        return bool(rule(self, context))

    # getters
    def get_appraisals(self): return self.appraisals
    def get_feelings(self): return self.feelings
    def get_appraisals_state(self): return self.appraisals_state
    def get_feelings_state(self): return self.feelings_state
