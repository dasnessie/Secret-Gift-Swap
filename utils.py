from copy import deepcopy
from random import shuffle


def _generate_pairing(participants: list[str]):
    shuffled_participants = deepcopy(participants)
    shuffle(shuffled_participants)
    result = {}
    for i in range(len(shuffled_participants)):
        result[shuffled_participants[i]] = shuffled_participants[(i + 1) % len(shuffled_participants)]
    return result