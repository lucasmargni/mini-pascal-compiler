program llamadas;
var base: integer;
function siguiente: integer;
begin
  base := base + 1;
  siguiente := base
end;
function doble(x: integer): integer;
begin
  doble := x * 2
end;
begin
  base := 0;
  write(doble(siguiente));
  write(doble(doble(siguiente) + 1));
  write(base)
end.
