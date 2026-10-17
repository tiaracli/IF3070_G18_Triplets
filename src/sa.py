import math
import random
import time

from core import value_fee, eta_value, check_placement
from neighbor import random_state, random_neighbor, all_neighbors


def schedule(t, T0, alpha, T_min):
    T = T0 * (alpha ** t)

    if T < T_min:
        return 0

    return T


def is_local_optimum(problem, state, objective="fee"):
    score_function = eta_value if objective == "eta" else value_fee

    v = score_function(problem, state)

    for nb in all_neighbors(problem, state):
        if score_function(problem, nb) > v:
            return False

    return True


def simulated_annealing(
    problem,
    T0=100.0,
    alpha=0.9998,
    T_min=0.1,
    initial=None,
    seed=None,
    objective="fee"
):
    if objective not in ("fee", "eta"):
        raise ValueError("Objective harus 'fee' atau 'eta'")

    if T0 <= 0:
        raise ValueError("T0 harus lebih besar dari 0")

    if not 0 < alpha < 1:
        raise ValueError("Alpha harus berada di antara 0 dan 1")

    if T_min <= 0:
        raise ValueError("T_min harus lebih besar dari 0")

    if seed is not None:
        random.seed(seed)

    score_function = eta_value if objective == "eta" else value_fee

    start = time.time()

    current = initial if initial is not None else random_state(problem)

    if not check_placement(problem, current):
        raise ValueError("Initial state tidak valid")

    cur_val = score_function(problem, current)

    best, best_val = current, cur_val
    awal = current

    history = [cur_val]
    probs = []
    stuck = 0
    worse_accepted = 0
    t = 0

    while True:
        t += 1
        T = schedule(t, T0, alpha, T_min)

        if T == 0:
            break

        nxt = random_neighbor(problem, current)

        if nxt is None:
            stuck += 1
            probs.append(None)
            history.append(cur_val)
            continue

        dE = score_function(problem, nxt) - cur_val

        if dE > 0:
            current, cur_val = nxt, cur_val + dE
            probs.append(None)
        else:
            p = math.exp(dE / T)
            probs.append(p)

            if random.random() < p:
                current, cur_val = nxt, cur_val + dE

                if dE < 0:
                    worse_accepted += 1
            else:
                stuck += 1

        if cur_val > best_val:
            best, best_val = current, cur_val

        history.append(cur_val)

    final_local_opt = is_local_optimum(problem, current, objective)

    return {
        "algo": "SA",
        "params": {
            "T0": T0,
            "alpha": alpha,
            "T_min": T_min,
            "seed": seed,
            "objective": objective
        },
        "initial_state": awal,
        "final_state": current,
        "final_value": cur_val,
        "best_state": best,
        "best_value": best_val,
        "iterations": t - 1,
        "duration": time.time() - start,
        "history": history,
        "probs": probs,
        "stuck": stuck,
        "stuck_freq": stuck / max(1, t - 1),
        "worse_accepted": worse_accepted,
        "final_local_opt": final_local_opt
    }
