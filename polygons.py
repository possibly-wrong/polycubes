from functools import reduce
from itertools import cycle, islice

def cross(p, q, r):
    """Return (+/0/-) if point r is (left/on/right) line from p to q."""
    return (q[0] - p[0]) * (r[1] - p[1]) - (r[0] - p[0]) * (q[1] - p[1])

def add_hull(hull, p):
    """Return modified hull stack adding point p in Graham scan."""
    while len(hull) > 1 and cross(hull[-2], hull[-1], p) <= 0:
        hull.pop()
    hull.append(p)
    return hull

def convex_hull(points):
    """Return convex hull of points in counterclockwise order."""
    points = sorted(set(tuple(p) for p in points))
    return (reduce(add_hull, points, [])[:-1] +
            reduce(add_hull, reversed(points), [])[:-1])

def in_polygon(p, polygon):
    """Return winding number, or 0 if point p is on polygon boundary."""
    winding = 0
    for v, w in zip(polygon, islice(cycle(polygon), 1, None)):
        if v[1] <= p[1]:
            if w[1] > p[1]:
                a = cross(v, w, p)
                if a > 0:
                    winding = winding + 1
                elif a == 0:
                    return 0
            elif v[1] == p[1] and (v[0] == p[0] or
                                   (p[1] == w[1] and v[0] <= p[0] <= w[0])):
                return 0
        else:
            if w[1] <= p[1]:
                a = cross(v, w, p)
                if a < 0:
                    winding = winding - 1
                elif a == 0:
                    return 0
    return winding
