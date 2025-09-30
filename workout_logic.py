# workout_logic.py
from dataclasses import dataclass

@dataclass
class Rec:
    sets: int
    reps_low: int
    reps_high: int
    rir: int

DEFAULT = Rec(sets=3, reps_low=8, reps_high=12, rir=1)

MAP = {
    "bench": Rec(4, 5, 8, 1),
    "incline": Rec(3, 8, 12, 1),
    "overhead": Rec(4, 5, 8, 1),
    "squat": Rec(4, 5, 8, 1),
    "deadlift": Rec(3, 3, 6, 1),
    "row": Rec(3, 8, 12, 1),
    "pulldown": Rec(3, 10, 14, 1),
    "curl": Rec(3, 10, 15, 1),
    "triceps": Rec(3, 10, 15, 1),
    "leg press": Rec(3, 8, 12, 1),
}

def recommend(exercise_name: str) -> Rec:
    name = (exercise_name or "").lower()
    for k, v in MAP.items():
        if k in name:
            return v
    return DEFAULT
