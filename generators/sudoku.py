import os

import matplotlib.pyplot as plt
import numpy as np
import sudokum

from generators.utils import create_directory, export_problems
from solvers.clingo_solver import ClingoSolver


def get_base_asp() -> str:
    return """
    % Define the domain for the Sudoku problem
    % x and y are the coordinates (rows and columns) ranging from 1 to 9
    x(1..9).
    y(1..9).

    % n represents the possible values for each cell, ranging from 1 to 9
    n(1..9).

    % Each cell (X, Y) must have exactly one value N from 1 to 9
    % This rule ensures that for each (X, Y) pair, there is exactly one N such that sudoku(X,Y,N) holds true
    {sudoku(X,Y,N) : n(N)}=1 :- x(X), y(Y).

    % Define a predicate to represent cells that belong to the same 3x3 subgrid
    % subgrid(X,Y,A,B) is true if cells (X,Y) and (A,B) are in the same subgrid
    subgrid(X,Y,A,B) :- x(X), x(A), y(Y), y(B), (X-1)/3 == (A-1)/3, (Y-1)/3 == (B-1)/3.

    % Constraints to ensure the validity of the Sudoku solution

    % Constraint ensuring no two cells in the same row (Y) have the same value (N)
    :- sudoku(X,Y,N), sudoku(A,Y,N), X != A.

    % Constraint ensuring no two cells in the same column (X) have the same value (N)
    :- sudoku(X,Y,N), sudoku(X,B,N), Y != B.

    % Constraint ensuring no two cells in the same 3x3 subgrid have the same value (V)
    :- sudoku(X,Y,V), sudoku(A,B,V), subgrid(X,Y,A,B), X != A, Y != B.

    """


def get_find_missing_asp(x: int, y: int) -> str:
    return f"""
    % Find the missing number in cell ({x},{y})
    1 {{ sudoku({x},{y},N) : n(N) }} 1.

    % Define the answer predicate to store the missing number
    answer(N) :- sudoku({x},{y},N).
    #show answer/1.
    """


def generate_valid_sudoku() -> list[list[int]]:
    while True:
        grid = sudokum.generate(mask_rate=0.0)
        sudoku_valid, _ = sudokum.check(grid)
        if sudoku_valid:
            return grid


def generate_invalid_sudoku() -> list[list[int]]:
    while True:
        grid = sudokum.generate(mask_rate=0.0)
        grid = np.array(grid)
        grid[np.random.randint(9), np.random.randint(9)] = np.random.randint(1, 10)
        grid = grid.tolist()
        sudoku_valid, _ = sudokum.check(grid)
        if not sudoku_valid:
            return grid


def generate_sudoku(valid: bool = True) -> list[list[int]]:
    return generate_valid_sudoku() if valid else generate_invalid_sudoku()


def visualize_sudoku(sudoku: np.ndarray) -> plt.Axes:
    _, ax = plt.subplots(figsize=(6, 6))

    # Wall color
    ax.set_facecolor("white")

    # Disable default grid lines
    ax.grid(False)

    # Draw the thinner lines for individual cells
    for i in range(10):
        lw = 2 if i % 3 == 0 else 0.5
        ax.plot([0, 9], [i, i], color="black", linewidth=lw)
        ax.plot([i, i], [0, 9], color="black", linewidth=lw)

    # Remove the axis labels (numbers on the axes)
    ax.set_xticks([])
    ax.set_yticks([])

    # Plot the numbers
    for i in range(9):
        for j in range(9):
            number = sudoku[i][j]
            if number != 0:
                ax.text(
                    j + 0.5, i + 0.5, str(number), va="center", ha="center", fontsize=20
                )
            # else fill the cell with blue color
            else:
                ax.fill([j, j + 1, j + 1, j], [i, i, i + 1, i + 1], "red")

    plt.axis("equal")
    return ax


def sudoku_grid_to_asp(sudoku_grid: np.ndarray) -> str:
    asp = "% Defining the initial Sudoku grid\n"
    for i in range(9):
        for j in range(9):
            if sudoku_grid[i, j] != 0:
                asp += f"sudoku({i + 1},{j + 1},{sudoku_grid[i, j]}). "
    return asp


def get_missing_asp(sudoku_grid: np.ndarray) -> str:
    missing_asp = ""
    for i in range(1, 10):
        for j in range(1, 10):
            if sudoku_grid[i - 1, j - 1] == 0:
                missing_asp += get_find_missing_asp(i, j)
    return missing_asp


def get_asp_for_sudoku(sudoku_grid: np.ndarray) -> str:
    asp_code = get_base_asp() + sudoku_grid_to_asp(sudoku_grid)
    if np.count_nonzero(sudoku_grid) < 81:
        asp_code += get_missing_asp(sudoku_grid)

    asp_code = asp_code.replace("    ", "")

    return asp_code


def generate_data(n_valid: int, n_invalid: int):
    valid_data = []
    invalid_data = []
    while len(valid_data) < n_valid:
        sudoku = generate_sudoku(valid=True)
        if sudoku not in valid_data:
            valid_data.append(sudoku)

    while len(invalid_data) < n_valid:
        sudoku = generate_sudoku(valid=False)
        if sudoku not in invalid_data:
            invalid_data.append(sudoku)

    return valid_data, invalid_data


def _generate_fill_in_options(missing_number: int) -> str:
    # generate_random three numbers that are not the missing number in range 1-9
    options = np.random.choice(
        [i for i in range(1, 10) if i != missing_number], 3, replace=False
    ).tolist()
    options.append(missing_number)
    # shuffle the options
    np.random.shuffle(options)
    formatted_options = [f"{chr(65 + i)}) {options[i]}" for i in range(4)]
    correct_option = chr(65 + options.index(missing_number))
    return formatted_options, correct_option


def _generate_valid_options(valid: bool) -> tuple[list[str], str]:
    options = ["Yes", "No"]
    np.random.shuffle(options)
    formatted_options = [f"{chr(65 + i)}) {options[i]}" for i in range(2)]
    correct_option = chr(65 + options.index("Yes" if valid else "No"))
    return formatted_options, correct_option


def format_sudoku_problem(
    sudokus: list[np.ndarray],
    problem_type: str,
    missing_numbers: list[int] = None,
    sudoku_is_valid: bool = True,
) -> dict:
    QUESTIONS = {
        "validity": "Here you have a picture of a solved sudoku board. Can you tell me if it is valid? Give me a letter of a valid answer.",
        "fill_in": "Here you have a picture of a sudoku board with one number missing, marked red color. Can you say what number is missing? Give me a letter of a valid answer.",
    }

    problems = []

    for i, sudoku in enumerate(sudokus):
        if problem_type == "validity":
            options, answer = _generate_valid_options(sudoku_is_valid)
        else:
            missing_number = missing_numbers[i]
            options, answer = _generate_fill_in_options(missing_number)

        problems.append(
            {
                "question": QUESTIONS[problem_type],
                "options": options,
                "answer": answer,
                "asp": get_asp_for_sudoku(np.array(sudoku)),
                "image": visualize_sudoku(sudoku).get_figure(),
            }
        )
    return problems


def remove_numbers(sudoku: np.ndarray, n: int) -> np.ndarray:
    sudoku = sudoku.copy()
    for _ in range(n):
        i, j = np.random.randint(9), np.random.randint(9)
        sudoku[i, j] = 0
    return sudoku


def _remove_random_number(sudoku: np.ndarray) -> tuple[np.ndarray, int]:
    sudoku = sudoku.copy()
    i, j = np.random.randint(9), np.random.randint(9)
    original_value = sudoku[i, j]
    sudoku[i, j] = 0
    return sudoku, original_value


def export_data(root_dir: str, n_samples: int, fill_in: bool = False):
    _dirname = os.path.dirname(__file__)

    create_directory(root_dir)

    if not fill_in:
        data_dir = os.path.join(root_dir, "sudoku_validity")
        create_directory(data_dir)

        valid_data, invalid_data = generate_data(n_samples + 1, n_samples + 1)
        valid_problems = format_sudoku_problem(
            valid_data, "validity", sudoku_is_valid=True
        )
        invalid_problems = format_sudoku_problem(
            invalid_data, "validity", sudoku_is_valid=False
        )
        valid_problem_sample = valid_problems.pop()
        invalid_problem_sample = invalid_problems.pop()

        all_problems = valid_problems + invalid_problems
        np.random.shuffle(all_problems)

        with open(
            os.path.join(_dirname, "prompt_templates/sudoku_validity.txt"), "r"
        ) as f:
            prompt_template = f.read()

        valid_prompt_template = prompt_template.replace(
            "[[ASP]]", valid_problem_sample["asp"]
        )
        invalid_prompt_template = prompt_template.replace(
            "[[ASP]]", invalid_problem_sample["asp"]
        )

        with open(os.path.join(data_dir, "valid_prompt_template.txt"), "w") as f:
            f.write(valid_prompt_template)

        with open(os.path.join(data_dir, "invalid_prompt_template.txt"), "w") as f:
            f.write(invalid_prompt_template)

        valid_problem_sample["image"].savefig(
            os.path.join(data_dir, "valid_prompt.png")
        )
        invalid_problem_sample["image"].savefig(
            os.path.join(data_dir, "invalid_prompt.png")
        )

        export_problems(all_problems, data_dir)

    else:
        data_dir = os.path.join(root_dir, "sudoku_fill_in")
        create_directory(data_dir)

        valid_data, _ = generate_data(n_samples + 1, 0)
        removed_numbers_data = []
        removed_numbers = []
        for i, sudoku in enumerate(valid_data):
            while True:
                data, removed_number = _remove_random_number(np.array(sudoku))
                asp = get_asp_for_sudoku(data)
                if ClingoSolver.get_models_count(asp) == 1:
                    break
            removed_numbers_data.append(data)
            removed_numbers.append(removed_number)

        fill_in_problems = format_sudoku_problem(
            removed_numbers_data, "fill_in", missing_numbers=removed_numbers
        )

        sample_fill_in_problem = fill_in_problems.pop()
        with open(
            os.path.join(_dirname, "prompt_templates/sudoku_fill_in.txt"), "r"
        ) as f:
            prompt_template = f.read()

        prompt_template = prompt_template.replace(
            "[[ASP]]", sample_fill_in_problem["asp"]
        )
        prompt_template = prompt_template.replace(
            "[[OPTIONS]]", "\n".join(sample_fill_in_problem["options"])
        )
        with open(os.path.join(data_dir, "prompt_template.txt"), "w") as f:
            f.write(prompt_template)

        sample_fill_in_problem["image"].savefig(
            os.path.join(data_dir, "sample_prompt.png")
        )

        export_problems(fill_in_problems, data_dir)
