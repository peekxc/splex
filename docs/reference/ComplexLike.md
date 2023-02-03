# ComplexLike

 --- 

Protocol interface for types that represent (abstract) simplicial complexes

An type _ComplexLike_ if it is a iterable collection of SimplexLike objects, and it the following methods:
  - dim : None -> int
  - faces : int -> Iterable[SimplexLike]


Protocols: Collection[Sized, Iterable, Container]
Methods: __contains__, __iter__, __len__

 --- 

## dim { #dim }

`dim(self)`

 --- 

## faces { #faces }

`faces(self, p: int)`