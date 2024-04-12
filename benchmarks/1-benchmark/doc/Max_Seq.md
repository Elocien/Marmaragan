```{=org}
#+EXPORT_FILE_NAME: ../../../maxmin/Max_Seq.org
```
# The Max~Seq~ algorithm

The `Max_Seq` algorithm returns the maximum value contained in an array.

Its signature can be defined as:

``` ada
function Max_Seq (A : T_Arr) return T;
```

This algorithm will use the previous `Max_Element` algorithm, therefore
it will be easy to write.

## Specification of Max~Seq~

``` ada
function Max_Seq
  (A : T_Arr)
   return T with
   Pre  => A'Length > 0,
   Post => (Has_Value (A, Max_Seq'Result))
   and then (Upper_Bound (A, Max_Seq'Result));
```

Because we are going to use the function `Max_Element` on `A` and want
to use the `Value` field of option, we forbid the case `A'Length = 0`.
This is expressed as a precondition.

The postconditions express the fact that

-   the value in contained in the array
-   the value returned is more or equal than the others values contained
    in the array.

## Implementation of Max~Seq~

``` ada
function Max_Seq
  (A : T_Arr)
   return T
is
begin
   return A (Max_Element (A).Value);
end Max_Seq;
```

The specification of `Max_Element` is sufficient to prove the `Max_Seq`
algorithm with `GNATprove`.
