
import random

from core import cek_placement, value_fee, value_eta


def nilai_state(problem, state, objective):
    if objective == "eta":
        return value_eta(problem, state)
    elif objective == "fee":
        return value_fee(problem, state)
    raise ValueError("Objective harus 'fee' atau 'eta'")


def steepestascent_hc(problem, initial_state, get_neighbors,
                   objective="fee", max_iterations=500):

    if not cek_placement(problem, initial_state):
        raise ValueError("Initial state tidak valid")

    current_state = initial_state
    current_score = nilai_state(problem, current_state, objective)

    history = [current_score]
    iterations = 0

    while iterations < max_iterations:
        best_state = None
        best_score = current_score

        for neighbor in get_neighbors(problem, current_state):
            if not cek_placement(problem, neighbor):
                continue

            neighbor_score = nilai_state(problem, neighbor, objective)

            if neighbor_score > best_score:
                best_state = neighbor
                best_score = neighbor_score

        if best_state is None:
            break

        current_state = best_state
        current_score = best_score

        iterations += 1
        history.append(current_score)

    return {
        "final_state": current_state,
        "final_score": current_score,
        "history": history,
        "iterations": iterations
    }


def stochastic_hc(problem, initial_state, get_neighbors,
                             objective="fee", max_iterations=500):

    if not cek_placement(problem, initial_state):
        raise ValueError("Initial state tidak valid")

    current_state = initial_state
    current_score = nilai_state(problem, current_state, objective)

    history = [current_score]
    iterations = 0

    while iterations < max_iterations:
        better_neighbors = []

        for neighbor in get_neighbors(problem, current_state):
            if not cek_placement(problem, neighbor):
                continue

            neighbor_score = nilai_state(problem, neighbor, objective)

            if neighbor_score > current_score:
                better_neighbors.append((neighbor, neighbor_score))

        if not better_neighbors:
            break

        chosen_state, chosen_score = random.choice(better_neighbors)

        current_state = chosen_state
        current_score = chosen_score

        iterations += 1
        history.append(current_score)

    return {
        "final_state": current_state,
        "final_score": current_score,
        "history": history,
        "iterations": iterations
    }


def sideways_hc(problem, initial_state, get_neighbors,
                           objective="fee", max_iterations=500,
                           max_sideways=20):

    if not cek_placement(problem, initial_state):
        raise ValueError("Initial state tidak valid")

    current_state = initial_state
    current_score = nilai_state(problem, current_state, objective)

    history = [current_score]
    iterations = 0
    sideways_count = 0
    total_sideways = 0

    visited = {tuple(current_state)}

    while iterations < max_iterations:
        best_state = None
        best_score = current_score
        equal_neighbors = []

        for neighbor in get_neighbors(problem, current_state):
            if not cek_placement(problem, neighbor):
                continue

            neighbor_score = nilai_state(problem, neighbor, objective)

            if neighbor_score > best_score:
                best_state = neighbor
                best_score = neighbor_score

            elif neighbor_score == current_score:
                if tuple(neighbor) not in visited:
                    equal_neighbors.append(neighbor)

        if best_state is not None:
            current_state = best_state
            current_score = best_score
            sideways_count = 0
            visited = {tuple(current_state)}

        elif equal_neighbors and sideways_count < max_sideways:
            current_state = random.choice(equal_neighbors)
            sideways_count += 1
            total_sideways += 1
            visited.add(tuple(current_state))

        else:
            break

        iterations += 1
        history.append(current_score)

    return {
        "final_state": current_state,
        "final_score": current_score,
        "history": history,
        "iterations": iterations,
        "sideways_moves": total_sideways,
        "max_sideways": max_sideways
    }


def randomrestart_hc(problem, initial_state, get_neighbors,
                                 random_state, objective="fee",
                                 max_restarts=10, max_iterations=500):

    if not cek_placement(problem, initial_state):
        raise ValueError("Initial state tidak valid")

    best_result = None
    restart_scores = []
    restart_iterations = []
    all_histories = []

    total_iterations = 0

    for restart in range(max_restarts + 1):
        if restart == 0:
            start_state = initial_state
        else:
            start_state = random_state(problem)

        result = steepestascent_hc(
            problem,
            start_state,
            get_neighbors,
            objective=objective,
            max_iterations=max_iterations
        )

        restart_scores.append(result["final_score"])
        restart_iterations.append(result["iterations"])
        all_histories.append(result["history"])

        total_iterations += result["iterations"]

        if best_result is None:
            best_result = result
        elif result["final_score"] > best_result["final_score"]:
            best_result = result

    return {
        "final_state": best_result["final_state"],
        "final_score": best_result["final_score"],
        "history": best_result["history"],
        "all_histories": all_histories,
        "iterations": total_iterations,
        "restarts": max_restarts,
        "restart_scores": restart_scores,
        "restart_iterations": restart_iterations,
        "max_restarts": max_restarts
    }