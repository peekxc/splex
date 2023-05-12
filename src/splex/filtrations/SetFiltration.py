import numpy as np  
from ..meta import *
from ..generics import *
from ..Simplex import *
from ..complexes import * 
from .filter_abcs import Filtration
from sortedcontainers import SortedSet
from more_itertools import spy

# Requires: __getitem__, __delitem__, __setitem__ , __iter__, and __len__ a
# Inferred: pop, clear, update, and setdefault
# https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/
class SetFiltration(Filtration, Sequence):
  """Filtered complex of simplices uses _SortedSet_.

  This class represents a filtration of simplices by associating keys of a given index set with _SortedSet_s 
  of _Simplex_ instances. This class also implements the Mapping[Any, SimplexConvertible] 
  Implements: __getitem__, __iter__, __len__, __contains__, keys, items, values, get, __eq__, and __ne__
  """

  @classmethod
  def _key_dim_lex(cls, s: ValueSimplex) -> bool:
    return (s.value, len(s), tuple(s), s)
  
  @classmethod
  def _key_dim_colex(cls, s: ValueSimplex) -> bool:
    return (s.value, len(s), tuple(s), s)

  @classmethod
  def _sorted_set(self, iterable: Iterable[ValueSimplex] = None, order: str = "lex") -> SortedSet:
    """Returns a newly allocated Sorted Set w/ lexicographical poset ordering."""
    if order == "lex":
      key = SetFiltration._key_dim_lex
    elif order == "colex":
      key = SetFiltration._key_dim_lex
    else: 
      raise ValueError(f"Invalid order '{str(order)}' given.")
    if iterable is not None: 
      head, iterable = spy(iterable)
      assert isinstance(head[0], ValueSimplex)
      return SortedSet(iterable, key)
    else:
      return SortedSet(None, key)
  
  def __init__(self, simplices: Union[ComplexLike, Iterable] = None, f: Optional[Callable] = None, order: str = 'lex') -> None:
    """Constructs a filtration by storing simplices in a _SortedSet_ container.

    Accepts any of the following pairs: 
      - Iterable of (key, simplex) pairs
      - Iterable[SimplexConvertible], f = None
      - Iterable[SimplexConvertible], f = Callable
    """
    self.data = SetFiltration._sorted_set()
    self.n_simplices = tuple()
    if isinstance(simplices, ComplexLike):
      if isinstance(f, Callable):
        self.update((ValueSimplex(s, f(s)) for s in simplices))
      else:
        raise ValueError("Must supply filter function 'f' for ComplexLike inputs.")
    elif isinstance(simplices, Iterable):
      if isinstance(f, Callable):
        self.update((ValueSimplex(s, f(s)) for s in simplices))
      else:
        self.update((ValueSimplex(s,k) for k,s in simplices)) ## accept pairs, like a normal dict
    elif simplices is None:
      pass
    else: 
      raise ValueError("Invalid input")

  ## --- Collection/Set requirements --- 
  def __iter__(self) -> Iterator[ValueSimplex]:
    yield from ((s.value, Simplex(s)) for s in self.data)
    # return iter(self.data)

  def __len__(self) -> int:
    return len(self.data)

  def __contains__(self, k: SimplexConvertible) -> bool: # simplex-wise only 
    return Simplex(k) in self.data

  ## --- Sequence requirements ---
  def __getitem__(self, key: Any) -> Simplex: 
    return self.data.__getitem__(key)

  ## --- MutableSequence requirements --- 
  # def __setitem__(self, key: Any, value: Union[Collection[Integral], SortedSet]):
  #   self.data.__setitem__(key, self._sorted_set(v))

  # def __delitem__(self, key: Any):
  #   self.data.pop(key)

  # def insert(self, index: Any, simplex: SimplexConvertible):
  #   self.data.add(ValueSimplex(simplex, index))

  ## --- MutableSet requirements ---
  def add(self, simplex: SimplexConvertible) -> None:
    assert isinstance(simplex, SimplexConvertible) # or isinstance(simplex, tuple)
    simplex = ValueSimplex(simplex, 1.0) if not hasattr(simplex, "value") else simplex
    ns = list(self.n_simplices) + [0]*(dim(simplex)-self.dim())
    for f in faces(simplex):
      if f not in self.data:
        self.data.add(ValueSimplex(f, simplex.value))
        ns[dim(f)] += 1
    self.n_simplices = tuple(ns)

  def update(self, simplices: Iterable[ValueSimplex]) -> None: 
    for s in simplices: 
      self.add(s)

  # def discard(self, simplex: ValueSimplex):
  #   assert isinstance(simplex, ValueSimplex) or isinstance(simplex, tuple)
  #   simplex = ValueSimplex(simplex[1], simplex[0]) if isinstance(simplex, tuple) else simplex
  #   s_cofaces = list(self.cofaces(simplex))
  #   ns = list(self.n_simplices) 
  #   for c in s_cofaces:
  #     self.data.discard(c)
  #     ns[dim(c)] -= 1
  #   self.n_simplices = tuple(rstrip(ns, lambda x: x <= 0))

  ## --- splex generics support --- 
  def dim(self) -> int:
    return len(self.n_simplices)-1

  def faces(self, p: int = None) -> Iterator[ValueSimplex]:
    assert isinstance(p, Integral) or p is None, f"Invalid p:{p} given"
    #return self.values() if p is None else filter(lambda s: len(s) == p+1, self.values())
    return iter(self.data) if p is None else filter(lambda s: len(s) == p+1, iter(self.data))

  ## --- Filtration specific enhancements --- 
  def reindex(self, index_set: Union[Iterable, Callable]) -> None:
    """Given a totally ordered key set of the same length of the filtation, or a callable, reindexes the simplices in the filtration"""
    if isinstance(index_set, Iterable):
      assert len(index_set) == len(self), "Index set length not match the number of simplices in the filtration!"
      assert all((i <= j for i,j in pairwise(index_set))), "Index set is not totally ordered!"
      new = SetFiltration(zip(iter(index_set), self.values()))
      self.data = new.data
    elif isinstance(index_set, Callable):
      new = SetFiltration(simplices=self.values(), f=index_set)
      self.data = new.data
    else:
      raise ValueError("invalid index set supplied")

  ## Additional 
  def cofaces(self, item: Collection[int]) -> Iterable:
    s = Simplex(item)
    yield from filter(lambda t: t >= s, iter(self))

  ## --- Miscelleneous --- 
  def copy(self) -> 'SetFiltration':
    new = SetFiltration()
    from copy import deepcopy
    new.data = deepcopy(self.data)
    new.n_simplices = deepcopy(self.n_simplices)
    return new 
  
  # def _add_ns(self, ) -> None:

  # ## delegate new behavior to new methods: __iadd__, __isub__
  # def update(self, other: Iterable[Tuple[Any, Collection[Integral]]]):
  #   for k,v in other:
  #     self.data.__setitem__(k, self._sorted_set(v))

  ## Returns the value of the item with the specified key.
  ## If key doesn't exist, set's F[key] = default and returns default
  # def setdefault(self, key, default=None):
  #   if key in self.data:
  #     return self[key] # value type 
  #   else:
  #     self.__setitem__(key, default)
  #     return self[key]   # value type  

  # https://peps.python.org/pep-0584/
  # def __or__(self, other: Union[Iterable[Tuple[int, int]], Mapping]):
  #   new = self.copy()
  #   new.update(SortedDict(other))
  #   return new

  # def __ror__(self, other: Union[Iterable[Tuple[int, int]], Mapping]):
  #   new = SortedDict(other)
  #   new.update(self.data)
  #   return new

  ## In-place union '|=' operator 
  # TODO: map Collection[Integral] -> SimplexLike? 
  # def __ior__(self, other: Union[Iterable[Tuple[int, int]], Mapping]):
  #   self.data.update(other)
  #   return self
  
  # ## In-place append '+=' operator ; true dict union/merge, retaining values
  # def __iadd__(self, other: Iterable[Tuple[Any, SimplexLike]]):
  #   for k,v in other:
  #     if len(Simplex(v)) >= 1:
  #       # print(f"key={str(k)}, val={str(v)}")
  #       s_set = self.setdefault(k, self._sorted_set())
  #       f = Simplex(v)
  #       if not(f in s_set):
  #         s_set.add(f)
  #         if len(f) > len(self.shape):
  #           self.shape = tuple(list(tuple(self.shape)) + [1])
  #         else:
  #           t = self.shape
  #           self.shape = tuple(t[i]+1 if i == (len(f)-1) else t[i] for i in range(len(t)))   
  #   return self

  # ## Copy-add '+' operator 
  # def __add__(self, other: Iterable[Tuple[int, int]]):
  #   new = self.copy()
  #   new += other 
  #   return new

  ## Keys yields the index set. Set expand = True to get linearized order. 
  ## TODO: Make view objects
  # def keys(self):
  #   it_keys = chain()
  #   for k,v in self.data.items():
  #     it_keys = chain(it_keys, repeat(k, len(v)))
  #   return it_keys

  # def values(self):
  #   it_vals = chain()
  #   for v in self.data.values():
  #     it_vals = chain(it_vals, iter(v))
  #   return it_vals

  # def items(self):
  #   it_keys, it_vals = chain(), chain()
  #   for k,v in self.data.items():
  #     it_keys = chain(it_keys, repeat(k, len(v)))
  #     it_vals = chain(it_vals, iter(v))
  #   return zip(it_keys, it_vals)



# class MySet(Set):
#   def __init__(self, L):
#     self.data = set(L)
#   def __contains__(self, val):
#     return val in self.data
#   def __iter__(self):
#     return iter(self.data)
#   def __len__(self):
#     return len(self.data)