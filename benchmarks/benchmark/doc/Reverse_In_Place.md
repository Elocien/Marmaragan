```{=org}
#+EXPORT_FILE_NAME: ../../../mutating/Reverse_In_Place.org
```
# The Reverse~InPlace~ algorithm

The `Reverse_In_Place` algorithm aims to achieve the same goal as
[*Reverse~Copy~*]{.spurious-link target="Reverse_Copy.org"} but the
result is stored in the original array, thus modifying it, instead of
copying it. Its signature reads:

``` ada
procedure Reverse_In_Place (A : in out T_Arr);
```

## Specification of Reverse~InPlace~

`Reverse_In_Place` can be specified as follows:

``` ada
procedure Reverse_In_Place (A : in out T_Arr) with
   Post => Is_Reversed (A, A'Old);
```

The postcondition ensures that `A` is indeed reversed at the end of the
procedure compared to its state at the beginning of the procedure (using
the `Old` attribute).

## Implementation of Reverse~InPlace~

### A first version using Swap

`Reverse_In_Place` can be implemented using the [*Swap*]{.spurious-link
target="Swap.org"} function defined earlier:

``` ada
procedure Reverse_In_Place (A : in out T_Arr) is
   Half : Positive :=
     (if A'Length > 1 then
  A'First + (A'Last - A'First) / 2 -
  (if A'Length mod 2 = 0 then 0 else 1)
      else 1);
begin

   if A'Length <= 1 then
      return;
   end if;

   for J in 0 .. Half - A'First loop

      pragma Assert (A'First + J /= A'Last - J);
      Swap (A (A'First + J), A (A'Last - J));

      pragma Loop_Variant (Increases => J);
      pragma Loop_Invariant
  (A (A'First + J + 1 .. A'Last - (J + 1)) =
   A'Loop_Entry (A'First + J + 1 .. A'Last - (J + 1)));
      pragma Loop_Invariant
  (Is_Reversed
     (A (A'First .. A'First + J),
      A'Loop_Entry (A'Last - J .. A'Last)));
      pragma Loop_Invariant
  (Is_Reversed
     (A'Loop_Entry (A'First .. A'First + J),
      A (A'Last - J .. A'Last)));

   end loop;

end Reverse_In_Place;
```

There are a few things to point out here:

-   `Half` is calculated so that if `A` has an odd length then we do not
    try to swap the middle value with itself. This helps avoid aliasing
    issues.
-   the first loop invariant specifies that the array remains unchanged
    in the `A'Length - 2 * J` middle indexes, which the algorithm has
    not yet covered at iteration `J`
-   the two other invariants specify that the sub-arrays `A(A'First
            .. A'First + J)` and `A(A'Last - J .. A'Last)` are reversed
    compared to the arrays before entering the loop.

With this implementation, `GNATprove` manages to prove everything but
one thing: it cannot verify that `A (A'First + J)` and `A
     (A'Last - J)` are not aliased (see [SPARK reference manual section
6.4.2](http://docs.adacore.com/spark2014-docs/html/lrm/subprograms.html#anti-aliasing)):

``` shell
reverse_in_place_swap_p.adb:23:15: medium: formal parameters "P" and "Q" might be aliased (SPARK RM 6.4.2)
```

Notice that even if the assertion `A'First + J /= A'Last - J` placed
before the call to `Swap` proves the absence of aliasing, `GNATprove`
emits the error message.

### Avoiding the aliasing

In order to avoid the aliasing issue, it is possible to modify the
implementation of `Reverse_In_Place` by removing the call to `Swap` and
doing the swap \"manually\" with an extra variable:

``` ada
procedure Reverse_In_Place (A : in out T_Arr) is
   Half : Positive :=
     (if A'Length > 1 then
  A'First + (A'Last - A'First) / 2 -
  (if A'Length mod 2 = 0 then 0 else 1)
      else 1);
   T1 : T;
begin

   if A'Length <= 1 then
      return;
   end if;

   for J in 0 .. Half - A'First loop
      T1              := A (A'First + J);
      A (A'First + J) := A (A'Last - J);
      A (A'Last - J)  := T1;

      pragma Loop_Variant (Increases => J);
      pragma Loop_Invariant
  (A (A'First + J + 1 .. A'Last - (J + 1)) =
   A'Loop_Entry (A'First + J + 1 .. A'Last - (J + 1)));
      pragma Loop_Invariant
  (Is_Reversed
     (A (A'First .. A'First + J),
      A'Loop_Entry (A'Last - J .. A'Last)));
      pragma Loop_Invariant
  (Is_Reversed
     (A'Loop_Entry (A'First .. A'First + J),
      A (A'Last - J .. A'Last)));

   end loop;

end Reverse_In_Place;
```

This implementation enables `GNATprove` to prove everything.
