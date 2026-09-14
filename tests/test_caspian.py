"""Tests for Caspian channel integration with mocks."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from channels.caspian import CaspianManager


class TestCaspianManager:
    """Test Caspian manager functionality with mocks."""
    
    def test_demo_mode_initialization(self):
        """Test initialization in demo mode."""
        with patch('channels.caspian.config.DEMO_MODE', True):
            manager = CaspianManager()
            handler = Mock()
            result = manager.initialize(handler)
            assert result is True
            assert manager._initialized is True
            assert manager.cx is None
    
    def test_initialization_without_api_key(self):
        """Test initialization fails without API key."""
        with patch('channels.caspian.config.DEMO_MODE', False):
            with patch('channels.caspian.config.CASPIAN_API_KEY', ''):
                manager = CaspianManager()
                handler = Mock()
                result = manager.initialize(handler)
                assert result is False
                assert manager._initialized is False
    
    @patch('channels.caspian.config.DEMO_MODE', False)
    @patch('channels.caspian.config.CASPIAN_API_KEY', 'test_key')
    @patch('channels.caspian.config.CASPIAN_BASE_URL', 'https://api.test.com')
    def test_successful_initialization(self):
        """Test successful Caspian SDK initialization."""
        mock_caspian = MagicMock()
        mock_thread = MagicMock()
        mock_message = MagicMock()
        mock_context = MagicMock()
        
        with patch('caspian.facade.caspian.Caspian', return_value=mock_caspian) as mock_caspian_class:
            manager = CaspianManager()
            handler = Mock()
            
            result = manager.initialize(handler)
            
            assert result is True
            assert manager._initialized is True
            assert manager.cx is not None
            mock_caspian_class.assert_called_once()
            mock_caspian.on_message.assert_called_once()
    
    @patch('channels.caspian.config.DEMO_MODE', False)
    @patch('channels.caspian.config.CASPIAN_API_KEY', 'test_key')
    def test_import_error_handling(self):
        """Test handling of Caspian SDK import error."""
        with patch('caspian.facade.caspian.Caspian', side_effect=ImportError("No module named 'caspian'")):
            manager = CaspianManager()
            handler = Mock()
            result = manager.initialize(handler)
            assert result is False
            assert manager._initialized is False
    
    def test_add_email_channel_not_initialized(self):
        """Test adding email channel when not initialized."""
        manager = CaspianManager()
        result = manager.add_email_channel("testuser")
        assert result is None
    
    @patch('channels.caspian.config.DEMO_MODE', False)
    @patch('channels.caspian.config.CASPIAN_API_KEY', 'test_key')
    @patch('channels.caspian.config.CASPIAN_BASE_URL', 'https://api.test.com')
    def test_add_email_channel_success(self):
        """Test successful email channel registration."""
        mock_caspian = MagicMock()
        mock_caspian.channels.add.return_value = "testuser@agents.trycaspianai.com"
        
        with patch('caspian.facade.caspian.Caspian', return_value=mock_caspian):
            manager = CaspianManager()
            handler = Mock()
            manager.initialize(handler)
            
            result = manager.add_email_channel("testuser")
            
            assert result == "testuser@agents.trycaspianai.com"
            assert manager._email_registered is True
            assert manager._email_address == "testuser@agents.trycaspianai.com"
            mock_caspian.channels.add.assert_called_once_with("email", username="testuser")
    
    @patch('channels.caspian.config.DEMO_MODE', False)
    @patch('channels.caspian.config.CASPIAN_API_KEY', 'test_key')
    @patch('channels.caspian.config.CASPIAN_BASE_URL', 'https://api.test.com')
    def test_add_email_channel_dict_response(self):
        """Test email channel registration with dict response."""
        mock_caspian = MagicMock()
        mock_caspian.channels.add.return_value = {"address": "testuser@agents.trycaspianai.com"}
        
        with patch('caspian.facade.caspian.Caspian', return_value=mock_caspian):
            manager = CaspianManager()
            handler = Mock()
            manager.initialize(handler)
            
            result = manager.add_email_channel("testuser")
            
            assert result == "testuser@agents.trycaspianai.com"
            assert manager._email_registered is True
    
    def test_add_telegram_channel_not_initialized(self):
        """Test adding Telegram channel when not initialized."""
        manager = CaspianManager()
        result = manager.add_telegram_channel("test_token")
        assert result is False
    
    @patch('channels.caspian.config.DEMO_MODE', False)
    @patch('channels.caspian.config.CASPIAN_API_KEY', 'test_key')
    @patch('channels.caspian.config.CASPIAN_BASE_URL', 'https://api.test.com')
    def test_add_telegram_channel_success(self):
        """Test successful Telegram channel registration."""
        mock_caspian = MagicMock()
        
        with patch('caspian.facade.caspian.Caspian', return_value=mock_caspian):
            manager = CaspianManager()
            handler = Mock()
            manager.initialize(handler)
            
            result = manager.add_telegram_channel("test_token")
            
            assert result is True
            assert manager._telegram_registered is True
            mock_caspian.channels.add.assert_called_once_with("telegram", bot_token="test_token")
    
    @patch('channels.caspian.config.DEMO_MODE', False)
    @patch('channels.caspian.config.CASPIAN_API_KEY', 'test_key')
    @patch('channels.caspian.config.CASPIAN_BASE_URL', 'https://api.test.com')
    def test_add_telegram_channel_failure(self):
        """Test Telegram channel registration failure."""
        mock_caspian = MagicMock()
        mock_caspian.channels.add.side_effect = Exception("Invalid token")
        
        with patch('caspian.facade.caspian.Caspian', return_value=mock_caspian):
            manager = CaspianManager()
            handler = Mock()
            manager.initialize(handler)
            
            result = manager.add_telegram_channel("invalid_token")
            
            assert result is False
            assert manager._telegram_registered is False
    
    @patch('channels.caspian.config.DEMO_MODE', False)
    @patch('channels.caspian.config.CASPIAN_API_KEY', 'test_key')
    @patch('channels.caspian.config.CASPIAN_BASE_URL', 'https://api.test.com')
    def test_run_event_loop(self):
        """Test running Caspian event loop."""
        mock_caspian = MagicMock()
        
        with patch('caspian.facade.caspian.Caspian', return_value=mock_caspian):
            manager = CaspianManager()
            handler = Mock()
            manager.initialize(handler)
            
            manager.run()
            
            assert manager._running is True
            mock_caspian.run.assert_called_once()
    
    @patch('channels.caspian.config.DEMO_MODE', False)
    @patch('channels.caspian.config.CASPIAN_API_KEY', 'test_key')
    @patch('channels.caspian.config.CASPIAN_BASE_URL', 'https://api.test.com')
    def test_start_in_background(self):
        """Test starting event loop in background thread."""
        mock_caspian = MagicMock()
        
        with patch('caspian.facade.caspian.Caspian', return_value=mock_caspian):
            manager = CaspianManager()
            handler = Mock()
            manager.initialize(handler)
            
            result = manager.start_in_background()
            
            assert result is True
            assert manager._run_thread is not None
            # Note: _running is set inside the thread, so we just verify thread was created
    
    def test_is_available(self):
        """Test is_available method."""
        manager = CaspianManager()
        assert manager.is_available() is False
        
        manager._initialized = True
        manager.cx = MagicMock()
        assert manager.is_available() is True
    
    def test_is_running(self):
        """Test is_running method."""
        manager = CaspianManager()
        assert manager.is_running() is False
        
        manager._running = True
        assert manager.is_running() is True
    
    def test_channel_registration_status(self):
        """Test channel registration status methods."""
        manager = CaspianManager()
        
        assert manager.is_email_registered() is False
        assert manager.is_telegram_registered() is False
        assert manager.get_email_address() is None
        
        manager._email_registered = True
        manager._telegram_registered = True
        manager._email_address = "test@agents.trycaspianai.com"
        
        assert manager.is_email_registered() is True
        assert manager.is_telegram_registered() is True
        assert manager.get_email_address() == "test@agents.trycaspianai.com"
    
    @patch('channels.caspian.config.DEMO_MODE', False)
    @patch('channels.caspian.config.CASPIAN_API_KEY', 'test_key')
    @patch('channels.caspian.config.CASPIAN_BASE_URL', 'https://api.test.com')
    def test_message_handler_routing(self):
        """Test that message handler is registered correctly."""
        mock_caspian = MagicMock()
        
        with patch('caspian.facade.caspian.Caspian', return_value=mock_caspian):
            manager = CaspianManager()
            mock_dv_handler = Mock()
            mock_dv_handler.handle_message.return_value = "response"
            
            manager.initialize(mock_dv_handler)
            
            # Verify on_message was called to register the handler
            mock_caspian.on_message.assert_called_once_with({"channel": "*"})
