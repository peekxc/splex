import numpy as np 
from collections.abc import Collection
from splex import * 
from more_itertools import unique_everseen

def all_in(S1: Iterable, S2: Collection) -> bool:
  return all([s in S2 for s in S1])

def test_faces():
  assert list(faces([0,1,2])) == [Simplex([0]), Simplex([1]), Simplex([2]), Simplex((0, 1)), Simplex((0, 2)), Simplex((1, 2)), Simplex((0, 1, 2))]
  assert list(faces([0,1], data=True)) == [(Simplex([0]), {}), (Simplex([1]), {}), (Simplex([0, 1]), {})]
  s = ValueSimplex([0,1,2], 1)
  ## intended 
  assert list(faces(s)) == [Simplex([0]), Simplex([1]), Simplex([2]), Simplex((0, 1)), Simplex((0, 2)), Simplex((1, 2)), Simplex((0, 1, 2))]

def test_generics():
  assert list(unique_everseen([[0], [0], [1], [0,1]])) == [[0], [1], [0,1]]
  S = simplicial_complex([[0,1,2]])
  assert card(S) == (3,3,1)
  assert card(S,0) == 3
  assert dim(S) == 2
  assert all_in(faces(S), list(map(Simplex, [(0,),(1,),(2,),(0,1),(0,2),(1,2),(0,1,2)])))
  assert all_in(faces(S, 0), list(map(Simplex, [(0),(1),(2)])))
  assert all_in(faces(S,1), list(map(Simplex, [(0,1),(0,2),(1,2)])))
  assert all_in(faces(S,2), list(map(Simplex, [(0,1,2)])))
  K = filtration(S)
  assert card(K) == (3,3,1)
  assert card(K,0) == 3
  assert dim(K) == 2
  assert all_in(faces(K), list(map(Simplex, [(0,),(1,),(2,),(0,1),(0,2),(1,2),(0,1,2)])))
  assert all_in(faces(K,0), list(map(Simplex, [(0,),(1,),(2,)])))
  assert all_in(faces(K,1), list(map(Simplex, [(0,1),(0,2),(1,2)])))
  assert all_in(faces(K,2), list(map(Simplex, [(0,1,2)])))