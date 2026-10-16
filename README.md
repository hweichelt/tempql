# Temporal Query Language

This is a temporal query language for temporal answer set planning programs, developed for [`tempXplain`](https://github.com/hweichelt/tempxplain).

## Grammar [`grammar.ebnf`](./grammar.ebnf)

```ebnf
program    = [separators] , [query] , { separators , query } , [separators] ;
query      = formula , [ "@" , number ] ;
formula    = disj ;
disj       = conj , { "|" , conj } ;
conj       = signed , { "&" , signed } ;
signed     = "-" , signed | primary ;
primary    = atom
              | "(" , formula , ")"
              | unary , "[" , formula , "]"
              | binary , "[" , formula , "," , formula , "]" ;
unary      = "X" | "P" | "G" | "F" ;
binary     = "U" | "S" ;
separators = separator , { separator } ;
separator  = ";" | newline ;
number     = digit , { digit } ;
digit      = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;

newline    = ? newline ? ;
atom       = ? a ground clingo symbol ? ;

```

## Examples

The following list of examples show how temporal queries can be formed.
They use the [elevator](https://github.com/hweichelt/tempxplain/examples/elevator) example of [tempxplain](https://github.com/hweichelt/tempxplain) for illustration.

### Plain Clingo Atoms

> The elevator is at floor `3` at time step `2`.

```tempql
holds(at(3),2)
```

> The elevator is not at floor `3` at time step `2`.

```tempql
-holds(at(3),2)
```

### Temporal Queries

> The elevator is at floor `3` at time step `2`.

```tempql
at(3) @ 2
```

> The elevator is either at floor `3` or `1` at time step `2`.

```tempql
at(3) | at(1) @ 2
```

> The elevator is either at floor `3` or `1` and `ready` at time step `2`.

```tempql
(at(3) | at(1)) & ready @ 2
```

#### With Temporal Operators

> At time step `2` the elevator was at floor `5` previously and will be at floor `7` next.

```tempql
P[at(5)] & X[at(7)] @ 2
```

> The elevator never visits the ground floor.

```tempql
G[-at(0)]
```

> Floor `4` was not served until floor `1` is.

```tempql
U[-served(4), served(1)]
```

> Floor `4` was served at or before time step `10`, and not called since.

```tempql
S[-called(4), served(4)] @ 10
```

### Multiple Queries

> The elevator is at floor `3` at time step `2` and never visits the ground floor.

```tempql
holds(at(3),2) ; G[-at(0)]
```
