"""Tests for pytest-forger's CodeAnalyzer."""

import pytest
from pathlib import Path
from pytest_forger.core import CodeAnalyzer, generate_test_content


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestCodeAnalyzer:
    """Tests for the CodeAnalyzer class."""

    def test_parse_valid_file(self):
        """Test parsing a valid Python file."""
        source_file = FIXTURES_DIR / "sample_module.py"
        analyzer = CodeAnalyzer(source_file)
        assert analyzer.tree is not None

    def test_extract_simple_function(self):
        """Test extracting a simple function."""
        source_file = FIXTURES_DIR / "sample_module.py"
        analyzer = CodeAnalyzer(source_file)
        functions = analyzer.extract_functions()

        simple_func = next((f for f in functions if f["name"] == "simple_function"), None)
        assert simple_func is not None
        assert [arg["name"] for arg in simple_func["args"]] == ["x", "y"]
        assert simple_func["is_async"] is False
        assert simple_func["return_type"] == "int"

    def test_extract_async_function(self):
        """Test extracting an async function."""
        source_file = FIXTURES_DIR / "sample_module.py"
        analyzer = CodeAnalyzer(source_file)
        functions = analyzer.extract_functions()

        async_func = next((f for f in functions if f["name"] == "async_function"), None)
        assert async_func is not None
        assert async_func["is_async"] is True
        assert [arg["name"] for arg in async_func["args"]] == ["name"]

    def test_extract_class_methods(self):
        """Test extracting class methods."""
        source_file = FIXTURES_DIR / "sample_module.py"
        analyzer = CodeAnalyzer(source_file)
        functions = analyzer.extract_functions()

        get_user = next((f for f in functions if f["name"] == "get_user"), None)
        assert get_user is not None
        assert get_user["class_name"] == "SampleService"
        assert [arg["name"] for arg in get_user["args"]] == ["user_id"]

    def test_exclude_dunder_methods(self):
        """Test that dunder methods are excluded."""
        source_file = FIXTURES_DIR / "sample_module.py"
        analyzer = CodeAnalyzer(source_file)
        functions = analyzer.extract_functions()

        dunder_methods = [f for f in functions if f["name"].startswith("__")]
        assert len(dunder_methods) == 0

    def test_exclude_private_methods(self):
        """Test that private methods (starting with _) are excluded."""
        source_file = FIXTURES_DIR / "sample_module.py"
        analyzer = CodeAnalyzer(source_file)
        functions = analyzer.extract_functions()

        private_methods = [f for f in functions if f["name"].startswith("_")]
        assert len(private_methods) == 0

    def test_extract_function_with_type_hints(self):
        """Test extracting function with type hints."""
        source_file = FIXTURES_DIR / "sample_module.py"
        analyzer = CodeAnalyzer(source_file)
        functions = analyzer.extract_functions()

        func = next((f for f in functions if f["name"] == "process_items"), None)
        assert func is not None
        assert len(func["args"]) == 1
        assert func["args"][0]["name"] == "items"
        assert func["args"][0]["type_hint"] == "List[str]"
        assert func["return_type"] == "int"

    def test_extract_function_docstring(self):
        """Test extracting function docstring."""
        source_file = FIXTURES_DIR / "sample_module.py"
        analyzer = CodeAnalyzer(source_file)
        functions = analyzer.extract_functions()

        func = next((f for f in functions if f["name"] == "simple_function"), None)
        assert func is not None
        assert func["docstring"] == "Add two numbers together."

    def test_extract_imports(self):
        """Test extracting import statements."""
        source_file = FIXTURES_DIR / "sample_module.py"
        analyzer = CodeAnalyzer(source_file)

        assert len(analyzer.imports) > 0
        datetime_import = next(
            (i for i in analyzer.imports if i.get("name") == "datetime"), None
        )
        assert datetime_import is not None
        assert datetime_import["type"] == "from"

    def test_get_external_dependencies(self):
        """Test identifying external dependencies."""
        source_file = FIXTURES_DIR / "external_deps_module.py"
        analyzer = CodeAnalyzer(source_file)
        external_deps = analyzer.get_external_dependencies()

        external_modules = [dep.get("module", "") for dep in external_deps]
        assert "requests" in external_modules
        assert "sqlalchemy" in external_modules
        assert "my_custom_lib" in external_modules

    def test_exclude_stdlib_dependencies(self):
        """Test that stdlib modules are not marked as external."""
        source_file = FIXTURES_DIR / "external_deps_module.py"
        analyzer = CodeAnalyzer(source_file)
        external_deps = analyzer.get_external_dependencies()

        # datetime is stdlib, should not be in external deps
        external_modules = [dep.get("module", "") for dep in external_deps]
        assert "datetime" not in external_modules


class TestGenerateTestContent:
    """Tests for the generate_test_content function."""

    def test_generate_header(self):
        """Test that generated content has proper header."""
        source_file = FIXTURES_DIR / "sample_module.py"
        functions = [{"name": "test_func", "args": [], "is_async": False, "docstring": None}]
        content = generate_test_content(source_file, functions)

        assert "import pytest" in content
        assert "from sample_module import *" in content
        assert "from unittest.mock import MagicMock, patch" in content

    def test_generate_empty_functions(self):
        """Test generation when no functions are found."""
        source_file = FIXTURES_DIR / "sample_module.py"
        content = generate_test_content(source_file, [])

        assert "No public functions found" in content
        assert "def test_placeholder():" in content
        assert "assert True" in content

    def test_generate_simple_function_test(self):
        """Test generation for a simple function."""
        source_file = FIXTURES_DIR / "sample_module.py"
        functions = [
            {
                "name": "simple_function",
                "args": [{"name": "x"}, {"name": "y"}],
                "is_async": False,
                "docstring": "Add two numbers.",
                "return_type": "int",
            }
        ]
        content = generate_test_content(source_file, functions)

        assert "def test_simple_function():" in content
        assert "# Arrange" in content
        assert "# Act" in content
        assert "# Assert" in content
        assert "x = None" in content
        assert "y = None" in content

    def test_generate_class_method_test(self):
        """Test generation for a class method."""
        source_file = FIXTURES_DIR / "sample_module.py"
        functions = [
            {
                "name": "get_user",
                "class_name": "SampleService",
                "args": [{"name": "user_id"}],
                "is_async": False,
                "docstring": "Get a user by ID.",
                "return_type": None,
            }
        ]
        content = generate_test_content(source_file, functions)

        assert "def test_SampleService_get_user():" in content
        assert "instance = sample_module.SampleService()" in content

    def test_generate_async_function_test(self):
        """Test generation for an async function."""
        source_file = FIXTURES_DIR / "sample_module.py"
        functions = [
            {
                "name": "async_function",
                "args": [{"name": "name"}],
                "is_async": True,
                "docstring": "An async function.",
                "return_type": "str",
            }
        ]
        content = generate_test_content(source_file, functions)

        assert "def test_async_function():" in content
        assert "await" in content
        assert "pytest-asyncio" in content

    def test_generate_with_type_hints(self):
        """Test generation with type-aware placeholders."""
        source_file = FIXTURES_DIR / "sample_module.py"
        functions = [
            {
                "name": "process_items",
                "args": [{"name": "items", "type_hint": "List[str]"}],
                "is_async": False,
                "docstring": None,
                "return_type": "int",
            }
        ]
        content = generate_test_content(source_file, functions)

        assert "items = List[str]()" in content or "items = None" in content

    def test_generate_with_external_deps(self):
        """Test generation with external dependencies."""
        source_file = FIXTURES_DIR / "external_deps_module.py"
        functions = [
            {
                "name": "fetch_data",
                "args": [{"name": "url"}],
                "is_async": False,
                "docstring": "Fetch data.",
                "return_type": "dict",
            }
        ]
        external_deps = [
            {"type": "import", "module": "requests"},
            {"type": "from", "module": "sqlalchemy", "name": "create_engine"},
        ]
        content = generate_test_content(source_file, functions, external_deps)

        assert "Mock setup for external dependencies" in content
        assert "requests = MagicMock()" in content or "# requests = MagicMock()" in content
