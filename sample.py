#!/usr/bin/env python3
"""
Sample Python File - Demonstrating Basic Python Concepts

This file serves as a comprehensive example of Python programming,
showcasing various language features and best practices.

Author: Sample
Date: 2024
"""

import math
import random
from typing import List, Dict, Optional


class Calculator:
    """A simple calculator class demonstrating object-oriented programming."""
    
    def __init__(self, name: str = "Basic Calculator"):
        """Initialize the calculator with a name."""
        self.name = name
        self.history: List[str] = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers and record the operation."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers and record the operation."""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def get_history(self) -> List[str]:
        """Return the calculation history."""
        return self.history.copy()


def demonstrate_data_structures() -> Dict[str, any]:
    """Demonstrate various Python data structures."""
    
    # Lists and list comprehensions
    numbers = [1, 2, 3, 4, 5]
    squares = [x**2 for x in numbers]
    
    # Dictionaries
    student_grades = {
        "Alice": 95,
        "Bob": 87,
        "Charlie": 92
    }
    
    # Sets
    unique_letters = set("hello world")
    
    # Tuples
    coordinates = (10, 20)
    
    return {
        "numbers": numbers,
        "squares": squares,
        "grades": student_grades,
        "unique_letters": unique_letters,
        "coordinates": coordinates
    }


def string_operations() -> None:
    """Demonstrate string operations and formatting."""
    
    name = "Python"
    version = 3.9
    
    # String formatting methods
    print(f"Welcome to {name} {version}!")
    print("Welcome to {} {}!".format(name, version))
    print("Welcome to %s %.1f!" % (name, version))
    
    # String methods
    text = "  Hello, World!  "
    print(f"Original: '{text}'")
    print(f"Stripped: '{text.strip()}'")
    print(f"Upper: '{text.upper()}'")
    print(f"Lower: '{text.lower()}'")


def file_and_exception_handling() -> Optional[str]:
    """Demonstrate file operations and exception handling."""
    
    try:
        # Create a temporary file for demonstration
        content = "This is a sample file content.\nPython is awesome!"
        
        # Writing to file
        with open("/tmp/sample.txt", "w") as file:
            file.write(content)
        
        # Reading from file
        with open("/tmp/sample.txt", "r") as file:
            file_content = file.read()
        
        return file_content
        
    except FileNotFoundError:
        print("File not found!")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def mathematical_operations() -> None:
    """Demonstrate mathematical operations and the math module."""
    
    # Basic math operations
    print("Mathematical Operations:")
    print(f"Square root of 16: {math.sqrt(16)}")
    print(f"Pi: {math.pi:.4f}")
    print(f"Euler's number: {math.e:.4f}")
    
    # Random numbers
    print(f"Random integer (1-10): {random.randint(1, 10)}")
    print(f"Random float: {random.random():.4f}")


def lambda_and_higher_order_functions() -> None:
    """Demonstrate lambda functions and higher-order functions."""
    
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Lambda functions with map, filter, reduce
    squares = list(map(lambda x: x**2, numbers))
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    
    print("Lambda and Higher-Order Functions:")
    print(f"Original numbers: {numbers}")
    print(f"Squares: {squares}")
    print(f"Even numbers: {evens}")


def main() -> None:
    """Main function demonstrating the sample Python features."""
    
    print("=" * 50)
    print("PYTHON SAMPLE FILE DEMONSTRATION")
    print("=" * 50)
    
    # Object-oriented programming
    print("\n1. Object-Oriented Programming:")
    calc = Calculator("Demo Calculator")
    result1 = calc.add(10, 5)
    result2 = calc.multiply(3, 7)
    print(f"Calculator name: {calc.name}")
    print(f"Addition result: {result1}")
    print(f"Multiplication result: {result2}")
    print(f"History: {calc.get_history()}")
    
    # Data structures
    print("\n2. Data Structures:")
    data = demonstrate_data_structures()
    for key, value in data.items():
        print(f"{key}: {value}")
    
    # String operations
    print("\n3. String Operations:")
    string_operations()
    
    # File operations
    print("\n4. File Operations:")
    file_content = file_and_exception_handling()
    if file_content:
        print(f"File content:\n{file_content}")
    
    # Mathematical operations
    print("\n5. Mathematical Operations:")
    mathematical_operations()
    
    # Lambda functions
    print("\n6. Lambda Functions:")
    lambda_and_higher_order_functions()
    
    print("\n" + "=" * 50)
    print("DEMONSTRATION COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()