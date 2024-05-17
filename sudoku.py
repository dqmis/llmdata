import os

import matplotlib.pyplot as plt
import numpy as np
import sudokum


def get_base_asp() -> str:
    return """
    x(1..9).
    y(1..9).
    n(1..9).

    {sudoku(X,Y,N): n(N)}=1 :- x(X) ,y(Y).

    subgrid(X,Y,A,B) :- x(X), x(A), y(Y), y(B),(X-1)/3 == (A-1)/3, (Y-1)/3 == (B-1)/3.

    :- sudoku(X,Y,N), sudoku(A,Y,N), X!=A.
    :- sudoku(X,Y,N), sudoku(X,B,N), Y!=B.
    :- sudoku(X,Y,V), sudoku(A,B,V), subgrid(X,Y,A,B), X != A, Y != B.

    """


def get_find_missing_asp(x: int, y: int) -> str:
    return f"""
    1 {{ sudoku({x},{y},N) : n(N) }} 1.
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


def plot_sudoku(sudoku: np.ndarray) -> plt.Axes:
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
    asp = ""
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

    return asp_code


def generate_data(n_valid: int, n_invalid: int):
    valid_data = []
    invalid_data = []
    while len(valid_data) < n_valid:
        sudoku = generate_sudoku(valid=True)
        if sudoku not in valid_data:
            valid_data.append(sudoku)

    while len(invalid_data) < n_valid + n_invalid:
        sudoku = generate_sudoku(valid=False)
        if sudoku not in invalid_data:
            invalid_data.append(sudoku)

    return valid_data, invalid_data


def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def save_sudoku_data(sudoku_data: list, root_dir: str, data_type: str):
    data_dir = os.path.join(root_dir, data_type)
    asp_dir = os.path.join(data_dir, "asp_code")
    images_dir = os.path.join(data_dir, "image")

    create_directory(data_dir)
    create_directory(asp_dir)
    create_directory(images_dir)

    data = []

    for i, sudoku in enumerate(sudoku_data):
        id = f"sudoku_{i}"
        {
            "id": id,
            "question": QUESTIONS["sudoku_valid"],
        }

        with open(os.path.join(asp_dir, f"{id}.asp"), "w") as f:
            f.write(get_asp_for_sudoku(np.array(sudoku)))

        plot_sudoku(sudoku).get_figure().savefig(os.path.join(images_dir, f"{id}.png"))


def remove_numbers(sudoku: np.ndarray, n: int) -> np.ndarray:
    sudoku = sudoku.copy()
    for _ in range(n):
        i, j = np.random.randint(9), np.random.randint(9)
        sudoku[i, j] = 0
    return sudoku


QUESTIONS = {
    "sudoku_valid": "Here you have a picture of a solved sudoku board. Can you tell me if it is valid? Give me a letter of a valid answer.",
    "missing_number": "Here you have a picture of a sudoku board with one number missing, marked red color. Can you say what number is missing by giving me a letter of a valid answer?",
}


def export_data(root_dir: str, n_samples: int, fill_in: bool = False):
    create_directory(root_dir)

    if not fill_in:
        valid_data, invalid_data = generate_data(n_samples, n_samples)

        save_sudoku_data(valid_data, root_dir, "valid")
        save_sudoku_data(invalid_data, root_dir, "invalid")
    else:
        valid_data, _ = generate_data(n_samples, 0)
        remove_numbers_data = [
            remove_numbers(np.array(sudoku), 1) for sudoku in valid_data
        ]
        save_sudoku_data(remove_numbers_data, root_dir, "fill_in")
