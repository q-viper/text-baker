"""
Tests for the CLI module.
"""

from typer.testing import CliRunner

from textbaker.cli import app

runner = CliRunner()


class TestCLIHelp:
    """Tests for CLI help commands."""

    def test_main_help(self):
        """Test main help displays correctly."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "TextBaker" in result.output or "textbaker" in result.output.lower()

    def test_gui_help(self):
        """Test gui command help."""
        result = runner.invoke(app, ["gui", "--help"])

        assert result.exit_code == 0
        assert "dataset" in result.output.lower() or "output" in result.output.lower()

    def test_generate_help(self):
        """Test generate command help."""
        result = runner.invoke(app, ["generate", "--help"])

        assert result.exit_code == 0
        assert "seed" in result.output.lower()

    def test_init_config_help(self):
        """Test init-config command help."""
        result = runner.invoke(app, ["init-config", "--help"])

        assert result.exit_code == 0


class TestInitConfig:
    """Tests for init-config command."""

    def test_init_config_yaml(self, temp_dir):
        """Test creating YAML config file."""
        output_path = temp_dir / "test_config.yaml"

        result = runner.invoke(
            app,
            [
                "init-config",
                "-o",
                str(output_path),
                "-f",
                "yaml",
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()

        # Verify it's valid YAML
        import yaml

        with open(output_path) as f:
            data = yaml.safe_load(f)
        assert "seed" in data

    def test_init_config_json(self, temp_dir):
        """Test creating JSON config file."""
        output_path = temp_dir / "test_config.json"

        result = runner.invoke(
            app,
            [
                "init-config",
                "-o",
                str(output_path),
                "-f",
                "json",
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()

        # Verify it's valid JSON
        import json

        with open(output_path) as f:
            data = json.load(f)
        assert "seed" in data


class TestGenerateCommand:
    """Tests for generate command."""

    def test_generate_with_text(self, sample_dataset, temp_dir):
        """Test generating specific text."""
        output_dir = temp_dir / "output"

        result = runner.invoke(
            app,
            [
                "generate",
                "ABC",
                "-d",
                str(sample_dataset),
                "-o",
                str(output_dir),
                "--seed",
                "42",
            ],
        )

        # Should succeed or warn about missing characters
        assert result.exit_code == 0 or "not found" in result.output.lower()

    def test_generate_random(self, sample_dataset, temp_dir):
        """Test generating random samples."""
        output_dir = temp_dir / "output"

        result = runner.invoke(
            app,
            [
                "generate",
                "-n",
                "3",
                "-d",
                str(sample_dataset),
                "-o",
                str(output_dir),
                "--seed",
                "42",
            ],
        )

        assert result.exit_code == 0

    def test_generate_with_transforms(self, sample_dataset, temp_dir):
        """Test generating with transform options."""
        output_dir = temp_dir / "output"

        result = runner.invoke(
            app,
            [
                "generate",
                "A",
                "-d",
                str(sample_dataset),
                "-o",
                str(output_dir),
                "--rotation",
                "-10,10",
                "--scale",
                "0.9,1.1",
            ],
        )

        assert result.exit_code == 0


class TestCLIValidation:
    """Tests for CLI input validation."""

    def test_invalid_seed_type(self):
        """Test that invalid seed type is handled."""
        result = runner.invoke(
            app,
            [
                "generate",
                "--seed",
                "not_a_number",
            ],
        )

        # Should fail with error
        assert result.exit_code != 0

    def test_invalid_range_format(self, sample_dataset, temp_dir):
        """Test that invalid range format is handled."""
        result = runner.invoke(
            app,
            [
                "generate",
                "A",
                "-d",
                str(sample_dataset),
                "-o",
                str(temp_dir),
                "--rotation",
                "invalid",
            ],
        )

        # Should fail or handle gracefully
        # The exact behavior depends on implementation
        assert result.exit_code != 0 or "error" in result.output.lower()
