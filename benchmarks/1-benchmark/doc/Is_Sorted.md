```{=org}
#+EXPORT_FILE_NAME: ../../../sorting/Is_Sorted.org
```
# The Is~Sorted~ algorithm

The `Is_Sorted` algorithm states if an array is sorted or not. Its
signature is the following:

``` ada
function Is_Sorted (A : T_Arr) return Boolean
```

## Specification of Is~Sorted~

The specification is simple to write:

``` ada
function Is_Sorted
  (A : T_Arr)
   return Boolean with
   Contract_Cases => (Sorted (A) => Is_Sorted'Result = True,
    others => Is_Sorted'Result = False);
```

## The Weakly~Sorted~ predicate and its lemma

The `Weakly_Sorted` predicate checks only the fact that each element
(except the last one) is less than the element just after it. It can be
expressed as follows:

``` ada
function Weakly_Sorted
  (A : T_Arr)
   return Boolean is
  (if A'Length > 0 then
     (for all J in A'First .. A'Last - 1 => A (J) <= A (J + 1)));
```

The `Weakly_Sorted` predicate implies the `Sorted` predicate, but the
prover cannot prove this implication on its own. We have to write a
lemma to prove it:

``` ada
procedure Weakly_To_Sorted (A : T_Arr) with
   Ghost,
   Pre  => Weakly_Sorted (A),
   Post => Sorted (A);
```

Its implementation is classic:

``` ada
procedure Weakly_To_Sorted (A : T_Arr) is
begin
   for J in A'Range loop
      null;
      pragma Loop_Invariant (Sorted (A (A'First .. J)));
   end loop;
end Weakly_To_Sorted;
```

## Implementation of Is~Sorted~

The implementation will check whether the array is weakly sorted or not.
If this is the case, we will apply our previous lemma and return `True`:

``` ada
function Is_Sorted
  (A : T_Arr)
   return Boolean
is
begin
   if A'Length > 0 then
      for J in A'First .. A'Last - 1 loop
   if A (J) > A (J + 1) then
      return False;
   end if;

   pragma Loop_Invariant (Weakly_Sorted (A (A'First .. J + 1)));

      end loop;
   end if;

   Weakly_To_Sorted (A);

   return True;
end Is_Sorted;
```

Everything is proved by `GNATprove`.
