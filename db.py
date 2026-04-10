import sqlite3
import datetime

DB_PATH = "familyquest.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def check_and_apply_migrations():
    conn = get_connection()
    c = conn.cursor()
    # Check if 'avatar' exists in users
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    
    if 'avatar' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT '👦'")
    if 'xp' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0")
    if 'age' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN age INTEGER DEFAULT 5")
        
    # Check if rewards table exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS store_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            cost REAL NOT NULL,
            icon TEXT DEFAULT '🎁'
        )
    ''')
    
    # Store purchases (child buying something)
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            item_name TEXT,
            cost REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (child_id) REFERENCES users (id)
        )
    ''')
    
    # Pets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            name TEXT,
            type TEXT,
            hunger INTEGER DEFAULT 50,
            happiness INTEGER DEFAULT 50,
            last_interaction DATETIME,
            FOREIGN KEY (child_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            pin TEXT,
            balance REAL DEFAULT 0.0,
            monthly_goal_name TEXT,
            monthly_goal_target REAL DEFAULT 0.0,
            avatar TEXT DEFAULT '👦',
            xp INTEGER DEFAULT 0,
            age INTEGER DEFAULT 5
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            frequency TEXT,
            reward REAL,
            status TEXT DEFAULT 'pending',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (child_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            description TEXT,
            amount REAL,
            type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (child_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            duration_minutes INTEGER,
            date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (child_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date DATE,
            description TEXT,
            attachment TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            name TEXT,
            type TEXT,
            hunger INTEGER DEFAULT 50,
            happiness INTEGER DEFAULT 50,
            last_interaction DATETIME,
            FOREIGN KEY (child_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()
    
    # Run migrations for existing DBs
    check_and_apply_migrations()

# --- User Functions ---

def get_users_by_role(role):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role=?", (role,))
    columns = [col[0] for col in c.description]
    users = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    columns = [col[0] for col in c.description]
    row = c.fetchone()
    conn.close()
    if row:
        return dict(zip(columns, row))
    return None

def create_user(name, role, pin=None, avatar='👦', age=5):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (name, role, pin, avatar, age) VALUES (?, ?, ?, ?, ?)", (name, role, pin, avatar, age))
    conn.commit()
    conn.close()

def update_user_goal(user_id, goal_name, goal_target):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET monthly_goal_name=?, monthly_goal_target=? WHERE id=?", (goal_name, goal_target, user_id))
    conn.commit()
    conn.close()

def update_user_profile(user_id, name, avatar, age):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET name=?, avatar=?, age=? WHERE id=?", (name, avatar, age, user_id))
    conn.commit()
    conn.close()

def add_user_xp(user_id, xp_amount):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET xp = xp + ? WHERE id=?", (xp_amount, user_id))
    conn.commit()
    conn.close()

# --- Task Functions ---

def create_task(child_id, title, description, frequency, reward):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (child_id, title, description, frequency, reward) VALUES (?, ?, ?, ?, ?)",
              (child_id, title, description, frequency, reward))
    conn.commit()
    conn.close()

def get_tasks_for_child(child_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE child_id=? ORDER BY status, id DESC", (child_id,))
    columns = [col[0] for col in c.description]
    tasks = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.close()
    return tasks

def update_task_status(task_id, new_status):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.datetime.now()
    c.execute("UPDATE tasks SET status=?, updated_at=? WHERE id=?", (new_status, now, task_id))
    conn.commit()
    conn.close()

# --- Transaction Functions ---

def create_transaction_and_update_balance(child_id, description, amount, t_type):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO transactions (child_id, description, amount, type) VALUES (?, ?, ?, ?)",
                  (child_id, description, amount, t_type))
        if t_type == 'earn':
            c.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, child_id))
        elif t_type == 'spend':
            c.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, child_id))
        conn.commit()
    except Exception as e:
        print("Error on transaction:", e)
        conn.rollback()
    finally:
        conn.close()

def get_transactions_for_child(child_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE child_id=? ORDER BY created_at DESC", (child_id,))
    columns = [col[0] for col in c.description]
    transactions = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.close()
    return transactions

# --- Study Session Functions ---

def add_study_session(child_id, duration_minutes):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO study_sessions (child_id, duration_minutes) VALUES (?, ?)", (child_id, duration_minutes))
    conn.commit()
    conn.close()
    # Also add 1 XP per minute studied
    add_user_xp(child_id, duration_minutes)
    # Restore pet happiness
    update_pet_status(child_id, happiness_delta=25)

def get_study_history(child_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT date, SUM(duration_minutes) as total_minutes FROM study_sessions WHERE child_id=? GROUP BY date ORDER BY date", (child_id,))
    columns = [col[0] for col in c.description]
    logs = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.close()
    return logs

# --- Event Functions ---

def create_event(title, date, description, attachment=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO events (title, date, description, attachment) VALUES (?, ?, ?, ?)", (title, date, description, attachment))
    conn.commit()
    conn.close()

def get_all_events():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY date")
    columns = [col[0] for col in c.description]
    events = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.close()
    return events
    
# --- Store and Purchase Functions ---

def create_store_item(title, cost, icon):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO store_items (title, cost, icon) VALUES (?, ?, ?)", (title, cost, icon))
    conn.commit()
    conn.close()

def delete_store_item(item_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM store_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

def get_all_store_items():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM store_items ORDER BY cost ASC")
    columns = [col[0] for col in c.description]
    items = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.close()
    return items

def buy_item(child_id, item_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        # Get Item cost and name
        c.execute("SELECT * FROM store_items WHERE id=?", (item_id,))
        item = c.fetchone()
        if not item: return False
        
        item_title = item[1]
        item_cost = item[2]
        
        # Check balance
        c.execute("SELECT balance FROM users WHERE id=?", (child_id,))
        balance = c.fetchone()[0]
        if balance < item_cost: return False
        
        # Deduct balance via transaction
        create_transaction_and_update_balance(child_id, f"Compra na Lojinha: {item_title}", item_cost, 'spend')
        
        # Add to purchases
        c.execute("INSERT INTO purchases (child_id, item_name, cost, status) VALUES (?, ?, ?, 'pending')", 
                  (child_id, item_title, item_cost))
        conn.commit()
        return True
    except Exception as e:
        print("Error buying item:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def get_purchases():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM purchases ORDER BY created_at DESC")
    columns = [col[0] for col in c.description]
    p = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.close()
    return p

def get_purchases_by_child(child_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM purchases WHERE child_id=? ORDER BY created_at DESC", (child_id,))
    columns = [col[0] for col in c.description]
    p = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.close()
    return p

def update_purchase_status(purchase_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE purchases SET status=? WHERE id=?", (status, purchase_id))
    conn.commit()
    conn.close()

# --- FUNCOES DO MASCOTE (PET) ---

def get_pet_for_child(child_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pets WHERE child_id = ?", (child_id,))
    pet = cursor.fetchone()
    conn.close()
    if pet:
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, pet))
    return None

def create_pet(child_id, name, type):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO pets (child_id, name, type, hunger, happiness, last_interaction) VALUES (?, ?, ?, ?, ?, ?)", 
                   (child_id, name, type, 50, 50, now_str))
    conn.commit()
    conn.close()

def update_pet_status(child_id, hunger_delta=0, happiness_delta=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, hunger, happiness FROM pets WHERE child_id = ?", (child_id,))
    pet = cursor.fetchone()
    if pet:
        pet_id = pet[0]
        hunger = pet[1]
        happ = pet[2]
        new_hunger = min(100, max(0, hunger + hunger_delta))
        new_happ = min(100, max(0, happ + happiness_delta))
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE pets SET hunger=?, happiness=?, last_interaction=? WHERE id=?", 
                       (new_hunger, new_happ, now_str, pet_id))
        conn.commit()
    conn.close()

def calculate_pet_decay(child_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, hunger, happiness, last_interaction FROM pets WHERE child_id = ?", (child_id,))
    pet = cursor.fetchone()
    if pet:
        pet_id, hunger, happ, last_interaction = pet
        if last_interaction:
            try:
                last_dt = datetime.datetime.strptime(last_interaction, "%Y-%m-%d %H:%M:%S")
                hours_passed = (datetime.datetime.now() - last_dt).total_seconds() / 3600.0
                decay = int(hours_passed * 2)
                if decay > 0:
                    new_hunger = max(0, hunger - decay)
                    new_happ = max(0, happ - decay)
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("UPDATE pets SET hunger=?, happiness=?, last_interaction=? WHERE id=?", 
                                   (new_hunger, new_happ, now_str, pet_id))
                    conn.commit()
            except Exception as e:
                pass
    conn.close()
