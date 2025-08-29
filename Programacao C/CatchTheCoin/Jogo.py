import pygame
import random
import sys
import os
import json

# Inicializa o pygame
pygame.init()

# Constantes da tela
LARGURA = 800
ALTURA = 600
FPS = 60

# Cores RGB
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

# Tempo total de jogo em segundos
TEMPO_TOTAL_JOGO = 180

# Criação da tela e do relógio para controle de FPS
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Catch the Coin")
clock = pygame.time.Clock()

# Fontes usadas no jogo
def fonte_grande(): return pygame.font.SysFont(None, 72)
def fonte_media(): return pygame.font.SysFont(None, 48)
def fonte_pequena(): return pygame.font.SysFont(None, 36)
def fonte_credito(): return pygame.font.SysFont(None, 24)

# Função para exibir o crédito nas telas
def desenhar_credito():
    texto_credito = fonte_credito().render("Desenvolvido por Andrei Faccin e Lucas Escobar", True, PRETO)
    tela.blit(texto_credito, (LARGURA // 2 - texto_credito.get_width() // 2, ALTURA - 30))

# Carrega imagens e sons usados no jogo
def carregar_recursos():
    global img_fundo, img_barco, img_moeda, som_moeda
    img_fundo = pygame.image.load("imagens/fundo.png")
    img_barco = pygame.transform.scale(pygame.image.load("imagens/barco.png"), (100, 70))
    img_moeda = {
        "bronze": pygame.transform.scale(pygame.image.load("imagens/moeda_bronze.png"), (30, 30)),
        "prata": pygame.transform.scale(pygame.image.load("imagens/moeda_prata.png"), (30, 30)),
        "ouro": pygame.transform.scale(pygame.image.load("imagens/moeda_ouro.png"), (30, 30))
    }
    pygame.mixer.music.load("sons/musica_fundo.mp3")
    pygame.mixer.music.play(-1)
    som_moeda = pygame.mixer.Sound("sons/som_moeda.mp3")

# Salva o ranking dos jogadores em um arquivo JSON
def salvar_ranking(nome, pontos):
    arquivo = "ranking.json"
    ranking = []
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            ranking = json.load(f)
    ranking.append({"nome": nome, "pontos": pontos})
    ranking = sorted(ranking, key=lambda x: x["pontos"], reverse=True)[:10]
    with open(arquivo, "w") as f:
        json.dump(ranking, f)

# Exibe a tela de ranking com os 10 melhores jogadores
def mostrar_ranking():
    rodando = True
    while rodando:
        tela.blit(img_fundo, (0, 0))
        titulo = fonte_grande().render("Ranking dos Jogadores", True, PRETO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 50))

        # Carrega e exibe o ranking salvo
        if os.path.exists("ranking.json"):
            with open("ranking.json", "r") as f:
                ranking = json.load(f)
            for i, jogador in enumerate(ranking):
                linha = fonte_pequena().render(f"{i+1}. {jogador['nome']} - {jogador['pontos']}", True, PRETO)
                tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 130 + i * 30))

        # Criação dos botões de voltar e sair
        botao_voltar = pygame.Rect(LARGURA // 2 - 160, 500, 150, 50)
        botao_sair = pygame.Rect(LARGURA // 2 + 10, 500, 150, 50)

        pygame.draw.rect(tela, (200, 200, 200), botao_voltar)
        pygame.draw.rect(tela, (200, 100, 100), botao_sair)

        texto_voltar = fonte_pequena().render("Voltar", True, PRETO)
        texto_sair = fonte_pequena().render("Sair", True, PRETO)

        tela.blit(texto_voltar, (botao_voltar.x + 30, botao_voltar.y + 10))
        tela.blit(texto_sair, (botao_sair.x + 40, botao_sair.y + 10))

        desenhar_credito()
        pygame.display.flip()

        # Eventos da tela de ranking
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_voltar.collidepoint(evento.pos):
                    rodando = False
                elif botao_sair.collidepoint(evento.pos):
                    pygame.quit()
                    sys.exit()

# Tela inicial com opções do menu principal
def menu_inicial():
    while True:
        tela.blit(img_fundo, (0, 0))

        titulo = fonte_grande().render("Catch the Coin", True, PRETO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 100))

        # Botões do menu
        botao_jogar = pygame.Rect(LARGURA // 2 - 100, 250, 200, 50)
        botao_ranking = pygame.Rect(LARGURA // 2 - 100, 330, 200, 50)
        botao_sair = pygame.Rect(LARGURA // 2 - 100, 410, 200, 50)

        pygame.draw.rect(tela, (180, 220, 180), botao_jogar)
        pygame.draw.rect(tela, (180, 180, 220), botao_ranking)
        pygame.draw.rect(tela, (220, 160, 160), botao_sair)

        texto_jogar = fonte_media().render("Jogar", True, PRETO)
        texto_ranking = fonte_media().render("Ver Ranking", True, PRETO)
        texto_sair = fonte_media().render("Sair", True, PRETO)

        tela.blit(texto_jogar, (botao_jogar.x + 50, botao_jogar.y + 10))
        tela.blit(texto_ranking, (botao_ranking.x + 20, botao_ranking.y + 10))
        tela.blit(texto_sair, (botao_sair.x + 65, botao_sair.y + 10))

        desenhar_credito()
        pygame.display.flip()

        # Eventos do menu
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar.collidepoint(evento.pos):
                    return True
                elif botao_ranking.collidepoint(evento.pos):
                    mostrar_ranking()
                elif botao_sair.collidepoint(evento.pos):
                    pygame.quit()
                    sys.exit()

# Função principal do jogo
def jogar():
    jogador_x = LARGURA // 2 - 50
    jogador_y = ALTURA - 50
    velocidade_jogador = 7
    moedas = []
    pontuacao = 0
    inicio = pygame.time.get_ticks()

    # Gera moedas com tipo e velocidade aleatória
    def gerar_moeda():
        tipo = random.choices(["bronze", "prata", "ouro"], weights=[0.6, 0.3, 0.1])[0]
        return {"x": random.randint(20, LARGURA - 20), "y": 0, "vel": random.uniform(2, 5), "tipo": tipo}

    rodando = True
    while rodando:
        clock.tick(FPS)
        tempo_decorrido = (pygame.time.get_ticks() - inicio) / 1000
        tempo_restante = max(0, TEMPO_TOTAL_JOGO - tempo_decorrido)

        # Encerra o jogo ao fim do tempo
        if tempo_restante == 0:
            break

        # Aumenta dificuldade conforme o tempo
        dificuldade = 1 if tempo_decorrido <= 60 else 2 if tempo_decorrido <= 120 else 3
        if random.random() < 0.02 * dificuldade:
            moedas.append(gerar_moeda())

        # Eventos do jogo
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Movimento do jogador
        teclas = pygame.key.get_pressed()
        vel_jogador = max(3, velocidade_jogador - pontuacao // 10)
        if teclas[pygame.K_LEFT] and jogador_x > 0:
            jogador_x -= vel_jogador
        if teclas[pygame.K_RIGHT] and jogador_x < LARGURA - 100:
            jogador_x += vel_jogador

        # Atualiza moedas e checa colisões
        for moeda in moedas[:]:
            moeda["y"] += moeda["vel"]
            if (jogador_y < moeda["y"] + 15 and jogador_y + 40 > moeda["y"] and
                jogador_x < moeda["x"] < jogador_x + 100):
                pontuacao += {"bronze": 1, "prata": 2, "ouro": 3}[moeda["tipo"]]
                som_moeda.play()
                moedas.remove(moeda)
            elif moeda["y"] > ALTURA:
                moedas.remove(moeda)

        # Desenha elementos do jogo na tela
        tela.blit(img_fundo, (0, 0))
        tela.blit(img_barco, (jogador_x, jogador_y))
        for moeda in moedas:
            tela.blit(img_moeda[moeda["tipo"]], (moeda["x"] - 15, int(moeda["y"]) - 15))

        texto = fonte_pequena().render(f"Pontos: {pontuacao} | Tempo: {int(tempo_restante)}s", True, PRETO)
        tela.blit(texto, (10, 10))

        # Créditos desativados na tela do jogo
        # desenhar_credito()
        pygame.display.flip()

    # Tela para digitar o nome ao final do jogo
    nome = ""
    input_ativo = True
    while input_ativo:
        tela.blit(img_fundo, (0, 0))
        msg = fonte_media().render("Digite seu nome e pressione Enter:", True, PRETO)
        entrada = fonte_media().render(nome, True, PRETO)
        tela.blit(msg, (LARGURA // 2 - msg.get_width() // 2, 200))
        tela.blit(entrada, (LARGURA // 2 - entrada.get_width() // 2, 260))
        desenhar_credito()
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if nome:
                        salvar_ranking(nome, pontuacao)
                    input_ativo = False
                elif evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                else:
                    if len(nome) < 12:
                        nome += evento.unicode

# Loop principal do programa
carregar_recursos()
while True:
    if menu_inicial():
        jogar()
