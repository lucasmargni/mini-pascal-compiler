program procedimientos;
procedure mostrar(a, b: integer; ok: boolean);
var suma, resta: integer;
begin
  suma := a + b;
  resta := a - b;
  if (ok) then write(suma) else write(resta)
end;
begin
  mostrar(10, 4, true);
  mostrar(10, 4, false)
end.
