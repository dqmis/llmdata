"""
Generating images with SET cards. Uses the `abstractor` repository.
The code is adapted from the notebook file
`experiments/set/set_classification.ipynb` within this repository.
"""

import copy
import os
import random

import matplotlib.pyplot as plt
import numpy as np

from generators.set_game.set_game import SetGame

np.random.seed(0)
random.seed(0)

from generators.utils import create_directory, export_problems
from solvers.clingo_solver import ClingoSolver

"""
Adds the card attributes from the txt files to a template
Answer Set Programming (ASP) file.
"""


# Constants to denote the card attributes
NUMBER = "number"
SHAPE = "shape"
COLOR = "color"
SHADING = "shading"


NUM_CARDS = 4
NUM_ROWS = 2
NUM_COLS = int(np.ceil(NUM_CARDS / NUM_ROWS))


def create_asp_file(
    cards,
    input_use_numerical_numbers=False,
    output_use_numerical_numbers=False,
    card_proposition="card_in_play",
    input_order=[NUMBER, COLOR, SHADING, SHAPE],
    output_order=[NUMBER, COLOR, SHADING, SHAPE],
):
    """
        Creates an ASP file with the card attributes from the input list of cards.
    s
        Parameters
        ----------
        cards : list of str
            List of strings with the card attributes. Each string should have the
            format following `input_order`

        input_use_numerical_numbers : bool
            If True, the input cards use numerical numbers.

        output_use_numerical_numbers : bool
            If True, the output cards use numerical numbers.

        card_proposition : str
            Name of the card proposition.

        input_order : list of str (using the constants NUMBER, COLOR, SHAPE, SHADING)
            Order of the card attributes in the input.

        output_order : list of str (using the constants NUMBER, COLOR, SHAPE, SHADING)
            Order of the card attributes in the output.


        Returns a list of strings which can be written to a .asp file.
    """
    strings = ["% Defining all possible numbers, shapes, colors, and shadings."]

    if output_use_numerical_numbers:
        strings.append("number(1; 2; 3).")
    else:
        strings.append("number(one; two; three).")

    strings.append("shape(oval; squiggle; diamond).")
    strings.append("color(red; green; purple).")
    strings.append("shading(solid; striped; empty).")
    strings.append("\n")

    strings.append("% Defining the card ids.")
    strings.append(f"card_id(1..{NUM_CARDS}).")

    capital_props = [name.capitalize() for name in output_order]
    propositions = ", ".join(
        ["card_id(Id)"]
        + [f"{name}({cname})" for name, cname in zip(output_order, capital_props)]
    )
    string_capitals = ", ".join(["Id"] + capital_props)
    strings.append(
        "% Defining the card object. Card has number of objects, shape, color, and shading."
    )
    strings.append(f"card(C) :- {propositions}, C = ({string_capitals}).")

    # String of variables for the card attributes, e.g. "Number1, Shape1, Color1, Shading1".
    # The order can be changed based on `output_order`.
    capital_variables = lambda i: ", ".join(
        ["_"] + [name + str(i) for name in capital_props]
    )

    strings.append(
        f"""
    % All cards in a set must have the same number or all different numbers.
    all_same_or_all_different(A, B, C) :- A = B, B = C, number(A), number(B), number(C).
    all_same_or_all_different(A, B, C) :- A < B < C, number(A), number(B), number(C).

    % All cards in a set must have the same shape or all different shapes.
    all_same_or_all_different(A, B, C) :- A = B, B = C, shape(A), shape(B), shape(C).
    all_same_or_all_different(A, B, C) :- A != B, A != C, B != C, shape(A), shape(B), shape(C).

    % All cards in a set must have the same color or all different colors.
    all_same_or_all_different(A, B, C) :- A = B, B = C, color(A), color(B), color(C).
    all_same_or_all_different(A, B, C) :- A != B, A != C, B != C, color(A), color(B), color(C).

    % All cards in a set must have the same shading or all different shadings.
    all_same_or_all_different(A, B, C) :- A = B, B = C, shading(A), shading(B), shading(C).
    all_same_or_all_different(A, B, C) :- A != B, A != C, B != C, shading(A), shading(B), shading(C).

    % A set is valid if the cards have the same number or all different numbers, the same shape or all different shapes,
    % the same color or all different colors, and the same shading or all different shadings.
    valid_set(C1, C2, C3) :-
        card(C1), card(C2), card(C3), C1 != C2, C1 != C3, C2 != C3,
        C1 = ({capital_variables(1)}),
        C2 = ({capital_variables(2)}),
        C3 = ({capital_variables(3)}),
        all_same_or_all_different(Number1, Number2, Number3),
        all_same_or_all_different(Shape1, Shape2, Shape3),
        all_same_or_all_different(Color1, Color2, Color3),
        all_same_or_all_different(Shading1, Shading2, Shading3).

    % A set is valid if the cards have the same number or all different numbers, the same shape or all different shapes,
    valid_set_in_play(C1, C2, C3) :-
        {card_proposition}(C1), {card_proposition}(C2), {card_proposition}(C3),
        valid_set(C1, C2, C3).

    """
    )

    strings.append("% The cards in play.")

    # Change the input's order and names of the attributes
    for id, card in enumerate(cards):
        if input_use_numerical_numbers != output_use_numerical_numbers:
            from_list = (
                ["1", "2", "3"]
                if input_use_numerical_numbers
                else ["one", "two", "three"]
            )
            to_list = (
                ["1", "2", "3"]
                if output_use_numerical_numbers
                else ["one", "two", "three"]
            )
            # Switch text and numerical numbers
            for f, t in zip(from_list, to_list):
                card = card.replace(f, t)

        # Change the order of the card attributes to match with the card proposition.
        attrs = card.replace("(", "").replace(")", "").replace(" ", "").split(",")

        index_mapping = {element: idx for idx, element in enumerate(input_order)}
        indices = [index_mapping[element] for element in output_order]

        ordered_card = [attrs[index] for index in indices]
        ordered_card.insert(0, str(id + 1))

        string_card = ", ".join(ordered_card).replace("'", "")

        strings.append(f"{card_proposition}(({string_card})).")

    strings.append("\n")
    strings.append("% The set is valid if there is a valid set in play. \n")
    strings.append(":- not valid_set_in_play(_, _, _).")

    return "\n".join(strings)


def generate_asp(setgame) -> str:
    hand = setgame.state.dealt_cards
    cards = [str(setgame.attributes_of_card(*card)) for card in hand]

    asp = create_asp_file(cards)
    asp = asp.replace("    ", "")
    return asp


def generate_image(setgame) -> plt.Figure:
    hand = setgame.state.dealt_cards

    fig, axarr = plt.subplots(nrows=NUM_ROWS, ncols=NUM_COLS)

    for i in range(len(hand)):
        card = hand[i]
        row = i // NUM_COLS
        col = i % NUM_COLS
        axarr[row, col].imshow(setgame.image_of_card(card[0], card[1]))
        axarr[row, col].axis("off")

    return fig


def duplicate_cards(setgame):
    _setgame = copy.deepcopy(setgame)
    current_state = _setgame.state.dealt_cards

    for i in range(random.randint(1, NUM_CARDS)):
        # randaomly duplicate a card and replace it with a new card
        card_to_duplicate = np.random.randint(0, NUM_CARDS)
        card_to_replace = random.choice(
            [i for i in range(NUM_CARDS) if i != card_to_duplicate]
        )
        new_card = _setgame.state.dealt_cards[card_to_duplicate]
        current_state[card_to_replace] = new_card

    return _setgame


def generate_games(valid: bool, n_samples: int):
    games = []

    while len(games) < n_samples:
        setgame = SetGame()
        _ = setgame.init_state(num_cards=NUM_CARDS, shuffle=True)
        if valid:
            games.append(setgame)
        else:
            _setgame = duplicate_cards(setgame)
            asp = generate_asp(_setgame)
            if not ClingoSolver.solve(asp):
                games.append(_setgame)

    return games


def _generate_valid_options(valid: bool) -> tuple[list[str], str]:
    options = ["Yes", "No"]
    np.random.shuffle(options)
    formatted_options = [f"{chr(65 + i)}) {options[i]}" for i in range(2)]
    correct_option = chr(65 + options.index("Yes" if valid else "No"))
    return formatted_options, correct_option


def format_problems(games, valid: bool) -> list[dict]:
    problems = []

    QUESTION = "You have a picture of SET card game deck. In the game, certain combinations of three cards are said to make up a "set". A set consists of three cards satisfying all of these conditions: they all have the same number or have three different numbers, shapes, shadings or colors. Can you tell if such set exists?"

    for game in games:
        asp = generate_asp(game)
        image = generate_image(game)
        options, answer = _generate_valid_options(valid)

        problems.append(
            {
                "question": QUESTION,
                "options": options,
                "answer": answer,
                "asp": asp,
                "image": image,
            }
        )

    return problems


def export_data(root_dir: str, n_samples: int):
    _dirname = os.path.dirname(__file__)
    create_directory(root_dir)

    data_dir = os.path.join(root_dir, "set_validity")
    create_directory(data_dir)

    valid_games = generate_games(valid=True, n_samples=n_samples + 1)
    invalid_games = generate_games(valid=False, n_samples=n_samples + 1)

    valid_problems = format_problems(valid_games, valid=True)
    invalid_problems = format_problems(invalid_games, valid=False)

    valid_problem_sample = valid_problems.pop()
    invalid_problem_sample = invalid_problems.pop()

    all_problems = valid_problems + invalid_problems
    np.random.shuffle(all_problems)

    with open(os.path.join(_dirname, "prompt_templates/set_validity.txt"), "r") as f:
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

    valid_problem_sample["image"].savefig(os.path.join(data_dir, "valid_prompt.png"))
    invalid_problem_sample["image"].savefig(
        os.path.join(data_dir, "invalid_prompt.png")
    )

    export_problems(all_problems, data_dir)

