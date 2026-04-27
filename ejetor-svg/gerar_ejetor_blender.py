# -*- coding: utf-8 -*-
"""
gerar_ejetor_blender.py — Script Python interno do Blender para gerar ejetores de brigadeiro

Este script é executado pelo lançador gerar_ejetor.py via:
    blender --background --python gerar_ejetor_blender.py -- [argumentos]

NÃO execute este arquivo diretamente — use o gerar_ejetor.py.

Saída: dois arquivos STL na pasta informada
    NOME_luva.stl   — peça externa (molda o exterior do brigadeiro)
    NOME_embolo.stl — peça interna (empurra e imprime o relevo na base)
"""

import sys
import os
import argparse
import math

import bpy
import bmesh
from mathutils import Vector


# ============================================================
# CONSTANTES
# ============================================================

# Deslocamento em Z para garantir sobreposição nas operações booleanas.
# O mesh de relevo é posicionado BOOLEAN_OVERLAP_Z mm abaixo de z=0
# e extrudado com BOOLEAN_DEPTH_MARGIN mm extras para que o boolean
# DIFFERENCE corte completamente através da face inferior do êmbolo.
BOOLEAN_OVERLAP_Z     = 0.01  # mm: offset negativo em Z antes da subtração
BOOLEAN_DEPTH_MARGIN  = 0.02  # mm: margem extra na profundidade do relevo


# ============================================================
# ANÁLISE DE ARGUMENTOS
# ============================================================

def analisar_argumentos():
    """
    Analisa os argumentos passados após o separador '--' do Blender.
    Exemplo de chamada:
        blender --background --python script.py -- --svg polvo.svg --saida . --nome polvo
    """
    # O Blender passa seus próprios argumentos antes de '--'
    # Tudo depois de '--' é para o nosso script
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Gera ejetores de brigadeiro no Blender")
    parser.add_argument("--svg",     required=True,       help="Caminho do arquivo SVG")
    parser.add_argument("--saida",   required=True,       help="Pasta de saída")
    parser.add_argument("--nome",    default="ejetor",    help="Nome base dos arquivos STL")
    parser.add_argument("--tamanho", type=float, default=30.0, help="Tamanho externo (mm)")
    parser.add_argument("--altura",  type=float, default=30.0, help="Altura da luva e do corpo (mm)")
    parser.add_argument("--relevo",  type=float, default=1.2,  help="Profundidade do relevo na base (mm)")
    parser.add_argument("--parede",  type=float, default=1.6,  help="Espessura da parede da luva (mm)")
    parser.add_argument("--folga",   type=float, default=0.35, help="Folga entre êmbolo e luva (mm)")
    return parser.parse_args(argv)


# ============================================================
# CONFIGURAÇÃO DA CENA
# ============================================================

def configurar_cena_mm():
    """
    Configura a cena do Blender para trabalhar em milímetros.
    1 unidade Blender = 1 milímetro.
    """
    cena = bpy.context.scene
    cena.unit_settings.system = 'METRIC'
    cena.unit_settings.length_unit = 'MILLIMETERS'
    cena.unit_settings.scale_length = 0.001


def limpar_cena():
    """Remove todos os objetos e dados órfãos da cena."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Remover dados de mesh órfãos
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    # Remover dados de curva órfãos
    for curva in list(bpy.data.curves):
        bpy.data.curves.remove(curva, do_unlink=True)
    # Remover coleções vazias (exceto a coleção raiz da cena)
    for col in list(bpy.data.collections):
        if not col.objects:
            bpy.data.collections.remove(col)


# ============================================================
# IMPORTAÇÃO E ESCALONAMENTO DO SVG
# ============================================================

def importar_svg(caminho_svg):
    """
    Importa o arquivo SVG e retorna a lista de objetos de curva gerados.
    O SVG é importado com as curvas na coleção ativa.
    """
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.import_curve.svg(filepath=caminho_svg)

    # Pegar todos os objetos importados (são do tipo CURVE)
    curvas = [obj for obj in bpy.context.selected_objects if obj.type == 'CURVE']

    if not curvas:
        # Alguns SVGs simples podem ser importados como MESH ou vazio
        curvas = [obj for obj in bpy.context.selected_objects]

    return curvas


def calcular_bbox_2d(objetos):
    """
    Calcula o bounding box 2D (no plano XY) de uma lista de objetos,
    levando em conta as transformações (matrix_world) de cada um.
    Retorna (min_x, min_y, max_x, max_y) ou None se não houver pontos.
    """
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    encontrou = False

    for obj in objetos:
        mat = obj.matrix_world

        if obj.type == 'CURVE':
            for spline in obj.data.splines:
                if spline.type == 'BEZIER':
                    pontos_co = [p.co for p in spline.bezier_points]
                else:
                    pontos_co = [p.co for p in spline.points]
                for co in pontos_co:
                    # Vetor 4D (x, y, 0, 1): a quarta componente '1' é a
                    # coordenada homogênea necessária para que matrix_world
                    # aplique também a translação do objeto (transformação afim).
                    pos = mat @ Vector((co[0], co[1], 0, 1))
                    min_x = min(min_x, pos.x)
                    max_x = max(max_x, pos.x)
                    min_y = min(min_y, pos.y)
                    max_y = max(max_y, pos.y)
                    encontrou = True

        elif obj.type == 'MESH':
            for v in obj.data.vertices:
                pos = mat @ v.co
                min_x = min(min_x, pos.x)
                max_x = max(max_x, pos.x)
                min_y = min(min_y, pos.y)
                max_y = max(max_y, pos.y)
                encontrou = True

    if not encontrou:
        return None
    return min_x, min_y, max_x, max_y


def escalar_e_centralizar(objetos, tamanho_alvo_mm):
    """
    Escala e centraliza os objetos no plano XY de modo que o maior
    lado do bounding box fique igual a 'tamanho_alvo_mm'.
    Retorna o fator de escala aplicado, ou 1.0 se não foi possível calcular.
    """
    bbox = calcular_bbox_2d(objetos)
    if bbox is None:
        print("  AVISO: Não foi possível calcular o bounding box dos objetos importados.")
        return 1.0

    min_x, min_y, max_x, max_y = bbox
    largura = max_x - min_x
    altura  = max_y - min_y
    maior_lado = max(largura, altura)

    if maior_lado < 1e-9:
        print("  AVISO: Objetos com dimensão zero; escala não aplicada.")
        return 1.0

    # O Blender importa SVG com escala_length=0.001:
    # 1 unidade Blender = 1mm, portanto maior_lado já está em mm aprox.
    # Calculamos o fator necessário para chegar em tamanho_alvo_mm.
    fator = tamanho_alvo_mm / maior_lado

    # Centro atual
    centro_x = (min_x + max_x) / 2.0
    centro_y = (min_y + max_y) / 2.0

    # Aplicar transformações em cada objeto
    for obj in objetos:
        # Centralizar no plano XY
        obj.location.x = (obj.location.x - centro_x) * fator
        obj.location.y = (obj.location.y - centro_y) * fator
        obj.location.z = 0.0
        # Escalar uniformemente
        obj.scale = (obj.scale.x * fator,
                     obj.scale.y * fator,
                     obj.scale.z * fator)

        # Aplicar transformações para "congelar" os valores
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    return fator


# ============================================================
# CONVERSÃO DE CURVA PARA MESH 2D SÓLIDO
# ============================================================

def converter_curvas_para_mesh(curvas, offset_mm=0.0, nome="objeto"):
    """
    Converte uma lista de curvas SVG em um único objeto mesh 2D preenchido.
    Aplica um offset (positivo = expandir, negativo = encolher) antes de converter.
    Retorna o objeto mesh resultante, ou None em caso de falha.
    """
    meshes = []

    for curva in curvas:
        if curva.type != 'CURVE':
            continue

        # Configurar curva como 2D preenchida
        curva.data.dimensions = '2D'
        curva.data.fill_mode  = 'BOTH'
        curva.data.extrude    = 0.0
        curva.data.bevel_depth = 0.0
        curva.data.resolution_u = 64

        # Aplicar offset (inflação/deflação do contorno).
        # Como transform_apply() já foi chamado em escalar_e_centralizar(),
        # as unidades da curva são agora diretamente em mm — o offset
        # é portanto informado em mm sem conversão adicional.
        curva.data.offset = offset_mm

        # Ativar e selecionar para converter
        bpy.ops.object.select_all(action='DESELECT')
        curva.select_set(True)
        bpy.context.view_layer.objects.active = curva
        bpy.ops.object.convert(target='MESH')

        obj_mesh = bpy.context.view_layer.objects.active
        meshes.append(obj_mesh)

    if not meshes:
        return None

    # Juntar todos os meshes em um único objeto
    if len(meshes) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for m in meshes:
            m.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.join()

    resultado = bpy.context.view_layer.objects.active
    resultado.name = nome

    # Garantir que as faces estejam preenchidas (fill_holes)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.fill_holes(sides=0)
    bpy.ops.object.mode_set(mode='OBJECT')

    return resultado


# ============================================================
# OPERAÇÕES GEOMÉTRICAS
# ============================================================

def extrudar_para_altura(obj, altura_mm):
    """
    Extruda um mesh 2D (plano) para cima (eixo +Z) pela altura indicada em mm.
    O objeto deve estar centrado em Z=0 antes da chamada.
    """
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    # Extrudar seleção e mover ao longo de Z
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0.0, 0.0, altura_mm)}
    )
    # Recalcular normais para garantir orientação correta
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj


def boolean_diferenca(obj_base, obj_ferramenta):
    """
    Aplica operação booleana DIFFERENCE em obj_base usando obj_ferramenta.
    Remove obj_ferramenta após a operação.
    Retorna obj_base modificado.
    """
    bpy.ops.object.select_all(action='DESELECT')
    obj_base.select_set(True)
    bpy.context.view_layer.objects.active = obj_base

    # Adicionar modificador booleano
    mod = obj_base.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object    = obj_ferramenta
    # Solver EXACT é mais preciso para geometrias complexas
    try:
        mod.solver = 'EXACT'
    except AttributeError:
        pass  # Versão antiga do Blender sem 'solver' — usa padrão

    # Aplicar o modificador
    bpy.ops.object.modifier_apply(modifier="Boolean")

    # Remover o objeto ferramenta da cena
    bpy.data.objects.remove(obj_ferramenta, do_unlink=True)

    return obj_base


def boolean_uniao(obj_base, obj_adicional):
    """
    Aplica operação booleana UNION em obj_base com obj_adicional.
    Remove obj_adicional após a operação.
    Retorna obj_base modificado.
    """
    bpy.ops.object.select_all(action='DESELECT')
    obj_base.select_set(True)
    bpy.context.view_layer.objects.active = obj_base

    mod = obj_base.modifiers.new(name="Union", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object    = obj_adicional
    try:
        mod.solver = 'EXACT'
    except AttributeError:
        pass

    bpy.ops.object.modifier_apply(modifier="Union")
    bpy.data.objects.remove(obj_adicional, do_unlink=True)
    return obj_base


# ============================================================
# CRIAÇÃO DO PEGADOR DO ÊMBOLO
# ============================================================

def criar_pegador(z_base, altura_pegador=12.0, d_base=16.0, d_topo=11.0, segmentos=64):
    """
    Cria o pegador cônico com esfera no topo (igual ao módulo pegador() do OpenSCAD).
    Estrutura:
        - Cilindro cônico de altura_pegador * 0.6 (de d_base a d_topo)
        - Esfera achatada (scale Z = 0.6) no topo
    Retorna o objeto mesh do pegador.
    """
    altura_cilindro = altura_pegador * 0.6
    z_centro_cil    = z_base + altura_cilindro / 2.0

    # --- Cilindro cônico ---
    bpy.ops.mesh.primitive_cylinder_add(
        radius=d_base / 2.0,
        depth=altura_cilindro,
        vertices=segmentos,
        location=(0.0, 0.0, z_centro_cil)
    )
    cilindro = bpy.context.view_layer.objects.active
    cilindro.name = "pegador_cilindro"

    # Modificar os vértices do topo para criar a forma cônica
    bm = bmesh.new()
    bm.from_mesh(cilindro.data)

    z_topo_local = altura_cilindro / 2.0
    fator_raio   = (d_topo / 2.0) / (d_base / 2.0)

    for v in bm.verts:
        # Vértices na face superior (z próximo de +altura/2)
        if v.co.z > z_topo_local - 0.001:
            v.co.x *= fator_raio
            v.co.y *= fator_raio

    bm.to_mesh(cilindro.data)
    bm.free()
    cilindro.data.update()

    # --- Esfera achatada no topo ---
    raio_esfera = d_topo / 2.0
    z_topo_cil  = z_base + altura_cilindro
    # Esfera centralizada logo acima do cilindro, achatada em Z por 0.6
    z_esfera = z_topo_cil + raio_esfera * 0.6

    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=raio_esfera,
        segments=segmentos,
        ring_count=16,
        location=(0.0, 0.0, z_esfera)
    )
    esfera = bpy.context.view_layer.objects.active
    esfera.name = "pegador_esfera"
    esfera.scale.z = 0.6
    bpy.ops.object.transform_apply(scale=True)

    # --- Unir cilindro + esfera em um único mesh ---
    bpy.ops.object.select_all(action='DESELECT')
    cilindro.select_set(True)
    esfera.select_set(True)
    bpy.context.view_layer.objects.active = cilindro
    bpy.ops.object.join()

    pegador = bpy.context.view_layer.objects.active
    pegador.name = "pegador"
    return pegador


# ============================================================
# EXPORTAÇÃO STL
# ============================================================

def exportar_stl(obj, caminho_stl):
    """
    Exporta o objeto informado como arquivo STL.
    Tenta as duas APIs de exportação do Blender (3.x e 4.x).
    """
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Tentar API do Blender 4.x primeiro, depois a do 3.x
    exportado = False
    try:
        bpy.ops.wm.stl_export(
            filepath=caminho_stl,
            export_selected_objects=True,
            global_scale=1.0,
            use_scene_unit=True,
            ascii_format=False,
            apply_modifiers=True,
        )
        exportado = True
    except AttributeError:
        pass

    if not exportado:
        try:
            bpy.ops.export_mesh.stl(
                filepath=caminho_stl,
                use_selection=True,
                global_scale=1.0,
                use_scene_unit=True,
                ascii=False,
                apply_modifiers=True,
            )
            exportado = True
        except Exception as erro:
            print(f"  ERRO ao exportar STL: {erro}")

    if exportado:
        print(f"  STL exportado: {caminho_stl}")
    return exportado


# ============================================================
# GERAÇÃO DA LUVA
# ============================================================

def criar_luva(svg_path, tamanho, altura, parede, nome, pasta_saida):
    """
    Gera a peça LUVA (cutter / cortador):
        - Parede externa com a forma do SVG
        - Espessura = parede mm
        - Altura = altura mm
        - Aberta nas duas extremidades (tubo)

    Estratégia:
        1. Importar SVG → curva com offset = +parede → mesh externo
        2. Importar SVG → curva com offset = 0      → mesh interno
        3. Extrudar ambos para 'altura'
        4. Boolean DIFFERENCE: externo - interno = tubo/luva
    """
    print("\n--- Criando LUVA ---")

    # === Mesh externo (contorno + parede) ===
    curvas_ext = importar_svg(svg_path)
    if not curvas_ext:
        print("  ERRO: Nenhuma curva foi importada do SVG.")
        return False

    fator = escalar_e_centralizar(curvas_ext, tamanho)
    print(f"  Fator de escala aplicado: {fator:.4f}")

    # Depois de escalar, recalcular o offset em unidades de cena
    # O offset do Blender é em unidades da cena (mm após configurar scale_length=0.001)
    # Porém, as curvas SVG são importadas em escala própria. Após aplicar transform_apply
    # com scale, o offset precisa ser informado na escala original da curva ANTES do apply.
    # Como já aplicamos transform_apply, o offset agora é direto em mm.
    mesh_ext = converter_curvas_para_mesh(curvas_ext, offset_mm=parede, nome="luva_externo")
    if mesh_ext is None:
        print("  ERRO: Falha ao converter SVG para mesh externo.")
        return False

    extrudar_para_altura(mesh_ext, altura)

    # === Mesh interno (contorno original) ===
    curvas_int = importar_svg(svg_path)
    if not curvas_int:
        print("  ERRO: Falha na segunda importação do SVG.")
        return False

    escalar_e_centralizar(curvas_int, tamanho)

    mesh_int = converter_curvas_para_mesh(curvas_int, offset_mm=0.0, nome="luva_interno")
    if mesh_int is None:
        print("  ERRO: Falha ao converter SVG para mesh interno.")
        return False

    extrudar_para_altura(mesh_int, altura)

    # === Boolean: externo - interno = parede ===
    print("  Aplicando boolean DIFFERENCE (externo - interno)...")
    luva = boolean_diferenca(mesh_ext, mesh_int)
    luva.name = f"{nome}_luva"

    # === Exportar ===
    stl_path = os.path.join(pasta_saida, f"{nome}_luva.stl")
    sucesso = exportar_stl(luva, stl_path)

    # Limpar objeto da cena
    bpy.data.objects.remove(luva, do_unlink=True)

    return sucesso


# ============================================================
# GERAÇÃO DO ÊMBOLO
# ============================================================

def criar_embolo(svg_path, tamanho, altura, folga, relevo, nome, pasta_saida):
    """
    Gera a peça ÊMBOLO (press / pistão):
        - Corpo sólido com o formato do SVG, reduzido por 'folga' para encaixar na luva
        - Altura = altura mm
        - Pegador cônico com esfera no topo (acima do corpo)
        - Relevo gravado na base (subtração do contorno do SVG na profundidade 'relevo')

    Estratégia:
        1. Importar SVG → curva com offset = -folga → mesh do corpo
        2. Extrudar para 'altura'
        3. Criar pegador cônico + esfera, unir ao corpo
        4. Importar SVG → curva com offset = 0 → mesh do relevo (extrudado por 'relevo')
        5. Boolean DIFFERENCE: corpo+pegador - relevo = gravação na base
    """
    print("\n--- Criando ÊMBOLO ---")

    # Parâmetros do pegador (iguais ao módulo OpenSCAD)
    PEGADOR_H      = 12.0   # altura total do pegador (mm)
    PEGADOR_D_BASE = 16.0   # diâmetro da base do cilindro cônico (mm)
    PEGADOR_D_TOPO = 11.0   # diâmetro do topo do cilindro cônico (mm)

    # === Corpo do êmbolo ===
    curvas_corpo = importar_svg(svg_path)
    if not curvas_corpo:
        print("  ERRO: Nenhuma curva foi importada do SVG.")
        return False

    fator = escalar_e_centralizar(curvas_corpo, tamanho)
    print(f"  Fator de escala aplicado: {fator:.4f}")

    # Reduzir por 'folga' para caber na luva com folga de ajuste
    mesh_corpo = converter_curvas_para_mesh(curvas_corpo, offset_mm=-folga, nome="embolo_corpo")
    if mesh_corpo is None:
        print("  ERRO: Falha ao converter SVG para mesh do corpo.")
        return False

    extrudar_para_altura(mesh_corpo, altura)

    # === Pegador ===
    pegador = criar_pegador(
        z_base=altura,
        altura_pegador=PEGADOR_H,
        d_base=PEGADOR_D_BASE,
        d_topo=PEGADOR_D_TOPO
    )

    # === Unir corpo + pegador ===
    print("  Unindo corpo e pegador...")
    bpy.ops.object.select_all(action='DESELECT')
    mesh_corpo.select_set(True)
    pegador.select_set(True)
    bpy.context.view_layer.objects.active = mesh_corpo
    bpy.ops.object.join()
    embolo = bpy.context.view_layer.objects.active
    embolo.name = f"{nome}_embolo"

    # === Relevo gravado na base ===
    # Importar SVG novamente para criar a subtração do relevo
    curvas_relevo = importar_svg(svg_path)
    if curvas_relevo:
        escalar_e_centralizar(curvas_relevo, tamanho)

        mesh_relevo = converter_curvas_para_mesh(
            curvas_relevo, offset_mm=0.0, nome="relevo_tool"
        )

        if mesh_relevo is not None:
            # Posicionar levemente abaixo da base para o boolean funcionar corretamente
            mesh_relevo.location.z = -BOOLEAN_OVERLAP_Z
            # Extrudar por profundidade = relevo + margem de sobreposição
            extrudar_para_altura(mesh_relevo, relevo + BOOLEAN_DEPTH_MARGIN)

            print("  Gravando relevo na base do êmbolo...")
            embolo = boolean_diferenca(embolo, mesh_relevo)
            embolo.name = f"{nome}_embolo"
        else:
            print("  AVISO: Não foi possível criar o relevo — SVG pode estar vazio.")
    else:
        print("  AVISO: Não foi possível importar SVG para o relevo.")

    # === Exportar ===
    stl_path = os.path.join(pasta_saida, f"{nome}_embolo.stl")
    sucesso = exportar_stl(embolo, stl_path)

    # Limpar objeto da cena
    bpy.data.objects.remove(embolo, do_unlink=True)

    return sucesso


# ============================================================
# PONTO DE ENTRADA PRINCIPAL
# ============================================================

def main():
    """Função principal: orquestra a geração dos dois STLs."""
    args = analisar_argumentos()

    print()
    print("=" * 60)
    print("  BLENDER — GERADOR DE EJETORES DE BRIGADEIRO")
    print("=" * 60)
    print(f"  SVG    : {args.svg}")
    print(f"  Saída  : {args.saida}")
    print(f"  Nome   : {args.nome}")
    print(f"  Tamanho: {args.tamanho} mm  |  Altura: {args.altura} mm")
    print(f"  Relevo : {args.relevo} mm  |  Parede: {args.parede} mm  |  Folga: {args.folga} mm")
    print("=" * 60)

    # Verificar se o SVG existe (segurança extra)
    if not os.path.isfile(args.svg):
        print(f"\nERRO: Arquivo SVG não encontrado: {args.svg}")
        sys.exit(1)

    # Garantir que a pasta de saída existe
    os.makedirs(args.saida, exist_ok=True)

    # Configurar cena para milímetros
    configurar_cena_mm()

    # --- Gerar LUVA ---
    limpar_cena()
    ok_luva = criar_luva(
        svg_path=args.svg,
        tamanho=args.tamanho,
        altura=args.altura,
        parede=args.parede,
        nome=args.nome,
        pasta_saida=args.saida,
    )

    # --- Gerar ÊMBOLO ---
    limpar_cena()
    ok_embolo = criar_embolo(
        svg_path=args.svg,
        tamanho=args.tamanho,
        altura=args.altura,
        folga=args.folga,
        relevo=args.relevo,
        nome=args.nome,
        pasta_saida=args.saida,
    )

    # --- Resultado ---
    print()
    print("=" * 60)
    if ok_luva and ok_embolo:
        print("  Geração concluída com sucesso!")
    else:
        print("  Geração concluída com ERROS:")
        if not ok_luva:
            print("    - Luva não foi gerada")
        if not ok_embolo:
            print("    - Êmbolo não foi gerado")
    print("=" * 60)


# Executar função principal
main()
