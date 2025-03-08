import pytest

from llm_context.highlighter.parser import Source
from llm_context.highlighter.tagger import ASTBasedTagger

TEST_CASES = [
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
        [
            "def factorial(n: int) -> int:\n    if n == 0 or n == 1:\n        return 1\n    return n * factorial(n - 1)",
            "class MathOperations:\n    @staticmethod\n    def square(x: float) -> float:\n        return x * x\n\n    def __init__(self, value: float):\n        self.value = value\n\n    def cube(self) -> float:\n        return self.value ** 3",
            "def square(x: float) -> float:\n        return x * x",
            "def __init__(self, value: float):\n        self.value = value",
            "def cube(self) -> float:\n        return self.value ** 3",
        ],
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
        [
            "function factorial(n) {\n    if (n === 0 || n === 1) return 1;\n    return n * factorial(n - 1);\n}",
            "class MathOperations {\n    static square(x) {\n        return x * x;\n    }\n\n    constructor(value) {\n        this.value = value;\n    }\n\n    cube() {\n        return Math.pow(this.value, 3);\n    }\n}",
            "static square(x) {\n        return x * x;\n    }",
            "constructor(value) {\n        this.value = value;\n    }",
            "cube() {\n        return Math.pow(this.value, 3);\n    }",
        ],
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
        [
            "function factorial(n: number): number {\n    if (n === 0 || n === 1) return 1;\n    return n * factorial(n - 1);\n}",
            "interface IMathOperations {\n    cube(): number;\n}",
            "class MathOperations implements IMathOperations {\n    static square(x: number): number {\n        return x * x;\n    }\n\n    constructor(private value: number) {}\n\n    cube(): number {\n        return Math.pow(this.value, 3);\n    }\n}",
            "static square(x: number): number {\n        return x * x;\n    }",
            "constructor(private value: number) {}",
            "cube(): number {\n        return Math.pow(this.value, 3);\n    }",
        ],
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
        [
            'public class MathOperations {\n    public static int factorial(int n) {\n        if (n == 0 || n == 1) return 1;\n        return n * factorial(n - 1);\n    }\n\n    public static double square(double x) {\n        return x * x;\n    }\n\n    private final double value;\n\n    public MathOperations(double value) {\n        this.value = value;\n    }\n\n    public double cube() {\n        return Math.pow(this.value, 3);\n    }\n\n    public static void main(String[] args) {\n        MathOperations mathOp = new MathOperations(3);\n        System.out.println("Factorial of 5: " + factorial(5));\n        System.out.println("Square of 4: " + square(4));\n        System.out.println("Cube of 3: " + mathOp.cube());\n    }\n}',
            "public static int factorial(int n) {\n        if (n == 0 || n == 1) return 1;\n        return n * factorial(n - 1);\n    }",
            "public static double square(double x) {\n        return x * x;\n    }",
            "public double cube() {\n        return Math.pow(this.value, 3);\n    }",
            'public static void main(String[] args) {\n        MathOperations mathOp = new MathOperations(3);\n        System.out.println("Factorial of 5: " + factorial(5));\n        System.out.println("Square of 4: " + square(4));\n        System.out.println("Cube of 3: " + mathOp.cube());\n    }',
        ],
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
        [
            "int factorial(int n) {\n    if (n == 0 || n == 1) return 1;\n    return n * factorial(n - 1);\n}",
            "double square(double x) {\n    return x * x;\n}",
            "MathOperations create_math_operations(double value) {\n    MathOperations mo = {value};\n    return mo;\n}",
            "double cube(MathOperations* mo) {\n    return pow(mo->value, 3);\n}",
            'int main() {\n    MathOperations mo = create_math_operations(3);\n    printf("Factorial of 5: %d\\n", factorial(5));\n    printf("Square of 4: %f\\n", square(4));\n    printf("Cube of 3: %f\\n", cube(&mo));\n    return 0;\n}',
        ],
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
        [
            "int factorial(int n) {\n    if (n == 0 || n == 1) return 1;\n    return n * factorial(n - 1);\n}",
            "class MathOperations {\npublic:\n    static double square(double x) {\n        return x * x;\n    }\n\n    MathOperations(double value) : value(value) {}\n\n    double cube() const {\n        return std::pow(value, 3);\n    }\n\nprivate:\n    double value;\n}",
            "static double square(double x) {\n        return x * x;\n    }",
            "MathOperations(double value) : value(value) {}",
            "double cube() const {\n        return std::pow(value, 3);\n    }",
            'int main() {\n    MathOperations mo(3);\n    std::cout << "Factorial of 5: " << factorial(5) << std::endl;\n    std::cout << "Square of 4: " << MathOperations::square(4) << std::endl;\n    std::cout << "Cube of 3: " << mo.cube() << std::endl;\n    return 0;\n}',
        ],
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
        [
            'public class MathOperations\n{\n    public static int Factorial(int n)\n    {\n        if (n == 0 || n == 1) return 1;\n        return n * Factorial(n - 1);\n    }\n\n    public static double Square(double x) => x * x;\n\n    private readonly double _value;\n\n    public MathOperations(double value)\n    {\n        _value = value;\n    }\n\n    public double Cube() => Math.Pow(_value, 3);\n\n    public static void Main(string[] args)\n    {\n        var mathOp = new MathOperations(3);\n        Console.WriteLine($"Factorial of 5: {Factorial(5)}");\n        Console.WriteLine($"Square of 4: {Square(4)}");\n        Console.WriteLine($"Cube of 3: {mathOp.Cube()}");\n    }\n}',
            "public static int Factorial(int n)\n    {\n        if (n == 0 || n == 1) return 1;\n        return n * Factorial(n - 1);\n    }",
            'public static void Main(string[] args)\n    {\n        var mathOp = new MathOperations(3);\n        Console.WriteLine($"Factorial of 5: {Factorial(5)}");\n        Console.WriteLine($"Square of 4: {Square(4)}");\n        Console.WriteLine($"Cube of 3: {mathOp.Cube()}");\n    }',
        ],
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
        [
            "def factorial(n)\n  return 1 if n == 0 || n == 1\n  n * factorial(n - 1)\nend",
            "class MathOperations\n  def self.square(x)\n    x * x\n  end\n\n  def initialize(value)\n    @value = value\n  end\n\n  def cube\n    @value ** 3\n  end\nend",
            "def self.square(x)\n    x * x\n  end",
            "def initialize(value)\n    @value = value\n  end",
            "def cube\n    @value ** 3\n  end",
        ],
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
        [
            "func factorial(n int) int {\n    if n == 0 || n == 1 {\n        return 1\n    }\n    return n * factorial(n-1)\n}",
            "MathOperations struct {\n    value float64\n}",
            "func (mo MathOperations) Cube() float64 {\n    return math.Pow(mo.value, 3)\n}",
            "func Square(x float64) float64 {\n    return x * x\n}",
            'func main() {\n    mathOp := MathOperations{value: 3}\n    fmt.Printf("Factorial of 5: %d\\n", factorial(5))\n    fmt.Printf("Square of 4: %.2f\\n", Square(4))\n    fmt.Printf("Cube of 3: %.2f\\n", mathOp.Cube())\n}',
        ],
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
        [
            "struct MathOperations {\n    value: f64,\n}",
            "fn new(value: f64) -> Self {\n        MathOperations { value }\n    }",
            "fn cube(&self) -> f64 {\n        self.value.powi(3)\n    }",
            "fn factorial(n: u64) -> u64 {\n    match n {\n        0 | 1 => 1,\n        _ => n * factorial(n - 1),\n    }\n}",
            "fn square(x: f64) -> f64 {\n    x * x\n}",
            'fn main() {\n    let math_op = MathOperations::new(3.0);\n    println!("Factorial of 5: {}", factorial(5));\n    println!("Square of 4: {}", square(4.0));\n    println!("Cube of 3: {}", math_op.cube());\n}',
        ],
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
        [
            "function factorial($n) {\n    if ($n == 0 || $n == 1) return 1;\n    return $n * factorial($n - 1);\n}",
            "class MathOperations {\n    private $value;\n\n    public function __construct($value) {\n        $this->value = $value;\n    }\n\n    public static function square($x) {\n        return $x * $x;\n    }\n\n    public function cube() {\n        return pow($this->value, 3);\n    }\n}",
            "public function __construct($value) {\n        $this->value = $value;\n    }",
            "public static function square($x) {\n        return $x * $x;\n    }",
            "public function cube() {\n        return pow($this->value, 3);\n    }",
        ],
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
        [
            "factorial n =\n    if n <= 1 then\n        1\n    else\n        n * factorial (n - 1)",
            "square x =\n    x * x",
            "cube (MathOp value) =\n    value ^ 3",
            'main =\n    let\n        mathOp =\n            MathOp 3\n    in\n    [ "Factorial of 5: " ++ String.fromInt (factorial 5)\n    , "Square of 4: " ++ String.fromFloat (square 4)\n    , "Cube of 3: " ++ String.fromFloat (cube mathOp)\n    ]\n        |> String.join "\\n"\n        |> Debug.log "Results"',
        ],
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
        [
            "defmodule MathOperations do\n  def factorial(0), do: 1\n  def factorial(1), do: 1\n  def factorial(n) when n > 1, do: n * factorial(n - 1)\n\n  def square(x), do: x * x\n\n  defstruct [:value]\n\n  def new(value), do: %__MODULE__{value: value}\n\n  def cube(%__MODULE__{value: value}), do: :math.pow(value, 3)\nend",
        ],
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
        [
            "(defun factorial (n)\n  (if (<= n 1)\n      1\n    (* n (factorial (- n 1)))))",
            "(defun square (x)\n  (* x x))",
            "(defun create-math-operations (value)\n  (make-math-operations :value value))",
            "(defun cube (math-op)\n  (expt (math-operations-value math-op) 3))",
        ],
    ),
]


@pytest.fixture
def tagger():
    from llm_context.highlighter.parser import ASTFactory

    return ASTBasedTagger.create("", ASTFactory.create())


@pytest.mark.parametrize("language,extension,code,expected_bodies", TEST_CASES)
def test_body_extraction(language, extension, code, expected_bodies, tagger):
    source = Source(f"test_file.{extension}", code)
    definitions = tagger.extract_definitions(source, with_body=True)

    # Extract the text of all definitions
    actual_bodies = [defn.text for defn in definitions if defn.text]

    # Ensure the number of definitions matches
    assert len(actual_bodies) == len(expected_bodies), (
        f"Mismatch in number of definitions for {language}: "
        f"Expected {len(expected_bodies)}, got {len(actual_bodies)}"
    )

    # Check each expected body is present in actual bodies
    for expected in expected_bodies:
        assert any(actual.strip() == expected.strip() for actual in actual_bodies), (
            f"Definition not found in {language}:\nExpected:\n{expected}\n\nActual:\n{actual_bodies}"
        )
