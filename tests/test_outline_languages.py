import pytest

from llm_context.highlighter.outliner import generate_outlines
from llm_context.highlighter.parser import Source


@pytest.mark.parametrize(
    "language,extension,code,expected_highlights",
    [
        (
            "python",
            "py",
            """
def factorial(n: int) -> int:
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

class MathOperations:
    @staticmethod
    def square(x: float) -> float:
        return x * x

    def __init__(self, value: float):
        self.value = value

    def cube(self) -> float:
        return self.value ** 3

if __name__ == "__main__":
    math_op = MathOperations(3)
    print(f"Factorial of 5: {factorial(5)}")
    print(f"Square of 4: {MathOperations.square(4)}")
    print(f"Cube of 3: {math_op.cube()}")
""",
            """⋮...
█def factorial(n: int) -> int:
⋮...
█class MathOperations:
⋮...
█    def square(x: float) -> float:
⋮...
█    def __init__(self, value: float):
⋮...
█    def cube(self) -> float:
⋮...
""".strip(),
        ),
        (
            "javascript",
            "js",
            """
function factorial(n) {
    if (n === 0 || n === 1) return 1;
    return n * factorial(n - 1);
}

class MathOperations {
    static square(x) {
        return x * x;
    }

    constructor(value) {
        this.value = value;
    }

    cube() {
        return Math.pow(this.value, 3);
    }
}

const mathOp = new MathOperations(3);
console.log(`Factorial of 5: ${factorial(5)}`);
console.log(`Square of 4: ${MathOperations.square(4)}`);
console.log(`Cube of 3: ${mathOp.cube()}`);
""",
            """⋮...
█function factorial(n) {
⋮...
█class MathOperations {
█    static square(x) {
⋮...
█    cube() {
⋮...
""".strip(),
        ),
        (
            "typescript",
            "ts",
            """
function factorial(n: number): number {
    if (n === 0 || n === 1) return 1;
    return n * factorial(n - 1);
}

interface IMathOperations {
    cube(): number;
}

class MathOperations implements IMathOperations {
    static square(x: number): number {
        return x * x;
    }

    constructor(private value: number) {}

    cube(): number {
        return Math.pow(this.value, 3);
    }
}

const mathOp: IMathOperations = new MathOperations(3);
console.log(`Factorial of 5: ${factorial(5)}`);
console.log(`Square of 4: ${MathOperations.square(4)}`);
console.log(`Cube of 3: ${mathOp.cube()}`);
""",
            """⋮...
█function factorial(n: number): number {
⋮...
█interface IMathOperations {
█    cube(): number;
⋮...
█class MathOperations implements IMathOperations {
█    static square(x: number): number {
⋮...
█    constructor(private value: number) {}
⋮...
█    cube(): number {
⋮...
""".strip(),
        ),
        (
            "java",
            "java",
            """
public class MathOperations {
    public static int factorial(int n) {
        if (n == 0 || n == 1) return 1;
        return n * factorial(n - 1);
    }

    public static double square(double x) {
        return x * x;
    }

    private final double value;

    public MathOperations(double value) {
        this.value = value;
    }

    public double cube() {
        return Math.pow(this.value, 3);
    }

    public static void main(String[] args) {
        MathOperations mathOp = new MathOperations(3);
        System.out.println("Factorial of 5: " + factorial(5));
        System.out.println("Square of 4: " + square(4));
        System.out.println("Cube of 3: " + mathOp.cube());
    }
}
""",
            """⋮...
█public class MathOperations {
█    public static int factorial(int n) {
⋮...
█    public static double square(double x) {
⋮...
█    public double cube() {
⋮...
█    public static void main(String[] args) {
⋮...
""".strip(),
        ),
        (
            "c",
            "c",
            """
#include <stdio.h>
#include <math.h>

int factorial(int n) {
    if (n == 0 || n == 1) return 1;
    return n * factorial(n - 1);
}

double square(double x) {
    return x * x;
}

typedef struct {
    double value;
} MathOperations;

MathOperations create_math_operations(double value) {
    MathOperations mo = {value};
    return mo;
}

double cube(MathOperations* mo) {
    return pow(mo->value, 3);
}

int main() {
    MathOperations mo = create_math_operations(3);
    printf("Factorial of 5: %d\\n", factorial(5));
    printf("Square of 4: %f\\n", square(4));
    printf("Cube of 3: %f\\n", cube(&mo));
    return 0;
}
""",
            """⋮...
█int factorial(int n) {
⋮...
█double square(double x) {
⋮...
█} MathOperations;
⋮...
█MathOperations create_math_operations(double value) {
⋮...
█double cube(MathOperations* mo) {
⋮...
█int main() {
⋮...
""".strip(),
        ),
        (
            "cpp",
            "cpp",
            """
#include <iostream>
#include <cmath>

int factorial(int n) {
    if (n == 0 || n == 1) return 1;
    return n * factorial(n - 1);
}

class MathOperations {
public:
    static double square(double x) {
        return x * x;
    }

    MathOperations(double value) : value(value) {}

    double cube() const {
        return std::pow(value, 3);
    }

private:
    double value;
};

int main() {
    MathOperations mo(3);
    std::cout << "Factorial of 5: " << factorial(5) << std::endl;
    std::cout << "Square of 4: " << MathOperations::square(4) << std::endl;
    std::cout << "Cube of 3: " << mo.cube() << std::endl;
    return 0;
}
""",
            """⋮...
█int factorial(int n) {
⋮...
█class MathOperations {
⋮...
█    static double square(double x) {
⋮...
█    MathOperations(double value) : value(value) {}
⋮...
█    double cube() const {
⋮...
█int main() {
⋮...
""".strip(),
        ),
        (
            "csharp",
            "cs",
            """
using System;

public class MathOperations
{
    public static int Factorial(int n)
    {
        if (n == 0 || n == 1) return 1;
        return n * Factorial(n - 1);
    }

    public static double Square(double x) => x * x;

    private readonly double _value;

    public MathOperations(double value)
    {
        _value = value;
    }

    public double Cube() => Math.Pow(_value, 3);

    public static void Main(string[] args)
    {
        var mathOp = new MathOperations(3);
        Console.WriteLine($"Factorial of 5: {Factorial(5)}");
        Console.WriteLine($"Square of 4: {Square(4)}");
        Console.WriteLine($"Cube of 3: {mathOp.Cube()}");
    }
}
""",
            """⋮...
█public class MathOperations
⋮...
█    public static int Factorial(int n)
⋮...
█    public static double Square(double x) => x * x;
⋮...
█    public double Cube() => Math.Pow(_value, 3);
⋮...
█    public static void Main(string[] args)
⋮...
""".strip(),
        ),
        (
            "ruby",
            "rb",
            """
def factorial(n)
  return 1 if n == 0 || n == 1
  n * factorial(n - 1)
end

class MathOperations
  def self.square(x)
    x * x
  end

  def initialize(value)
    @value = value
  end

  def cube
    @value ** 3
  end
end

math_op = MathOperations.new(3)
puts "Factorial of 5: #{factorial(5)}"
puts "Square of 4: #{MathOperations.square(4)}"
puts "Cube of 3: #{math_op.cube}"
""",
            """⋮...
█def factorial(n)
⋮...
█class MathOperations
█  def self.square(x)
⋮...
█  def initialize(value)
⋮...
█  def cube
⋮...
""".strip(),
        ),
        (
            "go",
            "go",
            """
package main

import (
    "fmt"
    "math"
)

func factorial(n int) int {
    if n == 0 || n == 1 {
        return 1
    }
    return n * factorial(n-1)
}

type MathOperations struct {
    value float64
}

func (mo MathOperations) Cube() float64 {
    return math.Pow(mo.value, 3)
}

func Square(x float64) float64 {
    return x * x
}

func main() {
    mathOp := MathOperations{value: 3}
    fmt.Printf("Factorial of 5: %d\\n", factorial(5))
    fmt.Printf("Square of 4: %.2f\\n", Square(4))
    fmt.Printf("Cube of 3: %.2f\\n", mathOp.Cube())
}
""",
            """⋮...
█func factorial(n int) int {
⋮...
█type MathOperations struct {
⋮...
█func (mo MathOperations) Cube() float64 {
⋮...
█func Square(x float64) float64 {
⋮...
█func main() {
⋮...
""".strip(),
        ),
        (
            "rust",
            "rs",
            """
struct MathOperations {
    value: f64,
}

impl MathOperations {
    fn new(value: f64) -> Self {
        MathOperations { value }
    }

    fn cube(&self) -> f64 {
        self.value.powi(3)
    }
}

fn factorial(n: u64) -> u64 {
    match n {
        0 | 1 => 1,
        _ => n * factorial(n - 1),
    }
}

fn square(x: f64) -> f64 {
    x * x
}

fn main() {
    let math_op = MathOperations::new(3.0);
    println!("Factorial of 5: {}", factorial(5));
    println!("Square of 4: {}", square(4.0));
    println!("Cube of 3: {}", math_op.cube());
}
""",
            """⋮...
█struct MathOperations {
⋮...
█    fn new(value: f64) -> Self {
⋮...
█    fn cube(&self) -> f64 {
⋮...
█fn factorial(n: u64) -> u64 {
⋮...
█fn square(x: f64) -> f64 {
⋮...
█fn main() {
⋮...
""".strip(),
        ),
        (
            "php",
            "php",
            """
<?php

function factorial($n) {
    if ($n == 0 || $n == 1) return 1;
    return $n * factorial($n - 1);
}

class MathOperations {
    private $value;

    public function __construct($value) {
        $this->value = $value;
    }

    public static function square($x) {
        return $x * $x;
    }

    public function cube() {
        return pow($this->value, 3);
    }
}

$mathOp = new MathOperations(3);
echo "Factorial of 5: " . factorial(5) . "\\n";
echo "Square of 4: " . MathOperations::square(4) . "\\n";
echo "Cube of 3: " . $mathOp->cube() . "\\n";
""",
            """⋮...
█function factorial($n) {
⋮...
█class MathOperations {
⋮...
█    public function __construct($value) {
⋮...
█    public static function square($x) {
⋮...
█    public function cube() {
⋮...
""".strip(),
        ),
        (
            "ocaml",
            "ml",
            """
let rec factorial n =
  match n with
  | 0 | 1 -> 1
  | _ -> n * factorial (n - 1)

module MathOperations = struct
  let square x = x *. x

  type t = { value : float }

  let create value = { value }

  let cube t = t.value ** 3.0
end

let () =
  let math_op = MathOperations.create 3.0 in
  Printf.printf "Factorial of 5: %d\\n" (factorial 5);
  Printf.printf "Square of 4: %f\\n" (MathOperations.square 4.0);
  Printf.printf "Cube of 3: %f\\n" (MathOperations.cube math_op)
""",
            """⋮...
█let rec factorial n =
⋮...
█module MathOperations = struct
█  let square x = x *. x
⋮...
█  let create value = { value }
⋮...
█  let cube t = t.value ** 3.0
⋮...
""".strip(),
        ),
        (
            "elm",
            "elm",
            """
module MathOperations exposing (factorial, square, cube)

factorial : Int -> Int
factorial n =
    if n <= 1 then
        1
    else
        n * factorial (n - 1)

square : Float -> Float
square x =
    x * x

type MathOp =
    MathOp Float

cube : MathOp -> Float
cube (MathOp value) =
    value ^ 3

main =
    let
        mathOp =
            MathOp 3
    in
    [ "Factorial of 5: " ++ String.fromInt (factorial 5)
    , "Square of 4: " ++ String.fromFloat (square 4)
    , "Cube of 3: " ++ String.fromFloat (cube mathOp)
    ]
        |> String.join "\\n"
        |> Debug.log "Results"
""",
            """⋮...
█module MathOperations exposing (factorial, square, cube)
⋮...
█factorial n =
⋮...
█square x =
⋮...
█type MathOp =
█    MathOp Float
⋮...
█cube (MathOp value) =
⋮...
█main =
⋮...
█        mathOp =
⋮...
""".strip(),
        ),
        (
            "elixir",
            "ex",
            """
defmodule MathOperations do
  def factorial(0), do: 1
  def factorial(1), do: 1
  def factorial(n) when n > 1, do: n * factorial(n - 1)

  def square(x), do: x * x

  defstruct [:value]

  def new(value), do: %__MODULE__{value: value}

  def cube(%__MODULE__{value: value}), do: :math.pow(value, 3)
end

math_op = MathOperations.new(3)

IO.puts "Factorial of 5: #{MathOperations.factorial(5)}"
IO.puts "Square of 4: #{MathOperations.square(4)}"
IO.puts "Cube of 3: #{MathOperations.cube(math_op)}"
""",
            """⋮...
█defmodule MathOperations do
█  def factorial(0), do: 1
█  def factorial(1), do: 1
█  def factorial(n) when n > 1, do: n * factorial(n - 1)
⋮...
█  def square(x), do: x * x
⋮...
█  def new(value), do: %__MODULE__{value: value}
⋮...
█  def cube(%__MODULE__{value: value}), do: :math.pow(value, 3)
⋮...
""".strip(),
        ),
        (
            "elisp",
            "el",
            """
(defun factorial (n)
  (if (<= n 1)
      1
    (* n (factorial (- n 1)))))

(defun square (x)
  (* x x))

(defstruct math-operations
  value)

(defun create-math-operations (value)
  (make-math-operations :value value))

(defun cube (math-op)
  (expt (math-operations-value math-op) 3))

(let ((math-op (create-math-operations 3)))
  (message "Factorial of 5: %d" (factorial 5))
  (message "Square of 4: %f" (square 4))
  (message "Cube of 3: %f" (cube math-op)))
""",
            """⋮...
█(defun factorial (n)
⋮...
█(defun square (x)
⋮...
█(defun create-math-operations (value)
⋮...
█(defun cube (math-op)
⋮...
""".strip(),
        ),
        (
            "ql",
            "ql",
            """
import javascript

int factorial(int n) {
  if (n <= 1) then result = 1
  else result = n * factorial(n - 1)
}

float square(float x) {
  result = x * x
}

class MathOperations extends @class {
  float value;
  
  MathOperations() { this.value = 0; }
  
  float cube() { result = Math::pow(this.value, 3); }
}

from MathOperations mo, Function f
where 
  f.getName() = "factorial" or
  f.getName() = "square" or
  mo.getAMethod().getName() = "cube"
select f.getName(), mo.getAMethod().getName()
""",
            """⋮...
█int factorial(int n) {
⋮...
█float square(float x) {
⋮...
█class MathOperations extends @class {
⋮...
█  float cube() { result = Math::pow(this.value, 3); }
⋮...
""".strip(),
        ),
    ],
)
def test_outline_generation(language, extension, code, expected_highlights):
    source = Source(f"test_file.{extension}", code)
    outlines = generate_outlines([source])

    assert len(outlines) == 1
    assert outlines[0]["rel_path"] == f"test_file.{extension}"
    assert "highlights" in outlines[0]

    actual_highlights = outlines[0]["highlights"].strip()
    assert (
        actual_highlights == expected_highlights
    ), f"Mismatch in {language} highlights:\nExpected:\n{expected_highlights}\n\nActual:\n{actual_highlights}"
