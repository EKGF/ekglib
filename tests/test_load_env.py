import os
from unittest.mock import MagicMock, patch

from ekg_lib.main import load_env


class TestLoadEnv:
    """Test dotenvage integration via load_env()."""

    @patch('ekg_lib.main.main.EnvLoader')
    def test_load_env_creates_loader_and_calls_load(self, mock_loader_cls):
        """Verify load_env() creates an EnvLoader and calls load()."""
        mock_instance = MagicMock()
        mock_loader_cls.return_value = mock_instance

        load_env()

        mock_loader_cls.assert_called_once()
        mock_instance.load.assert_called_once()

    @patch('ekg_lib.main.main.EnvLoader')
    def test_load_env_can_be_called_multiple_times(self, mock_loader_cls):
        """Verify load_env() can be called repeatedly without error."""
        mock_instance = MagicMock()
        mock_loader_cls.return_value = mock_instance

        load_env()
        load_env()

        assert mock_loader_cls.call_count == 2
        assert mock_instance.load.call_count == 2
