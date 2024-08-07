from typing import * 
from .meta import SimplexConvertible, SimplexLike
from .filter_abcs import * 
from .SetFiltration import SetFiltration
from .RankFiltration import RankFiltration
from .Simplex import Simplex

def filtration(simplices: Iterable[SimplexConvertible], f: Optional[Callable] = None, form: Optional[str] = "default", **kwargs):
  from functools import partial
  form = "rank" if form is None or form == "default" else form
  if f is None and is_complex_like(simplices): 
    index_map = { Simplex(s) : i for i, s in enumerate(simplices) }
    f = partial(lambda s, d: d[Simplex(s)], d=index_map)
  if form == "set":
    sf = SetFiltration(simplices, f, **kwargs)
  elif form == "rank":
    sf = RankFiltration(simplices, f, **kwargs)
  else: 
    raise ValueError(f"Unknown data structure '{str(type(form))}'.")
  return sf