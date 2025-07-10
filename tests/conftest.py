import os
import sys
import types

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# Create lightweight package stubs to avoid importing heavy modules
if 'tradingagents' not in sys.modules:
    pkg = types.ModuleType('tradingagents')
    pkg.__path__ = [os.path.join(PROJECT_ROOT, 'tradingagents')]
    sys.modules['tradingagents'] = pkg

if 'tradingagents.dataflows' not in sys.modules:
    subpkg = types.ModuleType('tradingagents.dataflows')
    subpkg.__path__ = [os.path.join(PROJECT_ROOT, 'tradingagents', 'dataflows')]
    sys.modules['tradingagents.dataflows'] = subpkg
