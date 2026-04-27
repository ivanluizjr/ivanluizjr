"""
gerar_ejetor.py
===============
Launcher Windows/Linux/macOS para geração automática do ejetor de brigadeiro.

Localiza o Blender automaticamente no PATH ou nos caminhos padrão de instalação
e executa o script Blender no modo background.

Uso:
  python gerar_ejetor.py arquivo.svg pasta_saida [nome]

Exemplos:
  python gerar_ejetor.py "concha.svg" "C:\\Ejetores" concha
  python gerar_ejetor.py "E:\\3D\\polvo.svg" "E:\\3D\\STLs"

O arquivo STL será salvo em:
  <pasta_saida>/<nome>_ejetor.stl
"""

import os
import sys
import subprocess

# ─────────────────────────── CAMINHOS PADRÃO ─────────────────────────────────
# Ajuste ou adicione caminhos caso sua instalação do Blender seja diferente.
BLENDER_PATHS_WINDOWS = [
    r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender\blender.exe",
]

BLENDER_PATHS_UNIX = [
    "/usr/bin/blender",
    "/usr/local/bin/blender",
    "/snap/bin/blender",
    "/Applications/Blender.app/Contents/MacOS/Blender",
]


def encontrar_blender() -> str | None:
    """
    Procura o executável do Blender:
    1. No PATH do sistema (funciona se Blender estiver no PATH).
    2. Nos caminhos padrão de instalação listados acima.
    Retorna o caminho completo ou None se não encontrado.
    """
    # 1. PATH do sistema
    for pasta in os.environ.get("PATH", "").split(os.pathsep):
        pasta = pasta.strip('"').strip("'")
        for nome_exe in ("blender.exe", "blender"):
            candidato = os.path.join(pasta, nome_exe)
            if os.path.isfile(candidato):
                return candidato

    # 2. Caminhos padrão
    caminhos = BLENDER_PATHS_WINDOWS + BLENDER_PATHS_UNIX
    for caminho in caminhos:
        if os.path.isfile(caminho):
            return caminho

    return None


def main() -> None:
    # ── Validar argumentos ────────────────────────────────────────────────
    if len(sys.argv) < 3:
        print(__doc__)
        print("ERRO: informe pelo menos o arquivo SVG e a pasta de saída.")
        sys.exit(1)

    svg   = os.path.abspath(sys.argv[1])
    saida = os.path.abspath(sys.argv[2])
    nome  = (
        sys.argv[3]
        if len(sys.argv) > 3
        else os.path.splitext(os.path.basename(svg))[0]
    )

    if not os.path.isfile(svg):
        print(f"ERRO: arquivo SVG não encontrado: {svg}")
        sys.exit(2)

    os.makedirs(saida, exist_ok=True)

    # ── Localizar Blender ─────────────────────────────────────────────────
    blender = encontrar_blender()
    if not blender:
        print("ERRO: Blender não encontrado no PATH nem nos caminhos padrão.")
        print()
        print("Soluções:")
        print("  1. Adicione a pasta do Blender ao PATH do Windows:")
        print("     Painel de Controle → Sistema → Variáveis de Ambiente → Path")
        print("  2. Ajuste a lista BLENDER_PATHS_WINDOWS em gerar_ejetor.py")
        sys.exit(3)

    # ── Localizar script Blender ──────────────────────────────────────────
    script_dir    = os.path.dirname(os.path.abspath(__file__))
    script_blender = os.path.join(script_dir, "gerar_ejetor_blender.py")
    if not os.path.isfile(script_blender):
        print(f"ERRO: 'gerar_ejetor_blender.py' não encontrado em: {script_dir}")
        sys.exit(4)

    # ── Executar Blender em modo background ───────────────────────────────
    cmd = [
        blender,
        "--background",
        "--python", script_blender,
        "--",          # tudo após '--' é passado ao script Python do Blender
        svg,
        saida,
        nome,
    ]

    print("=" * 60)
    print("  GERADOR DE EJETOR DE BRIGADEIRO")
    print("=" * 60)
    print(f"  Blender : {blender}")
    print(f"  SVG     : {svg}")
    print(f"  Saída   : {saida}")
    print(f"  Nome    : {nome}")
    print("=" * 60)
    print()

    resultado = subprocess.run(cmd)

    print()
    if resultado.returncode == 0:
        arquivo_final = os.path.join(saida, f"{nome}_ejetor.stl")
        print("=" * 60)
        print(f"  ✅  Concluído!")
        print(f"  STL : {arquivo_final}")
        print("=" * 60)
    else:
        print(f"ERRO: Blender encerrou com código {resultado.returncode}.")
        print("Verifique as mensagens acima para detalhes do erro.")
        sys.exit(resultado.returncode)


if __name__ == "__main__":
    main()
