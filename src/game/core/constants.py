import numpy as np
from typing import Dict

FIRST_SPACE: Dict[int, str] = {
    1: 'friendly', 2: 'receptive to opinion', 3: 'confident', 4: 'respecting',
    -1: 'hostile', -2: 'opposing to opinion', -3: 'uncertain', -4: 'disrespecting'
}

EMOTION_SPACE: Dict[int, str] = {
    1: 'happy', 2: 'sad', 3: 'surprised', 4: 'disgust', 5: 'angry', 6: 'afraid'
}

FEELINGS1 = np.array([0.2, 0.1, 0.0, 0.3, 0.08, 0.05, 0.05, 0.2])

FEELINGS_TO_EMOTIONS = {
    'friendly': [0, -1, 1, -1, -1, -1],
    'hostile': [-1, 0, 1, 1, 1, 1],
    'confident': [0, 0, -1, 0, 0, -1],
    'uncertain': [0, 0, 1, 0, 0, 1],
    'respecting': [0, -1, 1, -1, -1, -1],
    'disrespecting': [-1, 1, -1, 1, 1, 0],
    'receptive to opinion': [1, -1, -1, -1, -1, 0],
    'opposing to opinion': [-1, 1, 1, 1, 1, 0],
}

BARTENDER_INTENTION: Dict[int, str] = {
    1: 'professional', 2: 'weary', 3: 'impatient', 4: 'sympathetic',
    -1: 'dismissive', -2: 'skeptical', -3: 'abrupt', -4: 'cynical'
}

BARTENDER_FEELINGS = np.array([0.05, 0.1, 0.0, 0.4, 0.08, 0.05, 0.05, 0.1])

BARTENDER_FEELINGS_TO_EMOTIONS = {
    'professional': [0, 1, -1, 0, -1, 0],
    'weary': [-1, 1, -1, 0, 0, 0],
    'impatient': [-1, 0, -1, 1, 1, 0],
    'sympathetic': [0, 1, 0, -1, -1, 0],
    'dismissive': [-1, 0, -1, 1, 0, 0],
    'skeptical': [0, 0, 0, 1, 0, 0],
    'abrupt': [0, 0, -1, 0, 1, 0],
    'cynical': [-1, 1, -1, 1, 0, 0]
}


TRAVELER_INTENTION: Dict[str, str] = {
    1: 'wary', 2: 'self-reliant', 3: 'guarded', 4: 'observant',
    -1: 'trusting', -2: 'seeking companionship', -3: 'open', -4: 'disarming'
}

TRAVELER_FEELINGS = np.array([0.3, 0.3, 0.1, 0.3, 0.08, 0.2, 0.05, 0.1])

TRAVELER_FEELINGS_TO_EMOTIONS = {
    'wary': [0, 0, 1, 0, 0, 1],
    'trusting': [1, -1, -1, -1, -1, -1],
    'self-reliant': [0, 0, -1, -1, 0, -1],
    'seeking companionship': [1, 1, -1, -1, -1, -1],
    'guarded': [-1, 0, 1, 0, 0, 1],
    'open': [1, -1, 1, -1, -1, -1],
    'observant': [0, 0, 1, 0, 0, 0],
    'disarming': [1, -1, 1, -1, -1, -1]
}
