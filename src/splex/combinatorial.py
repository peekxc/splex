import numpy as np 
from typing import * 
from itertools import * 
from numbers import Integral
from math import comb, factorial
# import _combinatorial as comb_mod

def rank_C2(i: int, j: int, n: int) -> int:
  i, j = (j, i) if j < i else (i, j)
  return(int(n*i - i*(i+1)/2 + j - i - 1))

def unrank_C2(x: int, n: int) -> tuple:
  i = int(n - 2 - np.floor(np.sqrt(-8*x + 4*n*(n-1)-7)/2.0 - 0.5))
  j = int(x + i + 1 - n*(n-1)/2 + (n-i)*((n-i)-1)/2)
  return(i,j) 

def unrank_lex(r: int, k: int, n: int):
  result = [0]*k
  x = 1
  for i in range(1, k+1):
    while(r >= comb(n-x, k-i)):
      r -= comb(n-x, k-i)
      x += 1
    result[i-1] = (x - 1)
    x += 1
  return tuple(result)

def rank_lex(c: Iterable, n: int) -> int:
  c = tuple(sorted(c))
  k = len(c)
  index = sum([comb(n-ci-1,k-i) for i,ci in enumerate(c)])
  #index = sum([comb((n-1)-cc, kk) for cc,kk in zip(c, reversed(range(1, len(c)+1)))])
  return int(comb(n, k) - index - 1)

def rank_colex(c: Iterable) -> int:
  c = tuple(sorted(c))
  k = len(c)
  #return sum([comb(ci, i+1) for i,ci in zip(reversed(range(len(c))), reversed(c))])
  return sum([comb(ci,k-i) for i,ci in enumerate(reversed(c))])

def unrank_colex(r: int, k: int) -> np.ndarray:
  """
  Unranks a k-combinations rank 'r' back into the original combination in colex order
  
  From: Unranking Small Combinations of a Large Set in Co-Lexicographic Order
  """
  c = [0]*k
  for i in reversed(range(1, k+1)):
    m = i
    while r >= comb(m,i):
      m += 1
    c[i-1] = m-1
    r -= comb(m-1,i)
  return tuple(c)

def rank_combs(C: Iterable[tuple], n: int = None, order: str = ["colex", "lex"]):
  """
  Ranks k-combinations to integer ranks in either lexicographic or colexicographical order
  
  Parameters: 
    C : Iterable of combinations 
    n : cardinality of the set (lex order only)
    order : the bijection to use
  
  Returns: 
    list : unsigned integers ranks in the chosen order.
  """
  if (isinstance(order, list) and order == ["colex", "lex"]) or order == "colex":
    return [rank_colex(c) for c in C]
  else:
    assert n is not None, "Cardinality of set must be supplied for lexicographical ranking"
    return [rank_lex(c, n) for c in C]

def unrank_combs(R: Iterable[int], k: Union[int, Iterable], n: int = None, order: str = ["colex", "lex"]):
  """
  Unranks integer ranks to  k-combinations in either lexicographic or colexicographical order
  
  Parameters: 
    R : Iterable of integer ranks 
    n : cardinality of the set (lex order only)
    order : the bijection to use
  
  Returns: 
    list : k-combinations derived from R
  """
  if (isinstance(order, list) and order == ["colex", "lex"]) or order == "colex":
    if isinstance(k, Integral):
      return [unrank_colex(r, k) for r in R]
    else: 
      assert len(k) == len(R), "If 'k' is an iterable it must match the size of 'R'"
      return [unrank_colex(r, l) for l, r in zip(k,R)]
  else: 
    assert n is not None, "Cardinality of set must be supplied for lexicographical ranking"
    if isinstance(k, Integral):
      if k == 2: 
        return [unrank_C2(r, n) for r in R]
      else: 
        return [unrank_lex(r, k, n) for r in R]
    else:
      assert len(k) == len(R), "If 'k' is an iterable it must match the size of 'R'"
      return [unrank_lex(r, l) for l, r in zip(k,R)]

def inverse_choose(x: int, k: int):
	assert k >= 1, "k must be >= 1" 
	if k == 1: return(x)
	if k == 2:
		rng = np.array(list(range(int(np.floor(np.sqrt(2*x))), int(np.ceil(np.sqrt(2*x)+2) + 1))))
		final_n = rng[np.nonzero(np.array([comb(n, 2) for n in rng]) == x)[0].item()]
	else:
		# From: https://math.stackexchange.com/questions/103377/how-to-reverse-the-n-choose-k-formula
		if x < 10**7:
			lb = (factorial(k)*x)**(1/k)
			potential_n = np.array(list(range(int(np.floor(lb)), int(np.ceil(lb+k)+1))))
			idx = np.nonzero(np.array([comb(n, k) for n in potential_n]) == x)[0].item()
			final_n = potential_n[idx]
		else:
			lb = np.floor((4**k)/(2*k + 1))
			C, n = factorial(k)*x, 1
			while n**k < C: n = n*2
			m = (np.nonzero( np.array(list(range(1, n+1)))**k >= C )[0])[0].item()
			potential_n = np.array(list(range(int(np.max([m, 2*k])), int(m+k+1))))
			ind = np.nonzero(np.array([comb(n, k) for n in potential_n]) == x)[0].item()
			final_n = potential_n[ind]
	return(final_n)