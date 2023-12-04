```{=org}
#+EXPORT_FILE_NAME: ../../../mutating/Swap.org
```
# The Swap algorithm

The `Swap` algorithm exchanges the contents of two variables. Its
signature can be expressed as:

``` ada
procedure Swap (P : in out T; Q : in out T);
```

## Specification of Swap

The specification of `Swap` is the following:

``` ada
procedure Swap
  (P : in out T;
   Q : in out T) with
   Post => P = Q'Old and then Q = P'Old;
```

The postcondition expresses the fact that the two variables have
actually been exchanged, using the `Old` attribute available in SPARK.
This attribute stores the state of the variables **before** the
execution of the procedure.

## Implementation of Swap

The implementation of `Swap` is:

``` ada
procedure Swap
  (P : in out T;
   Q : in out T)
is
   Save : T := P;
begin
   P := Q;
   Q := Save;
end Swap;
```

A memory variable is used to store the value of `P`. Using `GNATprove`,
everything is proved.
