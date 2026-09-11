"""
anonimizar_evidencia.py - Sustituye rutas locales en docs/evidencia/txt/*.txt.

La guia P02 prohibe incluir rutas privadas en la evidencia. Este script reemplaza la ruta del
repositorio, la de Tomcat (CATALINA_HOME) y la carpeta de usuario por marcadores estables, en
sus dos formas (Windows con backslash y POSIX con slash). Lo invoca scripts/verify-module.sh.

Uso:  python scripts/anonimizar_evidencia.py
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVID = ROOT / "docs" / "evidencia" / "txt"


def variantes(ruta):
    """Devuelve las formas equivalentes de una ruta (POSIX, Windows, Git Bash)."""
    if not ruta:
        return []
    formas = {str(ruta), str(ruta).replace("\\", "/"), str(ruta).replace("/", "\\")}
    try:  # Git Bash: /c/Users/... <-> C:\Users\...
        win = subprocess.run(["cygpath", "-w", str(ruta)], capture_output=True, text=True).stdout.strip()
        if win:
            formas.update({win, win.replace("\\", "/")})
        posix = subprocess.run(["cygpath", "-u", str(ruta)], capture_output=True, text=True).stdout.strip()
        if posix:
            formas.add(posix)
    except (OSError, FileNotFoundError):
        pass
    return sorted((f for f in formas if len(f) > 3), key=len, reverse=True)


def main():
    reemplazos = [
        (ROOT, "<REPO>"),
        (os.environ.get("CATALINA_HOME", ""), "<CATALINA_HOME>"),
        (Path.home(), "<HOME>"),
    ]
    patrones = []
    for ruta, marcador in reemplazos:
        for forma in variantes(ruta):
            patrones.append((re.compile(re.escape(forma), re.IGNORECASE), marcador))

    total = 0
    for archivo in sorted(EVID.glob("*.txt")):
        texto = archivo.read_text(encoding="utf-8", errors="replace")
        nuevo = texto
        for patron, marcador in patrones:
            nuevo = patron.sub(marcador, nuevo)
        if nuevo != texto:
            archivo.write_text(nuevo, encoding="utf-8")
            total += 1
    print(f"[anonimizar] {total} archivo(s) actualizados en {EVID.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
