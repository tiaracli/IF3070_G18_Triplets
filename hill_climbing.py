
import random
from core import check_placement, value_fee, eta_value


def get_score(problem, state, objective):
    if objective == "eta":
        return eta_value(problem, state)
    return value_fee(problem, state)


def steepest_ascent(problem, initial_state, get_neighbors,
                   objective="fee", max_iterations=500):

    current_state = initial_state.copy()
    current_score = get_score(problem, current_state, objective)

    history = [current_score]
    iterations = 0

    while iterations < max_iterations:
        best_state = None
        best_score = current_score

        for neighbor in get_neighbors(current_state):
            if not check_placement(problem, neighbor):
                continue

            neighbor_score = get_score(problem, neighbor, objective)

            if neighbor_score > best_score:
                best_state = neighbor
                best_score = neighbor_score

        if best_state is None:
            break

        current_state = best_state.copy()
        current_score = best_score

        iterations += 1
        history.append(current_score)

    return {
        "final_state": current_state,
        "final_score": current_score,
        "history": history,
        "iterations": iterations
    }


def stochastic_hill_climbing(problem, initial_state, get_neighbors,
                             objective="fee", max_iterations=500):

    current_state = initial_state.copy()
    current_score = get_score(problem, current_state, objective)

    history = [current_score]
    iterations = 0

    while iterations < max_iterations:
        better_neighbors = []

        for neighbor in get_neighbors(current_state):
            if not check_placement(problem, neighbor):
                continue

            neighbor_score = get_score(problem, neighbor, objective)

            if neighbor_score > current_score:
                better_neighbors.append((neighbor, neighbor_score))

        if len(better_neighbors) == 0:
            break

        chosen_state, chosen_score = random.choice(better_neighbors)

        current_state = chosen_state.copy()
        current_score = chosen_score

        iterations += 1
        history.append(current_score)

    return {
        "final_state": current_state,
        "final_score": current_score,
        "history": history,
        "iterations": iterations
    }


def sideways_hill_climbing(problem, initial_state, get_neighbors,
                           objective="fee", max_iterations=500,
                           max_sideways=20):

    current_state = initial_state.copy()
    current_score = get_score(problem, current_state, objective)

    history = [current_score]
    iterations = 0
    sideways_count = 0
    total_sideways = 0

    while iterations < max_iterations:
        best_state = None
        best_score = current_score

        for neighbor in get_neighbors(current_state):
            if not check_placement(problem, neighbor):
                continue

            if neighbor == current_state:
                continue

            neighbor_score = get_score(problem, neighbor, objective)

            if neighbor_score > best_score:
                best_state = neighbor
                best_score = neighbor_score

            elif neighbor_score == best_score and best_state is None:
                best_state = neighbor

        if best_state is None:
            break

        if best_score == current_score:
            if sideways_count >= max_sideways:
                break

            sideways_count += 1
            total_sideways += 1
        else:
            sideways_count = 0

        current_state = best_state.copy()
        current_score = best_score

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


def random_restart_hill_climbing(problem, initial_state,
                                 get_neighbors, random_state,
                                 objective="fee", max_restarts=10,
                                 max_iterations=500):

    best_result = None
    restart_scores = []
    restart_iterations = []
    all_histories = []

    for restart in range(max_restarts + 1):
        if restart == 0:
            start_state = initial_state.copy()
        else:
            start_state = random_state()

        result = steepest_ascent(
            problem,
            start_state,
            get_neighbors,
            objective=objective,
            max_iterations=max_iterations
        )

        restart_scores.append(result["final_score"])
        restart_iterations.append(result["iterations"])
        all_histories.append(result["history"])

        if best_result is None:
            best_result = result
        elif result["final_score"] > best_result["final_score"]:
            best_result = result

    total_iterations = sum(restart_iterations)

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
