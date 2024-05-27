import clingo


class ClingoSolver:
    @staticmethod
    def _check_satisfied(control: clingo.Control) -> bool:
        with control.solve(yield_=True) as handle:
            if handle.get().satisfiable:
                return True
            return False

    @staticmethod
    def _get_answer(control: clingo.Control) -> int:
        with control.solve(yield_=True) as handle:
            if handle.get().satisfiable:
                for model in handle:
                    for atom in model.symbols(atoms=True):
                        if atom.name == "answer":
                            return atom.arguments[0]

    @staticmethod
    def get_models_count(asp_program: str) -> int:
        control = clingo.Control()
        control.add("base", [], asp_program)
        control.ground([("base", [])])
        control.configuration.solve.models = 0

        with control.solve(yield_=True) as handle:
            return len(list(handle))

    @staticmethod
    def solve(asp_program: str, check_satisfied: bool = True) -> bool:
        control = clingo.Control()
        control.add("base", [], asp_program)
        control.ground([("base", [])])
        control.configuration.solve.models = 0

        if check_satisfied:
            return ClingoSolver._check_satisfied(control)
        return ClingoSolver._get_answer(control)
