program testCase2;

var
  counter: integer;
  limit: integer;
  isEven: boolean;

begin
  counter := 0;
  limit := 5;

  while (counter < limit) do
  begin
    if (counter mod 2 = 0) then
      isEven := true
    else
      isEven := false;

    write(counter);
    counter := counter + 1;
  end;
end.