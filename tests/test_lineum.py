import builtins
import lineum
import pytest


def test_notify_file_creation_success(capsys):
    lineum.notify_file_creation('foo.txt')
    out = capsys.readouterr().out
    assert "Soubor 'foo.txt'" in out
    assert "úspěšně" in out


def test_notify_file_creation_failure(capsys):
    lineum.notify_file_creation('bar.txt', success=False, error=Exception('err'))
    out = capsys.readouterr().out
    assert "Nepodařilo se" in out
    assert 'bar.txt' in out


def test_save_csv_success(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(lineum, 'output_dir', tmp_path)
    lineum.save_csv('test.csv', ['a'], [(1,)])
    assert (tmp_path / 'test.csv').exists()
    out = capsys.readouterr().out
    assert 'test.csv' in out
    assert 'úspěšně' in out


def test_save_csv_failure(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(lineum, 'output_dir', tmp_path)

    def bad_open(*args, **kwargs):
        raise IOError('boom')

    monkeypatch.setattr(builtins, 'open', bad_open)
    lineum.save_csv('bad.csv', ['a'], [(1,)])
    out = capsys.readouterr().out
    assert 'Nepodařilo se' in out
    assert 'bad.csv' in out
