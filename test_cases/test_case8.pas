program aritmetica;
var a, b, c: integer;
begin
  a := 17;
  b := 5;
  write(a + b * 2);
  write((a + b) * 2);
  write(a div b);
  write(a - b - 2);
  c := -a + b;
  write(c);
  write(-(b - a))
end.
