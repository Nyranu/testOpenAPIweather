from weathBK import cli


def test_read_float(monkeypatch):
    inputs = iter(["abc", "200", "55,7"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = cli._read_float("Введите: ", -90, 90)
    assert result == 55.7


def test_read_days(monkeypatch):
    inputs = iter(["x", "8", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = cli._read_days()
    assert result == 5
