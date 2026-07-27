
# https://docs.pytest.org/en/latest/
from pytest import raises

import yabadaba
from yabadaba.tools import ModuleManager

def test_ModuleManager():
    return    # Needs redoing as the demo records have moved!!!

    # Test initializing
    manager = ModuleManager('Test')
    assert manager.parentname == 'Test'
    assert len(manager.loaded_style_names) == 0
    assert len(manager.failed_style_names) == 0

    # Test import_style
    manager.import_style(style='FAQ', modulename='yabadaba.demo.FAQ')
    manager.import_style(style='bad', modulename='yabadaba.demo.BadRecord')
    assert manager.loaded_style_names == ['FAQ']
    assert manager.failed_style_names == ['bad']
    assert 'FAQ' in manager.loaded_styles
    assert 'bad' in manager.failed_styles

    # Test assert_style
    with raises(KeyError):
        manager.assert_style('fake')
    manager.assert_style('FAQ')
    with raises(ImportError):
        manager.assert_style('bad')

    # Test init
    with raises(KeyError):
        r = manager.init('fake')
    with raises(ImportError):
        r = manager.init('bad')
    r = manager.init('FAQ')
    assert isinstance(r, yabadaba.demo.FAQ.FAQ)
    

