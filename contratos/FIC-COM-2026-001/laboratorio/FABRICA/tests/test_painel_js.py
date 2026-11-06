"""O script do painel precisa ser JavaScript válido; com erro de sintaxe a tela abre vazia."""
import re, shutil, subprocess, pathlib, pytest

HTML = pathlib.Path(__file__).resolve().parents[1] / 'static' / 'index.html'


def _script() -> str:
    m = re.search(r'<script>(.*?)</script>', HTML.read_text(encoding='utf-8'), re.S)
    assert m, 'index.html sem <script>'
    return m.group(1)


@pytest.mark.skipif(shutil.which('node') is None, reason='Node.js não instalado')
def test_script_do_painel_compila(tmp_path):
    arq = tmp_path / 'painel.js'
    arq.write_text(_script(), encoding='utf-8')
    r = subprocess.run(['node', '--check', str(arq)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_escape_html_cobre_apostrofo():
    # sem a entrada "'" o caractere vira o texto "undefined" na tela
    assert "\"'\":'&#39;'" in _script()
