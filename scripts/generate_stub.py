#!/usr/bin/env python3
"""
scripts/generate_stub.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Generate basic .pyi type stub files for roboat modules.
Helps IDEs provide autocomplete for roboat users.

Run: python scripts/generate_stub.py
Output: roboat/*.pyi
"""

import ast
import os
import sys
import textwrap


def extract_stubs(source: str) -> str:
    """Extract function signatures and class definitions from Python source."""
    tree = ast.parse(source)
    lines = source.splitlines()
    stubs = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Collect class with its methods
            class_lines = [f"class {node.name}:"]
            has_methods = False

            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    has_methods = True
                    args = []
                    for arg in item.args.args:
                        if arg.annotation:
                            ann = ast.unparse(arg.annotation)
                            args.append(f"{arg.arg}: {ann}")
                        else:
                            args.append(arg.arg)

                    returns = ""
                    if item.returns:
                        returns = f" -> {ast.unparse(item.returns)}"

                    prefix = "async def" if isinstance(item, ast.AsyncFunctionDef) else "def"
                    sig = f"    {prefix} {item.name}({', '.join(args)}){returns}: ..."

                    # Add docstring as comment if present
                    if (item.body and isinstance(item.body[0], ast.Expr)
                            and isinstance(item.body[0].value, ast.Constant)):
                        doc = item.body[0].value.value
                        first_line = doc.strip().split("\n")[0]
                        class_lines.append(f"    # {first_line}")

                    class_lines.append(sig)

            if has_methods:
                stubs.extend(class_lines)
                stubs.append("")

    return "\n".join(stubs)


def generate_stubs(src_dir: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    for fname in sorted(os.listdir(src_dir)):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue

        src_path = os.path.join(src_dir, fname)
        out_path = os.path.join(out_dir, fname.replace(".py", ".pyi"))

        with open(src_path, encoding="utf-8") as f:
            source = f.read()

        try:
            stubs = extract_stubs(source)
            if stubs.strip():
                header = f'# Auto-generated stub for roboat.{fname[:-3]}\n# Do not edit manually.\n\n'
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(header + stubs)
                print(f"  Generated: {out_path}")
        except Exception as e:
            print(f"  Skipped {fname}: {e}")


def main():
    print("\n  roboat — Stub Generator")
    print("  " + "─" * 40)
    print()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir   = os.path.dirname(script_dir)
    src_dir    = os.path.join(root_dir, "roboat")
    out_dir    = os.path.join(root_dir, "roboat")  # stubs alongside source

    if not os.path.exists(src_dir):
        print(f"  Error: {src_dir} not found")
        sys.exit(1)

    generate_stubs(src_dir, out_dir)

    print()
    print("  Done. .pyi files written to roboat/")
    print()


if __name__ == "__main__":
    main()
