import streamlit as st
import streamlit.components.v1 as components
import json, os
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

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

def data():
    return st.session_state.data

def persist():
    save_data(st.session_state.data)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="SHS Scheduler", page_icon="📅",
                   layout="wide", initial_sidebar_state="expanded")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: #1A3A5C !important; }
[data-testid="stSidebar"] * { color: #CBD5E0 !important; }
.metric-card { background:#fff; border:1px solid #E2E8F0; border-radius:12px;
               padding:1.2rem 1.4rem; text-align:center; }
.metric-card .mv { font-size:2.4rem; font-weight:700; line-height:1; }
.metric-card .ml { font-size:0.82rem; color:#6B7A8D; margin-top:0.3rem; }
.section-badge { display:inline-block; background:#D6E8FA; color:#1A3A5C;
    border-radius:6px; padding:0.15rem 0.6rem; font-size:0.78rem;
    font-weight:600; margin:2px; }
.stButton > button { background:#2563A8 !important; color:#fff !important;
    border:none !important; border-radius:8px !important;
    font-weight:600 !important; padding:0.45rem 1.2rem !important; }
.stButton > button:hover { background:#1A3A5C !important; }
.panel-card { background:#fff; border:1px solid #E2E8F0; border-radius:12px;
              padding:1.2rem 1.4rem; margin-bottom:1rem; }
.panel-title { font-size:0.95rem; font-weight:700; color:#1A3A5C;
               margin-bottom:0.8rem; border-bottom:1px solid #E2E8F0;
               padding-bottom:0.5rem; }
label { font-weight:500 !important; color:#1A3A5C !important; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1rem">
        <div style="font-size:2.2rem">📅</div>
        <h2 style="color:#fff!important;font-size:1.2rem;font-weight:700;margin:.25rem 0 0">SHS Scheduler</h2>
        <p style="color:#8FA3BC!important;font-size:.78rem;margin:0">Senior High School</p>
    </div>
    <hr style="border-color:#2D5275;margin:.5rem 0 1rem">
    """, unsafe_allow_html=True)

    page = st.radio("Navigation",
        ["🏠  Dashboard","📋  Schedule","📚  Subjects","👩‍🏫  Teachers","🏫  Sections"],
        label_visibility="collapsed")

    st.markdown("<hr style='border-color:#2D5275;margin:1rem 0 .5rem'>", unsafe_allow_html=True)
    total = sum(len(v) for v in data()["schedule"].values())
    st.markdown(f"""
    <div style='font-size:.75rem;color:#8FA3BC;padding:0 .5rem'>
        <div>📚 {len(data()['subjects'])} subjects</div>
        <div>👩‍🏫 {len(data()['teachers'])} teachers</div>
        <div>🏫 {len(data()['sections'])} sections</div>
        <div>📋 {total} scheduled entries</div>
    </div>""", unsafe_allow_html=True)

# ── Drag-and-Drop Timetable Component ────────────────────────────────────────
def drag_drop_timetable(section, subjects, teachers, schedule_entries):
    """Render an interactive drag-and-drop timetable and return updated entries."""

    days_js    = json.dumps(DAYS)
    periods_js = json.dumps(PERIODS)
    subj_js    = json.dumps(subjects)
    teach_js   = json.dumps(teachers)

    # Build cell map: "Day||Period" -> {subject, teacher}
    cell_map = {}
    for e in schedule_entries:
        cell_map[f"{e['day']}||{e['period']}"] = {
            "subject": e["subject"], "teacher": e["teacher"]
        }
    cell_map_js = json.dumps(cell_map)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', 'Segoe UI', sans-serif; background: #F4F7FB;
          padding: 12px; font-size: 13px; color: #1A2E45; }}

  /* ── Palette ── */
  .sidebar-panel {{ background:#fff; border:1px solid #E2E8F0; border-radius:10px;
                    padding:12px; margin-bottom:10px; }}
  .sidebar-panel h4 {{ font-size:11px; font-weight:700; color:#1A3A5C;
                       text-transform:uppercase; letter-spacing:.05em;
                       margin-bottom:8px; padding-bottom:6px;
                       border-bottom:1px solid #E2E8F0; }}

  /* ── Draggable pills ── */
  .pill {{ display:inline-flex; align-items:center; gap:5px;
           background:#2563A8; color:#fff; border-radius:20px;
           padding:4px 10px; margin:3px; font-size:11px; font-weight:600;
           cursor:grab; user-select:none; transition:opacity .15s,transform .15s;
           white-space:nowrap; }}
  .pill.teacher {{ background:#1D8A6E; }}
  .pill:active {{ opacity:.7; transform:scale(.96); cursor:grabbing; }}
  .pill.dragging {{ opacity:.4; }}

  /* ── Grid ── */
  .grid-wrap {{ overflow-x:auto; }}
  table {{ border-collapse:collapse; width:100%; min-width:640px; }}
  th {{ background:#1A3A5C; color:#fff; padding:8px 10px; text-align:center;
        font-size:12px; font-weight:600; white-space:nowrap; }}
  th.period-head {{ background:#2563A8; min-width:100px; }}
  td {{ border:1px solid #D6E8FA; vertical-align:middle;
        text-align:center; padding:4px; min-width:130px; height:62px; }}
  td.period-cell {{ background:#D6E8FA; color:#1A3A5C; font-weight:600;
                    font-size:11px; white-space:nowrap; padding:6px 10px;
                    min-width:100px; }}

  /* ── Drop target ── */
  .drop-cell {{ background:#F4F7FB; position:relative; transition:background .15s; }}
  .drop-cell.drag-over {{ background:#E0EFFF; outline:2px dashed #2563A8; }}

  /* ── Cell card (filled slot) ── */
  .cell-card {{ background:#2563A8; color:#fff; border-radius:7px;
                padding:5px 7px; font-size:11px; font-weight:600;
                position:relative; cursor:default; line-height:1.3; }}
  .cell-card .teacher-line {{ font-size:10px; font-weight:400; opacity:.85; margin-top:1px; }}
  .cell-card .remove-btn {{ position:absolute; top:3px; right:4px;
                            background:rgba(255,255,255,.25); border:none; color:#fff;
                            border-radius:50%; width:16px; height:16px; font-size:10px;
                            cursor:pointer; line-height:1; display:flex;
                            align-items:center; justify-content:center; }}
  .cell-card .remove-btn:hover {{ background:rgba(255,255,255,.5); }}

  /* ── Conflict flash ── */
  @keyframes flash-red {{ 0%,100%{{background:#FEE2E2}} 50%{{background:#FECACA}} }}
  .conflict {{ animation: flash-red .4s ease 2; }}

  /* ── Inline editor ── */
  .edit-overlay {{ position:absolute; top:0; left:0; width:100%; z-index:99;
                   background:#fff; border:2px solid #2563A8; border-radius:8px;
                   padding:7px; box-shadow:0 4px 16px rgba(0,0,0,.18); }}
  .edit-overlay select {{ width:100%; margin-bottom:4px; border:1px solid #D6E8FA;
                          border-radius:5px; padding:3px 5px; font-size:11px;
                          color:#1A2E45; background:#F4F7FB; }}
  .edit-overlay .btn-row {{ display:flex; gap:4px; margin-top:4px; }}
  .edit-overlay button {{ flex:1; padding:4px; border:none; border-radius:5px;
                          font-size:11px; font-weight:600; cursor:pointer; }}
  .btn-save {{ background:#2563A8; color:#fff; }}
  .btn-cancel {{ background:#E2E8F0; color:#1A2E45; }}

  /* ── Save bar ── */
  #save-bar {{ position:fixed; bottom:16px; right:16px; z-index:200;
               background:#1D8A6E; color:#fff; border:none; border-radius:8px;
               padding:9px 20px; font-size:13px; font-weight:700; cursor:pointer;
               box-shadow:0 4px 12px rgba(0,0,0,.2); transition:background .15s; }}
  #save-bar:hover {{ background:#155e4e; }}
  #save-bar.saved {{ background:#374151; }}

  /* ── Layout ── */
  .layout {{ display:grid; grid-template-columns:160px 1fr; gap:12px; }}
  @media(max-width:680px) {{ .layout {{ grid-template-columns:1fr; }} }}
  .left-panel {{ display:flex; flex-direction:column; gap:0; }}

  /* ── Instructions ── */
  .hint {{ font-size:10px; color:#8FA3BC; margin-top:4px; line-height:1.4; }}
</style>
</head>
<body>

<div class="layout">
  <!-- Left: draggable palette -->
  <div class="left-panel">
    <div class="sidebar-panel">
      <h4>📚 Subjects</h4>
      <div id="subj-pool"></div>
      <p class="hint">Drag a subject onto a cell</p>
    </div>
    <div class="sidebar-panel">
      <h4>👩‍🏫 Teachers</h4>
      <div id="teach-pool"></div>
      <p class="hint">Drag a teacher onto a filled cell to assign</p>
    </div>
    <div class="sidebar-panel">
      <h4>⏰ Period helper</h4>
      <div id="period-pool"></div>
      <p class="hint">Drag a period pill to swap a row's time slot</p>
    </div>
  </div>

  <!-- Right: timetable -->
  <div>
    <div class="grid-wrap">
      <table id="tt"></table>
    </div>
  </div>
</div>

<button id="save-bar" onclick="saveSchedule()">💾 Save Schedule</button>

<script>
const DAYS    = {days_js};
const PERIODS = {periods_js};
const SUBJECTS  = {subj_js};
const TEACHERS  = {teach_js};
let cellMap = {cell_map_js};   // "Day||Period" -> {{subject, teacher}}

// ── Build palette ─────────────────────────────────────────────────────────
function makePill(text, type, extra) {{
  const p = document.createElement('span');
  p.className = 'pill' + (type === 'teacher' ? ' teacher' : '');
  p.textContent = text;
  p.draggable = true;
  p.dataset.type  = type;
  p.dataset.value = text;
  if (extra) p.dataset.extra = extra;
  p.addEventListener('dragstart', onDragStart);
  p.addEventListener('dragend',   onDragEnd);
  return p;
}}

const subjPool  = document.getElementById('subj-pool');
const teachPool = document.getElementById('teach-pool');
const perPool   = document.getElementById('period-pool');

SUBJECTS.forEach(s  => subjPool.appendChild(makePill(s,  'subject')));
TEACHERS.forEach(t  => teachPool.appendChild(makePill(t, 'teacher')));
PERIODS.forEach(p   => perPool.appendChild(makePill(p,   'period')));

// ── Build table ───────────────────────────────────────────────────────────
function buildTable() {{
  const tt = document.getElementById('tt');
  tt.innerHTML = '';

  // Header row
  const hrow = tt.insertRow();
  const htop = document.createElement('th');
  htop.className = 'period-head';
  htop.textContent = 'Period';
  hrow.appendChild(htop);
  DAYS.forEach(d => {{
    const th = document.createElement('th');
    th.textContent = d;
    hrow.appendChild(th);
  }});

  // Data rows
  PERIODS.forEach(period => {{
    const row = tt.insertRow();

    // Period label cell (draggable to swap)
    const ptd = document.createElement('td');
    ptd.className = 'period-cell';
    ptd.dataset.period = period;
    ptd.innerHTML = `<span class="pill" style="background:#1A3A5C;cursor:grab"
      draggable="true"
      ondragstart="onPeriodDragStart(event,'${{period}}')"
      ondragend="onDragEnd(event)">${{period}}</span>`;
    row.appendChild(ptd);

    DAYS.forEach(day => {{
      const key = `${{day}}||${{period}}`;
      const td = document.createElement('td');
      td.className = 'drop-cell';
      td.dataset.day    = day;
      td.dataset.period = period;
      td.addEventListener('dragover',  onDragOver);
      td.addEventListener('dragleave', onDragLeave);
      td.addEventListener('drop',      onDrop);
      renderCell(td, key);
      row.appendChild(td);
    }});
  }});
}}

function renderCell(td, key) {{
  td.innerHTML = '';
  const entry = cellMap[key];
  if (!entry) return;

  const card = document.createElement('div');
  card.className = 'cell-card';
  card.innerHTML = `
    <div>${{entry.subject}}</div>
    <div class="teacher-line">${{entry.teacher || '<em style="opacity:.6">no teacher</em>'}}</div>
    <button class="remove-btn" onclick="removeCell('${{key}}')" title="Remove">✕</button>`;

  // Make card draggable for moving
  card.draggable = true;
  card.dataset.type  = 'move';
  card.dataset.value = key;
  card.addEventListener('dragstart', onDragStart);
  card.addEventListener('dragend',   onDragEnd);
  td.appendChild(card);
}}

// ── Drag state ────────────────────────────────────────────────────────────
let dragData = null;

function onDragStart(e) {{
  dragData = {{ type: e.currentTarget.dataset.type,
                value: e.currentTarget.dataset.value }};
  e.currentTarget.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'copy';
}}
function onDragEnd(e) {{
  e.currentTarget.classList.remove('dragging');
}}
function onPeriodDragStart(e, period) {{
  dragData = {{ type: 'period', value: period }};
  e.dataTransfer.effectAllowed = 'move';
}}

function onDragOver(e) {{
  e.preventDefault();
  e.currentTarget.classList.add('drag-over');
  e.dataTransfer.dropEffect = 'copy';
}}
function onDragLeave(e) {{
  e.currentTarget.classList.remove('drag-over');
}}

function onDrop(e) {{
  e.preventDefault();
  const td = e.currentTarget;
  td.classList.remove('drag-over');
  if (!dragData) return;

  const targetDay    = td.dataset.day;
  const targetPeriod = td.dataset.period;
  const targetKey    = `${{targetDay}}||${{targetPeriod}}`;

  if (dragData.type === 'subject') {{
    // Set or overwrite subject; keep existing teacher if any
    const existing = cellMap[targetKey] || {{}};
    cellMap[targetKey] = {{ subject: dragData.value,
                            teacher: existing.teacher || '' }};
    flashUpdated(td);
  }}
  else if (dragData.type === 'teacher') {{
    // Assign teacher only if cell has a subject
    if (!cellMap[targetKey]) {{
      td.classList.add('conflict');
      setTimeout(() => td.classList.remove('conflict'), 800);
      return;
    }}
    cellMap[targetKey].teacher = dragData.value;
    flashUpdated(td);
  }}
  else if (dragData.type === 'move') {{
    // Move existing entry to new slot
    const srcKey = dragData.value;
    if (srcKey === targetKey) return;
    if (cellMap[targetKey]) {{
      // Swap
      const tmp = cellMap[targetKey];
      cellMap[targetKey] = cellMap[srcKey];
      cellMap[srcKey] = tmp;
      refreshCell(srcKey);
    }} else {{
      cellMap[targetKey] = cellMap[srcKey];
      delete cellMap[srcKey];
      refreshCell(srcKey);
    }}
    flashUpdated(td);
  }}
  else if (dragData.type === 'period') {{
    // Swap entire period row with target row
    const srcPeriod = dragData.value;
    if (srcPeriod === targetPeriod) return;
    DAYS.forEach(day => {{
      const k1 = `${{day}}||${{srcPeriod}}`;
      const k2 = `${{day}}||${{targetPeriod}}`;
      const tmp = cellMap[k1];
      if (cellMap[k2]) cellMap[k1] = cellMap[k2]; else delete cellMap[k1];
      if (tmp) cellMap[k2] = tmp; else delete cellMap[k2];
    }});
    buildTable();
    return;
  }}

  renderCell(td, targetKey);
  markUnsaved();
}}

function refreshCell(key) {{
  const [day, period] = key.split('||');
  const td = document.querySelector(`td[data-day="${{day}}"][data-period="${{period}}"]`);
  if (td) renderCell(td, key);
}}

function removeCell(key) {{
  delete cellMap[key];
  const [day, period] = key.split('||');
  const td = document.querySelector(`td[data-day="${{day}}"][data-period="${{period}}"]`);
  if (td) renderCell(td, key);
  markUnsaved();
}}

function flashUpdated(td) {{
  td.style.transition = 'background .1s';
  td.style.background = '#BFDBFE';
  setTimeout(() => td.style.background = '', 400);
  markUnsaved();
}}

// ── Save ──────────────────────────────────────────────────────────────────
let unsaved = false;
function markUnsaved() {{
  unsaved = true;
  const btn = document.getElementById('save-bar');
  btn.textContent = '💾 Save Schedule';
  btn.classList.remove('saved');
}}

function saveSchedule() {{
  // Convert cellMap to array of entries
  const entries = Object.entries(cellMap)
    .filter(([k, v]) => v && v.subject)
    .map(([k, v]) => {{
      const [day, period] = k.split('||');
      return {{ day, period, subject: v.subject, teacher: v.teacher || '' }};
    }});

  // Send to Streamlit via query param trick (works with st.query_params)
  const payload = JSON.stringify(entries);
  window.parent.postMessage({{
    type: 'shs_schedule_save',
    section: '{section}',
    entries: payload
  }}, '*');

  const btn = document.getElementById('save-bar');
  btn.textContent = '✅ Saved!';
  btn.classList.add('saved');
  unsaved = false;
  setTimeout(() => {{ btn.textContent = '💾 Save Schedule'; }}, 2000);
}}

buildTable();
</script>
</body>
</html>
"""
    return html


# ── DASHBOARD ─────────────────────────────────────────────────────────────────
if page == "🏠  Dashboard":
    st.markdown("## 🏠 Dashboard")
    st.caption("Overview of your schedule setup")

    c1, c2, c3, c4 = st.columns(4)
    total_entries = sum(len(v) for v in data()["schedule"].values())
    for col, icon, label, val, color in [
        (c1,"📚","Subjects",  len(data()["subjects"]), "#2563A8"),
        (c2,"👩‍🏫","Teachers", len(data()["teachers"]), "#4A90D9"),
        (c3,"🏫","Sections",  len(data()["sections"]), "#1D8A6E"),
        (c4,"📋","Scheduled", total_entries,            "#1A3A5C"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.6rem">{icon}</div>
            <div class="mv" style="color:{color}">{val}</div>
            <div class="ml">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent entries table
    st.markdown('<div class="panel-card"><div class="panel-title">🕒 Recent Schedule Entries</div>',
                unsafe_allow_html=True)
    rows = []
    for sec, entries in data()["schedule"].items():
        for e in entries:
            rows.append({"Section": sec, "Day": e.get("day",""),
                         "Period": e.get("period",""), "Subject": e.get("subject",""),
                         "Teacher": e.get("teacher","")})
    if rows:
        st.dataframe(pd.DataFrame(rows[-25:]), use_container_width=True, hide_index=True)
    else:
        st.caption("No schedule entries yet. Go to Schedule to add some.")
    st.markdown('</div>', unsafe_allow_html=True)


# ── SCHEDULE ──────────────────────────────────────────────────────────────────
elif page == "📋  Schedule":
    st.markdown("## 📋 Schedule")
    st.caption("Drag subjects and teachers onto the timetable grid")

    if not data()["sections"]:
        st.warning("No sections found — add sections first.")
    elif not data()["subjects"]:
        st.warning("No subjects found — add subjects first.")
    else:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            selected_sec = st.selectbox("Select section", data()["sections"], key="tt_sec")
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑 Clear All Entries"):
                if selected_sec in data()["schedule"]:
                    del data()["schedule"][selected_sec]
                    persist()
                    st.rerun()

        entries = data()["schedule"].get(selected_sec, [])

        # Check for incoming saved data from JS postMessage via query params
        qp = st.query_params
        if "save_section" in qp and "save_data" in qp:
            save_sec = qp["save_section"]
            try:
                new_entries = json.loads(qp["save_data"])
                full = [dict(e, section=save_sec) for e in new_entries]
                data()["schedule"][save_sec] = full
                persist()
                st.query_params.clear()
                st.success(f"Schedule for {save_sec} saved — {len(full)} entries.")
                st.rerun()
            except Exception:
                pass

        # Render the drag-and-drop timetable
        html = drag_drop_timetable(selected_sec, data()["subjects"],
                                   data()["teachers"], entries)

        st.info("💡 **How to use:** Drag a **subject pill** onto any empty cell. "
                "Then drag a **teacher pill** onto a filled cell to assign. "
                "Drag an existing cell card to move it. Drag a **period pill** to swap entire rows. "
                "Click ✕ to remove. Hit **Save Schedule** when done.", icon=None)

        # Inject a listener bridge so the JS postMessage reaches Streamlit
        st.markdown("""
        <script>
        window.addEventListener('message', function(e) {
            if (e.data && e.data.type === 'shs_schedule_save') {
                const params = new URLSearchParams(window.location.search);
                params.set('save_section', e.data.section);
                params.set('save_data', e.data.entries);
                window.location.search = params.toString();
            }
        });
        </script>
        """, unsafe_allow_html=True)

        components.html(html, height=600, scrolling=True)


# ── SUBJECTS ──────────────────────────────────────────────────────────────────
elif page == "📚  Subjects":
    st.markdown("## 📚 Subjects")
    st.caption("Manage the subject catalog")

    st.markdown('<div class="panel-card"><div class="panel-title">➕ Add New Subject</div>',
                unsafe_allow_html=True)
    s1, s2 = st.columns([4, 1])
    with s1:
        new_sub = st.text_input("Subject name", placeholder="e.g. General Mathematics",
                                label_visibility="collapsed", key="new_sub")
    with s2:
        if st.button("Add Subject"):
            n = new_sub.strip()
            if not n:           st.warning("Enter a subject name.")
            elif n in data()["subjects"]: st.error("Already exists.")
            else:
                data()["subjects"].append(n); persist()
                st.success(f"Added '{n}'"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card"><div class="panel-title">📋 All Subjects</div>',
                unsafe_allow_html=True)
    if data()["subjects"]:
        for i, s in enumerate(data()["subjects"]):
            r1, r2 = st.columns([6, 1])
            r1.markdown(f'<span class="section-badge">{s}</span>', unsafe_allow_html=True)
            with r2:
                if st.button("🗑", key=f"ds{i}"):
                    data()["subjects"].remove(s); persist(); st.rerun()
    else:
        st.caption("No subjects yet.")
    st.markdown('</div>', unsafe_allow_html=True)


# ── TEACHERS ──────────────────────────────────────────────────────────────────
elif page == "👩‍🏫  Teachers":
    st.markdown("## 👩‍🏫 Teachers")
    st.caption("Manage teaching staff")

    st.markdown('<div class="panel-card"><div class="panel-title">➕ Add New Teacher</div>',
                unsafe_allow_html=True)
    t1, t2 = st.columns([4, 1])
    with t1:
        new_tch = st.text_input("Full name", placeholder="e.g. Ma. Santos",
                                label_visibility="collapsed", key="new_tch")
    with t2:
        if st.button("Add Teacher"):
            n = new_tch.strip()
            if not n:            st.warning("Enter a teacher name.")
            elif n in data()["teachers"]: st.error("Already exists.")
            else:
                data()["teachers"].append(n); persist()
                st.success(f"Added '{n}'"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card"><div class="panel-title">📋 All Teachers</div>',
                unsafe_allow_html=True)
    if data()["teachers"]:
        for i, t in enumerate(data()["teachers"]):
            r1, r2 = st.columns([6, 1])
            r1.markdown(f'<span class="section-badge" style="background:#E1F5EE;color:#0F6E56">{t}</span>',
                        unsafe_allow_html=True)
            with r2:
                if st.button("🗑", key=f"dt{i}"):
                    data()["teachers"].remove(t); persist(); st.rerun()
    else:
        st.caption("No teachers yet.")
    st.markdown('</div>', unsafe_allow_html=True)


# ── SECTIONS ──────────────────────────────────────────────────────────────────
elif page == "🏫  Sections":
    st.markdown("## 🏫 Sections")
    st.caption("Manage class sections")

    st.markdown('<div class="panel-card"><div class="panel-title">➕ Add New Section</div>',
                unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1: sec_name   = st.text_input("Section name", placeholder="e.g. Einstein", key="sec_name")
    with sc2: sec_grade  = st.selectbox("Grade level", GRADES, key="sec_grade")
    with sc3: sec_strand = st.selectbox("Strand", STRANDS, key="sec_strand")
    with sc4: st.text_input("Adviser (optional)", key="sec_adv")

    if st.button("Add Section"):
        n = sec_name.strip()
        if not n: st.warning("Section name required.")
        else:
            display = f"{n} ({sec_grade} - {sec_strand})"
            if display in data()["sections"]: st.error("Already exists.")
            else:
                data()["sections"].append(display); persist()
                st.success(f"Added '{display}'"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card"><div class="panel-title">🏫 All Sections</div>',
                unsafe_allow_html=True)
    if data()["sections"]:
        for i, sec in enumerate(data()["sections"]):
            r1, r2 = st.columns([6, 1])
            r1.markdown(f'<span class="section-badge" style="background:#EAF3DE;color:#3B6D11">{sec}</span>',
                        unsafe_allow_html=True)
            with r2:
                if st.button("🗑", key=f"dsec{i}"):
                    data()["sections"].remove(sec)
                    if sec in data()["schedule"]: del data()["schedule"][sec]
                    persist(); st.rerun()
    else:
        st.caption("No sections yet.")
    st.markdown('</div>', unsafe_allow_html=True)
