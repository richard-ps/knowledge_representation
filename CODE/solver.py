"""
SAT Assignment Part 2 - Non-consecutive Sudoku Solver (Puzzle -> SAT/UNSAT)

THIS is the file to edit.

Implement: solve_cnf(clauses) -> (status, model_or_None)"""


from typing import Iterable, List, Tuple
#from xml.parsers.expat import model

def solve_cnf(clauses: Iterable[Iterable[int]], num_vars: int) -> Tuple[str, List[int] | None]:
    """
    Implement your SAT solver here.
    Must return:
      ("SAT", model)  where model is a list of ints (DIMACS-style), or
      ("UNSAT", None)
    """
    # Convert to list of lists for proper manipulation
    clauses_list = [list(clause) for clause in clauses]
    return dpll_recursive(clauses_list)

def dpll_recursive(clauses, model=None):
    # Initialize model if None
    if model is None:
        model = set()

     # SAT
    if clauses == []:
        return "SAT", sorted(list(model))
    
    # UNSAT - check if any clause is empty
    if any(clause == [] for clause in clauses):
        return "UNSAT", None
    
    # Remove Tautologies
    clauses = remove_tautologies(clauses)
    # Unit Propagation
    clauses, model = unit_propagation(clauses, model)

    if clauses is None:
        return "UNSAT", None
    
    # Pure Literal Elimination
    clauses, model = pure_literal_elimination(clauses, model)
    
    # Check again after pure literal elimination
    if clauses == []:
        return "SAT", sorted(list(model))
    
    if any(clause == [] for clause in clauses):
        return "UNSAT", None
    
    # Branching Step
    # literal = branching_step(clauses, model)
    literal = maximum_occurence_minimal(clauses, 3)

    if literal is None:
        # No more literals to branch on
        # If clauses are empty, it's SAT, otherwise UNSAT
        if clauses == []:
            return "SAT", sorted(list(model))
        else:
            return "UNSAT", None

    # Try assigning literal to True
    model_copy = model.copy()
    model_copy.add(literal)
    # Simplify clauses with the assigned literal
    clauses_simplified = remove_literal(clauses, literal)
    sat, model2 = dpll_recursive(clauses_simplified, model_copy)

    if sat == "SAT":
        print("Found SAT by assigning literal:", literal)
        # Ensure model is returned as sorted list
        if isinstance(model2, set):
            return "SAT", sorted(list(model2))
        return "SAT", model2
    
    # Backtrack: try assigning literal to False
    print("Backtracking on literal:", literal)
    model_copy = model.copy()
    model_copy.add(-literal)
    # Simplify clauses with the negated literal
    clauses_simplified = remove_literal(clauses, -literal)
    sat, model3 = dpll_recursive(clauses_simplified, model_copy)
    if sat == "SAT":
        print("Found SAT by assigning literal:", -literal)
        # Ensure model is returned as sorted list
        if isinstance(model3, set):
            return "SAT", sorted(list(model3))
        return "SAT", model3
    else:
        return "UNSAT", None

def unit_propagation(clauses, model):
    # Repeat until no more unit clauses
    changed = True
    while changed:
        changed = False
        unit_clauses = [clause for clause in clauses if len(clause) == 1]
        
        for clause in unit_clauses:
            literal = clause[0]
            
            # Conflict detected
            if -literal in model:
                return None, None
            
            # Add unit literal to model if not already there
            if literal not in model:
                model.add(literal)
                clauses = remove_literal(clauses, literal)
                changed = True
                
                # Check for empty clause after simplification
                if any(c == [] for c in clauses):
                    return None, None
    
    return clauses, model

# DLCS (Dynamic Largest Combined Sum)
def branching_step(clauses, model):
    literals = set()
    max_sum = 0
    max_literal = None
    CP = {}
    CN = {}

    for clause in clauses:
        for literal in clause:
            literals.add(literal)
            if literal > 0:
                if literal not in CP:
                    CP[literal] = 1
                else:
                    CP[literal] += 1
            else:
                if literal not in CN:
                    CN[literal] = 1
                else:
                    CN[literal] += 1

    for literal in literals:
        CP_value = CP.get(literal, 0)
        CN_value = CN.get(literal, 0)
        combined_sum = CP_value + CN_value
        if combined_sum > max_sum:
            max_sum = combined_sum
            max_literal = literal

    print("Branching on literal:", max_literal)
    print("Max combined sum:", max_sum)
        
    return max_literal

def maximum_occurence_minimal(clauses, k):
    literals = set()
    count_x = {}
    count_x_prime = {}
    min_len = float("inf")
    max_f = float("-inf")
    max_literal = None
    min_clauses = []
    for clause in clauses:
        if len(clause) < min_len and len(clause) != 1:
            min_len = len(clause)
    for clause in clauses:
        if len(clause) == min_len:
            min_clauses.append(clause)
    if len(min_clauses) == 0 and min_len == float("inf"):
        min_clauses = clauses
    for clause in min_clauses:
        for literal in clause:
            literals.add(literal)
            if literal > 0:
                if literal not in count_x:
                    count_x[literal] = 1
                else:
                    count_x[literal] += 1
            else:
                if literal not in count_x_prime:
                    count_x_prime[literal] = 1
                else:
                    count_x_prime[literal] += 1
    for literal in literals:
        x = count_x.get(literal, 0)
        x_prime = count_x_prime.get(-literal, 0)  # Look for negation
        f_x = (x + x_prime)*2**k + x * x_prime
        if f_x > max_f:
            max_f = f_x
            max_literal = literal
    print("MOM's literal:", max_literal)
    print("max_function_value:", max_f)
    return max_literal


def remove_tautologies(clauses):
    # Don't modify list during iteration - create new list
    new_clauses = []
    for clause in clauses:
        # Check if clause contains both x and -x (tautology)
        is_tautology = False
        for lit in clause:
            if -lit in clause:
                is_tautology = True
                break
        if not is_tautology:
            new_clauses.append(clause)
    
    return new_clauses

def remove_literal(clauses, literal):
    new_clauses = []

    for clause in clauses:
        # If clause contains literal, it's satisfied - remove entire clause
        if literal in clause:
            continue
        # If clause contains -literal, remove -literal from clause
        elif -literal in clause:
            new_clause = [lit for lit in clause if lit != -literal]
            new_clauses.append(new_clause)
        # Otherwise, keep clause unchanged
        else:
            new_clauses.append(clause)
        
    return new_clauses

def pure_literal_elimination(clauses, model):
    literals = set()
    pure_literals = set()

    # Find all literals
    for clause in clauses:
        for literal in clause:
            literals.add(literal)

    # Find pure literals
    for literal in literals:
        if -literal not in literals:
            pure_literals.add(literal)

    # Remove pure literals from clauses and add to model
    for pure_literal in pure_literals:
        model.add(pure_literal)
        clauses = remove_literal(clauses, pure_literal)

    return clauses, model