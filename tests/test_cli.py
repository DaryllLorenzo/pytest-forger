"""Tests for pytest-forger CLI."""

import pytest
from typer.testing import CliRunner
from pytest_forger.cli import app
from pathlib import Path
import tempfile


runner = CliRunner()
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestVersionCommand:
    """Tests for the version command."""

    def test_version_command(self):
        """Test that version command displays version info."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "pytest-forger" in result.output
        assert "v" in result.output


class TestForgeCommand:
    """Tests for the forge command."""

    def test_forge_with_valid_file(self):
        """Test forge command with a valid source file."""
        source_file = FIXTURES_DIR / "sample_module.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = runner.invoke(
                app, ["forge", str(source_file), "--output", str(output_dir)]
            )

            assert result.exit_code == 0
            assert "Successfully forged" in result.output

            # Check that test file was created
            test_file = output_dir / "test_sample_module.py"
            assert test_file.exists()

    def test_forge_with_nonexistent_file(self):
        """Test forge command with a nonexistent file."""
        result = runner.invoke(app, ["forge", "nonexistent.py"])
        assert result.exit_code == 1
        assert "Error" in result.output
        assert "not found" in result.output

    def test_forge_with_verbose_flag(self):
        """Test forge command with verbose output."""
        source_file = FIXTURES_DIR / "sample_module.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = runner.invoke(
                app, ["forge", str(source_file), "--output", str(output_dir), "--verbose"]
            )

            assert result.exit_code == 0
            assert "Analyzing source file" in result.output
            assert "Found" in result.output
            assert "functions" in result.output

    def test_forge_with_function_filter(self):
        """Test forge command with specific function filter."""
        source_file = FIXTURES_DIR / "sample_module.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = runner.invoke(
                app,
                [
                    "forge",
                    str(source_file),
                    "--output",
                    str(output_dir),
                    "--function",
                    "simple_function",
                ],
            )

            assert result.exit_code == 0
            test_file = output_dir / "test_sample_module.py"
            assert test_file.exists()

            content = test_file.read_text()
            assert "test_simple_function" in content
            # Should only have one test function
            assert content.count("def test_") == 1

    def test_forge_with_nonexistent_function(self):
        """Test forge command with a nonexistent function name."""
        source_file = FIXTURES_DIR / "sample_module.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = runner.invoke(
                app,
                [
                    "forge",
                    str(source_file),
                    "--output",
                    str(output_dir),
                    "--function",
                    "nonexistent_func",
                ],
            )

            assert result.exit_code == 0
            assert "Warning" in result.output
            assert "not found" in result.output

    def test_forge_existing_file_without_overwrite(self):
        """Test forge command when output file already exists."""
        source_file = FIXTURES_DIR / "sample_module.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            # First run - create the file
            runner.invoke(app, ["forge", str(source_file), "--output", str(output_dir)])

            # Second run - should warn about existing file
            result = runner.invoke(
                app, ["forge", str(source_file), "--output", str(output_dir)]
            )

            assert result.exit_code == 0
            assert "Warning" in result.output
            assert "already exists" in result.output

    def test_forge_existing_file_with_overwrite(self):
        """Test forge command with overwrite flag."""
        source_file = FIXTURES_DIR / "sample_module.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            # First run - create the file
            runner.invoke(app, ["forge", str(source_file), "--output", str(output_dir)])

            # Second run - should overwrite
            result = runner.invoke(
                app, ["forge", str(source_file), "--output", str(output_dir), "--overwrite"]
            )

            assert result.exit_code == 0
            assert "Successfully forged" in result.output

    def test_forge_creates_output_directory(self):
        """Test that forge creates output directory if it doesn't exist."""
        source_file = FIXTURES_DIR / "sample_module.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "new_tests"
            assert not output_dir.exists()

            result = runner.invoke(
                app, ["forge", str(source_file), "--output", str(output_dir)]
            )

            assert result.exit_code == 0
            assert output_dir.exists()
            assert (output_dir / "test_sample_module.py").exists()

    def test_forge_with_external_deps(self):
        """Test forge command with file containing external dependencies."""
        source_file = FIXTURES_DIR / "external_deps_module.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = runner.invoke(
                app,
                [
                    "forge",
                    str(source_file),
                    "--output",
                    str(output_dir),
                    "--verbose",
                ],
            )

            assert result.exit_code == 0
            assert "external dependencies" in result.output

            test_file = output_dir / "test_external_deps_module.py"
            assert test_file.exists()

            content = test_file.read_text()
            assert "Mock setup for external dependencies" in content
