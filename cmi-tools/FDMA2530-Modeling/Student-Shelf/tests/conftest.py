# conftest.py
"""
Global test configuration for FDMA2530 shelf system tests.
This file ensures that Maya modules are always mocked for all tests,
so tests can run in any Python environment (including VS Code).
"""
import sys
import types
from unittest.mock import MagicMock

# Create maya as a module, not a MagicMock
maya_mod = types.ModuleType('maya')
cmds_mod = types.ModuleType('maya.cmds')
mel_mod = types.ModuleType('maya.mel')
utils_mod = types.ModuleType('maya.utils')

# Assign MagicMock to all attributes
for mod in (cmds_mod, mel_mod, utils_mod):
    mod.__dict__.update(MagicMock().__dict__)

# Add specific Maya command mocks
setattr(cmds_mod, 'shelfLayout', MagicMock())
setattr(cmds_mod, 'deleteUI', MagicMock())
setattr(cmds_mod, 'control', MagicMock())
setattr(cmds_mod, 'tabLayout', MagicMock())
setattr(cmds_mod, 'inViewMessage', MagicMock())
setattr(cmds_mod, 'internalVar', MagicMock())
setattr(cmds_mod, 'separator', MagicMock())
setattr(cmds_mod, 'shelfButton', MagicMock())
setattr(cmds_mod, 'warning', MagicMock())

# Add executeDeferred to maya.utils
setattr(utils_mod, 'executeDeferred', MagicMock())

# Attach submodules to maya using setattr
setattr(maya_mod, 'cmds', cmds_mod)
setattr(maya_mod, 'mel', mel_mod)
setattr(maya_mod, 'utils', utils_mod)

# Insert into sys.modules
sys.modules['maya'] = maya_mod
sys.modules['maya.cmds'] = cmds_mod
sys.modules['maya.mel'] = mel_mod
sys.modules['maya.utils'] = utils_mod
