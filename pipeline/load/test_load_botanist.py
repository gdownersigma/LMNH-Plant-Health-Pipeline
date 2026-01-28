"""Tests for the load_botanist module."""
import pytest
import pandas as pd
from load_botanist import (
    get_botanist_id,
    create_botanist,
    get_or_create_botanist,
    load_botanists
)


class TestGetBotanistId:
    """Tests for the get_botanist_id function."""

    def test_returns_id_when_found(self, mocker):
        """Should return botanist_id when email exists."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = (123,)
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_botanist_id(mock_conn, "test@example.com")

        assert result == 123

    def test_returns_none_when_not_found(self, mocker):
        """Should return None when email doesn't exist."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_botanist_id(mock_conn, "notfound@example.com")

        assert result is None


class TestCreateBotanist:
    """Tests for the create_botanist function."""

    def test_executes_insert_and_returns_id(self, mocker):
        """Should insert botanist and return new ID."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = (42,)
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = create_botanist(
            mock_conn, "Jane Doe", "jane@example.com", "+1-555-1234")

        assert result == 42
        assert mock_cursor.execute.call_count == 2


class TestGetOrCreateBotanist:
    """Tests for the get_or_create_botanist function."""

    def test_returns_existing_id(self, mocker):
        """Should return existing ID when botanist exists."""
        mocker.patch("load_botanist.get_botanist_id", return_value=99)
        mock_conn = mocker.MagicMock()

        result = get_or_create_botanist(
            mock_conn, "John Smith", "john@example.com", "+1-555-5678")

        assert result == 99

    def test_creates_new_botanist(self, mocker):
        """Should create new botanist when doesn't exist."""
        mocker.patch("load_botanist.get_botanist_id", return_value=None)
        mocker.patch("load_botanist.create_botanist", return_value=101)
        mock_conn = mocker.MagicMock()

        result = get_or_create_botanist(
            mock_conn, "New Person", "new@example.com", "+1-555-9999")

        assert result == 101


class TestLoadBotanists:
    """Tests for the load_botanists function."""

    def test_returns_email_to_id_mapping(self, mocker):
        """Should return dict mapping emails to IDs."""
        df = pd.DataFrame({
            'botanist_name': ['Alice', 'Bob'],
            'botanist_email': ['alice@test.com', 'bob@test.com'],
            'botanist_phone': ['+1-111-1111', '+1-222-2222']
        })

        mock_conn = mocker.MagicMock()
        mocker.patch("load_botanist.get_connection", return_value=mock_conn)
        mocker.patch("load_botanist.load_botanist", side_effect=[10, 20])

        result = load_botanists(df)

        assert result == {
            'alice@test.com': 10,
            'bob@test.com': 20
        }
        mock_conn.commit.assert_called_once()

    def test_rollback_on_error(self, mocker):
        """Should rollback on error."""
        df = pd.DataFrame({
            'botanist_name': ['Alice'],
            'botanist_email': ['alice@test.com'],
            'botanist_phone': ['+1-111-1111']
        })

        mock_conn = mocker.MagicMock()
        mocker.patch("load_botanist.get_connection", return_value=mock_conn)
        mocker.patch("load_botanist.load_botanist",
                     side_effect=Exception("error"))

        with pytest.raises(Exception):
            load_botanists(df)

        mock_conn.rollback.assert_called_once()
