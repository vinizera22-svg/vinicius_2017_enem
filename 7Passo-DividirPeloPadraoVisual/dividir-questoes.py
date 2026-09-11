from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def verificar_cor(pixel, cor_alvo, tolerancia=15):
    """Verifica se a cor do pixel está dentro da tolerância."""
    if len(pixel) == 4:
        r, g, b, _ = pixel
    else:
        r, g, b = pixel[:3]
    
    return (abs(r - cor_alvo[0]) <= tolerancia and
            abs(g - cor_alvo[1]) <= tolerancia and
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_faixa_azul(imagem, tolerancia=15):
    """
    Procura no último pixel da direita o padrão vertical:
    - 1 pixel de (255, 255, 255) [margem ±2px: de 1 a 3px]
    - 4 pixels de (101, 98, 99)   [margem ±2px: de 2 a 6px]
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    x = largura - 1  # Último pixel da direita
    
    cor_branca = (255, 255, 255)
    cor_cinza = (101, 98, 99)
    
    posicoes_corte = []
    y = 0

    while y < altura - 7:
        # Conta a quantidade de pixels brancos consecutivos
        brancos = 0
        y_atual = y
        while y_atual < altura and verificar_cor(pixels[x, y_atual], cor_branca, tolerancia):
            brancos += 1
            y_atual += 1

        # Aceita de 1 a 3 pixels brancos (1 pixel ±2)
        if 1 <= brancos <= 3:
            # Conta os pixels cinzas logo em seguida
            cinzas = 0
            while y_atual < altura and verificar_cor(pixels[x, y_atual], cor_cinza, tolerancia):
                cinzas += 1
                y_atual += 1

            # Aceita de 2 a 6 pixels cinzas (4 pixels ±2)
            if 2 <= cinzas <= 6:
                # Corta 19 pixels antes do padrão começar
                posicao_corte = y - 19
                if posicao_corte < 0:
                    posicao_corte = 0
                
                posicoes_corte.append(posicao_corte)
                print(f"Padrão encontrado em y={y}, cortando em y={posicao_corte}")
                
                # Avança a leitura além do padrão detectado
                y = y_atual
                continue

        y += 1

    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando com base no padrão localizado
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_faixa_azul(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte

    # Salva a última parte restante da imagem
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "NOME-DA-SUA-IMAGEM.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "NOME-PASTA-SAIDA"           # Substitua pela pasta de saída desejada
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")