import numpy as np 
from splex import * 
from more_itertools import unique_everseen
from itertools import product

def check_poset(S: ComplexLike):
  ## Reflexivity 
  for s in S: assert s <= s, "Simplex order not reflexive"

  ## Antisymmetry 
  for x, y in product(S, S):
    if x <= y and y <= x:
      assert x == y, "Simplex order not symmetric"

  ## Transitivity
  for x, y, z in product(S, S, S):
    if x <= y and y <= z:
      assert x <= z, "Simplex order not transitive"

  ## Test containment of faces 
  for s in S: 
    for face in faces(Simplex(s)):
      assert face in S

  return True 

def test_simplicial_complex_api():
  for form in ["set", "tree", "rank"]:
    # S = simplicial_complex(form=form)
    # assert isinstance(S, ComplexLike)
    S = simplicial_complex([[0,1,2,3,4]], form=form)
    assert isinstance(S, ComplexLike)

# def test_filtration_api():
#   for form in ["set", "tree", "rank"]:
#     # S = simplicial_complex(form=form)
#     # assert isinstance(S, ComplexLike)
#     K = filtration(enumerate(faces([[0,1,2,3,4]])), form=form)
#     assert isinstance(K, ComplexLike)
#     check_poset(K)

def test_set_complex():
  S = simplicial_complex([[0,1,2,3]], form="set")
  assert list(S.cofaces([0,1,2])) == [(0,1,2), (0,1,2,3)]
  S.remove([0,1,2,3])
  assert [0,1,2,3] not in S
  assert dim(S) == 2
  assert S.discard([0,1,2,3]) is None 
  assert S.discard([0,1]) is None 
  assert [0,1] not in S

## Testing reindexing capability 
def test_filtration():
  S = simplicial_complex([[0,1,2,3,4]], "set")
  assert isinstance(S, SetComplex)
  # K = filtration(S, "set_filtration")
  # assert isinstance(K, MutableFiltration)
  # L = K.copy()
  # K.reindex(lambda s: 10 + sum(s))
  # L_simplices = [tuple(s) for s in L.values()]
  # K_simplices = [tuple(s) for s in K.values()]
  # assert len(L_simplices) == len(K_simplices)
  # assert L_simplices != K_simplices
  # assert list(sorted(K_simplices)) == list(sorted(L_simplices))
  
def test_rips_complex():
  from splex.filters import flag_filter
  from splex.geometry import delaunay_complex
  X = np.random.uniform(size=(10,2))
  f = flag_filter(X)
  S = delaunay_complex(X)
  assert isinstance([f(s) for s in S], list)
  assert isinstance(filtration(S, f=f), FiltrationLike)

def test_rips_filtration():
  radius = 0.35
  X = np.random.uniform(size=(15,2))
  K = rips_filtration(X, radius)
  assert isinstance(K, FiltrationLike)

def test_generics():
  assert list(unique_everseen([[0], [0], [1], [0,1]])) == [[0], [1], [0,1]]
  S = simplicial_complex([[0,1,2]])
  ref = [(0,),(1,),(2,),(0,1),(0,2),(1,2),(0,1,2)]
  assert card(S) == (3,3,1)
  assert card(S,0) == 3
  assert dim(S) == 2
  assert all([s in ref for s in faces(S)])
  assert list(faces(S,0)) ==  list(map(Simplex, [(0),(1),(2)]))
  K = filtration(S)
  assert card(K) == (3,3,1)
  assert card(K,0) == 3
  assert dim(K) == 2
  all_faces = list(faces(K))
  assert all([tuple(s) in [(0,),(1,),(2,),(0,1),(0,2),(1,2),(0,1,2)] for s in all_faces])
  assert list(map(Simplex, faces(K,0))) == list(map(Simplex, [(0),(1),(2)]))
  
def test_boundary():
  K = filtration(enumerate(map(Simplex, [0,1,2,[0,1],[0,2],[1,2]])))
  D_test = boundary_matrix(K).todense()
  D_true = np.array([
    [ 0,  0,  0,  1,  1,  0],
    [ 0,  0,  0, -1,  0,  1],
    [ 0,  0,  0,  0, -1, -1],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0]
  ])
  assert np.allclose(D_test - D_true, 0.0)

  D1_test = boundary_matrix(K, p=1).todense()
  D1_true = np.array([
    [  1,  1,  0],
    [ -1,  0,  1],
    [  0, -1, -1],
  ])
  assert np.allclose(D1_test - D1_true, 0.0)