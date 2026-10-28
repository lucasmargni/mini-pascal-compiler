program repetitiva;
var i, s, f: integer;
begin
  i := 1;
  s := 0;
  f := 1;
  while (i <= 5) do
  begin
    s := s + i;
    f := f * i;
    i := i + 1
  end;
  write(s);
  write(f)
end.
