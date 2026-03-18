import sys
import requests
import os
from PyQt5.QtWidgets import (QApplication,QGraphicsOpacityEffect,QProgressBar, QWidget, QLabel, QPushButton, 
                             QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QGridLayout, QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPixmap, QFont, QColor,QMovie,QIcon
from PyQt5.QtCore import Qt,QUrl,QPropertyAnimation, QEasingCurve,QPropertyAnimation, QSequentialAnimationGroup, QPoint,QSize,QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent,QSoundEffect
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

class BuscaWorker(QThread):
    # Sinais para enviar os dados de volta para a UI
    resultado_pronto = pyqtSignal(dict)
    erro_ocorrido = pyqtSignal(str)

    def __init__(self, valor_busca):
        super().__init__()
        self.valor = valor_busca

    def run(self):
        try:
            url = f"https://www.demonslayer-api.com/api/v1/characters?{'id=' if self.valor.isdigit() else 'name='}{self.valor}"
            res = requests.get(url, timeout=8)
            data = res.json()
            
            if data.get('content'):
                # Envia o primeiro personagem encontrado para a UI
                self.resultado_pronto.emit(data['content'][0])
            else:
                self.erro_ocorrido.emit("Personagem não encontrado.")
        except Exception as e:
            self.erro_ocorrido.emit(str(e))

class ImageWorker(QThread):
    imagem_pronta = pyqtSignal(QPixmap, QLabel)

    def __init__(self, url, label, largura, altura):
        super().__init__()
        self.url = url
        self.label = label
        self.largura = largura
        self.altura = altura

    def run(self):
        try:
            r = requests.get(self.url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            pix = QPixmap()
            pix.loadFromData(r.content)
            if not pix.isNull():
                pix_redimensionada = pix.scaled(
                    self.largura, self.altura, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.imagem_pronta.emit(pix_redimensionada, self.label)
        except:
            pass # Silencioso para não travar a UI            

class DemonSlayerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.cache_traducoes = {}

    # --- CONFIGURAÇÃO DO EFEITO MP3 ---
        self.player_efeito = QMediaPlayer()
        # Pega o caminho completo da pasta onde o seu script está rodando
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_completo = os.path.join(pasta_atual, "biwa_demon_slayer.mp3")

        # Converte para URL de forma que o Windows entenda 100%
        self.player_efeito.setMedia(QMediaContent(QUrl.fromLocalFile(caminho_completo)))
        self.player_efeito.setVolume(100)

        if os.path.exists(caminho_completo):
            print(f"✅ Áudio encontrado em: {caminho_completo}")
        else:
            print(f"❌ ERRO: Arquivo não encontrado em: {caminho_completo}")
            
        # Mapeamento de cores principais por personagem (Nome: Cor Destaque)
        self.paleta_personagens ={
            # Protagonistas e Família
            "Tanjiro Kamado": "#004d40",     # Verde Quadriculado
            "Nezuko Kamado": "#ff80ab",      # Rosa Quimono
            "Zenitsu Agatsuma": "#fbc02d",   # Amarelo Relâmpago
            "Inosuke Hashibira": "#1e88e5",  # Azul Javali
            "Genya Shinazugawa": "#4a148c",  # Roxo Escuro
            "Kanao Tsuyuri": "#f06292",      # Rosa Capa
            
            # Hashiras (Pilares)
            "Giyu Tomioka": "#880e4f",       # Vinho/Azul
            "Shinobu Kocho": "#9c27b0",      # Roxo Borboleta
            "Kyojuro Rengoku": "#d32f2f",    # Vermelho Fogo
            "Tengen Uzui": "#607d8b",        # Cinza Metálico
            "Mitsuri Kanroji": "#f48fb1",    # Rosa/Verde Lima
            "Muichiro Tokito": "#00acc1",    # Turquesa Névoa
            "Gyomei Himejima": "#558b2f",    # Verde Oliva
            "Obanai Iguro": "#424242",       # Listrado Preto/Branco
            "Sanemi Shinazugawa": "#cfd8dc", # Branco Cicatriz
            
            # Vilões (Muzan e Luas Superiores/Inferiores)
            "Muzan Kibutsuji": "#212121",    # Preto Terno
            "Kokushibo": "#6d069c",          # Roxo Samurai
            "Doma": "#b71c1c",               # Vermelho Sangue
            "Akaza": "#e91e63",              # Rosa Marcas
            "Hantengu": "#4e342e",           # Marrom Sombrio
            "Gyokko": "#e0f2f1",             # Branco Vaso/Porcelana
            "Gyutaro": "#33691e",            # Verde Veneno
            "Daki": "#ad1457",               # Magenta Cinto
            "Kaigaku": "#1a237e",            # Azul Escuro Relâmpago
            "Enmu": "#283593",               # Azul Pijama
            "Rui": "#f5f5f5",                # Branco Teia
            "Nakime": "#263238",             # Cinza Biwa
            "Kyogai": "#795548",             # Marrom Tambor
            
            # Mestres e Suporte
            "Kagaya Ubuyashiki": "#e1bee7",  # Lavanda Pálido
            "Sakonji Urokodaki":"#0df8f8",  # Azul Ciano/Nuvens
            "Jigoro Kuwajima": "#ffa000",    # Âmbar Velho
            "Shinjuro Rengoku": "#bf360c",   # Laranja Queimado
            "Tamayo": "#4527a0",             # Roxo Floral
            "Yushiro": "#81c784",            # Verde Menta
            "Aoi Kanzaki": "#1976d2",        # Azul Uniforme
            "Sumi Nakahara": "#f8bbd0",      # Rosa Laço
            "Kiyo Terauchi": "#f8bbd0",      # Rosa Laço
            "Naho Takada": "#f8bbd0",        # Rosa Laço
            
            # Personagens de Flashback e Outros
            "Yoriichi Tsugikuni": "#bf360c", # Vermelho Sol
            "Sabito": "#ffab91",             # Pêssego Haori
            "Makomo": "#80cbc4",             # Ciano Floral
            "Hotaru Haganezuka": "#ff5722",  # Laranja Máscara
            "Susamaru": "#fb8c00",           # Laranja Kimono
            "Yahaba": "#2e7d32",             # Verde Setas
            "Murata": "#455a64"              # Cinza Uniforme Base
        }

        self.init_ui()

        self.player = QMediaPlayer()
        self.play_trilha_sonora()
        self.executor = ThreadPoolExecutor(max_workers=6) # Criamos um "time" de busca

        

    def play_trilha_sonora(self):
    # Substitua 'trilha.mp3' pelo nome do arquivo que você baixou
        url = QUrl.fromLocalFile("biwa_demon_slayer.mp3")
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.setVolume(50) # Volume de 0 a 100
        self.player.play()    

   
    def atualizar_estilo(self, cor_primaria):
          
        # Convertendo HEX para RGBA para efeitos de transparência (0.2 = 20% de opacidade)
        rgba_brilho = self.hex_to_rgba(cor_primaria, 0.5)
        rgba_borda = self.hex_to_rgba(cor_primaria, 0.5)

        self.wisteria.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {rgba_borda}, stop:1 transparent);")
        self.header_title.setStyleSheet(f"font-size: 50px; color: {cor_primaria}; font-weight: bold; letter-spacing: 10px; background: transparent;")
        rgba_fundo_scroll = self.hex_to_rgba(cor_primaria, 0.05)
        
        self.barra_respiracao.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #333;
                background: #000;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                            stop:0 {cor_primaria}, stop:1 #ffffff);
                border-radius: 5px;
            }}
        """)
        
        self.setStyleSheet(f"""
        QWidget {{
            background-color: #0d0d0d;
            background-image: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                              stop:0 #000000, stop:0.5 #0d0d0d, stop:1 #1a1a1a);
            font-family: 'Segoe UI', sans-serif;
            color: #e0e0e0;
        }}
                           
        
        /* Campo de Busca Estilizado */
        QLineEdit {{
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid {rgba_borda};
            border-bottom: 2px solid {cor_primaria};
            border-radius: 4px;
            padding: 12px;
            font-size: 15px;
            color: {cor_primaria};
            selection-background-color: {cor_primaria};
        }}
        QLineEdit:focus {{
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid {cor_primaria};
        }}

        /* Botão com Efeito de Elevação */
        QPushButton {{
            background-color: {cor_primaria};
            color: white;
            border-radius: 20px;
            padding: 12px 30px;
            font-weight: 900;
            font-size: 13px;
            letter-spacing: 1.5px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        QPushButton:hover {{
            background-color: white;
            color: {cor_primaria};
            border: 1px solid {cor_primaria};
        }}
        QPushButton:pressed {{
            background-color: #cccccc;
            padding-top: 14px; /* Efeito de clique */
        }}

        /* Títulos de Seção */
        QLabel#TituloSessao {{
            color: {cor_primaria};
            font-size: 20px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding-bottom: 5px;
            border-bottom: 1px solid {rgba_borda};
        }}

        /* --- ESTILIZAÇÃO DA SCROLL AREA E BARRA --- */
            QScrollArea {{
                border: 1px solid {rgba_borda};
                border-radius: 15px;
                background-color: {rgba_fundo_scroll};
            }}

            QScrollBar:vertical {{
                border: none;
                background: rgba(0, 0, 0, 0.2);
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }}

            /* O 'pegador' da barra com gradiente do personagem */
            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 {cor_primaria}, stop:1 {rgba_borda});
                min-height: 30px;
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            QScrollBar::handle:vertical:hover {{
                background: {cor_primaria}; /* Brilha mais ao passar o mouse */
            }}

            /* Fundo da trilha da barra */
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: {rgba_brilho};
                border-radius: 5px;
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px; /* Remove as setas para um visual moderno */
            }}

            /* Títulos de Seção */
            QLabel#TituloSessao {{
                color: {cor_primaria};
                font-size: 20px;
                font-weight: 800;
                letter-spacing: 2px;
                border-bottom: 1px solid {rgba_borda};
            }}
    """)

    # Adicione esta função auxiliar na sua classe para converter as cores
    def hex_to_rgba(self, hex_color, alpha):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"

    # ... [Métodos traduzir, carregar_imagem e executar_busca permanecem iguais] ...
    
    def traduzir(self, texto):
       if not texto or texto == "None": return "Desconhecido"
    
     # Dicionário fixo para termos que aparecem sempre (Muito mais rápido!)
       termos_comuns = {
                "Male": "Masculino",
                "Female": "Feminino",
                "Human": "Humano",
                "Demon": "Oni",
                "Celestial": "Celestial"
            }
            
       if texto in termos_comuns:
                return termos_comuns[texto]
                
       if texto in self.cache_traducoes: 
                return self.cache_traducoes[texto]

            # Só traduz se for um texto longo (descrição) e não estiver no cache
       try:
                traducao = GoogleTranslator(source='en', target='pt').translate(texto)
                self.cache_traducoes[texto] = traducao
                return traducao
       except:
                return texto

    def carregar_imagem(self, url, label, largura, altura):
        if not url: return
        
        # 1. Coloca um texto temporário ou ícone de "carregando"
        label.setText("⌛") 
        
        # 2. Cria a thread para baixar a imagem
        self.img_thread = ImageWorker(url, label, largura, altura)
        
        # 3. Conecta o sinal para colocar a imagem na label correta
        self.img_thread.imagem_pronta.connect(self.definir_pixmap_na_ui)
        
        # 4. Inicia o download em segundo plano
        self.img_thread.start()

    def definir_pixmap_na_ui(self, pixmap, label):
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
       

    def executar_busca(self):
     valor = self.input_busca.text().strip()
     if not valor: return

     # --- NOVA LÓGICA: Se for texto (nome), utiliza apenas as 3 primeiras letras ---
     #if not valor.isdigit():
      #  valor = valor[:3]

     # 1. Captura o tamanho real que o botão tem AGORA
     tamanho_original = self.btn_buscar.size()
     tamanho_expandido = QSize(tamanho_original.width() + 10, tamanho_original.height() + 5)

        # 2. Atualiza os valores da animação com tamanhos válidos
     self.anim_aumentar.setStartValue(tamanho_original)
     self.anim_aumentar.setEndValue(tamanho_expandido)
        
     self.anim_diminuir.setStartValue(tamanho_expandido)
     self.anim_diminuir.setEndValue(tamanho_original)

     # --- ANTES DA BUSCA ---
     self.player_efeito.stop() 
     self.player_efeito.play()
     self.anim_botao.start()
    
     self.btn_buscar.setEnabled(False)
     self.barra_respiracao.setVisible(True)
     self.barra_respiracao.setRange(0, 0) # Trava o botão
     self.btn_buscar.setText("CONCENTRANDO...")    
     # Mostra e inicia a barra de progresso (modo infinito/indeterminado)
     self.worker = BuscaWorker(valor)
        
        # Conecta os sinais às funções que mexem na UI
     self.worker.resultado_pronto.connect(self.finalizar_busca_sucesso)
     self.worker.erro_ocorrido.connect(self.finalizar_busca_erro)
    
     # Inicia a thread
     self.worker.start()
     
  
     QApplication.processEvents()

    def finalizar_busca_sucesso(self, dados_personagem):
        self.montar_tela(dados_personagem)
        self.limpar_estado_busca()

    def finalizar_busca_erro(self, mensagem):
        QMessageBox.warning(self, "Erro", f"A respiração falhou: {mensagem}")
        self.limpar_estado_busca()

    def limpar_estado_busca(self):
        self.barra_respiracao.setVisible(False)
        self.btn_buscar.setEnabled(True)
        self.anim_botao.stop()
        self.btn_buscar.setText("RESPIRAR E BUSCAR")

    def montar_tela(self, p):
        # 1. Identificar a cor do personagem
        nome = p.get('name', '').strip()
        self.cache_traducoes = {}
        # Tenta encontrar a cor. Se não achar o nome exato, busca se o nome está contido na chave
        cor_personagem = "#004d40" # Padrão
        for chave, cor in self.paleta_personagens.items():
            if chave.lower() in nome.lower() or nome.lower() in chave.lower():
                cor_personagem = cor
                break 
            elif "urokodaki" in nome.lower():
             cor_personagem = "#0df8f8"
             break
        
        self.atualizar_estilo(cor_personagem)
        # Limpar grid anterior
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self.carregar_imagem(p.get('img'), self.label_img_principal, 400, 300)
        self.label_img_principal.setStyleSheet(f"background-color: transparent ; border: 4px double {cor_personagem}; border-radius: 15px;")

        info_data = [
            ("NOME", p.get('name')),
            ("IDADE", str(p.get('age'))),
            ("GÊNERO", self.traduzir(p.get('gender'))),
            ("RAÇA", self.traduzir(p.get('race'))),
            ("DESCRIÇÃO", self.traduzir(p.get('description'))),
            ("FRASE", f"<i>'{self.traduzir(p.get('quote'))}'</i>")
        ]

        for row, (titulo, valor) in enumerate(info_data):
            lbl_t = QLabel(titulo)
            lbl_t.setStyleSheet(f"color: {cor_personagem}; font-weight: bold; font-size: 11px;")
            
            lbl_v = QLabel(valor)
            lbl_v.setWordWrap(True)
            lbl_v.setStyleSheet(f"""
                background-color: rgba(255, 255, 255, 0.03);
                border-left: 4px solid {cor_personagem};
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.5;
                              """)
            self.grid.addWidget(lbl_t, row*2, 0)
            self.grid.addWidget(lbl_v, row*2+1, 0)
        
          
        # Estilos de Combate
        if p.get('combat_style'):
            row_idx = len(info_data) * 2
            lbl_estilo_header = QLabel("ESTILOS DE COMBATE")
            lbl_estilo_header.setObjectName("TituloSessao")
            self.grid.addWidget(lbl_estilo_header, row_idx, 0)

            for idx, style in enumerate(p['combat_style']):
                frame = QFrame()
                frame.setStyleSheet(f"background-color: transparent; border: 1px solid {cor_personagem}; border-radius: 10px; margin-top: 5px;")
                f_lay = QHBoxLayout(frame)
                img_s = QLabel(); img_s.setFixedSize(100, 100)
                self.carregar_imagem(style.get('img'), img_s, 100, 100)
                txt_s = QLabel(f"<b>{self.traduzir(style.get('name'))}</b><br><small>{self.traduzir(style.get('description'))}</small>")
                txt_s.setWordWrap(True)
                f_lay.addWidget(img_s); f_lay.addWidget(txt_s)
                self.grid.addWidget(frame, row_idx + 1 + idx, 0)

         
                sombra_card = QGraphicsDropShadowEffect()
                sombra_card.setBlurRadius(15)
                sombra_card.setColor(QColor(0, 0, 0, 150))
                frame.setGraphicsEffect(sombra_card)
        

        

          

    # UI Base inicial (complemento do init_ui)
    def init_ui(self):
        self.setWindowTitle("Demon Slayer Database ")
        self.setFixedSize(750, 900)
        self.setWindowIcon(QIcon("goblin.png"))
        
        # --- NOVO: GIF DE FUNDO (NÉVOA/CHAMAS) ---
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, 950, 1100)
        self.bg_label.setScaledContents(True)
        # Substitua 'nevoa.gif' pelo seu arquivo de animação
        self.movie = QMovie("nevoa.gif") 
        self.bg_label.setMovie(self.movie)
        self.movie.start()
        self.bg_label.lower() # Garante que fique atrás de tudo

        self.wisteria = QLabel(self)
        self.wisteria.setGeometry(0, 0, 750, 150)
        # Se você tiver a imagem wisteria.png, use a linha abaixo:
        # self.wisteria.setPixmap(QPixmap("wisteria.png").scaled(750, 150, Qt.KeepAspectRatioByExpanding))
      

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 60, 40, 40)
        self.main_layout.setSpacing(15)

        # Header Estilizado
        self.header_title = QLabel("鬼滅の刃")
        self.header_title.setAlignment(Qt.AlignCenter)
        # Mudamos o background para transparent e removemos o roxo fixo
        
        self.main_layout.addWidget(self.header_title)

        self.sub_title = QLabel("KIMETSU NO YAIBA • ARCHIVE")
        self.sub_title.setAlignment(Qt.AlignCenter)
        # Garante que o subtítulo também seja transparente
        self.sub_title.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.6); letter-spacing: 6px; margin-bottom: 20px; background: transparent;")
        self.main_layout.addWidget(self.sub_title)
        
        self.barra_respiracao = QProgressBar()
        self.barra_respiracao.setVisible(False)
        self.barra_respiracao.setFixedHeight(10)
        self.barra_respiracao.setTextVisible(False)
        self.barra_respiracao.setStyleSheet("""
            QProgressBar { border: 1px solid #333; background: #000; border-radius: 5px; }
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00fbff, stop:1 #004d40); }
        """)
        self.main_layout.addWidget(self.barra_respiracao)

        # Busca com Glassmorphism
        busca_container = QFrame()
        busca_container.setStyleSheet("background: transparent;")
        busca_layout = QHBoxLayout(busca_container)

               
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Quem você procura?")
        self.input_busca.returnPressed.connect(self.executar_busca)
        self.btn_buscar = QPushButton("RESPIRAR E BUSCAR")
        self.btn_buscar.setCursor(Qt.PointingHandCursor)
        self.btn_buscar.clicked.connect(self.executar_busca)
                
        busca_layout.addWidget(self.input_busca)
        busca_layout.addWidget(self.btn_buscar)
        self.main_layout.addWidget(busca_container)
        self.img_container = QFrame()
        self.img_container.setFixedSize(450, 320)
        self.img_lay = QVBoxLayout(self.img_container)
        
        self.lbl_rank = QLabel("") # BADGE DE RANK
        self.lbl_rank.setAlignment(Qt.AlignCenter)
        self.lbl_rank.setFixedSize(120, 30)
        self.lbl_rank.hide()

        # Imagem Principal com Sombra
        self.label_img_principal = QLabel("Selecione um personagem")
        self.label_img_principal.setFixedSize(450, 320)
        self.label_img_principal.setAlignment(Qt.AlignCenter)
        self.label_img_principal.setObjectName("imagemPrincipal")
        self.label_img_principal.setStyleSheet("background: transparent;")
        self.main_layout.addWidget(self.label_img_principal, alignment=Qt.AlignCenter)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True) # ESSENCIAL
        self.scroll.setStyleSheet("border: none; background: transparent;")
        
        # Widget que conterá tudo (Imagem + Info)
        self.container_scroll = QWidget()
        self.scroll_layout = QVBoxLayout(self.container_scroll)
        self.scroll_layout.setAlignment(Qt.AlignTop) # Mantém tudo no topo
        
        
        # Grid de informações dentro do Scroll
        self.grid = QGridLayout()
        self.scroll_layout.addLayout(self.grid)

        self.scroll.setWidget(self.container_scroll)
        self.main_layout.addWidget(self.scroll)

        self.atualizar_estilo("#004d40")
        self.anim_botao = QSequentialAnimationGroup()
        
        # Criamos as animações, mas não definimos os valores ainda
        self.anim_aumentar = QPropertyAnimation(self.btn_buscar, b"minimumSize")
        self.anim_aumentar.setDuration(600)
        self.anim_aumentar.setEasingCurve(QEasingCurve.InOutSine)

        self.anim_diminuir = QPropertyAnimation(self.btn_buscar, b"minimumSize")
        self.anim_diminuir.setDuration(600)
        self.anim_diminuir.setEasingCurve(QEasingCurve.InOutSine)

        self.anim_botao.addAnimation(self.anim_aumentar)
        self.anim_botao.addAnimation(self.anim_diminuir)
        self.anim_botao.setLoopCount(-1)
       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DemonSlayerApp()
    win.show()
    sys.exit(app.exec_())