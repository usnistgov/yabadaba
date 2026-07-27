from unittest.mock import patch
import yabadaba

def test_screen_input():
    with patch('builtins.input') as mock_input:
        mock_input.return_value = 'some_input'
        assert yabadaba.tools.screen_input('prompt') == 'some_input'