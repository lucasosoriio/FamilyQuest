import streamlit as st
import db
import pandas as pd
import plotly.express as px
import time
import streamlit.components.v1 as components

def show_missions(user):
    st.markdown("<h2 style='text-align:center;'>🚀 Minhas Missões de Hoje!</h2>", unsafe_allow_html=True)
    tasks = db.get_tasks_for_child(user['id'])
    pending_tasks = [t for t in tasks if t['status'] == 'pending']
    waiting_tasks = [t for t in tasks if t['status'] == 'waiting_approval']
    completed_tasks = [t for t in tasks if t['status'] == 'completed']
    
    if not pending_tasks:
        st.info("🎈 Uhuu! Você não tem missões agora. Pode brincar!")
        
    for t in pending_tasks:
        with st.container(border=True):
            st.markdown(f"<h3 style='color:#FF9F1C; margin-bottom:5px;'>🧩 Missão: {t['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Prêmio:** 💰 R$ {t['reward']:.2f} + 15 XP ✨")
            if t['description']:
                st.markdown(f"*{t['description']}*")
            
            st.write("")
            if st.button(f"EU FIZ! 🌟", key=f"fiz_{t['id']}", type="primary"):
                db.update_task_status(t['id'], 'waiting_approval')
                st.balloons()
                st.toast("Magia feita! Os pais vão olhar em breve! ✨")
                time.sleep(1.5)
                st.rerun()
                    
    if waiting_tasks:
        st.write("---")
        st.markdown("<h3 style='color:#4A90E2;'>⏳ Pais estão analisando...</h3>", unsafe_allow_html=True)
        for t in waiting_tasks:
            st.warning(f"👀 {t['title']} (Aguardando)")

    if completed_tasks:
        with st.expander("Ver minhas Missões Ganhas! 🏆"):
            for t in completed_tasks:
                st.success(f"⭐ {t['title']}")

def show_study(user):
    st.markdown("<h2 style='text-align:center;'>📚 Hora de Ficar Inteligente!</h2>", unsafe_allow_html=True)
    
    st.info("Estudou sem celular e sem distrações? Marque seus minutos para ganhar XP!")
    minutes = st.number_input("Minutos treinando o cérebro:", min_value=1, max_value=120, value=20)
    
    if st.button("Ganhar XP de Inteligência! 🦸‍♂️", type="primary"):
        db.add_study_session(user['id'], minutes)
        # the XP is added inside the db function (+XP)
        st.toast("Você ficou mais sábio hoje! 🧠 +XP")
        st.rerun()

    st.write("---")
    st.markdown("<h3>📈 Minha Evolução do Saber</h3>", unsafe_allow_html=True)
    history = db.get_study_history(user['id'])
    if history:
        df = pd.DataFrame(history)
        fig = px.bar(df, x='date', y='total_minutes', labels={'date':'Dia', 'total_minutes': 'Minutos'}, title="Poder da Mente 🧠")
        fig.update_traces(marker_color='#2EC4B6')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Comece a estudar e veja o gráfico crescer!")

def show_vault(user):
    st.markdown("<h2 style='text-align:center;'>🐷 Meu Cofrinho</h2>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='coin-box'>🪙 Meu Tesouro:<br><span style='color:#EF476F; font-size:45px;'>R$ {user['balance']:.2f}</span></div>", unsafe_allow_html=True)
    st.write("")
    
    st.write("---")
    st.markdown("<h3>📝 Histórico de Moedas</h3>", unsafe_allow_html=True)
    transactions = db.get_transactions_for_child(user['id'])
    
    if transactions:
        df = pd.DataFrame(transactions)
        
        # Plotly chart
        summary = df.groupby('type')['amount'].sum().reset_index()
        summary['type'] = summary['type'].map({'earn': 'Moedas Ganhas', 'spend': 'Moedas Gastas'})
        
        color_map = {
            'Moedas Ganhas': '#2EC4B6',
            'Moedas Gastas': '#EF476F'
        }
        
        fig_pie = px.pie(summary, values='amount', names='type', hole=0.4, 
                     color='type', color_discrete_map=color_map)
        fig_pie.update_layout(margin=dict(t=10, b=10, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

        for tr in transactions:
            color = "#2EC4B6" if tr['type'] == 'earn' else "#EF476F"
            sign = "+ R$" if tr['type'] == 'earn' else "- R$"
            st.markdown(f"<div style='border-left: 5px solid {color}; padding:10px; margin-bottom:10px; background-color:white; border-radius:10px;'><b style='color:#1A202C;'>{tr['description']}</b><br><span style='color:{color}; font-weight:bold; font-size:18px;'>{sign} {tr['amount']:.2f}</span></div>", unsafe_allow_html=True)
            
    else:
        st.write("Sem moedas ainda...")

def show_store(user):
    st.markdown("<h2 style='text-align:center;'>🎁 A Lojinha Mágica!</h2>", unsafe_allow_html=True)
    st.write("Use seu tesouro para comprar prêmios reais! Peça o prêmio e seus pais entregarão.")
    
    st.markdown(f"<h3 style='color:#FF9F1C; text-align:center;'>Seu Saldo: R$ {user['balance']:.2f}</h3>", unsafe_allow_html=True)
    st.write("---")
    
    items = db.get_all_store_items()
    if not items:
        st.info("A lojinha está fechada agora. Ninguém colocou prêmios nela ainda! Reclame com a gerência (seus pais!)")
    else:
        col1, col2 = st.columns(2)
        
        for i, it in enumerate(items):
            current_col = col1 if i%2 == 0 else col2
            with current_col:
                with st.container(border=True):
                    st.markdown(f"<h1 style='text-align:center;'>{it['icon']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='text-align:center; color:#4A90E2;'>{it['title']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center; font-weight:900; font-size:24px; color:#EF476F;'>Moedas: {it['cost']:.2f}</div>", unsafe_allow_html=True)
                    st.write("")
                    
                    if user['balance'] >= it['cost']:
                        if st.button("COMPRAR! 🎟️", key=f"buy_{it['id']}", type="primary"):
                            success = db.buy_item(user['id'], it['id'])
                            if success:
                                st.balloons()
                                st.toast("Uhuuu! Compra feita! Avise os pais para lhe entregarem.")
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error("Tem algo errado com o saldo.")
                    else:
                        st.button("Moedas Insuficientes 🔒", key=f"nobuy_{it['id']}", disabled=True)
                        
    st.write("---")
    st.markdown("<h3>📦 Minhas Compras (Pedidos)</h3>", unsafe_allow_html=True)
    purchases = db.get_purchases_by_child(user['id'])
    for p in purchases:
        status_text = "Em Entrega..." if p['status'] == 'pending' else "Já Recebi! ✨"
        color = "orange" if p['status'] == 'pending' else "green"
        st.markdown(f"- **{p['item_name']}** (R$ {p['cost']:.2f}) -> <span style='color:{color};'>{status_text}</span>", unsafe_allow_html=True)

def show_arcade(user):
    st.markdown("<h2 style='text-align:center;'>🕹️ Fliperama da Família</h2>", unsafe_allow_html=True)
    st.write("Bem-vindo(a) ao Fliperama! Aproveite seus momentos de lazer.")
    
    game_choice = st.selectbox("Escolha seu cartucho:", ["🐍 Jogo da Cobrinha", "🧠 Jogo da Memória"])
    
    if game_choice == "🐍 Jogo da Cobrinha":
        html_code = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { margin: 0; padding: 0; background-color: transparent; color: #E6F1FF; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; overflow: hidden; }
                .arcade-machine { background-color: #08101E; padding: 20px; border-radius: 20px; border: 5px solid #FFCA4A; text-align: center; box-shadow: 0px 10px 20px rgba(0,0,0,0.3); margin-top:20px; }
                canvas { background-color: #111; border: 4px solid #2EC4B6; border-radius: 10px; width: 300px; height: 300px; }
                #scoreBoard { font-size: 24px; font-weight: 900; margin-bottom: 20px; color: #FFD166; }
                #controls { margin-top: 20px; display: grid; grid-template-columns: 60px 60px 60px; grid-gap: 10px; justify-content: center; justify-items: center;}
                .btn { background: #4A90E2; color: #FFF; width: 60px; height: 60px; line-height: 60px; border-radius: 10px; font-size: 25px; font-weight: bold; cursor: pointer; user-select: none; box-shadow: 0px 5px 0px #3174C6;}
                .btn:active { background: #FFD166; box-shadow: 0px 2px 0px #C9A033; transform:translateY(3px); }
                .btn:hover { opacity: 0.8; }
                #controls div.empty { background: transparent; box-shadow: none; }
            </style>
        </head>
        <body style="height: 100%; display: flex; flex-direction: column;">
            <div class="arcade-machine">
                <div id="scoreBoard">Pontos: 0 | Recorde: 0</div>
                <canvas id="gameCanvas" width="300" height="300"></canvas>
                
                <!-- Mobile D-PAD controls -->
                <div id="controls">
                   <div class="empty"></div><div class="btn" onclick="setDir('UP')">▲</div><div class="empty"></div>
                   <div class="btn" onclick="setDir('LEFT')">◀</div><div class="btn" onclick="setDir('DOWN')">▼</div><div class="btn" onclick="setDir('RIGHT')">▶</div>
                </div>
            </div>

            <script>
                const canvas = document.getElementById("gameCanvas");
                const ctx = canvas.getContext("2d");

                const grid = 15;
                let count = 0;
                let score = 0;
                let highscore = 0;

                let snake = {
                    x: 150,
                    y: 150,
                    dx: grid,
                    dy: 0,
                    cells: [],
                    maxCells: 4
                };

                let apple = { x: 45, y: 45 };

                function getRandomInt(min, max) { return Math.floor(Math.random() * (max - min)) + min; }

                function resetGame() {
                    snake.x = 150; snake.y = 150; snake.cells = []; snake.maxCells = 4; snake.dx = grid; snake.dy = 0;
                    score = 0;
                    document.getElementById('scoreBoard').innerText = "Pontos: " + score + " | Recorde: " + highscore;
                    apple.x = getRandomInt(0, 20) * grid; apple.y = getRandomInt(0, 20) * grid;
                }

                function loop() {
                    requestAnimationFrame(loop);

                    // Deixamos a cobrinha mais devagar mudando para < 10 (antes era 6)
                    if (++count < 10) return;
                    count = 0;

                    ctx.clearRect(0,0,canvas.width,canvas.height);

                    snake.x += snake.dx; snake.y += snake.dy;

                    if (snake.x < 0) snake.x = canvas.width - grid;
                    else if (snake.x >= canvas.width) snake.x = 0;
                    if (snake.y < 0) snake.y = canvas.height - grid;
                    else if (snake.y >= canvas.height) snake.y = 0;

                    snake.cells.unshift({x: snake.x, y: snake.y});
                    if (snake.cells.length > snake.maxCells) snake.cells.pop();

                    ctx.fillStyle = '#EF476F';
                    ctx.fillRect(apple.x, apple.y, grid-1, grid-1);

                    ctx.fillStyle = '#2EC4B6';
                    snake.cells.forEach(function(cell, index) {
                        ctx.fillRect(cell.x, cell.y, grid-1, grid-1);
                        if (cell.x === apple.x && cell.y === apple.y) {
                            snake.maxCells++; score += 10;
                            if(score > highscore) highscore = score;
                            document.getElementById('scoreBoard').innerText = "Pontos: " + score + " | Recorde: " + highscore;
                            apple.x = getRandomInt(0, 20) * grid; apple.y = getRandomInt(0, 20) * grid;
                        }
                        for (let i = index + 1; i < snake.cells.length; i++) {
                            if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) resetGame();
                        }
                    });
                }

                function setDir(dir) {
                    if (dir === 'LEFT' && snake.dx === 0) { snake.dx = -grid; snake.dy = 0; }
                    else if (dir === 'UP' && snake.dy === 0) { snake.dy = -grid; snake.dx = 0; }
                    else if (dir === 'RIGHT' && snake.dx === 0) { snake.dx = grid; snake.dy = 0; }
                    else if (dir === 'DOWN' && snake.dy === 0) { snake.dy = grid; snake.dx = 0; }
                }

                document.addEventListener('keydown', function(e) {
                    if([37, 38, 39, 40].indexOf(e.keyCode) > -1) e.preventDefault();
                    if (e.which === 37) setDir('LEFT');
                    else if (e.which === 38) setDir('UP');
                    else if (e.which === 39) setDir('RIGHT');
                    else if (e.which === 40) setDir('DOWN');
                });

                requestAnimationFrame(loop);
            </script>
        </body>
        </html>
        """
        components.html(html_code, height=600, scrolling=False)
        
    elif game_choice == "🧠 Jogo da Memória":
        html_code = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
          body { margin:0; padding:10px; background:transparent; color:#E6F1FF; font-family:'Segoe UI', sans-serif; text-align:center; display: flex; flex-direction: column; align-items: center;}
          #board { display: grid; grid-template-columns: repeat(4, 70px); grid-gap: 10px; justify-content: center; margin-top: 20px;}
          .card { width: 70px; height: 70px; background: #4A90E2; border-radius: 10px; font-size: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; user-select:none; box-shadow: 0px 5px 0px #3174C6;}
          .card.flipped { background: #FFF; border: 3px solid #2EC4B6; cursor: default; transform: translateY(3px); box-shadow: none;}
          .card.matched { background: #FFF3B0; border: 3px solid #FFCA4A; opacity: 0.8;}
          .arcade-machine { background:#08101E; padding:20px; border-radius:20px; border:5px solid #FFCA4A; color:white; margin-top:20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.3);}
          button.reset { margin-top:30px; padding:15px 30px; font-size:20px; font-weight:bold; border-radius:15px; background:#EF476F; color:white; border:none; cursor:pointer; box-shadow: 0px 5px 0px #C12A4F;}
          button.reset:active { transform:translateY(3px); box-shadow:none;}
          #status { font-size: 24px; font-weight: 900; color: #2EC4B6; }
        </style>
        </head>
        <body>
        <div class="arcade-machine">
          <div id="status">Encontre os pares!</div>
          <div id="board"></div>
          <button class="reset" onclick="init()">🔁 Embaralhar Novamente</button>
        </div>

        <script>
        const emojis = ['🐶', '🦊', '🐉', '🦄', '🦁', '🐸', '🦖', '🤖'];
        let deck = [...emojis, ...emojis];
        let board = document.getElementById('board');
        let firstCard = null;
        let secondCard = null;
        let lockBoard = false;
        let pairsFound = 0;

        function shuffle() {
          deck.sort(() => Math.random() - 0.5);
        }

        function init() {
          board.innerHTML = "";
          shuffle();
          firstCard = null;
          secondCard = null;
          lockBoard = false;
          pairsFound = 0;
          document.getElementById('status').innerText = "Encontre os pares!";
          
          deck.forEach((emoji, index) => {
            let card = document.createElement("div");
            card.classList.add("card");
            card.dataset.emoji = emoji;
            card.dataset.index = index;
            card.onclick = () => flipCard(card);
            board.appendChild(card);
          });
        }

        function flipCard(card) {
          if (lockBoard) return;
          if (card === firstCard) return;
          if (card.classList.contains("matched")) return;

          card.classList.add("flipped");
          card.innerText = card.dataset.emoji;

          if (!firstCard) {
            firstCard = card;
            return;
          }

          secondCard = card;
          lockBoard = true;
          checkForMatch();
        }

        function checkForMatch() {
          let isMatch = firstCard.dataset.emoji === secondCard.dataset.emoji;
          if (isMatch) {
            disableCards();
          } else {
            unflipCards();
          }
        }

        function disableCards() {
          firstCard.classList.add("matched");
          secondCard.classList.add("matched");
          pairsFound++;
          if (pairsFound === emojis.length) {
            document.getElementById('status').innerText = "Parabéns! Você Venceu! 🎉";
          }
          resetBoard();
        }

        function unflipCards() {
          setTimeout(() => {
            firstCard.classList.remove("flipped");
            firstCard.innerText = "";
            secondCard.classList.remove("flipped");
            secondCard.innerText = "";
            resetBoard();
          }, 1000);
        }

        function resetBoard() {
          firstCard = null;
          secondCard = null;
          lockBoard = false;
        }

        init();
        </script>
        </body>
        </html>
        """
        components.html(html_code, height=520, scrolling=False)
