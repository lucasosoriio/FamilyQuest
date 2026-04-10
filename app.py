import streamlit as st
import db
import parent_view
import child_view
import streamlit.components.v1 as components

# App Config for Mobile First look
st.set_page_config(
    page_title="FamilyQuest",
    page_icon="🧸",
    layout="centered",
    initial_sidebar_state="expanded",
)

def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');
        
        html, body, [class*="css"]  {
            font-family: 'Nunito', sans-serif !important;
        }
        
        /* Tema azul e texto braco é controlado de forma nativa pelo config.toml agora. */

        div.stButton > button:first-child {
            width: 100%;
            min-height: 60px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 22px;
            border: 3px solid #4A90E2;
            color: #4A90E2;
            background-color: white;
            transition: all 0.2s;
            box-shadow: 0px 4px 0px #4A90E2;
        }

        div.stButton > button:first-child:hover {
            transform: translateY(2px);
            box-shadow: 0px 2px 0px #4A90E2;
        }
        
        div.stButton > button[kind="primary"] {
            background-color: #FFD166;
            border: 3px solid #EF476F;
            color: #EF476F;
            box-shadow: 0px 5px 0px #EF476F;
            font-weight: 900;
        }
        div.stButton > button[kind="primary"]:hover {
            transform: translateY(2px);
            box-shadow: 0px 2px 0px #EF476F;
            color: #EF476F;
            background-color: #FFCA4A;
        }
        
        h1 {
            color: #FF9F1C;
            font-weight: 900 !important;
            text-align: center;
            text-shadow: 2px 2px 0px rgba(0,0,0,0.1);
        }
        h2, h3 {
            color: #2EC4B6;
            font-weight: 900 !important;
        }
        
        .coin-box {
            background-color: #FFF3B0;
            border: 4px solid #FF9F1C;
            border-radius: 20px;
            padding: 15px;
            text-align: center;
            font-size: 30px;
            font-weight: 900;
            color: #E71D36;
            box-shadow: 0px 5px 0px #FF9F1C;
        }
        
        .level-box {
            background-color: #4A90E2;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 900;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)

def init_app():
    if 'db_inited' not in st.session_state:
        db.init_db()
        st.session_state.db_inited = True
        parents = db.get_users_by_role('parent')
        if len(parents) == 0:
            db.create_user(name="Pai/Mãe", role="parent", pin="1234")

def login_page():
    st.markdown("<h1>🌟 Family Quest 🌟</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #4A90E2;'>A aventura da nossa família!</h3>", unsafe_allow_html=True)
    st.write("---")
    
    st.write("<h2 style='text-align: center;'>Escolha quem você é:</h2>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👩‍🏫 Sou Pai/Mãe"):
            st.session_state.temp_login_role = 'parent'
            st.rerun()
    with col2:
        if st.button("🧒 Sou Filho(a)", type="primary"):
            st.session_state.temp_login_role = 'child'
            st.rerun()
            
    if 'temp_login_role' in st.session_state:
        role = st.session_state.temp_login_role
        
        components.html(
            """
            <script>
            setTimeout(() => {
                var doc = window.parent.document;
                var app = doc.querySelector('.stApp') || doc.querySelector('.main') || doc.body;
                if(app) {
                    app.scrollTo({ top: app.scrollHeight, behavior: 'smooth' });
                }
                // Fallback Window
                window.parent.scrollTo({ top: doc.body.scrollHeight, behavior: 'smooth' });
            }, 700);
            </script>
            """, height=0
        )
        
        st.write("---")
        if role == 'parent':
            st.markdown("<h3>Painel dos Pais 🔒</h3>", unsafe_allow_html=True)
            pin = st.text_input("Digite a senha secreta", type="password", key="parent_pin")
            if st.button("Desbloquear Painel 🔑", key="btn_login_parent"):
                parents = db.get_users_by_role('parent')
                valid_pin = False
                for p in parents:
                    if p['pin'] == pin:
                        valid_pin = True
                        st.session_state.current_user = p
                        st.session_state.role = 'parent'
                        break
                if valid_pin:
                    st.toast("✅ Acesso Liberado!")
                    st.rerun()
                else:
                    st.error("Ops! Senha Incorreta. ❌")
        elif role == 'child':
            children = db.get_users_by_role('child')
            if len(children) == 0:
                st.warning("Poxa, você ainda não foi cadastrado! Peça para seus pais criarem sua conta. 🥺")
            else:
                st.markdown("<h3>Bem-vindo! Qual o seu nome? 👋</h3>", unsafe_allow_html=True)
                child_names = {c['name']: c for c in children}
                selected_name = st.selectbox("", list(child_names.keys()), label_visibility="collapsed")
                st.write("")
                if st.button("ENTRAR NO JOGO! 🎮", key="btn_login_child", type="primary"):
                    st.session_state.current_user = child_names[selected_name]
                    st.session_state.role = 'child'
                    st.toast(f"Eba! Olá, {selected_name}! 👋")
                    st.rerun()

def main():
    load_css()
    init_app()
    
    if 'current_user' not in st.session_state:
        login_page()
    else:
        # User is logged in, show sidebar logic
        if st.session_state.role == 'parent':
            with st.sidebar:
                st.markdown(f"<h2 style='text-align:center;'>👨‍👩‍👧 {st.session_state.current_user['name']}</h2>", unsafe_allow_html=True)
                st.write("---")
                nav = st.radio("Acesso Rápido", [
                    "🏠 Painel e Crianças", 
                    "✅ Ouvidoria (Aprovações)", 
                    "🛒 Lojinha de Prêmios", 
                    "📅 Agenda de Saúde",
                    "🚪 Sair"
                ])
                
            if nav == "🚪 Sair":
                for key in list(st.session_state.keys()):
                    if key != 'db_inited':
                        del st.session_state[key]
                st.rerun()
            elif nav == "🏠 Painel e Crianças":
                parent_view.show_main_dashboard()
            elif nav == "✅ Ouvidoria (Aprovações)":
                parent_view.show_approvals()
            elif nav == "🛒 Lojinha de Prêmios":
                parent_view.show_store_admin()
            elif nav == "📅 Agenda de Saúde":
                parent_view.show_agenda()

        elif st.session_state.role == 'child':
            user = db.get_user_by_id(st.session_state.current_user['id']) # get fresh
            db.calculate_pet_decay(user['id']) # Sync pet stats
            
            with st.sidebar:
                avatar_display = user.get('avatar', '👦')
                if avatar_display.startswith("data:image"):
                    st.markdown(f"<div style='text-align:center;'><img src='{avatar_display}' style='width:120px; height:120px; border-radius:50%; border:3px solid #FFCA4A; object-fit:cover;'/></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h1 style='font-size:80px; text-align:center; transform:translateY(20px);'>{avatar_display}</h1>", unsafe_allow_html=True)
                    
                st.markdown(f"<h2 style='text-align:center; color:#FFCA4A;'>{user['name']}</h2>", unsafe_allow_html=True)
                
                # Level Calculation
                xp = user.get('xp', 0)
                level = 1 + (xp // 100)
                next_xp = level * 100
                progress = (xp % 100) / 100
                
                st.markdown(f"<div style='text-align:center;'><span class='level-box'>Nível {level}</span><br><b>XP:</b> {xp}/{next_xp}</div>", unsafe_allow_html=True)
                st.progress(progress)
                st.write("---")
                
                nav = st.radio("Menu Mágico", [
                    "🎯 Minhas Missões", 
                    "🧠 Forte Mente", 
                    "💰 Meu Cofre", 
                    "🎁 Lojinha Mágica", 
                    "🕹️ Fliperama",
                    "🚪 Sair"
                ])

            if nav == "🚪 Sair":
                for key in list(st.session_state.keys()):
                    if key != 'db_inited':
                         del st.session_state[key]
                st.rerun()
            elif nav == "🎯 Minhas Missões":
                child_view.show_missions(user)
            elif nav == "🧠 Forte Mente":
                child_view.show_study(user)
            elif nav == "💰 Meu Cofre":
                child_view.show_vault(user)
            elif nav == "🎁 Lojinha Mágica":
                child_view.show_store(user)
            elif nav == "🕹️ Fliperama":
                child_view.show_arcade(user)

if __name__ == "__main__":
    main()
