# src/ui/app.py
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, date
import os  # 🔐 ДОБАВЛЕНО: Для работы с переменными окружения

st.set_page_config(page_title="Finance Tracker Pro", layout="wide")

INCOME_CATS = ["Зарплата", "Фриланс", "Инвестиции", "Подарки", "Кешбэк", "Другое"]
EXPENSE_CATS = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Дом", "Одежда", "Связь", "Подписки", "Другое"]

if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# 🔐 БЕЗОПАСНОЕ ОПРЕДЕЛЕНИЕ URL
# 1. Проверяем переменную окружения (если задана в Render)
BASE_URL = os.getenv("API_URL", "https://finance-tracker-api-q1qg.onrender.com")

# 2. Если не задана, определяем среду автоматически
if not BASE_URL:
    if os.getenv("RENDER"):  # Если мы в облаке Render
        BASE_URL = "https://finance-tracker-api-q1qg.onrender.com"
    else:                    # Если мы на компьютере (локально)
        BASE_URL = "http://127.0.0.1:8000"

# 🔐 БЕЗОПАСНЫЕ ФУНКЦИИ API (СКРЫВАЮТ ТЕХНИЧЕСКИЕ ДЕТАЛИ ОШИБОК)

@st.cache_data(ttl=10)
def fetch_transactions(token: str, tx_type: str = None, year: int = None, month: int = None, category: str = None):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"skip": 0, "limit": 500}
    if tx_type: params["type"] = tx_type
    if year: params["year"] = year
    if month: params["month"] = month
    if category and category != "Все": params["category"] = category
    
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/transactions/", headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            st.session_state.token = None # Сброс токена, если он протух
            return []
        else:
            return []
    except requests.exceptions.ConnectionError:
        return []
    except Exception:
        return []

@st.cache_data(ttl=10)
def fetch_summary(token: str, year: int = None, month: int = None, tx_type: str = None, category: str = None):
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if year: params["year"] = year
    if month: params["month"] = month
    if tx_type and tx_type != "Все": params["type"] = tx_type
    if category and category != "Все": params["category"] = category
    
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/transactions/summary", headers=headers, params=params, timeout=10)
        return resp.json() if resp.status_code == 200 else {}
    except:
        return {}

def create_transaction(token: str, amount: float, category: str, description: str, tx_date: str, tx_type: str, payment: str):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "amount": float(amount), 
        "category": category, 
        "description": description or "", 
        "date": tx_date, 
        "type": tx_type, 
        "payment_method": payment
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/transactions/", json=data, headers=headers, timeout=10)
        if resp.status_code == 201:
            return 201, resp.json()
        else:
            # Скрываем детали ошибки от пользователя
            return resp.status_code, "Ошибка сохранения данных"
    except requests.exceptions.ConnectionError:
        return 500, "Нет связи с сервером"
    except Exception:
        return 500, "Неизвестная ошибка"

def delete_transaction(token: str, tx_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.delete(f"{BASE_URL}/api/v1/transactions/{tx_id}", headers=headers, timeout=10)
        return resp.status_code
    except:
        return 500

# --- ИНТЕРФЕЙС АВТОРИЗАЦИИ ---

if not st.session_state.token:
    st.title("💰 Finance Tracker Pro")
    
    # 🔐 Переключатель между входом и регистрацией
    mode = st.radio("Выберите действие", ["🔐 Вход", "📝 Регистрация"], horizontal=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if mode == "🔐 Вход":
            st.subheader("Вход в аккаунт")
            email = st.text_input("Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("Пароль", type="password", key="login_password")
            
            if st.button("Войти", type="primary", use_container_width=True):
                if not email or not password:
                    st.warning("Введите email и пароль")
                else:
                    try:
                        resp = requests.post(
                            f"{BASE_URL}/api/v1/auth/login",
                            data={"username": email, "password": password},
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            timeout=10
                        )
                        if resp.status_code == 200:
                            st.session_state.token = resp.json()["access_token"]
                            st.session_state.user_email = email
                            st.rerun()
                        elif resp.status_code == 429:
                            st.error("🛑 Слишком много попыток. Подождите минуту.")
                        else:
                            st.error("Неверный email или пароль")
                    except requests.exceptions.ConnectionError:
                        st.error("Не удалось подключиться к серверу.")
                    except Exception:
                        st.error("Произошла ошибка. Попробуйте позже.")
        
        else:  # Регистрация
            st.subheader("Создать аккаунт")
            reg_email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
            reg_password = st.text_input("Пароль", type="password", key="reg_password")
            reg_password_confirm = st.text_input("Подтвердите пароль", type="password", key="reg_password_confirm")
            
            with st.expander("🔐 Требования к паролю"):
                st.markdown("""
                - Минимум **8 символов**
                - Хотя бы **1 заглавная** буква (A-Z)
                - Хотя бы **1 строчная** буква (a-z)
                - Хотя бы **1 цифра** (0-9)
                - Хотя бы **1 спецсимвол** (!@#$%^&*...)
                """)
            
            if st.button("Зарегистрироваться", type="primary", use_container_width=True):
                if not reg_email or not reg_password:
                    st.warning("Заполните все поля")
                elif reg_password != reg_password_confirm:
                    st.error("Пароли не совпадают")
                else:
                    try:
                        resp = requests.post(
                            f"{BASE_URL}/api/v1/auth/register",
                            json={"email": reg_email, "password": reg_password},
                            timeout=10
                        )
                        
                        if resp.status_code == 200:
                            st.success("✅ Регистрация успешна! Входим...")
                            # Автоматический вход после регистрации
                            st.session_state.token = resp.json()["access_token"]
                            st.session_state.user_email = reg_email
                            st.cache_data.clear()
                            st.balloons()
                            st.rerun()
                        elif resp.status_code == 400:
                            error_detail = resp.json().get("detail", "Ошибка регистрации")
                            st.error(f"❌ {error_detail}")
                        elif resp.status_code == 422:
                            st.error("❌ Неверный формат данных. Проверьте email и пароль.")
                        else:
                            st.error("❌ Ошибка при регистрации. Попробуйте позже.")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("Не удалось подключиться к серверу.")
                    except Exception:
                        st.error("Произошла ошибка. Попробуйте позже.")
    
    st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---

st.sidebar.title(f"👤 {st.session_state.user_email}")
if st.sidebar.button("🚪 Выйти"):
    st.session_state.token = None
    st.session_state.user_email = None
    st.cache_data.clear()
    st.rerun()

st.title("📊 Finance Dashboard Pro")

# 🔹 ФИЛЬТРЫ
with st.sidebar.expander("🔍 Фильтры", expanded=True):
    col_f1, col_f2 = st.columns(2)
    with col_f1: filter_year = st.selectbox("Год", options=[None] + list(range(2020, 2030)), index=0)
    with col_f2: filter_month = st.selectbox("Месяц", options=[None] + list(range(1, 13)), format_func=lambda x: f"{x:02d}" if x else "Все", index=0)
    
    filter_type = st.radio("Тип", options=["Все", "Доходы", "Расходы"], index=0)
    
    if filter_type == "Доходы":
        cat_filter_options = ["Все"] + INCOME_CATS
    elif filter_type == "Расходы":
        cat_filter_options = ["Все"] + EXPENSE_CATS
    else:
        cat_filter_options = ["Все"] + list(set(INCOME_CATS + EXPENSE_CATS))
    
    filter_category = st.selectbox("Категория", options=cat_filter_options)
    
    tx_type_param = None if filter_type == "Все" else ("income" if filter_type == "Доходы" else "expense")
    cat_param = filter_category if filter_category != "Все" else None
    
    if st.button("Применить фильтры"):
        st.cache_data.clear()

# 🔹 Загрузка данных
with st.spinner("Загрузка..."):
    transactions = fetch_transactions(st.session_state.token, tx_type_param, filter_year, filter_month, cat_param)
    
    summary_params = {"token": st.session_state.token, "year": filter_year, "month": filter_month}
    if tx_type_param: summary_params["tx_type"] = tx_type_param
    if cat_param: summary_params["category"] = cat_param
    
    summary = fetch_summary(**summary_params)

# 🔹 Метрики
col_bal1, col_bal2, col_bal3 = st.columns(3)

if summary and summary.get("total_income") is not None:
    col_bal1.metric("💰 Доходы", f"{summary.get('total_income', 0):,.2f} ₽")
    col_bal2.metric("💸 Расходы", f"{summary.get('total_expense', 0):,.2f} ₽")
    balance = summary.get("balance", 0)
    col_bal3.metric("⚖️ Баланс", f"{balance:,.2f} ₽", 
                   delta=f"{balance:+,.2f}", 
                   delta_color="normal" if balance >= 0 else "inverse")
else:
    if transactions:
        df_temp = pd.DataFrame(transactions)
        income = df_temp[df_temp["type"]=="income"]["amount"].sum()
        expense = df_temp[df_temp["type"]=="expense"]["amount"].sum()
        col_bal1.metric("💰 Доходы", f"{income:,.2f} ₽")
        col_bal2.metric(" Расходы", f"{expense:,.2f} ₽")
        col_bal3.metric("⚖️ Баланс", f"{income-expense:,.2f} ₽")

# 🔹 Графики
if transactions:
    df = pd.DataFrame(transactions)
    
    if filter_type == "Все":
        st.subheader("📊 Общая структура")
        total_income = df[df["type"]=="income"]["amount"].sum()
        expense_df = df[df["type"]=="expense"]
        labels, values, colors = [], [], []
        if total_income > 0: labels.append("Доходы"); values.append(total_income); colors.append("#2ECC71")
        if not expense_df.empty:
            grouped = expense_df.groupby("category")["amount"].sum().reset_index()
            for i, row in grouped.iterrows(): 
                labels.append(f"Расх: {row['category']}"); values.append(row["amount"]); colors.append(px.colors.qualitative.Plotly[i % 6])
        if labels:
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4, marker=dict(colors=colors))])
            st.plotly_chart(fig, use_container_width=True)
    elif filter_type == "Доходы":
        st.subheader("💰 Структура доходов")
        income_df = df[df["type"] == "income"]
        if not income_df.empty:
            fig = px.pie(income_df, values="amount", names="category", hole=0.0, color_discrete_sequence=['#2ecc71'] * len(income_df))
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Нет доходов за выбранный период")
    else:
        st.subheader("💸 Структура расходов")
        expense_df = df[df["type"] == "expense"]
        if not expense_df.empty:
            fig = px.pie(expense_df, values="amount", names="category", hole=0.4, color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Нет расходов за выбранный период")
else:
    st.info("Нет транзакций за выбранный период")

# 🔹 Список транзакций
st.subheader("📋 Управление транзакциями")
if transactions:
    df_sorted = df.sort_values("date", ascending=False)
    for index, row in df_sorted.iterrows():
        date_str = pd.to_datetime(row["date"]).strftime("%d.%m.%Y")
        is_income = row["type"] == "income"
        amount_str = f"+{row['amount']:,.2f} ₽" if is_income else f"-{row['amount']:,.2f} ₽"
        color = "green" if is_income else "red"
        pay_icon = "💳" if row.get("payment_method") == "card" else "💵"
        
        cols = st.columns([1.2, 1.2, 3, 1.2, 1, 0.5])
        with cols[0]: st.write(date_str)
        with cols[1]: st.markdown(f"**<span style='color:{color}'>{amount_str}</span>**", unsafe_allow_html=True)
        with cols[2]: st.write(f"**{row['category']}**: {row.get('description') or '-'}")
        with cols[3]: st.caption(f"{'Доход' if is_income else 'Расход'} {pay_icon}")
        with cols[4]: st.caption(row.get("payment_method", "").capitalize())
        with cols[5]:
            if st.button("🗑", key=f"del_{row['id']}"):
                if delete_transaction(st.session_state.token, row["id"]) == 200: 
                    st.cache_data.clear()
                    st.rerun()
else:
    st.info("Нет транзакций для отображения")

# 🔹 ФОРМА ДОБАВЛЕНИЯ
st.sidebar.subheader("➕ Новая запись")

tx_type_label = st.sidebar.radio("Тип операции", options=["Расходы", "Доходы"], index=0, horizontal=True)
tx_type_api = "expense" if tx_type_label == "Расходы" else "income"

cats = INCOME_CATS if tx_type_label == "Доходы" else EXPENSE_CATS
category_options = cats + ["➕ Добавить свою категорию"]
selected_cat = st.sidebar.selectbox("Категория", options=category_options, key="cat_select")

custom_cat = None
if selected_cat == "➕ Добавить свою категорию":
    custom_cat = st.sidebar.text_input("Введите название категории", key="custom_cat_input")
    final_category = custom_cat if custom_cat and custom_cat.strip() else "Другое"
else:
    final_category = selected_cat

payment_label = st.sidebar.radio("Вид оплаты", ["💳 Карта", "💵 Наличные"], horizontal=True, key="pay_radio")
payment_api = "card" if "Карта" in payment_label else "cash"

with st.sidebar.form("add_tx", clear_on_submit=False):
    amount = st.number_input("Сумма ₽", min_value=0.01, step=0.01, key="amount_input")
    description = st.text_input("Описание", key="desc_input")
    tx_date = st.date_input("Дата", value=date.today(), key="date_input")
    
    submitted = st.form_submit_button("💾 Добавить транзакцию", type="primary", use_container_width=True)
    
    if submitted:
        if amount <= 0:
            st.sidebar.error("❌ Введите сумму больше 0")
        elif not final_category:
            st.sidebar.error("❌ Выберите или введите категорию")
        else:
            with st.spinner("Сохранение..."):
                status, result = create_transaction(
                    st.session_state.token, 
                    amount, 
                    final_category, 
                    description, 
                    tx_date.isoformat(), 
                    tx_type_api, 
                    payment_api
                )
                
                if status == 201:
                    st.sidebar.success("✅ Транзакция добавлена!")
                    st.cache_data.clear()
                    st.balloons()
                    st.rerun()
                else:
                    st.sidebar.error(f"❌ Ошибка {status}: {result}")