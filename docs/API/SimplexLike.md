# SimplexLike

 --- 

An object is SimplexLike if it is Immutable, Hashable, and SetLike

By definition, this implies a simplex is sized, iterable, and acts as a container (supports vertex __contains__ queries)

Protocols: SetLike[Container, Comparable], Hashable, Immutable
Abstract Methods: __hash__, __contains__, __len__, __iter__, __setitem__