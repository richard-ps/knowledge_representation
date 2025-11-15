"""
SAT Assignment Part 2 - Non-consecutive Sudoku Solver (Puzzle -> SAT/UNSAT)

THIS is the file to edit.

Implement: solve_cnf(clauses) -> (status, model_or_None)"""


from typing import Iterable, List, Tuple

def solve_cnf(clauses: Iterable[Iterable[int]], num_vars: int) -> Tuple[str, List[int] | None]:
    """
    Implement your SAT solver here.
    Must return:
      ("SAT", model)  where model is a list of ints (DIMACS-style), or
      ("UNSAT", None)
    """
    return dpll_recursive(clauses)

def dpll_recursive(clauses, model=set()):
    
    # Simplification Steps
    # Remove Tautologies
    clauses = remove_tautologies(clauses)
    # Unit Propagation
    clauses, model = unit_propagation(clauses, model)
    
    if clauses is None:
        return "UNSAT", None
    
    # Pure Literal Elimination
    clauses, model = pure_literal_elimination(clauses, model)

     # SAT
    if clauses == []:
        return "SAT", model
    
    # UNSAT
    if is_empty(clauses):
        return "UNSAT", None
    
    # Branching Step
    literal = branching_step(clauses, model)
    # literal = maximum_occurence_minimal(clauses, 3)
    
    model.add(literal)
    
    sat, model2 = dpll_recursive(clauses , model)

    if sat == "SAT":
        return "SAT", sorted(model2)
    else:
        model.remove(literal)
        model.add(-literal)
        sat, model = dpll_recursive(clauses , model)
        if sat == "SAT":
            return "SAT", model
        else:
            print("UNSAT reached")
            # model.remove(-literal)
            return "UNSAT", None

def unit_propagation(clauses, model):
    unit_clauses = [clause for clause in clauses if len(clause) == 1]

    for clause in unit_clauses:
        literal = clause[0]

        if -literal in model:
            return None, model
        
        model.add(literal)
        clauses = remove_literal(clauses, literal)

    for literal in model:
        for clause in clauses:
            if literal in clause:
                clauses = remove_literal(clauses, literal)
    
    return clauses, model

# MOM's (Maximum Occurrence in clauses of Minimum Size)
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
    for clause in clauses:
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
        x_prime = count_x_prime.get(literal, 0)
        f_x = (x + x_prime)*2^k + x * x_prime
        if f_x > max_f:
            max_f = f_x
            max_literal = literal
    
    return max_literal

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
        
    return max_literal
            
def remove_tautologies(clauses):
    for clause in clauses:
        if len(clause) == 2:
            if clause[0] == -clause[1]:
                clauses.remove(clause)
    
    return clauses

def remove_literal(clauses, literal):
    new_clauses = []

    for clause in clauses:
        if literal not in clause and -literal not in clause:
            new_clauses.append(clause)
        if -1*literal in clause:
            new_clause = [lit for lit in clause if lit != -literal]
            # if new_clause != []:
            new_clauses.append(new_clause)
        
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

def is_empty(clauses):
    for clause in clauses:
        if clause == []:
            return True
    return False
