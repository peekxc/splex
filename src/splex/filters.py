import numpy as np 
from typing import Any, Union, Callable
from numpy.typing import * 
from dataclassy import dataclass
from combin import inverse_choose, comb_to_rank, rank_to_comb
from more_itertools import spy 
from numbers import Number
from hirola import HashTable
from .meta import *
from .predicates import *
from .generics import *
from .Simplex import Simplex


@dataclass(frozen=True, slots=True, init=False, repr=False, eq=False)
class GenericFilter:
  filter_f: Callable = lambda s: 1
  def __init__(self, f: Callable) -> None:
    object.__setattr__(self, 'filter_f', f)
  
  def __call__(self, S: Union[SimplexConvertible, ArrayLike]) -> Union[float, np.ndarray]:
    if is_simplex_like(S):
      return self.filter_f(Simplex(S))
    elif hasattr(S, "__array__") and is_complex_like(S):
      S = np.asarray(S)
      return np.array([self.filter_f(s) for s in map(Simplex, S)])
    else:
      assert isinstance(S, Iterable), "simplex iterable must be supplied"
      return np.array([self.filter_f(s) for s in map(Simplex, S)])

@dataclass(frozen=True, slots=True, init=False, repr=False, eq=False)
class HirolaFilter:
  table: dict = {}
  dtype: np.dtype = np.uint32
  def __init__(self, S: ComplexLike, values: Sequence[Any]) -> None:
    
    ## Extract the values
    values = np.asarray(values)
    (el,), iterable = spy(values)
    el_dtype = np.dtype(el)
    assert isinstance(el, Number), "Value types must be numbers"
    
    # values = values.astype(el_dtype)
    # values = np.ravel(np.fromiter(iterable, dtype=el_dtype))
    assert len(values) == len(S), "Number of values given must match number of simplices"

    ## Initialize the lookup tables
    lookup_table = {}
    for d in range(dim(S)+1):
      d_dtype = (np.uint32, d+1) if d > 0 else np.uint32
      T = HashTable(max(card(S,d) * 1.25, 2), d_dtype)
      lookup_table[d] = { 'table': T, 'values' : np.empty(card(S,d), dtype=el_dtype) } 

    ## Get the dimensions of each simplex 
    dims = np.array([dim(s) for s in S], dtype=np.uint8)
    for d in range(dim(S)+1):
      d_dtype = np.uint32
      d_simplices = np.array(list(map(Simplex, faces(S,d)))).astype(d_dtype)
      d_ids = np.ravel(lookup_table[d]['table'].add(d_simplices))
      lookup_table[d]['values'][d_ids] = values[dims == d]

    ## Finally, assign the table and value dtype
    object.__setattr__(self, 'table', lookup_table)
    object.__setattr__(self, 'dtype', el_dtype)

  def __call__(self, S: Union[SimplexConvertible, ArrayLike]) -> Union[float, np.ndarray]:
    if is_simplex_like(S):
      T = self.table[dim(S)]
      result = T['values'][T['table'][Simplex(S)]]
      return np.take(result, 0) if dim(S) == 0 else result
    elif hasattr(S, "__array__") and is_complex_like(S):
      S = np.array(S, dtype=np.uint32)
      T = self.table[S.shape[1]-1]
      return np.ravel(T['values'][T['table'][S]])
    # elif isinstance(S, Iterable) and is_repeatable(S):
    # 	dims = np.array([dim(s) for s in S], dtype=np.uint8)
    # 	return_values = np.empty(len(S), dtype=self.dtype)
    # 	for d in range(dim(S)):
    # 		d_dtype = (np.uint16, d+1) if d > 0 else np.uint16
    # 		d_simplices = np.fromiter(faces(S,d), dtype=d_dtype)
    # 	return 
    else: 
      assert isinstance(S, Iterable), "simplex iterable must be supplied"
      return np.array([self(s) for s in S])

@dataclass(frozen=True, slots=True, init=False, repr=False, eq=False)
class VertexFilter:
  vertex_weights: np.ndarray = np.empty(0, dtype=np.float32)

  def __init__(self, v: np.ndarray) -> None:
    object.__setattr__(self, 'vertex_weights', v)
  
  def __call__(self, S: Union[SimplexConvertible, ArrayLike]) -> Union[float, np.ndarray]:
    if (isinstance(S, Sized) and len(S) == 0) or (hasattr(S, 'shape') and 0 in list(S.shape)):
      return np.array([])
    if is_simplex_like(S):
      return np.max(self.vertex_weights[Simplex(S)]) # Simplices can be used for indexing!
    elif hasattr(S, "__array__") and is_complex_like(S):
      S = np.asarray(S)
      return np.max(self.vertex_weights[S], axis=-1) ## vectorized form
    else:
      assert isinstance(S, Iterable), "simplex iterable must be supplied"
      return np.array([np.max(self.vertex_weights[s]) for s in map(Simplex, S)])

@dataclass(frozen=True, slots=True, init=False, repr=False, eq=False)
class CliqueFilter:
  n: int = 0
  vertex_weights: np.ndarray = np.empty(0, dtype=np.float32)
  edge_weights: np.ndarray = np.empty(0, dtype=np.float32)
  def __init__(self, v: np.ndarray, pd: np.ndarray, n: int) -> None:
    object.__setattr__(self, 'n', n)
    object.__setattr__(self, 'vertex_weights', v)
    object.__setattr__(self, 'edge_weights', pd)
  def __call__(self, s: Union[SimplexConvertible, ArrayLike]) -> Union[float, np.ndarray]:
    if hasattr(s, "__array__") and is_complex_like(s):
      ## Handles numpy matrices of simplices OR array_convertible containers, so long as they are complex-like
      s = np.asarray(s)
      if s.ndim == 1 or (1 in s.shape):
        # print("hello")
        return np.ravel(self.vertex_weights[s])
      else: 
        if s.shape[1] == 2: 
          ind = comb_to_rank(s, n=self.n, order='lex')
          return self.edge_weights[ind]
        else:
          fw = np.zeros(s.shape[0])
          for i,j in combinations(range(s.shape[1]), 2):
            np.maximum(fw, self.edge_weights[comb_to_rank(s[:,[i,j]], n=self.n, order='lex')], out=fw)
          return fw
    elif is_simplex_like(s):
      if len(s) == 1: 
        return np.take(self.vertex_weights[s], 0) # always return simple value tyep for single simplex
      else: 
        ind = np.array(comb_to_rank(combinations(s, 2), n=self.n, order='lex'), dtype=np.uint64)
        # ind = np.fromiter((rank_lex(e, n=self.n) for e in combinations(s, 2)), dtype=np.uint32)
        return np.max(self.edge_weights[ind])
    else:
      # assert is_complex_like(s), "Input simplices must be complex like" # this is unneeded since not not be sized or repeatable
      rank_boundary = lambda f: np.array(comb_to_rank(combinations(f, 2), n=self.n, order='lex'), dtype=np.uint64)
      return np.array([np.max(self.edge_weights[rank_boundary(f)]) if dim(f) >= 1 else np.take(self.vertex_weights[f],0) for f in s], dtype=float)

## TODO: revamp to include support for arbitrary simplicial complexes via index tracking with hirola 
def fixed_filter(S: ComplexLike, values: np.ndarray):
  """Constructs a complex-parameterized callable that vectorizes a simplex-parameterized callable."""
  assert len(S) == len(values), "Number of filtration values must match size of complex."
  # _simplex_weight = { Simplex(s) : fv for s, fv in zip(S, values) }
  # filter_callable = GenericFilter(_simplex_weight.__getitem__)
  # return filter_callable
  return HirolaFilter(S, values)

def generic_filter(f: Callable) -> Callable:
  """Constructs a complex-parameterized callable that vectorizes a simplex-parameterized callable."""
  return GenericFilter(f)

def lower_star_filter(x: ArrayLike) -> Callable:
  """Factory method for constructing lower star filter functions. 

  Vertex labels are assumed to be 0-indexed for now. 
  
  If simplex-like, use 0-indexed vertex labels to index vertex values directly. 
  
  Otherwise assumes a 2d array of simplex labels is given and vectorizes the computation.
  """
  return VertexFilter(x)


def flag_filter(x: ArrayLike, vertex_weights: Optional[ArrayLike] = None) -> Callable:
  """Factory method for constructing flag/clique filter functions. 

  Parameters: 
    x: point cloud, vector of pairwise weights, or square matrix. 
    vertex_weights: optional weights to use for vertices. Defaults to None, which sets vertex weights to 0.

  Returns: 
    callable which takes as input a simplex or set of simplices and returns their clique weights. 
  """
  pd = as_pairwise_dist(x)
  n = inverse_choose(len(pd), 2)
  vertex_weights = np.zeros(n) if vertex_weights is None else vertex_weights
  assert len(vertex_weights) == n, "Invalid vertex weights"
  C = CliqueFilter(vertex_weights, pd, n)
  return C