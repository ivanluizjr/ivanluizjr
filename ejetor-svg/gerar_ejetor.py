# -*- coding: utf-8 -*-
"""
gerar_ejetor.py — Lançador Windows para geração de ejetores de brigadeiro via Blender

Uso:
    python gerar_ejetor.py "CAMINHO\\arquivo.svg" "PASTA_SAIDA" NOME_OPCIONAL [opções]

Exemplo:
    python gerar_ejetor.py "C:\\Meus SVGs\\polvo.svg" "C:\\STLs" polvo
    python gerar_ejetor.py "polvo.svg" "." polvo --tamanho 35 --altura 30
"""

import subprocess
import sys
import os
import shutil
import argparse


def verificar_blender():
    """
    Verifica se o Blender está disponível no sistema.
    Primeiro tenta a variável de ambiente BLENDER_PATH,
    depois busca automaticamente no PATH do Windows.
    Retorna o caminho para o executável do Blender.
    """
    # Verificar variável de ambiente personalizada
    blender_env = os.environ.get("BLENDER_PATH", "").strip()
    if blender_env:
        if os.path.isfile(blender_env):
            print(f"  Blender encontrado via BLENDER_PATH: {blender_env}")
            return blender_env
        else:
            print(f"AVISO: BLENDER_PATH definido mas não encontrado: {blender_env}")
            print("       Tentando localizar o Blender no PATH...")

    # Tentar localizar via PATH
    caminho_blender = shutil.which("blender")
    if caminho_blender:
        print(f"  Blender encontrado no PATH: {caminho_blender}")
        return caminho_blender

    # Não encontrado — mensagem de erro amigável
    print()
    print("=" * 60)
    print("ERRO: Blender não encontrado!")
    print("=" * 60)
    print()
    print("O Blender precisa estar acessível de uma dessas formas:")
    print()
    print("  OPÇÃO 1 — Adicionar ao PATH do Windows:")
    print("    1. Abra 'Configurações do Sistema' > 'Variáveis de Ambiente'")
    print("    2. Edite a variável PATH do usuário")
    print("    3. Adicione a pasta do Blender, por exemplo:")
    print("       C:\\Program Files\\Blender Foundation\\Blender 4.x")
    print("    4. Feche e reabra o Prompt de Comando")
    print()
    print("  OPÇÃO 2 — Definir BLENDER_PATH antes de rodar:")
    print("    set BLENDER_PATH=C:\\Program Files\\Blender Foundation\\Blender 4.x\\blender.exe")
    print("    python gerar_ejetor.py ...")
    print()
    print("  Download do Blender: https://www.blender.org/download/")
    print()
    sys.exit(1)


def analisar_argumentos():
    """
    Analisa os argumentos da linha de comando.
    Todos os parâmetros físicos estão em milímetros.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Gera STL de ejetores de brigadeiro (luva e êmbolo) "
            "a partir de um arquivo SVG usando o Blender."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python gerar_ejetor.py polvo.svg . polvo\n"
            "  python gerar_ejetor.py \"C:\\SVGs\\polvo.svg\" \"C:\\STLs\" polvo --tamanho 35\n"
            "  python gerar_ejetor.py estrela.svg saida estrela --parede 2.0 --folga 0.4\n"
        )
    )

    # Argumentos posicionais
    parser.add_argument(
        "svg",
        help="Caminho do arquivo SVG (use aspas se houver espaços no caminho)"
    )
    parser.add_argument(
        "saida",
        help="Pasta de saída onde os STLs serão salvos (será criada se não existir)"
    )
    parser.add_argument(
        "nome",
        nargs="?",
        default=None,
        help="Nome base dos arquivos de saída (padrão: nome do arquivo SVG sem extensão)"
    )

    # Parâmetros físicos (em mm)
    parser.add_argument(
        "--tamanho",
        type=float,
        default=30.0,
        metavar="MM",
        help="Tamanho externo do ejetor em mm (padrão: 30)"
    )
    parser.add_argument(
        "--altura",
        type=float,
        default=30.0,
        metavar="MM",
        help="Altura da luva e do corpo do êmbolo em mm (padrão: 30)"
    )
    parser.add_argument(
        "--relevo",
        type=float,
        default=1.2,
        metavar="MM",
        help="Profundidade do relevo gravado na base do êmbolo em mm (padrão: 1.2)"
    )
    parser.add_argument(
        "--parede",
        type=float,
        default=1.6,
        metavar="MM",
        help="Espessura da parede da luva em mm (padrão: 1.6)"
    )
    parser.add_argument(
        "--folga",
        type=float,
        default=0.35,
        metavar="MM",
        help="Folga entre o êmbolo e a luva em mm (padrão: 0.35)"
    )

    return parser.parse_args()


def main():
    """Ponto de entrada principal do lançador."""
    print()
    print("=" * 60)
    print("  GERADOR DE EJETORES DE BRIGADEIRO")
    print("=" * 60)

    args = analisar_argumentos()

    # --- Validar SVG ---
    svg_abs = os.path.abspath(args.svg)
    if not os.path.isfile(svg_abs):
        print(f"\nERRO: Arquivo SVG não encontrado: {svg_abs}")
        print("Verifique o caminho e tente novamente.")
        sys.exit(1)

    # --- Criar pasta de saída ---
    saida_abs = os.path.abspath(args.saida)
    try:
        os.makedirs(saida_abs, exist_ok=True)
    except OSError as erro:
        print(f"\nERRO: Não foi possível criar a pasta de saída: {saida_abs}")
        print(f"Detalhe: {erro}")
        sys.exit(1)

    # --- Determinar nome base ---
    if args.nome:
        nome = args.nome
    else:
        # Usa o nome do arquivo SVG sem extensão
        nome = os.path.splitext(os.path.basename(svg_abs))[0]
        # Remover caracteres inválidos para nome de arquivo
        nome = "".join(c for c in nome if c.isalnum() or c in ("-", "_")).strip() or "ejetor"

    # --- Localizar Blender ---
    print("\nLocalizando o Blender...")
    blender = verificar_blender()

    # --- Localizar script do Blender ---
    pasta_launcher = os.path.dirname(os.path.abspath(__file__))
    script_blender = os.path.join(pasta_launcher, "gerar_ejetor_blender.py")
    if not os.path.isfile(script_blender):
        print(f"\nERRO: Script do Blender não encontrado: {script_blender}")
        print("Certifique-se que 'gerar_ejetor_blender.py' está na mesma pasta que este script.")
        sys.exit(1)

    # --- Exibir resumo ---
    print()
    print("  SVG de entrada : " + svg_abs)
    print("  Pasta de saída : " + saida_abs)
    print("  Nome base      : " + nome)
    print(f"  Tamanho        : {args.tamanho} mm")
    print(f"  Altura         : {args.altura} mm")
    print(f"  Relevo (base)  : {args.relevo} mm")
    print(f"  Parede (luva)  : {args.parede} mm")
    print(f"  Folga          : {args.folga} mm")
    print()
    print("Iniciando o Blender em modo background...")
    print("(Isso pode demorar alguns segundos)")
    print()

    # --- Montar comando --- 
    # Usando lista de argumentos (não shell=True) para suportar espaços nos caminhos
    cmd = [
        blender,
        "--background",            # Sem interface gráfica
        "--python", script_blender,
        "--",                      # Separador: o que vem depois vai para o script Python
        "--svg",    svg_abs,
        "--saida",  saida_abs,
        "--nome",   nome,
        "--tamanho", str(args.tamanho),
        "--altura",  str(args.altura),
        "--relevo",  str(args.relevo),
        "--parede",  str(args.parede),
        "--folga",   str(args.folga),
    ]

    # --- Executar Blender ---
    try:
        resultado = subprocess.run(cmd)
    except FileNotFoundError:
        print(f"ERRO: Não foi possível executar o Blender: {blender}")
        print("Verifique se o caminho está correto.")
        sys.exit(1)

    if resultado.returncode != 0:
        print(f"\nERRO: O Blender encerrou com código de erro {resultado.returncode}.")
        print("Verifique as mensagens acima para mais detalhes.")
        sys.exit(resultado.returncode)

    # --- Verificar arquivos gerados ---
    luva_stl   = os.path.join(saida_abs, f"{nome}_luva.stl")
    embolo_stl = os.path.join(saida_abs, f"{nome}_embolo.stl")

    print()
    print("=" * 60)
    gerou_luva   = os.path.isfile(luva_stl)
    gerou_embolo = os.path.isfile(embolo_stl)

    if gerou_luva and gerou_embolo:
        print("  STLs gerados com sucesso!")
        print()
        print(f"  Luva   -> {luva_stl}")
        print(f"  Êmbolo -> {embolo_stl}")
        print()
        print("  Dicas para impressão:")
        print("  - Material: PLA ou PETG")
        print("  - Altura de camada: 0,15 mm")
        print("  - Infill: 30% ou mais")
        print("  - Suportes: não são necessários")
    else:
        print("  AVISO: Um ou mais arquivos STL não foram gerados.")
        if not gerou_luva:
            print(f"  Faltando: {luva_stl}")
        if not gerou_embolo:
            print(f"  Faltando: {embolo_stl}")
        print()
        print("  Verifique as mensagens do Blender acima para identificar o problema.")
        sys.exit(1)

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
