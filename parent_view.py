import streamlit as st
import db
import pandas as pd
import time

def show_main_dashboard():
    st.markdown("<h2>🏠 Gerenciar Participantes e Missões</h2>", unsafe_allow_html=True)
    
    with st.expander("Cadastrar Novo Participante 👦👧"):
        with st.form("new_child_form"):
            child_name = st.text_input("Qual o nome do filho(a)?")
            child_age = st.number_input("Idade", min_value=2, max_value=18, value=5)
            avatar = st.selectbox("Escolha um Avatar", ['👦', '👧', '🐶', '🦊', '🐉', '🦄', '🦁', '🐸'])
            submit = st.form_submit_button("Confirmar Cadastro")
            if submit and child_name:
                db.create_user(name=child_name, role="child", pin=None, avatar=avatar, age=child_age)
                st.success(f"Legal! {child_name} {avatar} entrou na brincadeira!")
                st.rerun()
                
    children = db.get_users_by_role('child')
    if not children:
        st.info("Nenhuma criança adicionada ainda.")
        return

    # Use just the name in the dropdown to avoid base64 breaking the UI 
    child_names = {f"{c['name']}": c for c in children}
    selected_child_name = st.selectbox("Escolha a criança para focar:", list(child_names.keys()))
    selected_child = child_names[selected_child_name]
    
    with st.expander(f"⚙️ Editar Perfil de {selected_child['name']}"):
        with st.form("edit_profile_form"):
            new_name = st.text_input("Atualizar Nome", value=selected_child['name'])
            new_age = st.number_input("Atualizar Idade", min_value=2, max_value=18, value=selected_child.get('age', 5))
            st.write("---")
            st.write("Você pode colocar uma foto ou usar um emoji de personagem:")
            new_photo = st.file_uploader("Enviar Nova Foto (Apaga a anterior)", type=['png', 'jpg', 'jpeg'])
            
            avatar_opts = ['Manter Atual', '👦', '👧', '🐶', '🦊', '🐉', '🦄', '🦁', '🐸', '🦖', '🤖']
            new_emoji = st.selectbox("Ou Escolher Personagem/Emoji", avatar_opts, index=0)
            
            if st.form_submit_button("Salvar Perfil"):
                import base64
                final_avatar = selected_child.get('avatar', '👦')
                if new_photo is not None:
                    base64_image = base64.b64encode(new_photo.read()).decode("utf-8")
                    final_avatar = f"data:{new_photo.type};base64,{base64_image}"
                elif new_emoji != 'Manter Atual':
                    final_avatar = new_emoji
                
                db.update_user_profile(selected_child['id'], new_name, final_avatar, new_age)
                st.toast("Perfil atualizado! 🪄")
                st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        a_disp = selected_child.get('avatar', '👦')
        img_html = f"<img src='{a_disp}' style='width:50px; height:50px; border-radius:50%; object-fit:cover; margin-right:10px; vertical-align:middle;'/>" if a_disp.startswith('data:image') else f"<span style='font-size:35px; vertical-align:middle;'>{a_disp}</span>"
        st.markdown(f"<div style='padding:15px; background-color:#F2FAFF; border-radius:10px; border-left:5px solid #4A90E2;'><div style='display:flex; align-items:center;'>{img_html}<b style='color:#1A202C;'>Cofre Mágico</b></div><h2 style='color:#FF9F1C; margin:0;'>R$ {selected_child['balance']:.2f}</h2></div>", unsafe_allow_html=True)
    with col2:
        level = 1 + (selected_child.get('xp', 0) // 100)
        st.markdown(f"<div style='padding:15px; background-color:#FFF3B0; border-radius:10px; border-left:5px solid #2EC4B6;'><h4 style='color:#1A202C; margin:0;'>Nível Atual</h4><h2 style='color:#2EC4B6; margin:0;'>Nível {level} <span style='font-size:16px;'>(XP: {selected_child.get('xp', 0)})</span></h2></div>", unsafe_allow_html=True)
    
    st.write("---")
    st.markdown("<h3>⚔️ Atribuir Novas Missões</h3>", unsafe_allow_html=True)
    
    c_age = selected_child.get('age', 5)
    st.write(f"Vimos que **{selected_child['name']}** tem **{c_age} anos**. Missões recomendadas nesta fase:")
    
    if c_age <= 5:
        suggestions = [
            ("Guardar os brinquedos na caixa", 1.0, "diaria"),
            ("Levar o prato para a pia", 1.0, "diaria"),
            ("Regar as plantinhas", 1.5, "diaria"),
            ("Escovar os dentes sem chorar", 2.0, "diaria"),
            ("Arrumar os sapatos no armário", 1.0, "diaria"),
            ("Comer todos os legumes da refeição", 1.5, "diaria"),
            ("Tomar banho sem enrolar", 1.5, "diaria")
        ]
    elif c_age <= 9:
        suggestions = [
            ("Arrumar a própria cama", 3.0, "diaria"),
            ("Organizar a mochila e uniforme", 2.0, "diaria"),
            ("Colocar ração/água pro pet", 2.0, "diaria"),
            ("Tomar banho no horário", 2.5, "diaria"),
            ("Fazer a lição de casa sem reclamar", 3.0, "diaria"),
            ("Tirar o pó das estantes ou móveis", 2.5, "unica"),
            ("Ajudar a colocar/tirar a mesa", 2.0, "diaria"),
            ("Ler um livro ou revista por 20 min", 3.0, "diaria")
        ]
    else:
        suggestions = [
            ("Lavar, secar e guardar a louça", 4.0, "diaria"),
            ("Tirar o lixo da casa para a rua", 3.0, "diaria"),
            ("Aspirar/Varrer o quarto", 5.0, "diaria"),
            ("Ajudar a fazer as refeições", 4.0, "diaria"),
            ("Passear com o cachorro / Lavar quintal", 5.0, "diaria"),
            ("Organizar todo o guarda-roupa", 10.0, "unica"),
            ("Estudar matéria escolar extra por 1h", 6.0, "diaria"),
            ("Ajudar a lavar o carro da família", 15.0, "unica")
        ]
        
    suggestion_dict = { s[0]: s for s in suggestions }
    selected_titles = st.multiselect("Selecione quais missões sugeridas deseja aplicar:", list(suggestion_dict.keys()))
        
    with st.form("new_task_form"):
        selected_presets = []
        if selected_titles:
            st.write("**Ajuste o valor e frequência das missões selecionadas:**")
            for i, title in enumerate(selected_titles):
                s_title, s_price, s_req_freq = suggestion_dict[title]
                st.markdown(f"**🔹 {s_title}**")
                col1, col2 = st.columns(2)
                with col1:
                    price = st.number_input("Recompensa (R$)", value=s_price, min_value=0.0, step=0.5, key=f"prc_{i}")
                with col2:
                    freq_opts = ["Diária", "Semanal", "Mensal", "Única"]
                    freq_idx = 0 if s_req_freq == 'diaria' else (1 if s_req_freq == 'semanal' else (2 if s_req_freq == 'mensal' else 3))
                    freq = st.selectbox("Frequência", freq_opts, index=freq_idx, key=f"frq_{i}")
                    
                freq_key = "diaria" if freq == "Diária" else ("semanal" if freq == "Semanal" else ("mensal" if freq == "Mensal" else "unica"))
                selected_presets.append((s_title, price, freq_key))
                st.write("---")
                
        st.write("**Ou envie uma missão Extra Personalizada:**")
        custom_title = st.text_input("Missão Personalizada:")
        task_desc = st.text_area("O que precisa ser feito exatamente? (Detalhes)")
        
        task_freq_opts = ["Diária (repete todo dia)", "Semanal (repete 1x na semana)", "Mensal (repete 1x no mês)", "Única (faz uma vez e acabou)"]
        task_freq = st.selectbox("Frequência:", task_freq_opts)
        
        if 'Diária' in task_freq: task_freq_key = 'diaria'
        elif 'Semanal' in task_freq: task_freq_key = 'semanal'
        elif 'Mensal' in task_freq: task_freq_key = 'mensal'
        else: task_freq_key = 'unica'
        
        custom_reward = st.number_input("Recompensa (R$)", min_value=0.0, step=0.5, value=2.0)
        
        if st.form_submit_button("Atribuir Missões ao Painel da Criança!"):
            launched = False
            for p_title, p_reward, p_freq in selected_presets:
                db.create_task(selected_child['id'], p_title, "", p_freq, p_reward)
                launched = True
            
            if custom_title.strip():
                db.create_task(selected_child['id'], custom_title.strip(), task_desc, task_freq_key, custom_reward)
                launched = True
                
            if launched:
                st.toast("✅ Missões lançadas com sucesso!")
                st.rerun()
            else:
                st.error("Ops! Você não marcou nem digitou nenhuma missão.")

    st.markdown("<h4>📋 Missões Ativas</h4>", unsafe_allow_html=True)
    tasks = db.get_tasks_for_child(selected_child['id'])
    if not tasks: st.write("Nenhuma missão.")
    status_map = {'completed': 'CONCLUÍDA', 'waiting_approval': 'AGUARDANDO APROVAÇÃO', 'pending': 'PENDENTE'}
    for t in tasks:
        color = "green" if t['status'] == 'completed' else ("orange" if t['status'] == 'waiting_approval' else "blue")
        status_pt = status_map.get(t['status'], t['status'].upper())
        f = t['frequency']
        freq_pt = 'Diária' if f == 'diaria' else ('Única' if f == 'unica' else f.capitalize())
        st.markdown(f"<div style='border-left: 5px solid {color}; padding:10px; background-color:white; border-radius:5px; margin-bottom:5px;'><b style='color:#1A202C;'>{t['title']}</b> <span style='color:#1A202C;'>- R$ {t['reward']:.2f} ({freq_pt})</span> <br> <span style='font-size:12px; font-weight:bold; color:{color}'>Status: {status_pt}</span></div>", unsafe_allow_html=True)

def show_approvals():
    st.markdown("<h2>✅ Ouvidoria e Aprovações</h2>", unsafe_allow_html=True)
    children = db.get_users_by_role('child')
    has_pending = False
    if children:
        for child in children:
            tasks = db.get_tasks_for_child(child['id'])
            pending = [t for t in tasks if t['status'] == 'waiting_approval']
            if pending:
                has_pending = True
                st.markdown(f"<h3 style='color:#EF476F;'>👑 {child['name']} alega ter feito...</h3>", unsafe_allow_html=True)
                for t in pending:
                    with st.container(border=True):
                        st.write(f"**{t['title']}** (Recompensa: **R$ {t['reward']:.2f}**)")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("VERDADE (Aprovar)", key=f"app_{t['id']}", type="primary"):
                                db.update_task_status(t['id'], 'completed')
                                db.create_transaction_and_update_balance(child['id'], f"Prêmio Missão: {t['title']}", t['reward'], 'earn')
                                db.add_user_xp(child['id'], 10)
                                db.update_pet_status(child['id'], hunger_delta=20)
                                st.toast(f"✅ Tarefa Aprovada! {child.get('name')} ganhou R$ {t['reward']:.2f}, +10 XP e alimentou o mascote!")
                                time.sleep(1.5)
                                st.rerun()
                        with col2:
                            if st.button("MENTIRA (Rejeitar)", key=f"rej_{t['id']}"):
                                db.update_task_status(t['id'], 'pending')
                                st.toast("Rejeitado!")
                                st.rerun()
    if not has_pending:
        st.success("Tudo liberado! Nenhuma missão aguardando sua validação.")

def show_store_admin():
    st.markdown("<h2>🛒 Gerenciar Lojinha de Recompensas</h2>", unsafe_allow_html=True)
    
    tabs = st.tabs(["🎁 Cadastrar Itens", "📦 Entregas e Pedidos"])
    
    with tabs[0]:
        st.write("Adicione itens que seus filhos podem resgatar usando moedas.")
        with st.form("add_item_form"):
            i_title = st.text_input("Nome da Recompensa (Ex: 1h de Videogame, Sorvete)")
            i_cost = st.number_input("Custo (em Moedas)", min_value=1.0, step=1.0, value=5.0)
            i_icon = st.selectbox("Ícone", ['🎮', '🍦', '🍕', '🎞️', '🧸', '🎟️', '🚲'])
            if st.form_submit_button("Colocar na Lojinha!"):
                db.create_store_item(i_title, i_cost, i_icon)
                st.toast("Item disponível na lojinha!")
                st.rerun()
                
        st.write("---")
        st.write("### Catálogo Atual")
        items = db.get_all_store_items()
        for it in items:
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(f"{it['icon']} **{it['title']}** - R$ {it['cost']:.2f}")
            with col2:
                if st.button("Apagar", key=f"del_{it['id']}"):
                    db.delete_store_item(it['id'])
                    st.rerun()

    with tabs[1]:
        st.write("Veja as recompensas compradas pelas crianças que aguardam entrega.")
        purchases = db.get_purchases()
        pending = [p for p in purchases if p['status'] == 'pending']
        if not pending:
            st.info("Nenhuma entrega pendente! Ufa.")
        else:
            for p in pending:
                child = db.get_user_by_id(p['child_id'])
                cname = child['name'] if child else "Desconhecido"
                with st.container(border=True):
                    st.write(f"**{cname}** comprou: **{p['item_name']}** (R$ {p['cost']:.2f})")
                    if st.button("Marcar como Entregue ✅", key=f"deliv_{p['id']}", type="primary"):
                        db.update_purchase_status(p['id'], 'delivered')
                        st.toast("Produto entregue!")
                        st.rerun()

def show_agenda():
    st.markdown("<h2>📅 Agenda da Família</h2>", unsafe_allow_html=True)
    with st.form("event_form"):
        e_title = st.text_input("Qual o compromisso? (Ex: Dentista da Maria)")
        e_date = st.date_input("Qual o dia?")
        e_desc = st.text_area("Anotações Adicionais (opcional)")
        
        if st.form_submit_button("Salvar no Calendário!"):
            if e_title:
                db.create_event(e_title, e_date, e_desc)
                st.toast("Adicionado a nossa Agenda!")
                st.rerun()
            else:
                st.error("Precisamos do título!")
                
    st.write("---")
    events = db.get_all_events()
    if events:
        for e in events:
            with st.container(border=True):
                st.markdown(f"<span style='color:#4A90E2; font-weight:bold;'>📆 Dia {e['date']}</span> - <b>{e['title']}</b>", unsafe_allow_html=True)
                if e['description']: st.markdown(f"*{e['description']}*")
    else:
        st.info("Agenda limpa por enquanto!")
