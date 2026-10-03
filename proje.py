import streamlit as st
import numpy as np
import json
import os
import time

# ==========================================
# 1. KRİPTOLOJİK ALTYAPI (KURAL 30)
# ==========================================

def rule30_generate(length, seed):
    np.random.seed(seed)
    state = np.random.randint(0, 2, size=length)
    next_state = np.zeros(length, dtype=int)
    
    for i in range(length):
        left = state[(i - 1) % length]
        center = state[i]
        right = state[(i + 1) % length]
        next_state[i] = left ^ (center | right)
        
    return next_state

def encrypt_text(text, secret_key):
    ascii_values = np.array([ord(char) for char in text], dtype=int)
    ca_key = rule30_generate(len(text), seed=secret_key)
    cipher_values = (ascii_values ^ ca_key) % 256
    cipher_text = "".join([chr(val) for val in cipher_values])
    return cipher_text, list(map(int, cipher_values))

def decrypt_text(cipher_values, secret_key):
    ca_key = rule30_generate(len(cipher_values), seed=secret_key)
    plain_ascii = (np.array(cipher_values) ^ ca_key) % 256
    plain_text = "".join([chr(val) for val in plain_ascii])
    return plain_text

# ==========================================
# 2. ORTAK VERİTABANI YÖNETİMİ (JSON)
# ==========================================

DB_FILE = "chat_db.json"

def load_messages():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_message(new_msg):
    messages = load_messages()
    messages.append(new_msg)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# ==========================================
# 3. CANLI SOHBET ARAYÜZÜ
# ==========================================

st.set_page_config(
    page_title="KriptoChat - Hücresel Otomat",
    page_icon="💬",
    layout="centered"
)

st.title("💬 KriptoChat: Şifreli Mesajlaşma")
st.caption("Kural 30 Hücresel Otomat & Modüler Aritmetik Altyapısı")
st.markdown("**Geliştiren:** Mehmet İhsan | *TÜBİTAK 2204-A Projesi*")

st.divider()

col_user, col_key = st.columns(2)

with col_user:
    username = st.text_input("Kullanıcı Adınız:", value="Kullanıcı_1")

with col_key:
    secret_key = st.number_input("Ortak Gizli Anahtar (Seed):", value=12345, step=1)

st.divider()

# Mesaj Gönderme Formu
with st.form(key="send_message_form", clear_on_submit=True):
    message_input = st.text_area("Gönderilecek Mesaj:", placeholder="Mesajınızı yazın...")
    submit_button = st.form_submit_button(label="🔒 Şifrele ve Gönder", use_container_width=True)

if submit_button and message_input.strip():
    cipher_text, cipher_vals = encrypt_text(message_input.strip(), int(secret_key))
    
    new_msg = {
        "sender": username,
        "time": time.strftime("%H:%M"),
        "cipher_text": cipher_text,
        "cipher_vals": cipher_vals,
        "key_used": int(secret_key)
    }
    save_message(new_msg)
    st.success("Mesaj ortak havuza gönderildi!")
    st.rerun()

st.divider()

# Yenileme Butonu ve Akış
col_head, col_ref = st.columns([3, 1])
with col_head:
    st.subheader("📥 Anlık Sohbet Akışı")
with col_ref:
    if st.button("🔄 Yenile"):
        st.rerun()

chat_history = load_messages()

if not chat_history:
    st.info("Henüz hiç mesaj gönderilmedi.")
else:
    for msg in reversed(chat_history):
        with st.expander(f"✉️ {msg['sender']} [{msg['time']}] — (Şifreli Mesaj)", expanded=True):
            st.write(f"**Şifreli Metin:** `{msg['cipher_text']}`")
            st.caption(f"Matris/Sayısal Kodlar: {msg['cipher_vals']}")
            
            # Anahtar Kontrolü ve Çözme
            if int(secret_key) == msg["key_used"]:
                decrypted_msg = decrypt_text(msg["cipher_vals"], int(secret_key))
                st.success(f"🔓 **Çözülen Orijinal Mesaj:** {decrypted_msg}")
            else:
                st.error("🔒 **HATA:** Girilen Gizli Anahtar uyuşmuyor!")