from PIL import Image
import os

def encontrar_padrao(imagem, tolerancia=15):
    """
    Encontra posições onde há o padrão vertical de cores no último pixel da direita
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Cores do padrão (RGB 0-255)
    c1 = (255, 255, 255)
    c2 = (101, 98, 99)
    c3 = (189, 188, 188)
    
    y = 0
    while y < altura - 6:
        match = False
        padrao_altura_total = 0
        
        # Margem de erro de 1px na altura de cada faixa (nominal: 1, 4, 1)
        for h1 in range(1, 3):      # 1 a 2 px
            for h2 in range(3, 6):    # 3 a 5 px
                for h3 in range(1, 3):  # 1 a 2 px
                    total_h = h1 + h2 + h3
                    if y + total_h > altura:
                        continue
                    
                    ok = True
                    curr_y = y
                    
                    # Verificar faixa 1 (Branco)
                    for dy in range(h1):
                        p = pixels[largura - 1, curr_y + dy]
                        r, g, b = p[:3] if len(p) >= 3 else (p, p, p)
                        if abs(r - c1[0]) > tolerancia or abs(g - c1[1]) > tolerancia or abs(b - c1[2]) > tolerancia:
                            ok = False
                            break
                    if not ok: continue
                    curr_y += h1
                    
                    # Verificar faixa 2 (Cinza escuro)
                    for dy in range(h2):
                        p = pixels[largura - 1, curr_y + dy]
                        r, g, b = p[:3] if len(p) >= 3 else (p, p, p)
                        if abs(r - c2[0]) > tolerancia or abs(g - c2[1]) > tolerancia or abs(b - c2[2]) > tolerancia:
                            ok = False
                            break
                    if not ok: continue
                    curr_y += h2
                    
                    # Verificar faixa 3 (Cinza claro)
                    for dy in range(h3):
                        p = pixels[largura - 1, curr_y + dy]
                        r, g, b = p[:3] if len(p) >= 3 else (p, p, p)
                        if abs(r - c3[0]) > tolerancia or abs(g - c3[1]) > tolerancia or abs(b - c3[2]) > tolerancia:
                            ok = False
                            break
                    
                    if ok:
                        match = True
                        padrao_altura_total = total_h
                        break
                if match: break
            if match: break
        
        if match:
            # Corta 17 pixels antes do padrão começar, deixando-os no início da nova imagem
            posicao_corte = y - 17
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão encontrado em y={y}, cortando em y={posicao_corte}")
            y += padrao_altura_total
        else:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando antes dos padrões encontrados
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
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
    
    # Corta a seção final após o último padrão
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "colunas"           # Substitua pelo nome da pasta de saída desejada
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")