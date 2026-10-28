program booleanos;
var x, y: integer;
    p, q: boolean;
begin
  x := 3;
  y := 7;
  p := x < y;
  q := not p or (x = y);
  write(p);
  write(q);
  if (p and not q) then write(1) else write(0);
  write(x <= 3);
  write(x <> 3)
end.
