"""
gerar_ejetor_blender.py
=======================
Script para Blender 5.x — gera ejetor/carimbo de brigadeiro gourmet
como UMA PEÇA INTERIÇA (sem luva e êmbolo separados) a partir de um SVG.

Design da peça (uma única peça sólida):
  ┌────────────────────────────┐  ← topo / face de pressão (z = 30 mm)
  │   CORPO PRINCIPAL (28 mm)  │    contorno externo do desenho SVG
  │   sólido, 44 x 40 mm       │
  ├────────────────────────────┤  ← z = 2 mm
  │  RELEVO DO CARIMBO (2 mm)  │    mesmo SVG em escala reduzida (85%)
  │  face do carimbo / base    │    pressiona sobre o brigadeiro e deixa
  └────────────────────────────┘  ← base (z = 0)   o desenho impresso

Uso interno (chamado pelo launcher gerar_ejetor.py):
  blender --background --python gerar_ejetor_blender.py \\
          -- caminho.svg pasta_saida nome_arquivo

Parâmetros ajustáveis:
  LARGURA_MM      — largura total (L) em mm          padrão: 44
  COMPRIMENTO_MM  — comprimento total (C) em mm      padrão: 40
  ALTURA_TOTAL_MM — altura total (A) em mm            padrão: 30
  RELEVO_MM       — altura do relevo do carimbo em mm padrão: 2
  ESCALA_RELEVO   — tamanho do relevo vs contorno (0-1) padrão: 0.85
"""

import bpy
import sys
import os

# ─────────────────────────── PARÂMETROS ──────────────────────────────────────
LARGURA_MM      = 44.0   # Largura  (L) em mm  ← ajuste aqui para outro tamanho
COMPRIMENTO_MM  = 40.0   # Comprimento (C) em mm
ALTURA_TOTAL_MM = 30.0   # Altura total (A) em mm
RELEVO_MM       = 2.0    # Altura do relevo na face do carimbo (mm)
ESCALA_RELEVO   = 0.85   # Escala do relevo em relação ao contorno externo

# Altura do corpo principal = altura total − relevo
ALTURA_CORPO_MM = ALTURA_TOTAL_MM - RELEVO_MM  # 28 mm


def mm(v: float) -> float:
    """Converte mm para metros (unidade padrão do Blender)."""
    return v / 1000.0


# ─────────────────────────── ARGUMENTOS ──────────────────────────────────────
_args = sys.argv
_sep = _args.index("--") if "--" in _args else -1
if _sep < 0 or len(_args) < _sep + 4:
    print(
        "Uso interno:\n"
        "  blender --background --python gerar_ejetor_blender.py"
        " -- arquivo.svg pasta_saida nome"
    )
    sys.exit(1)

CAMINHO_SVG = _args[_sep + 1]
PASTA_SAIDA = _args[_sep + 2]
NOME        = _args[_sep + 3]


# ─────────────────────────── UTILITÁRIOS ─────────────────────────────────────

def limpar_cena() -> None:
    """Remove todos os objetos e dados órfãos da cena."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    for blk in list(bpy.data.meshes):
        bpy.data.meshes.remove(blk)
    for blk in list(bpy.data.curves):
        bpy.data.curves.remove(blk)
    for blk in list(bpy.data.materials):
        bpy.data.materials.remove(blk)


def importar_svg(caminho: str) -> bpy.types.Object:
    """
    Importa todas as paths de um SVG simples, une em um único objeto curva
    2D (fill_mode=BOTH), centraliza na origem e zera localização.
    Retorna o objeto curva.
    """
    nomes_antes = {o.name for o in bpy.data.objects}

    bpy.ops.import_curve.svg(filepath=caminho)

    novos = [
        o for o in bpy.data.objects
        if o.name not in nomes_antes and o.type == "CURVE"
    ]
    if not novos:
        print(f"ERRO: nenhuma curva SVG importada de: {caminho}")
        sys.exit(2)

    # Unir múltiplas curvas em um único objeto
    bpy.ops.object.select_all(action="DESELECT")
    for o in novos:
        o.select_set(True)
    bpy.context.view_layer.objects.active = novos[0]
    if len(novos) > 1:
        bpy.ops.object.join()

    obj = bpy.context.active_object

    # Configurar para 2D com preenchimento (necessário para gerar face sólida)
    obj.data.dimensions = "2D"
    obj.data.fill_mode  = "BOTH"

    # Centralizar origem na geometria e zerar localização
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    obj.location = (0.0, 0.0, 0.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    return obj


def escalar_para_dimensoes(obj: bpy.types.Object,
                 largura_m: float,
                 comprimento_m: float) -> None:
    """
    Escala o objeto para as dimensões exatas em metros (L x C).
    Usa escalas independentes em X e Y para forçar as dimensões alvo.
    """
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()

    dx = obj.dimensions.x
    dy = obj.dimensions.y
    sx = largura_m    / dx if dx > 1e-9 else 1.0
    sy = comprimento_m / dy if dy > 1e-9 else 1.0

    obj.scale = (sx, sy, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Re-centralizar após escalar
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    obj.location = (0.0, 0.0, 0.0)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)


def converter_e_extrudar(obj: bpy.types.Object, altura_m: float) -> None:
    """
    Converte a curva 2D para mesh sólido e extrudar na direção +Z
    pelo valor altura_m (em metros).
    O mesh resultante ocupa z=0 até z=altura_m.
    """
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Curva → Mesh (a face 2D vira malha plana)
    bpy.ops.object.convert(target="MESH")

    # Extrudar a face para cima
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0.0, 0.0, altura_m)}
    )
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def mover_para_z(obj: bpy.types.Object, z_base_m: float) -> None:
    """Move o objeto para que sua base fique em z_base_m."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()

    z_atual = obj.location.z - obj.dimensions.z / 2.0
    obj.location.z += (z_base_m - z_atual)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)


def exportar_stl(obj: bpy.types.Object, caminho_saida: str) -> None:
    """Exporta o objeto ativo como STL (Blender 5.x)."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        bpy.ops.wm.stl_export(filepath=caminho_saida)
        print(f"  STL salvo em: {caminho_saida}")
    except Exception as exc:
        print(f"ERRO ao exportar STL: {exc}")
        sys.exit(5)


# ─────────────────────────── PIPELINE PRINCIPAL ──────────────────────────────

def main() -> None:
    print()
    print("=" * 60)
    print("  GERADOR DE EJETOR DE BRIGADEIRO — Blender 5.x")
    print("=" * 60)
    print(f"  Nome     : {NOME}")
    print(f"  SVG      : {CAMINHO_SVG}")
    print(f"  Medidas  : {LARGURA_MM} x {COMPRIMENTO_MM} x {ALTURA_TOTAL_MM} mm")
    print(f"  Relevo   : {RELEVO_MM} mm  (escala {ESCALA_RELEVO*100:.0f}%)")
    print("=" * 60)
    print()

    limpar_cena()

    # ── 1. CORPO PRINCIPAL ──────────────────────────────────────────────────
    print("[1/4] Importando contorno externo e criando corpo principal...")
    corpo = importar_svg(CAMINHO_SVG)
    corpo.name = "corpo_principal"
    escalar_para_dimensoes(corpo, mm(LARGURA_MM), mm(COMPRIMENTO_MM))
    converter_e_extrudar(corpo, mm(ALTURA_CORPO_MM))
    # Corpo: z=0 até z=ALTURA_CORPO_MM (28 mm)

    # ── 2. RELEVO DO CARIMBO ────────────────────────────────────────────────
    print("[2/4] Importando contorno para relevo do carimbo...")
    relevo = importar_svg(CAMINHO_SVG)
    relevo.name = "relevo_carimbo"
    escalar_para_dimensoes(
        relevo,
        mm(LARGURA_MM      * ESCALA_RELEVO),
        mm(COMPRIMENTO_MM  * ESCALA_RELEVO),
    )
    converter_e_extrudar(relevo, mm(RELEVO_MM))
    # Relevo começa em z=0; precisa estar no topo do corpo (z=ALTURA_CORPO_MM)
    mover_para_z(relevo, mm(ALTURA_CORPO_MM))
    # Relevo: z=ALTURA_CORPO_MM até z=ALTURA_TOTAL_MM (28–30 mm)

    # ── 3. UNIR EM UMA PEÇA ─────────────────────────────────────────────────
    print("[3/4] Unindo corpo + relevo em uma peça única...")
    bpy.ops.object.select_all(action="DESELECT")
    corpo.select_set(True)
    relevo.select_set(True)
    bpy.context.view_layer.objects.active = corpo
    bpy.ops.object.join()

    ejetor = bpy.context.active_object
    ejetor.name = f"ejetor_{NOME}"

    # Centralizar origem no bounding box
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

    # ── 4. EXPORTAR STL ─────────────────────────────────────────────────────
    print("[4/4] Exportando STL...")
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    caminho_stl = os.path.join(PASTA_SAIDA, f"{NOME}_ejetor.stl")
    exportar_stl(ejetor, caminho_stl)

    print()
    print("=" * 60)
    print(f"  ✅  Ejetor '{NOME}' gerado com sucesso!")
    print(f"  Arquivo : {caminho_stl}")
    print(f"  Peça    : {LARGURA_MM} x {COMPRIMENTO_MM} x {ALTURA_TOTAL_MM} mm (L x C x A)")
    print(f"  Corpo   : {ALTURA_CORPO_MM} mm  |  Relevo: {RELEVO_MM} mm")
    print("=" * 60)
    print()


# Blender executa o script como __main__ quando chamado via --python,
# portanto esta guarda cobre ambos os casos de uso.
if __name__ == "__main__":
    main()
