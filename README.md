# 🍫 Gerador Automático de Ejetores de Brigadeiro (STL)

Script Python que converte imagens PNG/JPG em pares de arquivos STL prontos para impressão 3D — seguindo o padrão de ejetor de brigadeiro com **luva** (parte externa) e **êmbolo** (parte interna).

---

## Índice

1. [O que o script faz](#o-que-o-script-faz)
2. [Requisitos](#requisitos)
3. [Instalação passo a passo (Windows)](#instalação-passo-a-passo-windows)
4. [Como preparar as imagens](#como-preparar-as-imagens)
5. [Como executar](#como-executar)
6. [Parâmetros configuráveis](#parâmetros-configuráveis)
7. [Saída gerada](#saída-gerada)
8. [Exemplos de uso](#exemplos-de-uso)
9. [Solução de problemas](#solução-de-problemas)

---

## O que o script faz

```
PNG / JPG  →  SVG (vtracer)  →  STL par (Blender headless)
                                    ├── NOME_luva.stl
                                    └── NOME_embolo.stl
```

| Peça | Descrição |
|------|-----------|
| **Luva** | Tubo oco no formato do animal. Funciona como cortador — pressione sobre o brigadeiro para dar a forma. |
| **Êmbolo** | Peça sólida que cabe dentro da luva (com folga de 0,3 mm). Tem pegador cônico no topo. Empurre para ejetar o brigadeiro. |

- **Tamanho da luva = tamanho do êmbolo** (mesma altura, mesma forma base).
- Forma 100% baseada na sua imagem — o contorno é vetorizado automaticamente.
- Roda 100% por linha de comando no Windows (cmd / PowerShell). Sem interface gráfica.

---

## Requisitos

| Requisito | Versão mínima | Link |
|-----------|--------------|------|
| **Python** | 3.8+ | https://www.python.org/downloads/ |
| **Blender** | 3.6 LTS ou 4.x | https://www.blender.org/download/ |
| **vtracer** | qualquer | `pip install vtracer` |

> **Importante:** Instale o Blender normalmente (instalador `.msi`). O script detecta automaticamente os caminhos comuns de instalação.

---

## Instalação passo a passo (Windows)

### 1. Instalar Python 3.8+

Baixe em https://www.python.org/downloads/windows/ e marque **"Add Python to PATH"** durante a instalação.

Verifique no cmd:
```
python --version
```

### 2. Instalar vtracer

Abra o **Prompt de Comando (cmd)** ou **PowerShell** e execute:
```
pip install vtracer
```

### 3. Instalar Blender

Baixe e instale o Blender em https://www.blender.org/download/

Para que o script detecte automaticamente, você pode:

**Opção A — Adicionar ao PATH do Windows:**
1. Pressione `Win + R` → `sysdm.cpl` → Avançado → Variáveis de Ambiente
2. Em "Variáveis do sistema", selecione `Path` → Editar → Novo
3. Adicione o caminho da pasta do Blender, ex.:
   ```
   C:\Program Files\Blender Foundation\Blender 4.1
   ```
4. Clique OK e reinicie o cmd.

**Opção B — Informar o caminho na hora de executar** (sem precisar mexer no PATH):
```
python generate_molds.py --blender "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
```

### 4. Baixar os scripts deste repositório

```
git clone https://github.com/ivanluizjr/ivanluizjr.git
cd ivanluizjr
```

Ou baixe o ZIP pelo botão **"Code → Download ZIP"** no GitHub e extraia.

Os dois arquivos necessários são:
- `generate_molds.py` — script principal
- `blender_worker.py` — script do Blender (deve estar na mesma pasta)

---

## Como preparar as imagens

- Formatos aceitos: **PNG** ou **JPG/JPEG**
- Fundo **branco** e desenho **preto** (ou fundo muito claro e desenho escuro) funcionam melhor
- Resolução recomendada: **500 × 500 px** a **1500 × 1500 px**
- Quanto mais limpo e contrastado o contorno, melhor o resultado
- Imagens com muitos detalhes finos podem gerar geometria complexa

Exemplo de estrutura de pastas:
```
ivanluizjr/
├── generate_molds.py
├── blender_worker.py
├── input_images/           ← coloque suas imagens aqui
│   ├── polvo.png
│   ├── tartaruga.jpg
│   └── estrela.png
└── output_stl/             ← criada automaticamente
    ├── polvo_luva.stl
    ├── polvo_embolo.stl
    ├── tartaruga_luva.stl
    └── tartaruga_embolo.stl
```

---

## Como executar

### Uso básico (com configurações padrão — 30 mm)

```cmd
python generate_molds.py
```

O script vai:
1. Procurar imagens em `input_images\`
2. Gerar os STL em `output_stl\`

### Especificando pastas

```cmd
python generate_molds.py --input minhas_imagens --output moldes_impressao
```

### Com tamanho personalizado

```cmd
python generate_molds.py --size-mm 35 --height-mm 30
```

### Com caminho explícito do Blender

```cmd
python generate_molds.py --blender "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
```

### Modo verboso (ver todos os detalhes)

```cmd
python generate_molds.py --verbose
```

---

## Parâmetros configuráveis

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--input` / `-i` | `input_images` | Pasta com as imagens PNG/JPG de entrada |
| `--output` / `-o` | `output_stl` | Pasta de saída para os arquivos STL |
| `--size-mm` | `30` | Largura máxima final do ejetor em **mm** |
| `--height-mm` | `30` | Altura do ejetor em **mm** (luva e êmbolo têm a mesma altura) |
| `--wall-mm` | `1.8` | Espessura da parede da luva em **mm** |
| `--clearance-mm` | `0.3` | Folga entre êmbolo e luva em **mm** |
| `--handle-height-mm` | `12` | Altura do pegador cônico do êmbolo em **mm** |
| `--blender` | *(auto)* | Caminho completo para `blender.exe` |
| `--verbose` / `-v` | *(off)* | Exibe saída detalhada do Blender |

---

## Saída gerada

Para cada imagem `NOME.png` (ou `.jpg`), o script gera:

```
output_stl/
├── NOME_luva.stl       ← peça externa (cortador em forma de animal)
├── NOME_embolo.stl     ← peça interna (prensa com pegador)
└── _svg_temp/
    └── NOME.svg        ← SVG intermediário (pode ser descartado)
```

Os arquivos STL estão em **milímetros** e prontos para abrir em qualquer slicer (Cura, PrusaSlicer, Bambu Studio etc.).

---

## Exemplos de uso

### Exemplo 1 — Configuração padrão (30 × 30 mm)
```cmd
python generate_molds.py
```

### Exemplo 2 — Ejetores maiores (40 mm) com parede mais grossa
```cmd
python generate_molds.py --size-mm 40 --wall-mm 2.0 --height-mm 32
```

### Exemplo 3 — Pasta personalizada, Blender em caminho não-padrão
```cmd
python generate_molds.py ^
  --input C:\Users\ivan\Desktop\bichinhos ^
  --output C:\Users\ivan\Desktop\stl_prontos ^
  --size-mm 30 ^
  --blender "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe" ^
  --verbose
```

### Exemplo 4 — PowerShell
```powershell
python generate_molds.py `
  --input .\imagens `
  --output .\stl `
  --size-mm 30 --height-mm 30 --verbose
```

---

## Solução de problemas

### "Blender não encontrado"
- Verifique se o Blender está instalado.
- Use `--blender "caminho\completo\blender.exe"`.
- Adicione a pasta do Blender ao PATH do Windows (veja [Instalação](#instalação-passo-a-passo-windows)).

### "vtracer não está instalado"
```cmd
pip install vtracer
```

### "No curves imported" ou STL não gerado
- Verifique se a imagem tem bom contraste (fundo claro, desenho escuro).
- Execute com `--verbose` para ver a saída completa do Blender.
- Tente simplificar a imagem (menos detalhes finos, bordas mais nítidas).

### Êmbolo não encaixa na luva
- Aumente `--clearance-mm` (padrão 0.3 mm). Tente 0.4 ou 0.5 mm.
- Depende da tolerância da sua impressora 3D.

### STL parece deformado ou tem buracos
- Use imagens com contorno muito bem definido.
- Execute com `--verbose` para checar mensagens de erro do Blender.

---

---

## Olá, me chamo Ivan Junior
- 👀 Sou Desenvolvedor, formado em Análise e Desenvolvimento de Sistemas.
- 🌱 Desenvolvimento de aplicativos móveis híbridos Android e iOS em Flutter/Dart. Experiência em:
  - Clean Architecture e Clean Code
  - Design Patterns e Princípios SOLID
  - Gerenciamento de estado (Bloc, Getx, Mobx, ValueNotifier, ChangeNotifier)
  - Consumo de APIs (Dio e HTTP)
  - Integrações com Firebase (Push Notification, Analytics, Crashlytics)
  - Publicação de apps nas lojas Google Play e App Store
  - Controle de versão com GitHub e GitLab
  - Metodologias ágeis (Scrum/Kanban)
  - Injeção de dependências (Get It, Modular)
  - Flutter Web
  - Testes Unitários de Integração e Widgets
- 💞️ Desejo colaborar com projetos voltados ao Flutter e outros que forem possíveis colaborar.
- 📫 Para falar comigo basta enviar um e-mail para ivanluizjr@hotmail.com.


## Hello, my name is Ivan Junior
- 👀 I'm a Developer, graduated in Systems Analysis and Development, passionate about mobile development, mainly Flutter.
- 🌱 Development of hybrid Android and iOS mobile applications in Flutter/Dart. Experience in:
  - Clean Architecture and Clean Code
  - Design Patterns and SOLID Principles
  - State management (Bloc, Getx, Mobx, ValueNotifier, ChangeNotifier)
  - Consumption of APIs (Dio and HTTP)
  - Integrations with Firebase (Push Notification, Analytics, Crashlytics)
  - Publishing apps on Google Play and App Store
  - Version control with GitHub and GitLab
  - Agile methodologies (Scrum/Kanban)
  - Dependency injection (Get It, Modular)
  - FlutterWeb
  - Integration Unit Tests and Widgets
- 💞️ I want to collaborate with projects aimed at Flutter and others that are possible to collaborate with.
- 📫 To talk to me, just send an email to ivanluizjr@hotmail.com.

<div align=>
  <a href="https://github.com/ivanluizjr">
  <img height="180em" src="https://github-readme-stats.vercel.app/api?username=ivanluizjr&show_icons=true&theme=radical&include_all_commits=true&count_private=true"/>
  <img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username=ivanluizjr&layout=compact&langs_count=7&theme=radical"/>
</div>

<div style="display: inline_block"><br>
  <img align="center" alt="Ivan-Js" height="30" width="60" src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
  <img align="center" alt="Ivan_PHP" height="30" width="60" src="https://img.shields.io/badge/PHP-777BB4?style=for-the-badge&logo=php&logoColor=white">
  <img align="center" alt="Ivan-Flutter" height="30" width="60" src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white">
  <img align="center" alt="Ivan-HTML" height="30" width="60" src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white">
  <img align="center" alt="Ivan-CSS" height="30" width="60" src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white">
  <img align="center" alt="Ivan-Csharp" height="30" width="60" src="https://img.shields.io/badge/C%23-239120?style=for-the-badge&logo=c-sharp&logoColor=white">
  <img align="center" alt="Ivan-Dart" height="30" width="60" src="https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white">
</div>
  
##

<div> 
  <a href="https://www.youtube.com/channel/UCYOERw6eNKfIZNiUo3bOlgw" target="_blank"><img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" target="_blank"></a>
  <a href="https://www.instagram.com/ivanjunior775/" target="_blank"><img src="https://img.shields.io/badge/-Instagram-%23E4405F?style=for-the-badge&logo=instagram&logoColor=white" target="_blank"></a>
 	<a href="https://www.twitch.tv/dookan_" target="_blank"><img src="https://img.shields.io/badge/Twitch-9146FF?style=for-the-badge&logo=twitch&logoColor=white" target="_blank"></a>
 </a> 
  <a href = "mailto:ivanluizpjr@gmail.com"><img src="https://img.shields.io/badge/-Gmail-%23333?style=for-the-badge&logo=gmail&logoColor=white" target="_blank"></a>
  <a href="https://www.linkedin.com/in/ivan-junior-407768134/" target="_blank"><img src="https://img.shields.io/badge/-LinkedIn-%230077B5?style=for-the-badge&logo=linkedin&logoColor=white" target="_blank"></a> 
</div>
<!---
ivanluizjr/ivanluizjr is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
