# 🍫 Ejetor de Brigadeiro Gourmet — Blender 5.x

Script Python que gera um **ejetor/carimbo de brigadeiro como uma única peça sólida**
a partir de um arquivo SVG, exportando diretamente para STL pronto para impressão 3D.

---

## 📐 Design da peça

```
  ┌────────────────────────────┐  ← topo / face de pressão  (z = 30 mm)
  │   CORPO PRINCIPAL  28 mm   │    contorno externo do SVG
  │   sólido  44 × 40 mm       │
  ├────────────────────────────┤  ← z = 2 mm
  │   RELEVO DO CARIMBO  2 mm  │    mesmo SVG em 85% do tamanho
  │   face de carimbar         │    → imprime o desenho no brigadeiro
  └────────────────────────────┘  ← base (z = 0)
```

| Dimensão          | Valor padrão |
|-------------------|:------------:|
| Largura (L)       | 44 mm        |
| Comprimento (C)   | 40 mm        |
| Altura total (A)  | 30 mm        |
| Relevo carimbo    |  2 mm        |
| Escala do relevo  | 85 %         |

**Como usar:** pressione a base (z = 0) contra o brigadeiro para carimbá-lo;
o contorno externo dá a forma e o relevo imprime o desenho.

---

## 🗂 Arquivos

| Arquivo                     | Descrição                                     |
|-----------------------------|-----------------------------------------------|
| `gerar_ejetor.py`           | Launcher (Windows/Linux/macOS) — chame este   |
| `gerar_ejetor_blender.py`   | Script interno do Blender (não chame direto)  |

---

## 🚀 Como usar (Windows)

### Pré-requisitos

- **Blender 5.x** instalado ([blender.org](https://www.blender.org/))
- **Python 3.8+** no PATH do Windows (instalado separadamente — *não* o Python embutido no Blender)
- Um arquivo **SVG vetorizado simples** (veja a seção abaixo)

### Comando

```cmd
python gerar_ejetor.py "caminho\para\desenho.svg" "pasta\de\saida" nome_opcional
```

**Exemplos:**

```cmd
python gerar_ejetor.py "C:\Ejetores\concha.svg" "C:\Ejetores\STL" concha
python gerar_ejetor.py "E:\3D PRINTERS\polvo.svg" "E:\3D PRINTERS\STL"
```

O STL será salvo em `<pasta_de_saida>\<nome>_ejetor.stl`.

### Resultado esperado no terminal

```
============================================================
  GERADOR DE EJETOR DE BRIGADEIRO
============================================================
  Blender : C:\Program Files\Blender Foundation\Blender 5.1\blender.exe
  SVG     : C:\Ejetores\concha.svg
  Saída   : C:\Ejetores\STL
  Nome    : concha
============================================================
[1/4] Importando contorno externo e criando corpo principal...
[2/4] Importando contorno para relevo do carimbo...
[3/4] Unindo corpo + relevo em uma peça única...
[4/4] Exportando STL...
  STL salvo em: C:\Ejetores\STL\concha_ejetor.stl
✅  Concluído!
```

---

## 🖼 Como preparar o SVG corretamente

O Blender importa SVGs com **apenas paths (caminhos vetoriais)**.
Para garantir compatibilidade:

### No Inkscape (recomendado, gratuito)

1. Abra sua imagem/desenho no Inkscape.
2. Converta tudo para paths:
   - Selecione todos os objetos → `Caminho → Objeto para Caminho` (`Shift+Ctrl+C`)
   - Se tiver texto: `Texto → Converter em Path`
3. Exporte como **SVG Simples**:
   - `Arquivo → Salvar uma Cópia → Formato: SVG simples (*.svg)`
4. Verifique: abra o arquivo `.svg` em um editor de texto — deve conter
   apenas elementos `<path d="...">` (sem `<image>`, `<text>`, `<rect>` etc.).

### Regras do SVG

| ✅ Aceito                        | ❌ Não suportado            |
|---------------------------------|-----------------------------|
| `<path d="M...Z">`              | Imagens raster (`<image>`)  |
| Paths compostos (múltiplos sub-paths) | Texto (`<text>`)      |
| Paths com fill                  | Gradientes, filtros         |

---

## ⚙️ Ajustando para outro tamanho

Edite as constantes no início de **`gerar_ejetor_blender.py`**:

```python
LARGURA_MM      = 44.0   # Largura total (L) em mm
COMPRIMENTO_MM  = 40.0   # Comprimento total (C) em mm
ALTURA_TOTAL_MM = 30.0   # Altura total (A) em mm
RELEVO_MM       = 2.0    # Altura do relevo do carimbo em mm
ESCALA_RELEVO   = 0.85   # Tamanho do relevo vs contorno (0.0 – 1.0)
```

**Exemplos de outros tamanhos:**

| Brigadeiro        | LARGURA | COMPRIMENTO | ALTURA |
|-------------------|:-------:|:-----------:|:------:|
| Mini (trufinha)   | 30 mm   | 28 mm       | 25 mm  |
| Gourmet (padrão)  | 44 mm   | 40 mm       | 30 mm  |
| Grande/festa      | 55 mm   | 50 mm       | 35 mm  |

---

## 🔧 Blender não encontrado?

Se o script não localizar o Blender automaticamente, adicione o caminho
da instalação em `BLENDER_PATHS_WINDOWS` no arquivo `gerar_ejetor.py`:

```python
BLENDER_PATHS_WINDOWS = [
    r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
    r"D:\Blender\blender.exe",   # ← adicione seu caminho aqui
    ...
]
```

**Ou** adicione a pasta do Blender ao PATH do Windows:
`Painel de Controle → Sistema → Variáveis de Ambiente → Path → Editar → Novo`

---

## 🖨️ Configurações de impressão recomendadas

| Parâmetro         | Valor          |
|-------------------|----------------|
| Material          | PLA ou PETG    |
| Altura de camada  | 0,15 – 0,2 mm  |
| Preenchimento     | 40 – 60 %      |
| Suportes          | Não necessário |
| Orientação        | Base (z=0) na mesa de impressão |

---

## 📝 Notas

- O script usa **apenas bibliotecas nativas do Blender** — não requer instalação de pacotes pip.
- Compatível com **Blender 5.x** (usa `bpy.ops.wm.stl_export`).
- Para Blender 4.x: substitua `bpy.ops.wm.stl_export` por `bpy.ops.export_mesh.stl`.
