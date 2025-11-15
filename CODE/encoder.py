"""
SAT Assignment Part 1 - Non-consecutive Sudoku Encoder (Puzzle -> CNF)

THIS is the file to edit.

Implement: to_cnf(input_path) -> (clauses, num_vars)

You're required to use a variable mapping as follows:
    var(r,c,v) = r*N*N + c*N + v
where r,c are in range (0...N-1) and v in (1...N).

You must encode:
  (1) Exactly one value per cell
  (2) For each value v and each row r: exactly one column c has v
  (3) For each value v and each column c: exactly one row r has v
  (4) For each value v and each sqrt(N)×sqrt(N) box: exactly one cell has v
  (5) Non-consecutive: orthogonal neighbors cannot differ by 1
  (6) Clues: unit clauses for the given puzzle
"""


from typing import Tuple, Iterable
import math

def to_cnf(input_path: str) -> Tuple[Iterable[Iterable[int]], int]:
    """
    Read puzzle from input_path and return (clauses, num_vars).

    - clauses: iterable of iterables of ints (each clause), no trailing 0s
    - num_vars: must be N^3 with N = grid size
    """

    with open(input_path, 'r') as f:
        puzzle = [list(map(int, line.strip().split())) for line in f]

    # print("Puzzle:", puzzle)

    N = len(puzzle)
    num_vars = N * N * N

    clauses = []
    clauses += at_least_one(N)       # (1) At least one value per cell
    clauses += exactly_one_in_col(N) # (2) For each value v and each row r: exactly one column c has v
    clauses += exactly_one_in_row(N) # (3) For each value v and each column c: exactly one row r has v
    clauses += exactly_one_in_box(N) # (4) For each value v and each sqrt(N)×sqrt(N) box: exactly one cell has v
    clauses += non_consecutive(N)    # (5) Non-consecutive: orthogonal neighbors cannot differ by 1
    clauses += clues(puzzle, N)      # (6) Clues: unit clauses for the given puzzle
  
    #print("Clauses after (6):", len(clauses))
    # print("Clauses: ", clauses)

    return clauses, num_vars

# Helper function to map (r,c,v) to variable number
def var(r: int, c: int, v: int, N: int) -> int:
    return r * N * N + c * N + v

# (1) At least one value per cell
def at_least_one(N):
    clauses = []

    for x in range(N):
        for y in range(N):
            clause = []
            for v in range(1, N + 1):
                clause.append(var(x, y, v, N))
            clauses.append(clause)

    return clauses

# (2) For each value v and each row r: exactly one column c has v
def exactly_one_in_col(N):
    clauses = []

    for x in range(N):
        for z in range(1, N + 1):
            for y in range(N-1):
                for i in range(y+1, N):
                    clauses.append([-var(x, y, z, N), -var(x, i, z, N)])    

    return clauses

# (3) For each value v and each column c: exactly one row r has v
def exactly_one_in_row(N):
    clauses = []

    for y in range(N):
        for z in range(1, N + 1):
            for x in range(N-1):
                for i in range(x+1, N):
                    clauses.append([-var(x, y, z, N), -var(i, y, z, N)])    

    return clauses

# (4) For each value v and each sqrt(N)×sqrt(N) box: exactly one cell has v
def exactly_one_in_box(N):
    clauses = []
    b = math.isqrt(N)
    
    for z in range(1, N+1):
        for i in range(0, b):
            for j in range(0, b):
                for x in range(0, b):
                    for y in range(0, b):
                        for k in range(y+1, b):
                            clause = [-var(b*i+x, b*j+y, z, N), -var(b*i+x, b*j+k, z, N)]
                            clauses.append(clause)
                        for k in range(x+1, b):
                            for l in range(0, b):
                                clause = [-var(b*i+x, b*j+y, z, N), -var(b*i+k, b*j+l, z, N)]
                                clauses.append(clause)

    return clauses

# (5) Non-consecutive: orthogonal neighbors cannot differ by 1
def non_consecutive(N):
    clauses = []

    for x in range(N):
        for y in range(N):
            for dx in [-1, 1]:
                if 0 <= x + dx < N:
                    for v in range(1, N + 1):
                        if v + 1 <= N:
                            clauses.append([-var(x, y, v, N), -var(x + dx, y, v + 1, N)])
                        if v - 1 >= 1:
                            clauses.append([-var(x, y, v, N), -var(x + dx, y, v - 1, N)])
            for dy in [-1, 1]:
                if 0 <= y + dy < N:
                    for v in range(1, N + 1):
                        if v - 1 >= 1:
                            clauses.append([-var(x, y, v, N), -var(x, y + dy, v - 1, N)])
                        if v + 1 <= N:
                            clauses.append([-var(x, y, v, N), -var(x, y + dy, v + 1, N)])

    return clauses

# (6) Clues: unit clauses for the given puzzle
def clues(puzzle, N):
    clauses = []

    for r in range(N):
        for c in range(N):
            v = puzzle[r][c]
            if v != 0:
                clause = var(r, c, v, N)
                clauses.append([clause])

    return clauses