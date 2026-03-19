⚔️ Demon Slayer Database Archive
Uma aplicação desktop imersiva desenvolvida em Python e PyQt5 que serve como uma enciclopédia interativa do universo Kimetsu no Yaiba (Demon Slayer). O projeto consome dados em tempo real e adapta toda a sua identidade visual de acordo com o personagem consultado.

✨ Funcionalidades
Busca Inteligente: Pesquise personagens por nome ou ID através da Demon Slayer API.

Interface Adaptativa (Dynamic UI): A paleta de cores da aplicação (botões, barras de progresso, bordas e sombras) muda automaticamente para refletir as cores icônicas do personagem exibido.

Multithreading: Utiliza QThread para garantir que a interface nunca trave durante requisições de API ou carregamento de imagens pesadas.

Tradução Automática: Integração com deep-translator para traduzir descrições e frases do inglês para o português em tempo real.

Experiência Sonora: Efeito sonoro de Biwa (instrumento japonês) ao realizar buscas, trazendo a atmosfera do Castelo Infinito para o app.

Design Moderno: Uso de efeitos de Glassmorphism, sombras projetadas (QGraphicsDropShadowEffect) e animações suaves de transição.

🛠️ Tecnologias Utilizadas
Linguagem: Python 3

Framework UI: PyQt5 (Widgets, Multimedia, Animation)

Conectividade: Requests (Consumo de API REST)

Processamento: ThreadPoolExecutor & QThreads

Tradução: Deep Translator (Google API)

📸 Demonstração da Paleta Dinâmica
A aplicação reconhece automaticamente personagens como:

Tanjiro Kamado: Tons de Verde Escuro.

Kyojuro Rengoku: Tons de Vermelho Fogo.

Shinobu Kocho: Tons de Roxo Borboleta.

Sakonji Urokodaki: Azul Ciano/Nuvens.

📝 Licença
Este projeto é para fins de estudo e apreciação da obra de Koyoharu Gotouge. Sinta-se à vontade para clonar e melhorar!

Desenvolvido com dedicação por um fã de tecnologia e Demon Slayer. 👺
