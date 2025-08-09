from orchestrator.ib_executor import IbExecutor
from orchestrator.config_types import IBConfig


def test_ib_health_import_error(monkeypatch):
    # Force import error by shadowing module import
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == 'ib_insync':
            raise ImportError('ib_insync not available')
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', fake_import)
    ex = IbExecutor(IBConfig(host='localhost', port=4002, client_id=1, paper=True))
    h = ex.check_health()
    assert h.ok is False and 'import_error' in (h.reason or '')


