with Types; use Types;

package body Sorted_P with
   Spark_Mode,
   Ghost
 is

    function Weakly_Sorted
      (A : T_Arr)
      return Boolean 
    is
      (for all J in A'First .. A'Last - 1 => A (J) <= A (J + 1));

    function Sorted
      (A : T_Arr)
      return Boolean 
    is
      (for all J in A'First .. A'Last - 1 => A (J) < A (J + 1));

end Sorted_P;