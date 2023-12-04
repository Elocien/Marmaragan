```{=org}
#+EXPORT_FILE_NAME: ../../../mutating/Rotate.org
```
# The Rotate algorithm

The `Rotate` Algorithm aims to achieve the same goal as the
[*Rotate~Copy~*]{.spurious-link target="Rotate_Copy.org"} algorithm, but
instead of storing the result in another array, it does the shift in
place:

``` ada
procedure Rotate (A : in out T_Arr, N : Positive)
```

## Specification of Rotate

Since `Rotate` is quite similar to `Rotate_Copy`, their specifications
do not differ greatly. `Rotate` can be specified as follows:

``` ada
procedure Rotate
  (A : in out T_Arr;
   N :        Positive) with
   Pre  => N < A'Length,
   Post => A'Old (A'First .. A'First + (N - 1)) =
   A (A'Last - (N - 1) .. A'Last)
   and then A'Old (A'First + N .. A'Last) = A (A'First .. A'Last - N);
```

The postcondition expresses that the first `N` elments of `A` before the
procedure become the last `N` elements after the call, and the
`A'Length - N` last elements of `A` before the procedure become the N
first after the procedure.

## Implementation of Rotate

As in [ACSL by
Example](https://github.com/fraunhoferfokus/acsl-by-example), `Rotate`
is implemented to benefit from the [*Reverse~InPlace~*]{.spurious-link
target="Reverse_In_Place.org"} procedure, making the procedure easy and
compact:

``` ada
procedure Rotate
  (A : in out T_Arr;
   N :        Positive)
is
begin
   Reverse_In_Place (A (A'First .. A'First + (N - 1)));
   Reverse_In_Place (A (A'First + N .. A'Last));
   Reverse_In_Place (A);
end Rotate;
```

`GNATprove` doesn\'t need any additional annotations in order to prove
everything.
