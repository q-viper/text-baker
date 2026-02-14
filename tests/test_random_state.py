"""
Tests for the random state management module.
"""

import pytest

from textbaker.utils.random_state import DEFAULT_SEED, RandomState, rng


class TestRandomState:
    """Tests for RandomState class."""

    def test_default_seed(self):
        """Test that default seed is set correctly."""
        rs = RandomState()
        assert rs.current_seed == DEFAULT_SEED

    def test_custom_seed(self):
        """Test initialization with custom seed."""
        rs = RandomState(seed=123)
        assert rs.current_seed == 123

    def test_seed_method(self):
        """Test seed method updates the seed."""
        rs = RandomState(seed=1)
        rs.seed(999)
        assert rs.current_seed == 999

    def test_reproducibility(self):
        """Test that same seed produces same results."""
        rs1 = RandomState(seed=42)
        rs2 = RandomState(seed=42)

        # Generate some random values
        vals1 = [rs1.randint(0, 100) for _ in range(10)]
        vals2 = [rs2.randint(0, 100) for _ in range(10)]

        assert vals1 == vals2

    def test_randint_range(self):
        """Test randint returns values in range."""
        rs = RandomState(seed=42)

        for _ in range(100):
            val = rs.randint(10, 20)
            assert 10 <= val <= 20

    def test_uniform_range(self):
        """Test uniform returns values in range."""
        rs = RandomState(seed=42)

        for _ in range(100):
            val = rs.uniform(0.5, 1.5)
            assert 0.5 <= val < 1.5

    def test_choice_single(self):
        """Test choice returns element from sequence."""
        rs = RandomState(seed=42)
        items = ["a", "b", "c", "d"]

        for _ in range(20):
            result = rs.choice(items)
            assert result in items

    def test_choice_empty_raises(self):
        """Test choice raises on empty sequence."""
        rs = RandomState(seed=42)

        with pytest.raises(IndexError):
            rs.choice([])

    def test_choices_count(self):
        """Test choices returns correct count."""
        rs = RandomState(seed=42)
        items = [1, 2, 3, 4, 5]

        result = rs.choices(items, k=3)
        assert len(result) == 3
        assert all(r in items for r in result)

    def test_shuffle_modifies_list(self):
        """Test shuffle modifies the list in place."""
        rs = RandomState(seed=42)
        items = [1, 2, 3, 4, 5]
        original = items.copy()

        rs.shuffle(items)

        # Should have same elements
        assert sorted(items) == sorted(original)
        # High probability of different order (not guaranteed but very likely)
        # Just check it doesn't error


class TestGlobalRng:
    """Tests for the global rng instance."""

    def test_global_rng_exists(self):
        """Test that global rng is available."""
        assert rng is not None
        assert isinstance(rng, RandomState)

    def test_global_rng_seed(self):
        """Test that global rng can be reseeded."""
        rng.seed(999)
        assert rng.current_seed == 999

        # Reset to default
        rng.seed(DEFAULT_SEED)
