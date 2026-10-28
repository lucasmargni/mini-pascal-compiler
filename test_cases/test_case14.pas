program anidamiento;
var g: integer;
procedure outer(a: integer; b: boolean);
var x, y: integer;
  procedure inner(c: integer);
  var g: integer;
  begin
    g := 100;
    x := x + c + a;
    write(g)
  end;
begin
  x := 1;
  y := 0;
  inner(10);
  if (b) then write(x);
  g := g + x
end;
begin
  g := 5;
  outer(2, true);
  write(g)
end.
