import os
import shutil
import re
import sys
import subprocess

def install_pillow():
    try:
        import PIL
        print("Pillow já está instalado.")
    except ImportError:
        print("Pillow não encontrado. Instalando via pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)

def main():
    # 1. Instalar Pillow se necessário
    install_pillow()
    from PIL import Image, ImageDraw, ImageFont

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Diretório raiz do projeto: {base_dir}")

    # 1. Crie as pastas: data/, assets/, assets/rooms/, assets/places/, templates/, dist/
    folders = [
        "data",
        "assets",
        "assets/rooms",
        "assets/places",
        "templates",
        "dist"
    ]
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Diretório garantido: {folder}")

    # 2. Mover o arquivo welcome-book-exemplo.yaml para data/welcome-book.yaml
    exemplo_path = os.path.join(base_dir, "welcome-book-exemplo.yaml")
    destino_path = os.path.join(base_dir, "data", "welcome-book.yaml")

    if os.path.exists(exemplo_path):
        shutil.move(exemplo_path, destino_path)
        print("welcome-book-exemplo.yaml movido para data/welcome-book.yaml")
    else:
        if os.path.exists(destino_path):
            print("welcome-book-exemplo.yaml não encontrado na raiz, mas data/welcome-book.yaml já existe.")
        else:
            print("AVISO: Nenhum arquivo welcome-book-exemplo.yaml ou data/welcome-book.yaml encontrado!")
            return

    # 3. Leia o arquivo data/welcome-book.yaml e liste TODOS os caminhos de imagem que ele referencia
    with open(destino_path, "r", encoding="utf-8") as f:
        yaml_content = f.read()

    # Encontrar caminhos de imagens usando expressão regular
    # Ex: assets/logo.png, assets/rooms/chale.jpg, etc.
    image_paths = re.findall(r'assets/[\w/-]+\.(?:png|jpg|jpeg)', yaml_content)
    # Remover duplicatas mantendo a ordem
    image_paths = list(dict.fromkeys(image_paths))
    print(f"\nImagens encontradas no YAML ({len(image_paths)}):")
    for ip in image_paths:
        print(f"  - {ip}")

    # 4. Para cada caminho de imagem listado, gere uma imagem placeholder
    # Cores harmoniosas predefinidas
    colors = [
        (210, 105, 30),   # Chocolate / Terracota
        (70, 130, 180),   # Steel Blue
        (46, 139, 87),    # Sea Green
        (128, 0, 128),    # Purple
        (218, 165, 32),   # Goldenrod
        (188, 143, 143),  # Rosy Brown
        (25, 25, 112),    # Midnight Blue
        (107, 142, 35),   # Olive Drab
        (205, 92, 92),    # Indian Red
        (0, 139, 139),    # Dark Cyan
        (105, 105, 105),  # Dim Gray
        (139, 69, 19),    # Saddle Brown
        (75, 0, 130),     # Indigo
        (85, 107, 47),    # Dark Olive Green
    ]

    # Carregar fonte do sistema se possível para ficar maior e legível
    font_large = None
    font_logo = None
    # No Windows, tentamos a Arial
    possible_fonts = [
        "C:\\Windows\\Fonts\\arial.ttf",
        "arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf"
    ]
    for pf in possible_fonts:
        try:
            font_large = ImageFont.truetype(pf, size=48)
            font_logo = ImageFont.truetype(pf, size=150)
            break
        except Exception:
            continue

    if not font_large:
        # Fallback para fonte padrão
        try:
            font_large = ImageFont.load_default(size=48)
            font_logo = ImageFont.load_default(size=150)
        except Exception:
            font_large = ImageFont.load_default()
            font_logo = ImageFont.load_default()

    def get_text_size(draw, text, font):
        try:
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            return right - left, bottom - top
        except AttributeError:
            return draw.textsize(text, font=font)

    print("\nGerando placeholders...")
    for idx, rel_path in enumerate(image_paths):
        abs_img_path = os.path.join(base_dir, rel_path)
        # Garantir a pasta da imagem
        os.makedirs(os.path.dirname(abs_img_path), exist_ok=True)

        filename = os.path.basename(rel_path)

        if rel_path == "assets/logo.png":
            # PNG 600x600 com fundo transparente e "VL" no centro
            img = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # Desenhar um círculo sutil ou apenas o texto
            # Vamos colocar o círculo cinza/azul elegante com transparência e texto branco no centro
            circle_color = (70, 130, 180, 220)
            draw.ellipse([50, 50, 550, 550], fill=circle_color)
            
            text = "VL"
            w, h = get_text_size(draw, text, font_logo)
            # Centralizar
            x = (600 - w) / 2
            y = (600 - h) / 2 - 15  # ajuste de offset vertical do texto
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font_logo)
            img.save(abs_img_path, "PNG")
            print(f"  [PNG] {rel_path} gerado com sucesso.")
        else:
            # JPEG 1080x720, cor sólida diferente, texto com nome no centro
            color = colors[idx % len(colors)]
            img = Image.new("RGB", (1080, 720), color)
            draw = ImageDraw.Draw(img)
            
            text = filename
            w, h = get_text_size(draw, text, font_large)
            # Centralizar
            x = (1080 - w) / 2
            y = (720 - h) / 2
            
            # Adicionar um retângulo de fundo translúcido para o texto para melhorar legibilidade se necessário
            # mas o fundo já é sólido, então texto branco direto é perfeito.
            draw.text((x, y), text, fill=(255, 255, 255), font=font_large)
            img.save(abs_img_path, "JPEG", quality=90)
            print(f"  [JPEG] {rel_path} gerado com cor {color}.")

    # 5. Confirme que TODOS os caminhos de imagem do YAML agora existem no disco
    print("\nVerificando se todos os caminhos existem no disco:")
    all_exist = True
    for rel_path in image_paths:
        abs_img_path = os.path.join(base_dir, rel_path)
        exists = os.path.exists(abs_img_path)
        status = "[OK]" if exists else "[FALHOU]"
        print(f"  - {rel_path}: {status}")
        if not exists:
            all_exist = False

    if all_exist:
        print("Confirmação: Todas as imagens referenciadas existem no disco!")
    else:
        print("ERRO: Algumas imagens não foram geradas com sucesso!")

    # 6. Inicialize um repositório git na pasta (git init) e crie um .gitignore adequado
    print("\nInicializando repositório git...")
    try:
        subprocess.run(["git", "init"], cwd=base_dir, check=True)
        print("Git inicializado com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar Git: {e}")

    # Verificar / criar .gitignore
    gitignore_path = os.path.join(base_dir, ".gitignore")
    required_ignores = ["__pycache__/", ".venv/", "venv/", "env/"]
    
    existing_content = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

    # Se 'dist/' estiver sendo ignorado, removemos
    lines = existing_content.splitlines()
    new_lines = []
    has_changes = False
    
    # Garantir que dist/ não é ignorado
    for line in lines:
        if line.strip() == "dist/" or line.strip() == "dist":
            has_changes = True
            continue
        new_lines.append(line)

    # Adicionar o que está faltando
    for ignore in required_ignores:
        if ignore not in existing_content:
            new_lines.append(ignore)
            has_changes = True

    if not os.path.exists(gitignore_path) or has_changes:
        # Se o arquivo não existia, criamos um padrão básico adequado
        if not os.path.exists(gitignore_path):
            new_lines = required_ignores + ["*.py[cod]", "*.env", ".idea/", ".vscode/"]
        
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")
        print(".gitignore atualizado/criado.")
    else:
        print(".gitignore já está adequado.")

    # Mostrar árvore de arquivos usando listagem recursiva no Python
    print("\nÁrvore de pastas do projeto:")
    print_tree(base_dir)

def print_tree(startpath):
    # Vamos ignorar .git, __pycache__, e .venv na listagem para ficar limpa
    ignore_dirs = {".git", "__pycache__", ".venv", "venv", "env", ".idea", ".vscode"}
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        folder_name = os.path.basename(root)
        if folder_name == os.path.basename(startpath):
            print(f"{folder_name}/")
        else:
            print(f"{indent}{folder_name}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

if __name__ == "__main__":
    main()
