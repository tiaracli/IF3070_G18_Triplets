
import csv
import json
import random
import time
from pathlib import Path

from core import (
    load_problem,
    check_placement,
    value_fee,
    eta_value,
    count_misplaced_urgent
)

from neighbor import random_state, all_neighbors

from hill_climbing import (
    steepest_ascent,
    stochastic_hill_climbing,
    sideways_hill_climbing,
    random_restart_hill_climbing
)


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "src" / "data" / "kasus_1.json"

MAX_ITERATIONS = 500
MAX_SIDEWAYS = 20
MAX_RESTARTS = 10

SEEDS = [42, 43, 44]


def save_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def run_algorithm(problem, name, initial_state, objective):
    if name == "steepest":
        return steepest_ascent(
            problem,
            initial_state,
            all_neighbors,
            objective=objective,
            max_iterations=MAX_ITERATIONS
        )

    elif name == "stochastic":
        return stochastic_hill_climbing(
            problem,
            initial_state,
            all_neighbors,
            objective=objective,
            max_iterations=MAX_ITERATIONS
        )

    elif name == "sideways":
        return sideways_hill_climbing(
            problem,
            initial_state,
            all_neighbors,
            objective=objective,
            max_iterations=MAX_ITERATIONS,
            max_sideways=MAX_SIDEWAYS
        )

    elif name == "random_restart":
        return random_restart_hill_climbing(
            problem,
            initial_state,
            all_neighbors,
            random_state,
            objective=objective,
            max_restarts=MAX_RESTARTS,
            max_iterations=MAX_ITERATIONS
        )

    raise ValueError("Nama algoritma tidak dikenal")


def run_experiments(problem, objective):
    algorithms = [
        "steepest",
        "stochastic",
        "sideways",
        "random_restart"
    ]

    summary = []
    details = []

    for seed in SEEDS:
        random.seed(seed)
        initial_state = random_state(problem)

        if not check_placement(problem, initial_state):
            raise ValueError("Initial state tidak valid")

        if objective == "eta":
            initial_score = eta_value(problem, initial_state)
        else:
            initial_score = value_fee(problem, initial_state)

        for name in algorithms:
            random.seed(seed)

            start = time.perf_counter()

            result = run_algorithm(
                problem,
                name,
                initial_state,
                objective
            )

            duration = time.perf_counter() - start
            final_state = result["final_state"]

            row = {
                "algorithm": name,
                "objective": objective,
                "seed": seed,
                "initial_score": initial_score,
                "final_score": result["final_score"],
                "iterations": result["iterations"],
                "duration_seconds": round(duration, 4),
                "total_fee": value_fee(problem, final_state),
                "eta_score": eta_value(problem, final_state),
                "misplaced_urgent": count_misplaced_urgent(
                    problem, final_state
                ),
                "vehicles_loaded": sum(
                    1 for p in final_state if p[0] != -1
                )
            }

            detail = {
                **row,
                "initial_state": initial_state,
                "final_state": final_state,
                "history": result["history"]
            }

            if name == "sideways":
                detail["sideways_moves"] = result["sideways_moves"]

            if name == "random_restart":
                detail["restart_scores"] = result["restart_scores"]
                detail["restart_iterations"] = result["restart_iterations"]
                detail["all_histories"] = result["all_histories"]

            summary.append(row)
            details.append(detail)

            print(
                f'{name} | seed={seed} | '
                f'objective={objective} | '
                f'score={result["final_score"]} | '
                f'iterasi={result["iterations"]}'
            )

    return summary, details


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"File dataset tidak ditemukan: {DATA_PATH}"
        )

    problem = load_problem(DATA_PATH)

    for objective in ("fee", "eta"):
        print(f"\nMenjalankan eksperimen HC: {objective}")

        summary, details = run_experiments(
            problem,
            objective
        )

        if objective == "fee":
            output_dir = ROOT / "output" / "hc"
            filename = "hc"
        else:
            output_dir = ROOT / "output" / "bonus_eta"
            filename = "eta"

        save_csv(
            output_dir / f"hasil_{filename}.csv",
            summary
        )

        save_json(
            output_dir / f"detail_{filename}.json",
            details
        )

        print(f"Hasil tersimpan di {output_dir}")


if __name__ == "__main__":
    main()