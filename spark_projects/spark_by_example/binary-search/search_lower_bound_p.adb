package body Search_Lower_Bound_P with
   Spark_Mode
 is

   function Search_Lower_Bound
     (A : T_Arr;
      V : T)
      return Option
   is

      Result : Option  := (Exists => False);
      Right  : Integer := A'Last + 1;
      Middle : Integer := A'Last + 1;
   begin

      if A'Length = 0 then
         return Result;
      else
         Result := (Exists => True, Value => A'First);

         while Result.Value < Right loop
            Middle := Result.Value + (Right - Result.Value) / 2;
            if A (Middle) < V then
               Result.Value := Middle + 1;
            else
               Right := Middle;
            end if;

            pragma Loop_Variant (Decreases => Right - Result.Value);
            
            -- Put invariants here

         end loop;

         return Result;
      end if;
   end Search_Lower_Bound;
end Search_Lower_Bound_P;