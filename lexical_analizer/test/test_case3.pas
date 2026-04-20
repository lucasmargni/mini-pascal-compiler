program testCase3;

var
  x, y: integer;
  result: integer;

procedure multiply(a, b: integer);
var
  temp: integer;
begin
  temp := a * b;
  write(temp);
end;

function isGreater(a, b: integer): boolean;
begin
  if (a > b) then
    isGreater := true
  else
    isGreater := false;
end;

begin
  x := 3;
  y := 4;

  multiply(x, y);

  if (isGreater(y, x)) then
    result := y
  else
    result := x;

  write(result);
end.