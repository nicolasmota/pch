import socket

from hub_desktop.launch import choose_port, native_gui_available, port_free


def test_port_free_detects_bound_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    try:
        assert port_free("127.0.0.1", port) is False
    finally:
        sock.close()
    assert port_free("127.0.0.1", port) is True


def test_choose_port_skips_busy(monkeypatch):
    busy = 18765
    monkeypatch.setattr("hub_desktop.launch.health_ok", lambda host, port, timeout=0.4: False)
    monkeypatch.setattr("hub_desktop.launch.port_free", lambda host, port: port != busy)
    port, already = choose_port("127.0.0.1", busy)
    assert already is False
    assert port == busy + 1


def test_native_gui_probe_does_not_raise():
    assert native_gui_available() in (True, False)
