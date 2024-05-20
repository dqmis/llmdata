import os
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from generators.utils import create_directory, export_problems
from solvers.clingo_solver import ClingoSolver

COLOURS = ["red", "blue", "green", "yellow", "purple", "orange"]
MAX_NODES = len(COLOURS)


def generate_coloring_facts(node_colors: list[str]):
    asp = "% Defining colored node facts\n"
    asp_coloring_rule = ""
    for i, color in enumerate(node_colors):
        if color == "grey":
            asp_coloring_rule = f"""
                % Ensure the grey node (node {i})is assigned exactly one color
                1 {{ coloring({i},Color) : color(Color) }} 1.
                % Define the answer as the color of the grey node
                answer(Color) :- coloring({i},Color).

                % Output the final answer
                #show answer/1.

                """
        else:
            asp += f"coloring({i},{color}).\n"
    asp += asp_coloring_rule

    return asp


def _generate_connected_graph(max_nodes: int) -> nx.Graph:
    n = random.randint(5, max_nodes)
    G = nx.Graph()
    G.add_nodes_from(range(n))

    nodes = list(G.nodes())
    random.shuffle(nodes)

    for i in range(n - 1):
        G.add_edge(nodes[i], nodes[i + 1])

    for i in range(n):
        for j in range(i + 1, n):
            if not G.has_edge(i, j) and random.random() < 0.3:
                G.add_edge(i, j)

    return G


def assign_colors_to_graph(graph: nx.Graph) -> tuple[list[str], list[str]]:
    color_map = nx.coloring.greedy_color(graph, strategy="largest_first")

    # Convert color assignments to a list of node colors
    color_palette = COLOURS

    node_colors = [color_palette[color_map[node]] for node in graph.nodes()]
    grey_node = random.choice(list(graph.nodes()))
    original_node_colors = node_colors.copy()
    node_colors[grey_node] = "grey"

    return node_colors, original_node_colors


def generate_fill_in_connected_graphs(
    max_nodes: int, n_samples: int = 10
) -> tuple[list[nx.Graph], list[list[str]], list[list[str]]]:
    graphs: list[nx.Graph] = []
    original_node_colors_list = []
    node_colors_list = []

    while len(graphs) < n_samples:
        G = _generate_connected_graph(max_nodes)

        node_colors, original_node_colors = assign_colors_to_graph(G)
        if len(set(original_node_colors)) < 4:
            continue
        asp = get_fill_in_asp(G, set(original_node_colors), node_colors)
        # There are more than one possible solutions
        if ClingoSolver.get_models_count(asp) > 1:
            continue
        else:
            node_colors_list.append(node_colors)
            original_node_colors_list.append(original_node_colors)
            graphs.append(G)

    return graphs, node_colors_list, original_node_colors_list


def generate_validity_graphs(max_nodes: int, n_samples: int = 10) -> tuple[
    list[nx.Graph],
    list[str],
    list[list[str]],
    list[nx.Graph],
    list[str],
    list[list[str]],
]:
    valid_graphs: list[nx.Graph] = []
    invalid_graphs: list[nx.Graph] = []

    valid_asp: list[str] = []
    invalid_asp: list[str] = []

    valid_color_choices: list[list[str]] = []
    invalid_color_choices: list[list[str]] = []

    while len(valid_graphs) < n_samples or len(invalid_graphs) < n_samples:
        G = _generate_connected_graph(max_nodes)
        asp, color_choices = generate_validity_asp(G)
        if ClingoSolver.solve(asp):
            if len(valid_graphs) >= n_samples:
                continue

            valid_graphs.append(G)
            valid_asp.append(asp)
            valid_color_choices.append(color_choices)
        else:
            if len(invalid_graphs) >= n_samples:
                continue

            invalid_graphs.append(G)
            invalid_asp.append(asp)
            invalid_color_choices.append(color_choices)

    return (
        valid_graphs,
        valid_asp,
        valid_color_choices,
        invalid_graphs,
        invalid_asp,
        invalid_color_choices,
    )


def visualize_graph(G, node_colors: list[str] | None = None) -> plt.Figure:
    fig = plt.figure(figsize=(5, 5))
    pos = nx.spring_layout(G)  # positions for all nodes
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors or "grey",
        node_size=900,
        edge_color="black",
        width=3,
    )

    return fig


def generate_asp_facts(G):
    nodes = list(G.nodes())
    edges = list(G.edges())

    asp_facts = "% Define the nodes and edges in the graph\n"

    for node in nodes:
        asp_facts += f"node({node}).\n"

    for edge in edges:
        asp_facts += f"edge({edge[0]}, {edge[1]}).\n"

    return asp_facts


def generate_validity_asp(graph: nx.Graph) -> tuple[str, list[str]]:
    asp = base_asp()
    color_facts, color_choices = generate_color_facts(graph.nodes.__len__())
    asp_facts = generate_asp_facts(graph)

    asp_code = asp + color_facts + asp_facts
    asp_code = asp_code.replace("    ", "")

    return asp_code, color_choices


def generate_color_facts(
    nodes_count: int, color_choices: list[str] | None = None
) -> tuple[str, list[str]]:
    color_facts = "% Define predefined colorings for specific nodes\n"
    if not color_choices:
        number_of_colors = random.randint(2, nodes_count)
        color_choices = random.sample(COLOURS, number_of_colors)
    for color in color_choices:
        color_facts += f"color({color}).\n"

    color_facts += "\n"
    return color_facts, color_choices


def base_asp():
    return """
    % Allocate exactly one color to each node
    % This rule ensures that each node is assigned exactly one color
    1{coloring(Node, Color): color(Color)}1 :- node(Node).

    % Constraint to prevent two connected nodes (i.e., nodes connected by an edge) from having the same color
    % This ensures that any valid coloring does not assign the same color to adjacent nodes
    :- edge(Node1, Node2), coloring(Node1, Color), coloring(Node2, Color).

    """


def generate_fill_in_options(
    node_colors: list[str], original_node_colors: list[str]
) -> tuple[list[str], str]:
    idx_of_replaced_color = node_colors.index("grey")
    answer_color = original_node_colors[idx_of_replaced_color]
    options = list(set(original_node_colors) - set([answer_color]))
    if len(options) > 3:
        options = random.sample(options, 3)
    options.append(answer_color)

    np.random.shuffle(options)
    formatted_options = [f"{chr(65 + i)}) {options[i]}" for i in range(4)]
    correct_option = chr(65 + options.index(answer_color))

    return formatted_options, correct_option


def get_fill_in_asp(
    graph: nx.Graph, original_colors: set[str], node_colors: list[str]
) -> str:
    asp = base_asp()
    color_facts, _ = generate_color_facts(graph.nodes.__len__(), original_colors)
    coloring_facts = generate_coloring_facts(node_colors)
    asp_facts = generate_asp_facts(graph)

    asp_code = asp + color_facts + asp_facts + coloring_facts
    asp_code = asp_code.replace("    ", "")

    return asp_code


def format_fill_in_problem(
    graphs: list[nx.Graph],
    node_colors_list: list[list[str]] | None = None,
    original_colors_list: list[list[str]] | None = None,
):
    problems = []

    for i, graph in enumerate(graphs):
        node_colors, original_node_colors = (
            node_colors_list[i],
            original_colors_list[i],
        )
        image = visualize_graph(graph, node_colors)
        asp_program = get_fill_in_asp(graph, set(original_node_colors), node_colors)
        options, answer = generate_fill_in_options(node_colors, original_node_colors)
        problems.append(
            {
                "question": "You have a picture of a graph with multiple nodes connected by edges. Each node has a specific color, except for one. Given that no two connected nodes can have the same color, can you determine what color the uncolored (grey) node should be? Give me a letter of a valid answer.",
                "options": options,
                "answer": answer,
                "asp": asp_program,
                "image": image,
            }
        )

    return problems


def _generate_valid_options(valid: bool) -> tuple[list[str], str]:
    options = ["Yes", "No"]
    np.random.shuffle(options)
    formatted_options = [f"{chr(65 + i)}) {options[i]}" for i in range(2)]
    correct_option = chr(65 + options.index("Yes" if valid else "No"))
    return formatted_options, correct_option


def format_validity_problem(
    graphs: list[nx.Graph],
    asp_programs: list[str],
    color_choices: list[list[str]],
    valid: bool = True,
):
    problems = []

    QUESTION = "You have a picture of a graph with multiple nodes connected by edges. Currently all nodes are grey color. Each node has to have a specific color assigned to each. Given that no two connected nodes can have the same color, can you determine if with given set of colors you can color each node so it would not break the ruleYou have a picture of a graph with multiple nodes connected by edges. Currently, all nodes are grey. Each node needs to be assigned a specific color. Given that no two connected nodes can share the same color, can you determine whether it is possible to color the graph according to this rule with the given set of colors? Give me a letter of a valid answer."

    for i, graph in enumerate(graphs):
        asp_program = asp_programs[i]
        color_choice = color_choices[i]

        image = visualize_graph(graph)
        options, answer = _generate_valid_options(valid)
        problems.append(
            {
                "question": QUESTION
                + "\nAvailable colors:\n"
                + ", ".join(color_choice),
                "color_choices": color_choice,
                "options": options,
                "answer": answer,
                "asp": asp_program,
                "image": image,
            }
        )

    return problems


def _remove_color_choices_from_problems(problems: list[dict]) -> list[dict]:
    for problem in problems:
        del problem["color_choices"]
    return problems


def export_data(root_dir: str, n_samples: str, fill_in: bool = False):
    _dirname = os.path.dirname(__file__)

    create_directory(root_dir)
    if not fill_in:
        data_dir = os.path.join(root_dir, "graph_validity")
        create_directory(data_dir)

        (
            valid_graphs,
            valid_asp,
            valid_color_choices,
            invalid_graphs,
            invalid_asp,
            invalid_color_choices,
        ) = generate_validity_graphs(MAX_NODES, n_samples + 1)

        valid_problems = format_validity_problem(
            valid_graphs, valid_asp, valid_color_choices, valid=True
        )
        invalid_problems = format_validity_problem(
            invalid_graphs, invalid_asp, invalid_color_choices, valid=False
        )
        valid_problem_sample = valid_problems.pop()
        invalid_problem_sample = invalid_problems.pop()

        problems = valid_problems + invalid_problems
        np.random.shuffle(problems)

        with open(
            os.path.join(_dirname, "prompt_templates/graph_validity.txt"), "r"
        ) as f:
            prompt_template = f.read()

        valid_prompt_template = prompt_template.replace(
            "[[ASP]]", valid_problem_sample["asp"]
        )
        invalid_prompt_template = prompt_template.replace(
            "[[ASP]]", invalid_problem_sample["asp"]
        )
        valid_prompt_template = valid_prompt_template.replace(
            "[[COLORS]]", ", ".join(valid_problem_sample["color_choices"])
        )
        invalid_prompt_template = invalid_prompt_template.replace(
            "[[COLORS]]", ", ".join(invalid_problem_sample["color_choices"])
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

        problems = _remove_color_choices_from_problems(problems)
        export_problems(problems, data_dir)

    else:
        data_dir = os.path.join(root_dir, "graph_fill_in")
        create_directory(data_dir)

        graphs, node_colors_list, original_colors_list = (
            generate_fill_in_connected_graphs(MAX_NODES, n_samples + 1)
        )
        fill_in_problems = format_fill_in_problem(
            graphs, node_colors_list, original_colors_list
        )
        sample_fill_in_problem = fill_in_problems.pop()
        with open(
            os.path.join(_dirname, "prompt_templates/graph_fill_in.txt"), "r"
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
