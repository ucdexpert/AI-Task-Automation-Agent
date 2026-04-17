"""Tests for backend tools"""
import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone


class TestFileTool:
    """Test file tool operations"""

    @pytest.mark.asyncio
    async def test_read_file_success(self):
        """Test reading a file"""
        from app.tools.file_tool import FileTool

        tool = FileTool()

        # Create a test file
        test_dir = os.path.abspath("documents")
        os.makedirs(test_dir, exist_ok=True)
        test_file = os.path.join(test_dir, "test.txt")

        with open(test_file, "w", encoding='utf-8') as f:
            f.write("Test content")

        result = await tool.execute(operation="read", file_path="test.txt")

        assert result["success"] is True
        assert result["content"] == "Test content"

        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

    @pytest.mark.asyncio
    async def test_write_file_success(self):
        """Test writing to a file"""
        from app.tools.file_tool import FileTool

        tool = FileTool()

        result = await tool.execute(
            operation="write",
            file_path="test_write.txt",
            content="Test content"
        )

        assert result["success"] is True

        # Verify file was created
        test_file = os.path.abspath(os.path.join("documents", "test_write.txt"))
        assert os.path.exists(test_file)

        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

    @pytest.mark.asyncio
    async def test_path_traversal_attack_blocked(self):
        """CRITICAL: Verify that path traversal attacks are blocked"""
        from app.tools.file_tool import FileTool

        tool = FileTool()

        # Try to access file outside documents directory
        result = await tool.execute(
            operation="read",
            file_path="../../../etc/passwd"
        )

        # Must be blocked
        assert result["success"] is False
        assert "traversal" in result.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_list_files(self):
        """Test listing files in directory"""
        from app.tools.file_tool import FileTool

        tool = FileTool()

        # Create some test files
        test_dir = os.path.abspath("documents")
        os.makedirs(test_dir, exist_ok=True)

        test_files = []
        for i in range(3):
            p = os.path.join(test_dir, f"file{i}.txt")
            with open(p, "w", encoding='utf-8') as f:
                f.write(f"Content {i}")
            test_files.append(p)

        # list operation requires file_path (directory)
        result = await tool.execute(operation="list", file_path=".")

        assert result["success"] is True
        assert len(result["files"]) >= 3

        # Cleanup
        for p in test_files:
            if os.path.exists(p):
                os.remove(p)


class TestWebScraperTool:
    """Test web scraper tool operations"""

    @pytest.mark.asyncio
    @patch('app.tools.web_scraper_tool.httpx.AsyncClient.get')
    async def test_scrape_success(self, mock_get):
        """Test successful web scraping"""
        from app.tools.web_scraper_tool import WebScraperTool

        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><h1>Test Page</h1></body></html>"
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response

        tool = WebScraperTool()
        # Use a safe URL to avoid SSRF check failure in test
        result = await tool.execute(url="https://www.google.com")

        assert result["success"] is True
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_ssrf_attack_blocked(self):
        """HIGH: Verify that SSRF attacks are prevented"""
        from app.tools.web_scraper_tool import WebScraperTool

        tool = WebScraperTool()

        # These URLs should be blocked
        dangerous_urls = [
            "http://localhost:8080",
            "http://127.0.0.1:5432",
            "file:///etc/passwd"
        ]

        for url in dangerous_urls:
            result = await tool.execute(url=url)
            assert result["success"] is False
            assert "security" in result.get("message", "").lower()


class TestWhatsAppTool:
    """Test WhatsApp tool operations"""

    @pytest.mark.asyncio
    @patch('app.tools.whatsapp_tool.httpx.AsyncClient')
    async def test_send_message_success(self, mock_client_class):
        """Test sending WhatsApp message"""
        from app.tools.whatsapp_tool import WhatsAppTool

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [{"id": "test_message_id"}]
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        with patch('app.config.settings.WHATSAPP_ACCESS_TOKEN', 'test_token'):
            with patch('app.config.settings.WHATSAPP_PHONE_NUMBER_ID', '123456'):
                with patch('app.config.settings.WHATSAPP_RECIPIENT_NUMBER', '+923001234567'):
                    tool = WhatsAppTool()
                    result = await tool.execute(
                        operation="send_text",
                        message="Test message"
                    )

                    assert result["success"] is True


class TestGoogleCalendarTool:
    """Test Google Calendar tool operations"""

    @pytest.mark.asyncio
    @patch('app.tools.google_calendar_tool.build')
    async def test_create_event_success(self, mock_build):
        """Test creating calendar event"""
        from app.tools.google_calendar_tool import GoogleCalendarTool

        # Mock Google Calendar API
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_event = {
            'id': 'test_event_id',
            'summary': 'Test Event',
            'start': {'dateTime': '2026-04-15T10:00:00'},
            'end': {'dateTime': '2026-04-15T11:00:00'}
        }
        mock_service.events().insert().execute.return_value = mock_event

        with patch('app.config.settings.GOOGLE_CALENDAR_CREDENTIALS', '{}'):
            tool = GoogleCalendarTool()
            result = await tool.execute(
                operation="create",
                summary="Test Event",
                start_time="2026-04-15T10:00:00",
                end_time="2026-04-15T11:00:00"
            )

            assert result["success"] is True
            assert result["event_id"] == "test_event_id"

    def test_no_bare_except_clause(self):
        """Verify that bare except clause is removed from GoogleCalendarTool"""
        import inspect
        from app.tools.google_calendar_tool import GoogleCalendarTool

        source = inspect.getsource(GoogleCalendarTool)

        # Verify bug is fixed - no bare except:
        assert "except:" not in source, "Bare except clause still found"


class TestRobotTool:
    """Test robot tool operations"""

    @pytest.mark.asyncio
    async def test_robot_tool_initialization(self):
        """Test robot tool can be initialized"""
        from app.tools.robot_tool import RobotTool

        tool = RobotTool()
        assert tool is not None
