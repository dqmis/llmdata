from generators.graph import export_data as export_graph_data
from generators.set_cards import export_data as export_set_data
from generators.sudoku import export_data as export_sudoku_data

N_SAMPLES = 200
ROOT_DIR = "./data"

if __name__ == "__main__":
    print("Exporting data...")

    print("Exporting Sudoku data...")
    export_sudoku_data(ROOT_DIR, N_SAMPLES, fill_in=False)
    export_sudoku_data(ROOT_DIR, N_SAMPLES, fill_in=True)

    print("Exporting Graph data...")
    export_graph_data(ROOT_DIR, N_SAMPLES, fill_in=False)
    export_graph_data(ROOT_DIR, N_SAMPLES, fill_in=True)

    print("Exporting SET data...")
    export_set_data(ROOT_DIR, N_SAMPLES)

    print("Data exported successfully!")
