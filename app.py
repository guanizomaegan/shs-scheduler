import streamlit as st
import json, os
from datetime import datetime
import pandas as pd

# ── Constants ─────────────────────────────────────────────────────────────────
DAYS    = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = ["7:30–8:30", "8:30–9:30", "9:30–10:30", "10:30–11:30",
           "12:30–1:30", "1:30–2:30", "2:30–3:30", "3:30–4:30"]
STRANDS = ["STEM", "ABM", "HUMSS", "TVL", "GAS", "SPORTS"]
GRADES  = ["Grade 11", "Grade 12"]
DATA_FILE = "shs_schedule_data.json"

# ── Data Layer ────────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"subjects": [], "teachers": [], "sections": [], "schedule": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Keep data in session state so changes persist across reruns
if "data" not in st.session_state:
    st.session_state.data = load_data()

def data():
    return st.session_state.data

def persist():
    save_data(st.session_state.data)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SHS Scheduler",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #1A3A5C !important;
}
[data-testid="stSidebar"] * { color: #CBD5E0 !important; }
[data-testid="stSidebar"] .sidebar-logo {
    text-align: center; padding: 1.5rem 0 1rem;
}
[data-testid="stSidebar"] .sidebar-logo h2 {
    color: #FFFFFF !important; font-size: 1.2rem; font-weight: 700; margin: 0.25rem 0 0;
}
[data-testid="stSidebar"] .sidebar-logo p {
    color: #8FA3BC !important; font-size: 0.78rem; margin: 0;
}
[data-testid="stSidebarNav"] { display: none; }

/* ── Metric cards ── */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}
.metric-card .metric-value {
    font-size: 2.4rem; font-weight: 700; line-height: 1;
}
.metric-card .metric-label {
    font-size: 0.82rem; color: #6B7A8D; margin-top: 0.3rem; font-weight: 500;
}

/* ── Timetable ── */
.tt-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.tt-table th {
    background: #2563A8; color: #FFFFFF;
    padding: 0.6rem 0.5rem; text-align: center;
    font-weight: 600; border: 1px solid #1A3A5C;
}
.tt-table td {
    border: 1px solid #E2E8F0;
    padding: 0.55rem 0.5rem; text-align: center;
    background: #F4F7FB; min-width: 120px;
}
.tt-table td.filled {
    background: #2563A8; color: #FFFFFF;
    font-weight: 500; border-radius: 4px;
}
.tt-table td.period-label {
    background: #D6E8FA; color: #1A3A5C;
    font-weight: 600; white-space: nowrap;
}

/* ── Section badge ── */
.section-badge {
    display: inline-block;
    background: #D6E8FA; color: #1A3A5C;
    border-radius: 6px; padding: 0.15rem 0.6rem;
    font-size: 0.78rem; font-weight: 600; margin: 2px;
}

/* ── Buttons ── */
.stButton > button {
    background: #2563A8 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.2rem !important;
}
.stButton > button:hover {
    background: #1A3A5C !important;
}

/* ── Success/Warning banners ── */
.banner-success {
    background: #D1FAE5; border-left: 4px solid #1D8A6E;
    border-radius: 8px; padding: 0.75rem 1rem;
    color: #064E3B; font-weight: 500; margin: 0.5rem 0;
}
.banner-error {
    background: #FEE2E2; border-left: 4px solid #C0392B;
    border-radius: 8px; padding: 0.75rem 1rem;
    color: #7F1D1D; font-weight: 500; margin: 0.5rem 0;
}

/* ── Panel card ── */
.panel-card {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 1rem;
}
.panel-title {
    font-size: 0.95rem; font-weight: 700;
    color: #1A3A5C; margin-bottom: 0.8rem;
    border-bottom: 1px solid #E2E8F0; padding-bottom: 0.5rem;
}

/* ── Form labels ── */
label { font-weight: 500 !important; color: #1A3A5C !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    border-radius: 8px !important;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:2.2rem">📅</div>
        <h2>SHS Scheduler</h2>
        <p>Senior High School</p>
    </div>
    <hr style="border-color:#2D5275; margin: 0.5rem 0 1rem">
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=["🏠  Dashboard", "📋  Schedule", "📚  Subjects",
                 "👩‍🏫  Teachers", "🏫  Sections"],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#2D5275; margin: 1rem 0 0.5rem'>",
                unsafe_allow_html=True)
    total = sum(len(v) for v in data()["schedule"].values())
    st.markdown(f"""
    <div style='font-size:0.75rem; color:#8FA3BC; padding: 0 0.5rem;'>
        <div>📚 {len(data()['subjects'])} subjects</div>
        <div>👩‍🏫 {len(data()['teachers'])} teachers</div>
        <div>🏫 {len(data()['sections'])} sections</div>
        <div>📋 {total} scheduled entries</div>
    </div>
    """, unsafe_allow_html=True)

# ── Helper: timetable HTML ────────────────────────────────────────────────────
def render_timetable(section):
    lookup = {}
    for entry in data()["schedule"].get(section, []):
        lookup[(entry["day"], entry["period"])] = entry

    rows = ['<table class="tt-table"><thead><tr>',
            '<th>Period</th>']
    for day in DAYS:
        rows.append(f'<th>{day}</th>')
    rows.append('</tr></thead><tbody>')

    for period in PERIODS:
        rows.append(f'<tr><td class="period-label">{period}</td>')
        for day in DAYS:
            entry = lookup.get((day, period))
            if entry:
                rows.append(
                    f'<td class="filled">{entry["subject"]}<br>'
                    f'<span style="font-size:0.72rem;opacity:.85">{entry["teacher"]}</span></td>'
                )
            else:
                rows.append('<td style="color:#8FA3BC">—</td>')
        rows.append('</tr>')

    rows.append('</tbody></table>')
    return ''.join(rows)

# ── Pages ─────────────────────────────────────────────────────────────────────

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
if page == "🏠  Dashboard":
    st.markdown("## 🏠 Dashboard")
    st.caption("Overview of your schedule setup")

    # Stat cards
    c1, c2, c3, c4 = st.columns(4)
    total_entries = sum(len(v) for v in data()["schedule"].values())
    for col, icon, label, val, color in [
        (c1, "📚", "Subjects",  len(data()["subjects"]),  "#2563A8"),
        (c2, "👩‍🏫","Teachers", len(data()["teachers"]),  "#4A90D9"),
        (c3, "🏫", "Sections",  len(data()["sections"]),  "#1D8A6E"),
        (c4, "📋", "Scheduled", total_entries,             "#1A3A5C"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.6rem">{icon}</div>
            <div class="metric-value" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick-add form
    st.markdown('<div class="panel-card"><div class="panel-title">➕ Quick Add Schedule Entry</div>',
                unsafe_allow_html=True)

    if not (data()["sections"] and data()["subjects"] and data()["teachers"]):
        st.info("Add at least one Section, Subject, and Teacher first to create schedule entries.")
    else:
        qa1, qa2, qa3 = st.columns(3)
        qa4, qa5, qa6 = st.columns([2, 2, 1])
        with qa1:
            q_sec = st.selectbox("Section", data()["sections"], key="q_sec")
        with qa2:
            q_day = st.selectbox("Day", DAYS, key="q_day")
        with qa3:
            q_per = st.selectbox("Period", PERIODS, key="q_per")
        with qa4:
            q_sub = st.selectbox("Subject", data()["subjects"], key="q_sub")
        with qa5:
            q_tch = st.selectbox("Teacher", data()["teachers"], key="q_tch")
        with qa6:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Add Entry", key="qa_save"):
                entries = data()["schedule"].setdefault(q_sec, [])
                conflict = next((e for e in entries
                                 if e["day"] == q_day and e["period"] == q_per), None)
                if conflict:
                    st.markdown(
                        f'<div class="banner-error">⚠️ Conflict: that slot is taken by {conflict["subject"]}.</div>',
                        unsafe_allow_html=True)
                else:
                    entries.append({"section": q_sec, "day": q_day, "period": q_per,
                                    "subject": q_sub, "teacher": q_tch})
                    persist()
                    st.markdown('<div class="banner-success">✅ Entry added!</div>',
                                unsafe_allow_html=True)
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Recent entries
    st.markdown('<div class="panel-card"><div class="panel-title">🕒 Recent Schedule Entries</div>',
                unsafe_allow_html=True)
    rows = []
    for sec, entries in data()["schedule"].items():
        for e in entries:
            rows.append({"Section": e.get("section", sec), "Day": e.get("day", ""),
                         "Period": e.get("period", ""), "Subject": e.get("subject", ""),
                         "Teacher": e.get("teacher", "")})
    if rows:
        df = pd.DataFrame(rows[-20:])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No schedule entries yet.")
    st.markdown('</div>', unsafe_allow_html=True)


# ── SCHEDULE ──────────────────────────────────────────────────────────────────
elif page == "📋  Schedule":
    st.markdown("## 📋 Schedule")
    st.caption("Weekly class timetable per section")

    if not data()["sections"]:
        st.info("No sections found. Add sections first.")
    else:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            selected_sec = st.selectbox("Select section to view", data()["sections"],
                                        key="tt_section")
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            add_entry = st.button("➕ Add Entry", key="tt_add")

        # Timetable
        st.markdown(f"### {selected_sec}")
        st.markdown(render_timetable(selected_sec), unsafe_allow_html=True)

        # Delete entry
        sec_entries = data()["schedule"].get(selected_sec, [])
        if sec_entries:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🗑 Remove a schedule entry"):
                entry_labels = [
                    f"{e['day']} | {e['period']} | {e['subject']} ({e['teacher']})"
                    for e in sec_entries
                ]
                to_delete = st.selectbox("Select entry to remove", entry_labels, key="del_entry")
                if st.button("Remove Entry", key="del_btn"):
                    idx = entry_labels.index(to_delete)
                    data()["schedule"][selected_sec].pop(idx)
                    if not data()["schedule"][selected_sec]:
                        del data()["schedule"][selected_sec]
                    persist()
                    st.success("Entry removed.")
                    st.rerun()

        # Add entry form
        if add_entry or st.session_state.get("show_add_form"):
            st.session_state["show_add_form"] = True
            st.markdown("---")
            st.markdown("#### Add New Entry")
            if not (data()["subjects"] and data()["teachers"]):
                st.warning("Add subjects and teachers first.")
            else:
                f1, f2, f3 = st.columns(3)
                f4, f5 = st.columns(2)
                with f1:
                    a_day = st.selectbox("Day", DAYS, key="a_day")
                with f2:
                    a_per = st.selectbox("Period", PERIODS, key="a_per")
                with f3:
                    a_sub = st.selectbox("Subject", data()["subjects"], key="a_sub")
                with f4:
                    a_tch = st.selectbox("Teacher", data()["teachers"], key="a_tch")
                with f5:
                    st.markdown("<br>", unsafe_allow_html=True)
                    s1, s2 = st.columns(2)
                    with s1:
                        if st.button("Save", key="save_entry"):
                            entries = data()["schedule"].setdefault(selected_sec, [])
                            conflict = next(
                                (e for e in entries if e["day"] == a_day and e["period"] == a_per),
                                None)
                            if conflict:
                                st.error(f"Conflict with {conflict['subject']}.")
                            else:
                                entries.append({
                                    "section": selected_sec, "day": a_day,
                                    "period": a_per, "subject": a_sub, "teacher": a_tch
                                })
                                persist()
                                st.session_state["show_add_form"] = False
                                st.success("Added!")
                                st.rerun()
                    with s2:
                        if st.button("Cancel", key="cancel_entry"):
                            st.session_state["show_add_form"] = False
                            st.rerun()


# ── SUBJECTS ──────────────────────────────────────────────────────────────────
elif page == "📚  Subjects":
    st.markdown("## 📚 Subjects")
    st.caption("Manage the subject catalog")

    st.markdown('<div class="panel-card"><div class="panel-title">➕ Add New Subject</div>',
                unsafe_allow_html=True)
    s_col1, s_col2 = st.columns([4, 1])
    with s_col1:
        new_subject = st.text_input("Subject name", placeholder="e.g. General Mathematics",
                                    label_visibility="collapsed", key="new_subject")
    with s_col2:
        if st.button("Add Subject"):
            name = new_subject.strip()
            if not name:
                st.warning("Please enter a subject name.")
            elif name in data()["subjects"]:
                st.error("Subject already exists.")
            else:
                data()["subjects"].append(name)
                persist()
                st.success(f"Added '{name}'")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card"><div class="panel-title">📋 All Subjects</div>',
                unsafe_allow_html=True)
    if data()["subjects"]:
        for i, subj in enumerate(data()["subjects"]):
            row1, row2 = st.columns([6, 1])
            row1.markdown(f'<span class="section-badge">{subj}</span>', unsafe_allow_html=True)
            with row2:
                if st.button("🗑", key=f"del_subj_{i}", help=f"Delete {subj}"):
                    data()["subjects"].remove(subj)
                    persist()
                    st.rerun()
    else:
        st.caption("No subjects added yet.")
    st.markdown('</div>', unsafe_allow_html=True)


# ── TEACHERS ──────────────────────────────────────────────────────────────────
elif page == "👩‍🏫  Teachers":
    st.markdown("## 👩‍🏫 Teachers")
    st.caption("Manage teaching staff")

    st.markdown('<div class="panel-card"><div class="panel-title">➕ Add New Teacher</div>',
                unsafe_allow_html=True)
    t_col1, t_col2 = st.columns([4, 1])
    with t_col1:
        new_teacher = st.text_input("Full name", placeholder="e.g. Ma. Santos",
                                    label_visibility="collapsed", key="new_teacher")
    with t_col2:
        if st.button("Add Teacher"):
            name = new_teacher.strip()
            if not name:
                st.warning("Please enter a teacher name.")
            elif name in data()["teachers"]:
                st.error("Teacher already exists.")
            else:
                data()["teachers"].append(name)
                persist()
                st.success(f"Added '{name}'")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card"><div class="panel-title">📋 All Teachers</div>',
                unsafe_allow_html=True)
    if data()["teachers"]:
        for i, teacher in enumerate(data()["teachers"]):
            r1, r2 = st.columns([6, 1])
            r1.markdown(f'<span class="section-badge" style="background:#E1F5EE;color:#0F6E56">{teacher}</span>',
                        unsafe_allow_html=True)
            with r2:
                if st.button("🗑", key=f"del_tch_{i}", help=f"Delete {teacher}"):
                    data()["teachers"].remove(teacher)
                    persist()
                    st.rerun()
    else:
        st.caption("No teachers added yet.")
    st.markdown('</div>', unsafe_allow_html=True)


# ── SECTIONS ──────────────────────────────────────────────────────────────────
elif page == "🏫  Sections":
    st.markdown("## 🏫 Sections")
    st.caption("Manage class sections")

    st.markdown('<div class="panel-card"><div class="panel-title">➕ Add New Section</div>',
                unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        sec_name = st.text_input("Section name", placeholder="e.g. Einstein", key="sec_name")
    with sc2:
        sec_grade = st.selectbox("Grade level", GRADES, key="sec_grade")
    with sc3:
        sec_strand = st.selectbox("Strand", STRANDS, key="sec_strand")
    with sc4:
        sec_adviser = st.text_input("Adviser (optional)", key="sec_adviser")

    if st.button("Add Section"):
        name = sec_name.strip()
        if not name:
            st.warning("Section name is required.")
        else:
            display = f"{name} ({sec_grade} - {sec_strand})"
            if display in data()["sections"]:
                st.error("Section already exists.")
            else:
                data()["sections"].append(display)
                persist()
                st.success(f"Added '{display}'")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card"><div class="panel-title">🏫 All Sections</div>',
                unsafe_allow_html=True)
    if data()["sections"]:
        for i, sec in enumerate(data()["sections"]):
            r1, r2 = st.columns([6, 1])
            r1.markdown(f'<span class="section-badge" style="background:#EAF3DE;color:#3B6D11">{sec}</span>',
                        unsafe_allow_html=True)
            with r2:
                if st.button("🗑", key=f"del_sec_{i}", help=f"Delete {sec}"):
                    data()["sections"].remove(sec)
                    if sec in data()["schedule"]:
                        del data()["schedule"][sec]
                    persist()
                    st.rerun()
    else:
        st.caption("No sections added yet.")
    st.markdown('</div>', unsafe_allow_html=True)
