[![Python package](https://github.com/peekxc/splex/actions/workflows/python-package.yml/badge.svg)](https://github.com/peekxc/splex/actions/workflows/python-package.yml)
[![coverage_badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/peekxc/ef42349965f40edf4232737026690c5f/raw/coverage_info.json)](https://coveralls.io/github/peekxc/splex)
[![python_badge](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://github.com/peekxc/splex/actions/workflows/python-package.yml)]

<!-- [![Appveyor Windows Build status](https://img.shields.io/appveyor/ci/peekxc/splex/master.svg?logo=windows&logoColor=DDDDDD)](https://github.com/peekxc/splex/actions/workflows/python-package.yml)
[![Travis OS X Build status](https://img.shields.io/travis/peekxc/splex/master.svg?logo=Apple&logoColor=DDDDDD&env=BADGE=osx&label=build)](https://github.com/peekxc/splex/actions/workflows/python-package.yml)
[![Travis Linux X Build status](https://github.com/peekxc/splex/actions/workflows/python-package.yml)](https://travis-ci.com/peekxc/splex) --> 
<!-- [![Coverage Status](https://coveralls.io/repos/github/peekxc/splex/badge.svg?branch=main)](https://coveralls.io/github/peekxc/splex?branch=main) -->

`splex` is an experimental package for constructing, manipulating, and computing with simplicial complexes. 

## Quickstart 

What if there was a natural type for representing simplices? 
```python
s, t = Simplex([0,1,2]),  Simplex([0,1])

print(s.dim(), ":", s)
# 2 : (0,1,2)

t < s, t <= s, s < t
# True, True, False

t in s.boundary()
# True 

print(list(s.faces()))
# [(0), (1), (2), (0,1), (0,2), (1,2), (0,1,2)]
```

What if said type was flexible and easy to work with, supporting no-fuss construction

```python
Simplex(2) == Simplex([2])                      # value-types are always unboxed 
Simplex([1,2]) == Simplex([1, 2, 2])            # simplices have unique entries, are hashable 
Simplex((1,5,3)) == Simplex(np.array([5,3,1]))  # arrays and tuples supported out of the box 
Simplex((0,1,2)) == Simplex(range(3))           # ... as are generators, iterables, collections, etc
```

What if it was easy to use with other native Python tools?
```python
s = Simplex([0,1,3,4])
np.array(s)          # native __array__ conversion enabled
len(s)               # __len__ is as expected 
3 in 3               # __contains__ acts vertex-wise
list(iter(s))        # __iter__ also acts vertex-wise
s[0]                 # __getitem__ as well 
s[0] = 5             # __setitem__ is *not*: Simplices are immutable!

# Which means native support for the expected protocols 
isinstance(s, Sized)     # True 
isinstance(s, Container) # True 
isinstance(s, Iterable)  # True 
isinstance(s, Mapping)   # False 
```

What if there was a similar construction for simplicial complexes?
```python
S = simplicial_complex([[0,1,2,3], [4,5], [6]])
print(S)
# 3-d complex with (7, 7, 4, 1)-simplices of dimension (0, 1, 2, 3)

[s for s in S.faces()] # [(0), (1), ..., (1,2,3), (0,1,2,3)]
S.add([5,6]) # adds Simplex([5,6]) to the complex 
```

.. and for filtered complexes as well?
```python
K = filtration(S)
print(K)
# 3-d filtered complex with (7, 7, 4, 1)-simplices of dimension (0, 1, 2, 3)
print(format(K))
# 3-d filtered complex with (7, 7, 4, 1)-simplices of dimension (0, 1, 2, 3)
# I: 0   ≤ 1   ≤ 2   ≤ 3   ≤ 4   ≤  ...  ≤ 17      ≤ 18       
# S: (0) ⊆ (1) ⊆ (2) ⊆ (3) ⊆ (4) ⊆  ...  ⊆ (1,2,3) ⊆ (0,1,2,3)

[s for s in K.faces()] # [(0), (1), ..., (1,2,3), (0,1,2,3)]
```

What if there were multiple choices in representation...


```python
SS = simplicial_complex([[0,1,2,3]], form="set")  # simplices stored as sets: simple and extensible
ST = simplicial_complex([[0,1,2,3]], form="tree") # simplex trees are compact and efficient to modify
SR = simplicial_complex([[0,1,2,3]], form="rank") # simplices stored in arrays integers: cache efficient to read
# ... 
```

...but every representation was supported through _generics_


```python
faces(SS)           # calls overloaded .faces()
faces(ST)           # same as above, but using a simplex tree
faces(SR)           # same as above, but using a rank complex 
faces([[0,1,2,3]]) # Equivalent! Falls back to combinations! 
# same goes for .card(), .dim(), .boundary(), ...
```

What if extending support to all such types generically was as easy as

```python
def faces(S: ComplexLike) -> Iterator[SimplexConvertible]:
  if hasattr(S, "faces"):
    yield from S.faces()
  else:
    ...
```

...where `ComplexLike` is a protocol defining a minimal interface needed for Python types to be interpreted as complexes. 
This is duck typing---no direct inheritance needed! Just define your type, make it _pythonic_ via abc.collections and go. 


```python
def MyCellComplex(ComplexLike):
  def __iter__(self) -> Iterator[SimplexConvertible]:
    ...
```

<!-- Of course, if the types could be *narrowed* for highly performant, type-specific algorithms?

```{python}

``` 
-->

<!-- These are the goals of the `splex` package. Clean, extensible, performant.   -->

