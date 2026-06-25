import ast
import os
import sys
from pathlib import Path

def check_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        print(f"Syntax Error in {filepath}: {e}")
        return []

    errors = []
    
    # Simple AST node checker
    class Checker(ast.NodeVisitor):
        def __init__(self):
            self.imports = set()
            self.defined_names = set()
            self.undefined_references = []
            self.current_function = None

        def visit_Import(self, node):
            for alias in node.names:
                self.imports.add(alias.asname or alias.name)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            for alias in node.names:
                self.imports.add(alias.asname or alias.name)
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            old_func = self.current_function
            self.current_function = node.name
            # Arguments are defined
            for arg in node.args.args:
                self.defined_names.add(arg.arg)
            self.generic_visit(node)
            self.current_function = old_func

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.defined_names.add(target.id)
            self.generic_visit(node)

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load):
                name = node.id
                # Builtins, imports, and self-defined names are fine
                if name not in self.imports and name not in self.defined_names and name not in dir(__builtins__):
                    # We might have false positives for standard modules or dynamic definitions,
                    # but it's a good check.
                    self.undefined_references.append((node.lineno, name))
            self.generic_visit(node)

    checker = Checker()
    checker.visit(tree)
    
    # Check for specific known attribute references like database.load_config
    # We will search the source content for patterns
    lines = content.splitlines()
    for i, line in enumerate(lines):
        lineno = i + 1
        if "filter_type=" in line and "get_all_riwayat" in line:
            errors.append((lineno, "get_all_riwayat uses 'filter_time' keyword argument, not 'filter_type'"))
            
    return errors

def main():
    py_files = list(Path(".").glob("*.py")) + list(Path("ui").glob("*.py"))
    all_errors = {}
    for f in py_files:
        errors = check_file(f)
        if errors:
            all_errors[str(f)] = errors

    print("--- LINTER ANALYSIS RESULTS ---")
    if not all_errors:
        print("No automated attribute/keyword errors found.")
    for f, errs in all_errors.items():
        print(f"\nFile: {f}")
        for lineno, msg in errs:
            print(f"  Line {lineno}: {msg}")

if __name__ == "__main__":
    main()
