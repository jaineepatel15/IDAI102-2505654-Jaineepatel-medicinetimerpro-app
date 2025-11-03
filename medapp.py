import streamlit as st
from datetime import datetime
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="💊 MedTimer Pro", page_icon="💊", layout="centered")

# --- Initialize session state ---
if "meds" not in st.session_state:
    st.session_state.meds = []
if "history" not in st.session_state:
    st.session_state.history = []
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "best_streak" not in st.session_state:
    st.session_state.best_streak = 0
if "show_motivation" not in st.session_state:
    st.session_state.show_motivation = False

# --- Custom CSS ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    h1, h2, h3, label, p {
        color: #e0e0e0 !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- App Header ---
st.title("💊 MedTimer Pro")
st.write("Your friendly, daily medicine tracker — simple, calm, and motivating.")

st.markdown("---")

# --- Add Medicine ---
st.subheader("➕ Add a Medication")

col1, col2 = st.columns(2)
med_name = col1.text_input("Medicine Name", key="med_name_input")
med_type = col2.selectbox("Type", [
    "💊 Pill/Tablet",
    "💉 Injection",
    "🥤 Syrup/Liquid",
    "🌬️ Inhaler",
    "💧 Drops",
    "🩹 Patch",
    "🧴 Cream/Ointment",
    "⚪ Capsule"
], key="med_type_input")

col3, col4 = st.columns(2)
med_time = col3.time_input("Scheduled Time", key="med_time_input")
med_dosage = col4.text_input("Dosage (optional)", key="med_dosage_input")

if st.button("Add Medication", key="add_med_btn"):
    if med_name.strip():
        type_icon = med_type.split()[0]
        
        st.session_state.meds.append({
            "name": med_name,
            "time": med_time.strftime("%H:%M"),
            "type_icon": type_icon,
            "dosage": med_dosage,
            "taken": False
        })
        st.success(f"✅ Added {med_name} at {med_time.strftime('%I:%M %p')}")
        st.rerun()
    else:
        st.warning("⚠️ Please enter a medicine name!")

st.markdown("---")

# --- Display Medicines ---
st.subheader("📋 Today's Schedule")

if len(st.session_state.meds) == 0:
    st.info("📭 No medicines added yet. Add your first medication above!")
else:
    now = datetime.now().strftime("%H:%M")
    
    for idx, med in enumerate(st.session_state.meds):
        med_time = med["time"]
        
        # Determine status
        if med["taken"]:
            status = "🟢 Taken"
            color = "#28a745"
        elif med_time < now:
            status = "🔴 Missed"
            color = "#dc3545"
        else:
            status = "🟡 Upcoming"
            color = "#ffc107"
        
        # Display medication in a nice box
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1.5, 2, 1.5])
            
            with col1:
                st.markdown(f"**{med['name']}**")
                if med['dosage']:
                    st.caption(f"Dosage: {med['dosage']}")
            
            with col2:
                st.markdown(f"<div style='font-size: 2em; text-align: center;'>{med['type_icon']}</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<span style='color:{color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
                st.caption(f"Time: {med['time']}")
            
            with col4:
                if not med["taken"]:
                    if st.button("✓ Mark Taken", key=f"taken_{idx}"):
                        st.session_state.meds[idx]["taken"] = True
                        st.session_state.history.append({
                            "Date": datetime.now().strftime("%Y-%m-%d"),
                            "Type": med["type_icon"],
                            "Medicine": med["name"],
                            "Dosage": med["dosage"] if med["dosage"] else "-",
                            "Scheduled": med["time"],
                            "Taken At": datetime.now().strftime("%H:%M:%S")
                        })
                        st.rerun()
                
                if st.button("🗑️ Delete", key=f"delete_{idx}"):
                    st.session_state.meds.pop(idx)
                    st.rerun()
            
            st.markdown("---")

st.markdown("---")

# --- Progress / Adherence ---
st.subheader("📈 Today's Progress")

if len(st.session_state.meds) > 0:
    taken_count = sum(1 for m in st.session_state.meds if m["taken"])
    total = len(st.session_state.meds)
    adherence = round((taken_count / total) * 100, 1)
else:
    taken_count, total, adherence = 0, 0, 0.0

st.progress(adherence / 100)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Adherence Score", value=f"{adherence}%")
with col2:
    st.metric(label="Medications Taken", value=f"{taken_count}/{total}")

# --- Motivation Message ---
if st.button("🎨 Show Motivation", key="motivation_btn"):
    st.session_state.show_motivation = not st.session_state.show_motivation

if st.session_state.show_motivation:
    if adherence == 100:
        st.success("## 🏆 Perfect Adherence!")
        st.balloons()
    elif adherence >= 80:
        st.success("## 😊 Great Job!")
    elif adherence >= 50:
        st.info("## 💪 Keep Going!")
    else:
        st.warning("## 🌱 Try Again Tomorrow!")

st.markdown("---")

# --- Actions ---
st.subheader("⚡ Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("📅 Start New Day", key="new_day_btn"):
        if total > 0:
            # Update streak
            if adherence >= 80:
                st.session_state.streak += 1
                if st.session_state.streak > st.session_state.best_streak:
                    st.session_state.best_streak = st.session_state.streak
            else:
                st.session_state.streak = 0
            
            # Reset all medications
            for m in st.session_state.meds:
                m["taken"] = False
            
            st.session_state.show_motivation = False
            st.success("✨ New day started! All medications reset.")
            st.rerun()
        else:
            st.warning("⚠️ Add some medicines first!")

with col2:
    if st.button("🗑️ Clear All Data", key="clear_all_btn"):
        st.session_state.meds = []
        st.session_state.history = []
        st.session_state.streak = 0
        st.session_state.best_streak = 0
        st.session_state.show_motivation = False
        st.warning("🧹 All data cleared!")
        st.rerun()

st.markdown("---")

# --- Stats Section ---
st.subheader("🔥 Your Stats")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="🔥 Current Streak", value=f"{st.session_state.streak} days")

with col2:
    st.metric(label="🏆 Best Streak", value=f"{st.session_state.best_streak} days")

st.markdown("---")

# --- History ---
st.subheader("📜 Medication History")
if len(st.session_state.history) == 0:
    st.info("📭 No history yet. Start taking your medications to see history!")
else:
    # Create DataFrame and display last 10 entries
    history_df = pd.DataFrame(st.session_state.history)
    
    # Reverse to show most recent first
    recent_history = history_df.tail(10).iloc[::-1]
    
    st.dataframe(
        recent_history,
        use_container_width=True,
        hide_index=True
    )
    
    if len(st.session_state.history) > 10:
        st.caption(f"Showing last 10 of {len(st.session_state.history)} total records")

st.markdown("---")

# --- Motivational Tip ---
tips = [
    "💡 Take your medicine at the same time each day for best results!",
    "💡 Drinking water helps your body absorb most medicines better.",
    "💡 Consistency builds healthy habits!",
    "💡 You're doing great — every dose counts!",
    "💡 Set reminders on your phone to never miss a dose!",
    "💡 Keep your medications in a visible place as a reminder.",
    "💡 Track your progress - you're building a healthy routine!",
    "💡 Small steps lead to big health improvements!"
]

tip_index = datetime.now().day % len(tips)
st.info(tips[tip_index])

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.7;'>Made with ❤️ for your health</p>", unsafe_allow_html=True)