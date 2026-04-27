# 🍫 Gerador de Ejetores de Brigadeiro — SVG → STL

Script Python para Windows que gera automaticamente os arquivos STL de ejetores de brigadeiro (**luva** e **êmbolo**) a partir de um arquivo SVG, usando o **Blender** via API Python.

---

## 📁 Arquivos

| Arquivo | Descrição |
|---|---|
| `gerar_ejetor.py` | **Lançador** — rode este no Prompt de Comando |
| `gerar_ejetor_blender.py` | Script interno do Blender — **não execute diretamente** |
| `README.md` | Este arquivo de instruções |

---

## 🔧 Pré-requisitos

### 1. Python 3.8 ou superior

Verifique com:
```
python --version
```
Download: <https://www.python.org/downloads/>

> ⚠️ Durante a instalação, marque **"Add Python to PATH"**.

### 2. Blender 3.x ou 4.x

Download: <https://www.blender.org/download/>

> ⚠️ O Blender precisa estar acessível de uma dessas formas:

**Opção A — Adicionar ao PATH do Windows:**
1. Instale o Blender normalmente
2. Abra o **Menu Iniciar** → pesquise **"Variáveis de Ambiente"**
3. Clique em **"Editar as variáveis de ambiente do sistema"**
4. Em **"Variáveis de usuário"**, clique em **PATH** → **Editar**
5. Clique em **Novo** e adicione o caminho da pasta do Blender (substitua `4.x` pela sua versão), por exemplo:
   ```
   C:\Program Files\Blender Foundation\Blender 4.x
   ```
6. Clique em **OK** em todas as janelas
7. Feche e reabra o Prompt de Comando

**Opção B — Definir BLENDER_PATH antes de rodar:**
```cmd
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.x\blender.exe
python gerar_ejetor.py ...
```

---

## ▶️ Como Usar

### Sintaxe básica

```cmd
python gerar_ejetor.py "CAMINHO\arquivo.svg" "PASTA_SAIDA" NOME_OPCIONAL
```

### Exemplos

```cmd
REM Uso mais simples (na mesma pasta dos scripts):
python gerar_ejetor.py polvo.svg . polvo

REM Com caminhos completos (aspas são obrigatórias se houver espaços):
python gerar_ejetor.py "C:\Meus Designs\polvo.svg" "C:\STLs Prontos" polvo

REM Sem nome — usa o nome do arquivo SVG automaticamente:
python gerar_ejetor.py "C:\SVGs\estrela.svg" "C:\STLs"

REM Personalizando parâmetros físicos:
python gerar_ejetor.py polvo.svg saida polvo --tamanho 35 --parede 2.0

REM Todos os parâmetros:
python gerar_ejetor.py polvo.svg saida polvo --tamanho 30 --altura 30 --relevo 1.2 --parede 1.6 --folga 0.35
```

### Resultado

Ao finalizar, você terá dois arquivos STL na pasta de saída:

```
NOME_luva.stl    ← cortador externo (paredes no formato do bicho)
NOME_embolo.stl  ← êmbolo/pistão (encaixa na luva, com relevo na base)
```

---

## ⚙️ Parâmetros Configuráveis

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `svg` | — | Caminho do arquivo SVG (obrigatório) |
| `saida` | — | Pasta onde os STLs serão salvos (obrigatório) |
| `nome` | nome do SVG | Nome base dos arquivos gerados |
| `--tamanho` | `30` | Tamanho externo do ejetor em mm |
| `--altura` | `30` | Altura da luva e do corpo do êmbolo em mm |
| `--relevo` | `1.2` | Profundidade do relevo gravado na base do êmbolo em mm |
| `--parede` | `1.6` | Espessura da parede da luva em mm |
| `--folga` | `0.35` | Folga entre êmbolo e luva em mm (para ajuste de impressão) |

---

## 📐 Estrutura das Peças Geradas

### Luva (cortador)

```
Vista lateral:

    ┌──┐  ←─ parede (1.6mm)
    │  │
    │  │  altura (30mm)
    │  │
    └──┘

Vista superior:

  ┌──────────┐
  │ ┌──────┐ │  ← paredes na forma do SVG
  │ │ vazio│ │  ← interior aberto
  │ └──────┘ │
  └──────────┘
```

- Peça **aberta** em cima e embaixo (tubo)
- Pressionada sobre o brigadeiro para cortar o formato
- Espessura da parede configurável com `--parede`

### Êmbolo (pistão)

```
Vista lateral:

       ●       ← esfera do pegador
      ╱ ╲
    ┌─────┐    ← cilindro cônico do pegador
    └─────┘
  ┌─────────┐  ← corpo sólido (forma do SVG)
  │░░░░░░░░░│  ← relevo gravado na base (profundidade = relevo)
  └─────────┘
```

- Corpo sólido com o formato do SVG, levemente menor que a luva (folga de ajuste)
- Pegador cônico com esfera no topo para prender com os dedos
- Relevo gravado na base: ao pressionar o êmbolo, imprime o desenho no brigadeiro

---

## 🖼️ Como Preparar o SVG

O resultado final depende muito da qualidade do SVG. Siga estas dicas para os melhores resultados:

### Fontes recomendadas de SVG

| Fonte | Observação |
|---|---|
| [Freepik](https://www.freepik.com) | Pesquise "animal silhouette vector" |
| [Flaticon](https://www.flaticon.com) | Ícones e silhuetas gratuitas |
| [SVGRepo](https://www.svgrepo.com) | Biblioteca aberta, sem cadastro |
| [Vecteezy](https://www.vecteezy.com) | Boa variedade de silhuetas |
| Inkscape (gratuito) | Crie ou edite seu próprio SVG |

### ✅ SVG ideal para ejetores

- **Silhueta única e fechada** — sem buracos internos ou paths separados
- **Forma simples e compacta** — sem elementos muito finos que quebram na impressão
- **Fundo branco ou transparente** — sem moldura/borda extra
- **Salvo em SVG simples** (não SVG Tiny, não SVG 1.2)

### Exportando SVG perfeito no Inkscape

1. Abra sua imagem ou desenhe a silhueta
2. Selecione o objeto → **Caminho → Objeto para Caminho**
3. Se houver vários objetos: **Caminho → União** (unir tudo em um único path)
4. **Arquivo → Salvar como** → formato **SVG simples** *(não "SVG do Inkscape")*
5. Confirme que o arquivo não tem grupos (`<g>`) aninhados com transformações complexas

### ❌ Erros comuns e como corrigir

| Problema | Sintoma | Solução |
|---|---|---|
| SVG com múltiplos paths soltos | Luva/êmbolo com peças separadas | Selecionar tudo → **Caminho → União** no Inkscape |
| SVG com clipPath ou máscara | Erro no Blender ou peça incorreta | Exportar como SVG simples sem clipPath |
| SVG muito detalhado (cabelos finos, etc.) | Falha no boolean ou peças com buracos | Simplificar: **Caminho → Simplificar** no Inkscape |
| Forma muito grande no SVG | Êmbolo maior que a luva | O script normaliza para `--tamanho` automaticamente |
| SVG com texto | Texto não importa como curva | Converter texto: **Texto → Objeto para Caminho** no Inkscape |
| SVG com bitmap embutido | Nenhuma curva importada | Use SVG vetorial (não raster/PNG incorporado) |
| Grupos com transformações | Escala errada | Selecionar → **Objeto → Flatten Transformações** |

---

## 🖨️ Configurações de Impressão 3D Recomendadas

| Configuração | Valor recomendado |
|---|---|
| Material | PLA ou PETG |
| Temperatura do bico | 200–210°C (PLA) / 230–240°C (PETG) |
| Temperatura da mesa | 60°C |
| Altura de camada | 0,15 mm |
| Velocidade de impressão | 40–50 mm/s |
| Infill | 30% mínimo |
| Suportes | Não são necessários |
| Número de perímetros | 3 ou mais |
| Resfriamento | Ligado (PLA) |
| Cor sugerida | Rosa pastel, lilás, azul bebê |

> 💡 **Dica:** Imprima a luva e o êmbolo separadamente. Teste o encaixe antes de usar — se estiver muito apertado, aumente `--folga` (tente 0.5 mm); se solto demais, diminua (tente 0.2 mm).

---

## 🐛 Solução de Problemas

### "Blender não encontrado no PATH"

```
ERRO: Blender não encontrado!
```

Solução: defina a variável antes de rodar:
```cmd
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.3\blender.exe
python gerar_ejetor.py polvo.svg . polvo
```

### "Arquivo SVG não encontrado"

Verifique o caminho. Se houver espaços, use aspas duplas:
```cmd
python gerar_ejetor.py "C:\Meus Designs\polvo bonito.svg" saida polvo
```

### Blender abre mas fecha sem gerar os STLs

- Veja as mensagens exibidas no Prompt de Comando
- Verifique se o SVG é válido (abra no Inkscape)
- Teste com um SVG simples (um círculo) para confirmar que o ambiente funciona
- Certifique-se de que `gerar_ejetor_blender.py` está na **mesma pasta** que `gerar_ejetor.py`

### Luva ou êmbolo com geometria incorreta (buracos, peças soltas)

- O SVG provavelmente tem paths não fechados ou com self-intersections
- No Inkscape: **Extensões → Gerar por Caminho → Verificar e corrigir** ou **Caminho → União**
- Experimente reduzir o `--relevo` para `0.8` mm
- Experimente aumentar `--folga` para `0.5` mm

### Erro de boolean no Blender

```
AVISO: Um ou mais arquivos STL não foram gerados.
```

- O SVG pode ter geometria muito complexa ou não-manifold
- Simplifique o SVG no Inkscape: **Caminho → Simplificar** (Ctrl+L)
- Tente reduzir `--parede` para `1.4` mm ou aumentar para `2.0` mm

---

## 📋 Fluxo Completo — Resumo Rápido

```
1. Instalar Python 3.8+
2. Instalar Blender 3.x ou 4.x (adicionar ao PATH)
3. Baixar o SVG do bicho de sua escolha (Freepik, Flaticon, SVGRepo)
4. No Inkscape: simplificar → unir paths → exportar como SVG simples
5. Rodar no Prompt de Comando (cmd):
       cd "C:\pasta\dos\scripts"
       python gerar_ejetor.py "caminho\bicho.svg" "C:\STLs" bicho
6. Importar NOME_luva.stl e NOME_embolo.stl no slicer (PrusaSlicer, Bambu Studio, etc.)
7. Imprimir!
```

---

## 📜 Licença

Uso livre para projetos pessoais e comerciais. Créditos apreciados. 🍫
