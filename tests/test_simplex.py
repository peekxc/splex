from splex import * 
from splex.meta import _data_attributes 

def test_simplex():
  s = Simplex([0,1,2])
  assert isinstance(s, Simplex)
  assert isinstance(s, SimplexLike)
  assert isinstance(s, SimplexConvertible)
  t = Simplex([0,1])
  assert t < s
  assert t <= s
  assert not s < t
  assert s > t and s >= t
  assert s == s 
  assert t != s
  assert s[0] == 0 and s[1] == 1 and s[2] == 2
  assert len(list(s.faces())) == 7
  assert 0 in s
  assert s.dim() == 2
  assert s.vertices == (0,1,2)
  assert len(list(s.boundary())) == 3
  assert s - t == Simplex(2)
  assert hash(s) is not None

def test_simplex_varieties():
  s = Simplex([0,1,2])
  f = ValueSimplex([0,1,2], 1)
  p = PropertySimplex([0,1,2])
  p.color = 'red'
  p.data = 1
  assert _data_attributes(s) == ['vertices']
  assert _data_attributes(f) == ['value', 'vertices']
  assert _data_attributes(p) == ['color', 'data', 'vertices']

  ## New: retain the value-semantics with the Property and Value simplices
  assert s == p and f == s
  
  