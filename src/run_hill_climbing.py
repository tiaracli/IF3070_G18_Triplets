import random
from core import check_placement
from hill_climbing import (
    steepest_ascent,
    stochastic_hill_climbing,
    sideways_hill_climbing,
    random_restart_hill_climbing
)

problem = {
    "ships": [
        {"w": 8, "l": 8, "max_weight": 22}
    ],
    "vehicles": [
        {"id": "mini1", "w": 1, "l": 2, "weight": 1, "fee": 10, "eta": 2},
        {"id": "sedan1", "w": 2, "l": 3, "weight": 2, "fee": 30, "eta": 5},
        {"id": "truk1", "w": 3, "l": 4, "weight": 5, "fee": 70, "eta": 3}
    ]
}

initial_state = {
    "mini1": (0, 0, 0, "H"),
    "sedan1": None,
    "truk1": None
}


def contoh_neighbors(state):
    neighbors = []

    positions = {
        "mini1": (0, 0, 0, "H"),
        "sedan1": (0, 2, 0, "H"),
        "truk1": (0, 4, 0, "H")
    }

    for vid in state:
        new_state = state.copy()

        if state[vid] is None:
            new_state[vid] = positions[vid]
        else:
            new_state[vid] = None

        if check_placement(problem, new_state):
            neighbors.append(new_state)

    return neighbors


def contoh_random_state():
    state = {
        "mini1": None,
        "sedan1": None,
        "truk1": None
    }

    positions = {
        "mini1": (0, 0, 0, "H"),
        "sedan1": (0, 2, 0, "H"),
        "truk1": (0, 4, 0, "H")
    }

    for vid in state:
        if random.choice([True, False]):
            state[vid] = positions[vid]

    return state


def tampilkan_hasil(nama, result):
    print("\n", nama)
    print("Final state:", result["final_state"])
    print("Final score:", result["final_score"])
    print("History:", result["history"])
    print("Iterations:", result["iterations"])
    print("Valid:", check_placement(problem, result["final_state"]))


if __name__ == "__main__":
    random.seed(42)

    print("Initial state:", initial_state)
    print("Initial valid:", check_placement(problem, initial_state))

    steepest = steepest_ascent(
        problem, initial_state, contoh_neighbors
    )
    tampilkan_hasil("STEEPEST ASCENT", steepest)

    stochastic = stochastic_hill_climbing(
        problem, initial_state, contoh_neighbors
    )
    tampilkan_hasil("STOCHASTIC", stochastic)

    sideways = sideways_hill_climbing(
        problem, initial_state, contoh_neighbors,
        max_sideways=5
    )
    tampilkan_hasil("SIDEWAYS MOVE", sideways)
    print("Sideways moves:", sideways["sideways_moves"])

    restart = random_restart_hill_climbing(
        problem, initial_state, contoh_neighbors,
        contoh_random_state, max_restarts=3
    )
    tampilkan_hasil("RANDOM RESTART", restart)
    print("Restarts:", restart["restarts"])
    print("Scores per restart:", restart["restart_scores"])
    print("Iterations per restart:", restart["restart_iterations"])

    for nama, result in [
        ("Steepest", steepest),
        ("Stochastic", stochastic),
        ("Sideways", sideways),
        ("Restart", restart)
    ]:
        berhasil = (
            result["final_score"] == 110
            and check_placement(problem, result["final_state"])
        )
        print(nama, "PASS" if berhasil else "FAIL")
