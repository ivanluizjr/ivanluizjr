#!/usr/bin/env python3
"""
gerar_ejetor.py
---------------
Gera o arquivo OpenSCAD de um ejetor de brigadeiro paramétrico
(barril + êmbolo), pronto para fatiamento e impressão 3D.

Uso:
    python gerar_ejetor.py [saida.scad]

Se nenhum argumento for passado, grava em 'ejetor_brigadeiro.scad'
no mesmo diretório deste script.

Peças geradas
-------------
  PEÇA 1 – Barril (barrel)
    Cilindro oco com:
      - Diâmetro externo configurable (padrão 34 mm)
      - Parede de 2 mm
      - Altura de 60 mm
      - 4 ranhuras de preensão no exterior
      - Bocal de saída na base (diâmetro 20 mm, afunila 5 mm)

  PEÇA 2 – Êmbolo (plunger)
    - Haste cilíndrica que desliza dentro do barril
    - Cabo em disco no topo (diâmetro 40 mm, espessura 4 mm)
    - Folga de 0,3 mm em relação ao barril
"""

import sys
import os
import textwrap


# ─────────────────────────────────────────────
# Parâmetros globais (mm)
# ─────────────────────────────────────────────
PARAMS = {
    "fn":             80,     # resolução de curvas
    "barrel_od":      34.0,   # diâmetro externo do barril (configurável)
    "wall_t":          2.0,   # espessura de parede do barril
    "barrel_h":       60.0,   # altura do barril
    "nozzle_h":        5.0,   # altura da zona de bocal
    "nozzle_d":       20.0,   # diâmetro da abertura do bocal
    "grip_n":          4,     # número de ranhuras de preensão
    "grip_depth":      1.5,   # profundidade de cada ranhura
    "grip_w":          4.0,   # largura linear de cada ranhura (mm, eixo y do sphere)
    "clearance":       0.3,   # folga entre êmbolo e barril
    "handle_d":       40.0,   # diâmetro do cabo do êmbolo
    "handle_t":        4.0,   # espessura do cabo
    "plunger_extra":   5.0,   # altura extra do êmbolo além do barril
}


def build_scad(p: dict) -> str:
    """Retorna o código OpenSCAD completo como string."""

    barrel_id   = p["barrel_od"] - 2 * p["wall_t"]
    plunger_od  = barrel_id - 2 * p["clearance"]
    plunger_h   = p["barrel_h"] - p["nozzle_h"] + p["plunger_extra"]

    code = textwrap.dedent(f"""\
        // =====================================================
        // EJETOR DE BRIGADEIRO
        // Gerado por gerar_ejetor.py
        //
        // PEÇA 1: barril  — posicionado em x = -{p["barrel_od"] + 10:.1f}
        // PEÇA 2: êmbolo  — posicionado em x =  {p["barrel_od"] + 10:.1f}
        //
        // Imprima cada peça separadamente.
        // Fatiador: coloque o barril de cabeça para baixo (bocal no
        // alto) para melhor bridging; imprima o êmbolo normalmente.
        // =====================================================
        $fn = {p["fn"]};

        barrel_od    = {p["barrel_od"]};
        barrel_id    = {barrel_id:.2f};
        barrel_h     = {p["barrel_h"]};
        wall_t       = {p["wall_t"]};
        nozzle_h     = {p["nozzle_h"]};
        nozzle_d     = {p["nozzle_d"]};
        grip_n       = {p["grip_n"]};
        grip_depth   = {p["grip_depth"]};
        grip_w       = {p["grip_w"]};
        clearance    = {p["clearance"]};
        handle_d     = {p["handle_d"]};
        handle_t     = {p["handle_t"]};
        plunger_od   = {plunger_od:.2f};
        plunger_h    = {plunger_h:.2f};

        // =====================================================
        // PEÇA 1: BARRIL
        // =====================================================
        module barrel() {{
            difference() {{
                union() {{
                    // corpo principal
                    cylinder(d=barrel_od, h=barrel_h);
                    // anel de reforço no topo
                    translate([0, 0, barrel_h - 3])
                        cylinder(d=barrel_od + 2, h=3);
                }}

                // canal interno
                translate([0, 0, -0.1])
                    cylinder(d=barrel_id, h=barrel_h + 0.2);

                // bocal cônico na base
                translate([0, 0, -0.1])
                    cylinder(d1=nozzle_d, d2=barrel_id, h=nozzle_h + 0.1);

                // ranhuras de preensão no exterior
                for(i = [0 : grip_n - 1]) {{
                    rotate([0, 0, i * (360 / grip_n)])
                        translate([barrel_od / 2, 0, barrel_h * 0.25])
                            scale([grip_depth, grip_w, barrel_h * 0.5])
                                sphere(r=1);
                }}
            }}
        }}

        // =====================================================
        // PEÇA 2: ÊMBOLO
        // =====================================================
        module plunger() {{
            union() {{
                // haste
                cylinder(d=plunger_od, h=plunger_h);
                // cabo em disco
                translate([0, 0, plunger_h])
                    cylinder(d=handle_d, h=handle_t);
                // chanfro de entrada (facilita inserção no barril)
                translate([0, 0, -0.1])
                    cylinder(d1=plunger_od - 2, d2=plunger_od, h=2);
            }}
        }}

        // =====================================================
        // VISUALIZAÇÃO LADO A LADO
        // =====================================================
        translate([-(barrel_od + 10), 0, 0]) barrel();
        translate([ (barrel_od + 10), 0, 0]) plunger();
    """)
    return code


def main():
    output_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ejetor_brigadeiro.scad"
    )

    scad_content = build_scad(PARAMS)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(scad_content)

    print(f"Arquivo gerado: {output_path}")
    print()
    print("Próximos passos:")
    print("  1. Abra o arquivo no OpenSCAD (https://openscad.org).")
    print("  2. Pressione F6 para renderizar.")
    print("  3. Exporte cada peça como STL separado:")
    print("     - Barril:  descomente apenas 'barrel();'  e exporte.")
    print("     - Êmbolo:  descomente apenas 'plunger();' e exporte.")
    print("  4. Fatie e imprima em PLA ou PETG (alimentar).")
    print()
    print("Parâmetros usados:")
    for k, v in PARAMS.items():
        print(f"  {k:20s} = {v}")


if __name__ == "__main__":
    main()
