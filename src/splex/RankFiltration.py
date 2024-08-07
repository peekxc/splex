
import numbers
import numpy as np

from operator import itemgetter
from combin import comb_to_rank, rank_to_comb

from .meta import *
from .generics import SimplexConvertible
from .RankComplex import RankComplex
from .predicates import is_complex_like
from .generics import faces
from .Simplex import Simplex
from .filter_abcs import Filtration
DEBUG = {}

class RankFiltration(Filtration):
  def __init__(self, simplices: Union[ComplexLike, Iterable], f: Callable = None, value_dtype = np.float64):
    s_dtype= np.dtype([('rank', np.int64), ('dim', np.uint16), ('value', value_dtype)])
    if is_complex_like(simplices):
      if isinstance(f, Callable):
        self.simplices = np.array([(comb_to_rank(s), len(s)-1, f(s)) for s in simplices], dtype=s_dtype)
      else:
        raise ValueError("Must supply filter function 'f' for ComplexLike inputs.")
    elif isinstance(simplices, Iterable):
      if isinstance(f, Callable):
        self.simplices = np.array([(comb_to_rank(s), len(s)-1, f(s)) for s in simplices], dtype=s_dtype)
      else:
        global DEBUG 
        # DEBUG['s_dtype'] = s_dtype
        # DEBUG['simplices'] = list(simplices)
        self.simplices = np.array([(comb_to_rank(s), len(s)-1, np.ravel(k).item()) for k, s in simplices], dtype=s_dtype)
    elif simplices is None:
      # Allow default constructible for empty filtrations
      self.simplices = np.empty(shape=(0,), dtype=s_dtype)
    else: 
      error_msg = "Invalid input; if filter 'f' is supplied, 'simplices' must be an iterable of simplex-like objects\n" 
      error_msg += "Otherwise, 'simplices' should be an iterable of pairs"
      raise ValueError(error_msg)
    self._order = 'colex'
    self.reindex()
    
  def comb_to_rank(self, combs, **kwargs):
    assert 'order' not in kwargs, "Order is fixed by the filtration"
    order = 'colex' if 'co' in self.order else 'lex'
    n = np.max(self.simplices['rank'][self.simplices['dim'] == 0]) + 1
    return comb_to_rank(combs, order=order, n=n, **kwargs)

  @property
  def order(self):
    return self._order 
  
  @order.setter
  def order(self, value):
    assert value in ['colex', 'lex', 'reverse colex', 'reverse lex']
    order = 'colex' if 'co' in value else 'lex'
    stored_colex, request_colex = 'co' in self._order, 'co' in value
    if stored_colex != request_colex:
      n = int(np.max(self.simplices['rank'][self.simplices['dim'] == 0])) + 1
      self.simplices['rank'] = np.array([comb_to_rank(s, order=order, n = n) for i,s in iter(self)], dtype=np.int64) 
    self._order = value
    self.reindex()

  def __iter__(self) -> Iterable:
    """Enumerates the faces of the complex."""
    order = 'colex' if 'co' in self.order else 'lex'
    n = np.max(self.simplices['rank'][self.simplices['dim'] == 0]) + 1
    simplices = rank_to_comb(self.simplices['rank'], k=self.simplices['dim']+1, n = n, order=order)
    # yield from zip(self.simplices['value'], simplices)
    return zip(self.simplices['value'], simplices)

  def __len__(self) -> int:
    return len(self.simplices)

  def __contains__(self, k: SimplexConvertible) -> bool:
    order = 'colex' if 'co' in self.order else 'lex'
    s = np.array(Simplex(k))
    n = np.max(self.simplices['rank'][self.simplices['dim'] == 0]) + 1
    r = comb_to_rank(s, order=order, n=n)
    ind = np.flatnonzero(self.simplices['rank'] == r)
    return (len(k)-1) in self.simplices['dim'][ind]
  
  ## --- Sequence requirements ---
  def __getitem__(self, key: Any) -> Simplex: 
    order = 'colex' if 'co' in self.order else 'lex'
    s = rank_to_comb(self.simplices['rank'][key], k=self.simplices['dim'][key]+1, order=order)
    return self.simplices['value'][key], s

  def reindex(self, f: Callable['SimplexLike', Any] = None) -> None:
    if f is not None:
      assert isinstance(f, Callable), "f must be a callable filter function"
      self.simplices['value'] = f(faces(self))
    if 'reverse' in self.order:
      np.negative(self.simplices['rank'], self.simplices['rank'])
    ind = np.argsort(self.simplices, order=('value', 'dim', 'rank'))
    if 'reverse' in self.order:
      np.negative(self.simplices['rank'], self.simplices['rank'])
    self.simplices = self.simplices[ind]

  ## --- splex generics support --- 
  def dim(self) -> int:
    return np.max(self.simplices['dim'])

  def faces(self, p: int = None, **kwargs) -> Iterable:
    assert isinstance(p, Integral) or p is None, f"Invalid p:{p} given"
    simplices_map = map(itemgetter(1), iter(self))
    if p is None:
      return iter(simplices_map)
    else:
      p_ind = self.simplices['dim'] == p
      order = 'colex' if 'co' in self.order else 'lex'
      if np.sum(p_ind) == 0: 
        return np.empty(shape=(0,), dtype=np.int64)
      return rank_to_comb(self.simplices['rank'][p_ind], k=p+1, order=order)
    
  def indices(self, p: int = None) -> Iterable[Any]:
    if p is None:
      return self.simplices['value']
    else: 
      return self.simplices['value'][self.simplices['dim'] == int(p)]
  
  def card(self, p: int = None) -> Union[tuple, int]:
    if p is None: 
      return tuple(np.bincount(self.simplices['dim']))
    else: 
      return np.sum(self.simplices['dim'] == int(p))

#   ## Mapping interface
#   __iter__ = lambda self: iter(self.simplices['f'])
#   def __getitem__(self, k) -> SimplexLike: 
#     i = np.searchsorted(self.simplices['f'])
#     r,d,f = self.simplices[i][:2]
#     return unrank_colex(r, d)
  
#   ## Mapping mixins
#   keys = lambda self: iter(self.simplices['f'])
#   values = lambda self: self.faces()
#   items = lambda self: zip(self.keys(), self.values())
#   __eq__ = lambda self, other: all(self.simplices == other.simplices) if len(self.simplices) == len(other.simplices) else False
#   __ne__ = lambda self, other: any(self.simplices != other.simplices) if len(self.simplices) == len(other.simplices) else False


  ## MutableMapping Interface 
  # __setitem__, __delitem__, pop, popitem, clear, update, setdefault

# class MutableCombinatorialFiltration(CombinatorialComplex, Mapping):

    #   self.simplices = simplices
    #   self.indices = range(len(simplices)) if I is None else I
    #   assert all([isinstance(s, SimplexLike) for s in simplices]), "Must all be simplex-like"
    #   if I is not None: assert len(simplices) == len(I)
    #   self.simplices = [Simplex(s) for s in simplices]
    #   self.index_set = np.arange(0, len(simplices)) if I is None else np.asarray(I)
    #   self.dtype = [('s', Simplex), ('index', I.dtype)]
    # self.data = SortedDict()
    # self.shape = tuple()
    # if isinstance(iterable, SimplicialComplex):
    #   if isinstance(f, Callable):
    #     self += ((f(s), s) for s in iterable)
    #   elif f is None:
    #     index_set = np.arange(len(iterable))  
    #     iterable = sorted(iter(iterable), key=lambda s: (len(s), tuple(s), s)) # dimension, lex, face poset
    #     self += zip(iter(index_set), iterable)
    #   else:
    #     raise ValueError("Invalid input for simplicial complex")
    # elif isinstance(iterable, Iterable):
    #   self += iterable ## accept pairs, like a normal dict
    # elif iterable is None:
    #   pass
    # else: 
    #   raise ValueError("Invalid input")

  # ## delegate new behavior to new methods: __iadd__, __isub__
  # def update(self, other: Iterable[Tuple[Any, Collection[Integral]]]):
  #   for k,v in other:
  #     self.data.__setitem__(k, self._sorted_set(v))

  # def __getitem__(self, key: Any) -> Simplex: 
  #   return self.data.__getitem__(key)

  # def __setitem__(self, k: Any, v: Union[Collection[Integral], SortedSet]):
  #   self.data.__setitem__(k, self._sorted_set(v))
  
  # ## Returns the value of the item with the specified key.
  # ## If key doesn't exist, set's F[key] = default and returns default
  # def setdefault(self, key, default=None):
  #   if key in self.data:
  #     return self[key] # value type 
  #   else:
  #     self.__setitem__(key, default)
  #     return self[key]   # value type   

  # def __delitem__(self, k: Any):
  #   self.data.__del__(k)
  
  # def __iter__(self) -> Iterator:
  #   return iter(self.keys())

  # def __len__(self) -> int:
  #   return sum(self.shape)
  #   #return self.data.__len__()

  # # https://peps.python.org/pep-0584/
  # def __or__(self, other: Union[Iterable[Tuple[int, int]], Mapping]):
  #   new = self.copy()
  #   new.update(SortedDict(other))
  #   return new

  # def __ror__(self, other: Union[Iterable[Tuple[int, int]], Mapping]):
  #   new = SortedDict(other)
  #   new.update(self.data)
  #   return new

  # ## In-place union '|=' operator 
  # # TODO: map Collection[Integral] -> SimplexLike? 
  # def __ior__(self, other: Union[Iterable[Tuple[int, int]], Mapping]):
  #   self.data.update(other)
  #   return self
  
  # ## In-place append '+=' operator ; true dict union/merge, retaining values
  # def __iadd__(self, other: Iterable[Tuple[int, int]]):
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

  # ## Simple copy operator 
  # def copy(self) -> 'MutableFiltration':
  #   new = MutableFiltration()
  #   new.data = self.data.copy()
  #   new.shape = self.shape.copy()
  #   return new 

  # ## Keys yields the index set. Set expand = True to get linearized order. 
  # ## TODO: Make view objects
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

  # def reindex_keys(self, index_set: Iterable):
  #   ''' Given a totally ordered key set of the same length of the filtation, reindexes '''
  #   assert len(index_set) == len(self)
  #   assert all((i <= j for i,j in pairwise(index_set)))
  #   new = MutableFiltration(zip(iter(index_set), self.values()))
  #   return new

  # def faces(self, p: int = None) -> Iterable:
  #   return filter(lambda s: len(s) == p+1, self.values())

  # def __repr__(self) -> str:
  #   # from collections import Counter
  #   # cc = Counter([len(s)-1 for s in self.values()])
  #   # cc = dict(sorted(cc.items()))
  #   n = len(self.shape)
  #   return f"{n-1}-d filtered complex with {self.shape}-simplices of dimension {tuple(range(n))}"

  # def print(self, **kwargs) -> None:
  #   import sys
  #   fv_s, fs_s = [], []
  #   for k,v in self.items():
  #     ks = len(str(v))
  #     fv_s.append(f"{str(k):<{ks}.{ks}}")
  #     fs_s.append(f"{str(v): <{ks}}")
  #     assert len(fv_s[-1]) == len(fs_s[-1])
  #   sym_le, sym_inc = (' ≤ ', ' ⊆ ') if sys.getdefaultencoding()[:3] == 'utf' else (' <= ', ' <= ') 
  #   print(repr(self))
  #   print("I: " + sym_le.join(fv_s[:5]) + sym_le + ' ... ' + sym_le + sym_le.join(fv_s[-2:]), **kwargs)
  #   print("S: " + sym_inc.join(fs_s[:5]) + sym_inc + ' ... ' + sym_inc + sym_inc.join(fs_s[-2:]), **kwargs)

  # def validate(self, light: bool = True) -> bool:
  #   fs = list(self.values())
  #   for i, s in enumerate(fs): 
  #     p = s.dimension() - 1 if light and len(s) >= 2 else None
  #     assert all([fs.index(face) <= i for face in s.faces(p)])
  #   assert all([k1 <= k2 for k1, k2 in pairwise(self.keys())])

  # def __format__(self, format_spec = "default") -> str:
  #   from io import StringIO
  #   s = StringIO()
  #   self.print(file=s)
  #   res = s.getvalue()
  #   s.close()
  #   return res
  