import boards # https://github.com/possibly-wrong/dlx
import polygons
import numpy as np
from itertools import product, chain
import functools
from fractions import Fraction

rotations = {tuple(tuple(row) for row in np.array(a).dot(b).dot(c).tolist())
             for a, b, c in product(*(boards.matrix_powers(r, 4)
                                      for r in [boards.x, boards.y, boards.z]))}
neighborhood = {tuple(s * v) for v in np.eye(3, dtype='int') for s in (1, -1)}

def canonical(polycube):
    """Return polycube in canonical position and orientation."""
    views = set()
    for r in rotations:
        view = np.array([np.array(r).dot(x) for x in polycube])
        view = view - view.min(0) # flush with axes
        bound = min(view.tolist()) # guarantee origin is a cubie
        views.add(tuple(sorted(tuple(x - bound) for x in view)))
    return min(views)

def grow(polycube):
    """Return set of polycubes obtained by growing one cubie."""
    new = set()
    for x in polycube:
        for dx in neighborhood:
            neighbor = tuple(np.array(x) + dx)
            if neighbor not in polycube:
                new.add(canonical(polycube + (neighbor,)))
    return new

@functools.lru_cache(maxsize=None)
def polycubes(n):
    """Return set of polycubes with n cubies."""
    if n == 1:
        return {((0, 0, 0),)}
    return sorted(set().union(*(grow(polycube)
                                for polycube in polycubes(n - 1))))

def stable(polycube):
    """Return polycube oriented with lowest CG within supported base."""
    views = set()
    for r in rotations:
        view = np.array([np.array(r).dot(x) for x in polycube])
        view = view - view.min(0)
        cg = [Fraction(int(x), len(view)) + Fraction(1, 2) for x in sum(view)]
        support = polygons.convex_hull(chain.from_iterable(
            ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1))
            for x, y, z in view if z == 0))
        if polygons.in_polygon(cg, support):
            views.add((cg[2], tuple(sorted(tuple(x) for x in view))))
    return min(views, default=(None, None))[1]

def burr_piece(polycube):
    """Return polycube in PuzzleCAD/OpenSCAD format."""
    cols, rows, layers = np.array(polycube).max(0) + 1
    return ['|'.join(''.join(('x' if (x, y, z) in polycube else '.')
                             for x in range(cols)) for y in range(rows))
            for z in range(layers)]

if __name__ == '__main__':

    # Find all Soma Cube-like puzzles using distinct polycubes with 1 to 6
    # cubies.
    board = {(x, y, z) for x in range(3) for y in range(3) for z in range(3)}
    pieces = dict(enumerate(chain.from_iterable(polycubes(n)
                                                for n in range(1, 7))))
    (pairs, optional, rows) = boards.board_cover(board, pieces, rotations,
                                                 'pieces')
    with open('polycubes-rows.txt', 'w') as f:
        print(len(rows), file=f)
        for name, cubies in rows:
            print(name, str(cubies).replace(' ',''), file=f)
    with open('polycubes-puzzle.txt', 'w') as f:
        boards.print_cover((pairs, optional, rows), f)

    # Generate 3D-printable polycubes with 1 to 6 cubies.
    for n in range(1, 7):
        for polycube in polycubes(n):
            print('burr_piece({});'.format(
                str(burr_piece(stable(polycube))).replace("'", '"')))
