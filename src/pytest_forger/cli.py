# ---------------------------------------------------
# Project: pytest_forger (ptf)
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

"""
Entry point for pytest_forger CLI (`ptf`).

Available commands:
- `ptf version`: Show version and information about pytest-forger
- `ptf forge <source_file.py>`: Forge PyTest tests from existing Python source code
"""

import typer
import sys
from pathlib import Path
from typing import Optional

# Import core logic
from pytest_forger.core import CodeAnalyzer, generate_test_content

app = typer.Typer(
    name="ptf",
    help="pytest-forger: Forge PyTest-ready tests from existing Python source code.",
    add_completion=False,
    no_args_is_help=True,
)

def get_version() -> str:
    """
    Retrieve the current version of pytest-forger.
    Returns:
        str: Version string (e.g., "0.1.0")
    """
    try:
        from pytest_forger import __version__
        return __version__
    except ImportError:
        return "0.1.0-dev"

@app.command()
def version():
    """
    Display version information about pytest-forger.
    """
    version_str = get_version()
   
    typer.echo(f"pytest-forger v{version_str}")
    typer.echo("https://github.com/daryll/pytest-forger")
    typer.echo("MIT License (c) 2025 Daryll Lorenzo Alfonso")

@app.command()
def forge(
    source_file: str = typer.Argument(
        ...,
        help="Path to the Python source file to analyze and generate tests for"
    ),
    function_name: Optional[str] = typer.Option(
        None, 
        "--function", "-f",
        help="Generate tests only for a specific function (default: all functions in the module)"
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Directory where generated tests will be saved (default: 'tests/' in current directory)"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite", "-w",
        help="Overwrite existing test files if they already exist"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed information about the test generation process"
    ),
):
    """
    Forge PyTest tests from an existing Python source file.
    
    This command analyzes a Python source file, extracts its functions,
    and generates corresponding PyTest test cases.
    """
    
    # 1. Initial Validation
    src_path = Path(source_file)
    if not src_path.exists() or not src_path.is_file():
        typer.secho(f"Error: Source file '{source_file}' not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if verbose:
        typer.echo(f"Analyzing source file: {src_path.absolute()}")

    # 2. Parsing
    try:
        analyzer = CodeAnalyzer(src_path)
        functions = analyzer.extract_functions()
    except Exception as e:
        typer.secho(f"Error parsing file: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Filter by specific function if requested
    if function_name:
        functions = [f for f in functions if f['name'] == function_name]
        if not functions:
            typer.secho(f"Warning: Function '{function_name}' not found in source.", fg=typer.colors.YELLOW)

    if verbose:
        typer.echo(f"Found {len(functions)} functions/methods to test.")

    # 3. Output Directory Preparation
    default_out = Path("tests")
    out_path = Path(output_dir) if output_dir else default_out
    
    if not out_path.exists():
        out_path.mkdir(parents=True)
        if verbose:
            typer.echo(f"Created directory: {out_path}")

    # Define test filename
    test_filename = f"test_{src_path.stem}.py"
    test_file_path = out_path / test_filename

    # 4. Generation and Writing
    if test_file_path.exists() and not overwrite:
        typer.secho(f"Warning: File '{test_file_path}' already exists. Use --overwrite to replace it.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    test_content = generate_test_content(src_path, functions)

    try:
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        typer.secho(f"Successfully forged: {test_file_path}", fg=typer.colors.GREEN)
        if verbose:
            typer.echo("Generated tests for:")
            for f in functions:
                typer.echo(f"   - {f['name']}")

    except IOError as e:
        typer.secho(f"Error writing file: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose output for debugging"
    )
):
    """
    pytest-forger: Automated PyTest test generation.
    """
    # Store verbose flag in context for use in commands
    ctx.obj = {"verbose": verbose}

if __name__ == "__main__":
    app()