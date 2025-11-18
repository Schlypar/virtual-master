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
FEELINGS2 = FEELINGS1.copy()
FEELINGS3 = FEELINGS1.copy()
FEELINGS4 = np.array([0.3, 0.2, 0.2, 0.1, 0.08, 0.08])

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
