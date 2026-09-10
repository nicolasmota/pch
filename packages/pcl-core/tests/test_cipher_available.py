from pcl_core.vault.engine import cipher_available


def test_cipher_available_true_when_import_works():
    assert cipher_available() is True


def test_cipher_available_false_when_import_fails(monkeypatch):
    import pcl_core.vault.engine as engine

    monkeypatch.setattr(engine, "sqlcipher", None)
    assert engine.cipher_available() is False
