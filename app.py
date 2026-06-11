import streamlit as st
import streamlit.components.v1 as components
import json, os
from datetime import datetime, timedelta
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
DAYS    = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
STRANDS = ["STEM","ABM","HUMSS","TVL","GAS","SPORTS"]
GRADES  = ["Grade 11","Grade 12"]
DATA_FILE = "shs_schedule_data.json"

DEFAULT_TIME_CFG = {
    "start_time"    : "07:30",
    "class_duration": 60,
    "break_after"   : [3],
    "break_duration": 60,
    "periods_per_day": 8,
}

# ─────────────────────────────────────────────────────────────────────────────
# Data layer
# ─────────────────────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            d = json.load(f)
        # back-compat: migrate old single time_config → per-grade
        if "time_config" in d and "time_configs" not in d:
            d["time_configs"] = {"Grade 11": d.pop("time_config"),
                                 "Grade 12": dict(DEFAULT_TIME_CFG)}
        if "time_configs" not in d:
            d["time_configs"] = {"Grade 11": dict(DEFAULT_TIME_CFG),
                                 "Grade 12": dict(DEFAULT_TIME_CFG)}
        return d
    return {
        "subjects": [], "teachers": [], "sections": [], "schedule": {},
        "time_configs": {
            "Grade 11": dict(DEFAULT_TIME_CFG),
            "Grade 12": dict(DEFAULT_TIME_CFG),
        }
    }

def save_data(d):
    with open(DATA_FILE,"w") as f:
        json.dump(d, f, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

def D():   return st.session_state.data
def persist(): save_data(st.session_state.data)

# ─────────────────────────────────────────────────────────────────────────────
# Period helpers
# ─────────────────────────────────────────────────────────────────────────────
def gen_periods(cfg):
    start   = datetime.strptime(cfg["start_time"], "%H:%M")
    dur     = int(cfg["class_duration"])
    breaks  = cfg.get("break_after", [])
    brk_dur = int(cfg.get("break_duration", 60))
    n       = int(cfg["periods_per_day"])
    labels, cur = [], start
    for i in range(n):
        end = cur + timedelta(minutes=dur)
        s = cur.strftime("%I:%M %p").lstrip("0")
        e = end.strftime("%I:%M %p").lstrip("0")
        labels.append(f"{s} – {e}")
        cur = end + timedelta(minutes=brk_dur) if i in breaks else end
    return labels

def get_periods(grade):
    cfg = D()["time_configs"].get(grade, DEFAULT_TIME_CFG)
    return gen_periods(cfg)

def sections_for(grade):
    return [s for s in D()["sections"] if grade in s]

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="SHS Class Scheduler", page_icon="📅",
                   layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset ── */
*,*::before,*::after{box-sizing:border-box}
html,body,[class*="css"]{
    font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
    -webkit-font-smoothing:antialiased;color:#1E293B}
#MainMenu,footer,header{visibility:hidden}
[data-testid="stDecoration"]{display:none}

/* ══════════════════════════════════════════════
   SIDEBAR — locked, never collapsible
══════════════════════════════════════════════ */
[data-testid="stSidebar"]{
    width:260px!important;min-width:260px!important;max-width:260px!important;
    background:#0F2744!important;
    border-right:1px solid rgba(255,255,255,.05)!important;
    box-shadow:3px 0 20px rgba(0,0,0,.25)!important}
[data-testid="stSidebar"]>div:first-child{width:260px!important;padding:0!important}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[kind="header"]{display:none!important}

/* Sidebar text */
[data-testid="stSidebar"] *{color:#8BAEC8!important}
[data-testid="stSidebarNav"]{display:none}

/* Radio nav */
[data-testid="stSidebar"] [data-testid="stRadio"]>label{display:none}
[data-testid="stSidebar"] [data-testid="stRadio"]>div{
    display:flex;flex-direction:column;gap:2px;padding:0 12px}
[data-testid="stSidebar"] [data-testid="stRadio"]>div>label{
    display:flex!important;align-items:center;padding:11px 14px!important;
    border-radius:10px!important;margin:0!important;cursor:pointer;
    transition:all .15s;font-size:.875rem!important;font-weight:500!important;
    color:#7A9EBA!important;border:none!important;background:transparent!important;
    letter-spacing:.01em}
[data-testid="stSidebar"] [data-testid="stRadio"]>div>label:hover{
    background:rgba(255,255,255,.08)!important;color:#E2EEF8!important}
[data-testid="stSidebar"] [data-testid="stRadio"]>div>label[data-baseweb="radio"] span:first-child{
    display:none!important}
[data-testid="stSidebar"] [data-testid="stRadio"]>div>label[aria-checked="true"]{
    background:linear-gradient(90deg,rgba(59,130,246,.25),rgba(59,130,246,.10))!important;
    color:#FFFFFF!important;font-weight:700!important;
    border-left:3px solid #60A5FA!important;padding-left:11px!important}

/* ══════════════════════════════════════════════
   MAIN AREA
══════════════════════════════════════════════ */
.main .block-container{
    padding:0!important;max-width:100%!important;background:#F1F5FA}
section[data-testid="stMainBlockContainer"]{background:#F1F5FA}

/* ── Top bar ── */
.topbar{
    background:#fff;border-bottom:1px solid #E2EAF3;
    padding:1.1rem 2.2rem;
    display:flex;align-items:center;justify-content:space-between;
    position:sticky;top:0;z-index:50}
.topbar-left h1{font-size:1.45rem;font-weight:800;color:#0F2744;
    letter-spacing:-.025em;margin:0 0 1px}
.topbar-left p{font-size:.8rem;color:#64748B;margin:0;font-weight:400}
.topbar-right{display:flex;gap:8px;align-items:center}
.badge-stat{background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;
    border-radius:20px;padding:4px 12px;font-size:.75rem;font-weight:600}

/* ── Page content ── */
.pcontent{padding:1.8rem 2.2rem}

/* ── Cards ── */
.card{background:#fff;border:1px solid #E2EAF3;border-radius:16px;
    padding:1.4rem 1.6rem;margin-bottom:1rem;
    box-shadow:0 1px 3px rgba(15,39,68,.04),0 4px 12px rgba(15,39,68,.03)}
.card-title{font-size:.82rem;font-weight:700;color:#0F2744;margin-bottom:.9rem;
    padding-bottom:.7rem;border-bottom:1px solid #F1F5FA;
    display:flex;align-items:center;gap:.5rem;text-transform:uppercase;
    letter-spacing:.06em}

/* ── Stat cards ── */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1.4rem}
.scard{background:#fff;border:1px solid #E2EAF3;border-radius:14px;
    padding:1.2rem 1.4rem;display:flex;align-items:center;gap:1rem;
    box-shadow:0 1px 3px rgba(15,39,68,.04);transition:all .2s}
.scard:hover{box-shadow:0 6px 20px rgba(15,39,68,.08);transform:translateY(-2px)}
.scard-icon{width:44px;height:44px;border-radius:11px;display:flex;
    align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0}
.scard-v{font-size:1.9rem;font-weight:800;line-height:1;color:#0F2744}
.scard-l{font-size:.7rem;font-weight:600;color:#94A3B8;text-transform:uppercase;
    letter-spacing:.06em;margin-top:2px}

/* ── Grade switcher tabs ── */
.grade-tabs{display:flex;gap:6px;margin-bottom:1.2rem;
    background:#EFF6FF;border-radius:12px;padding:5px;width:fit-content}
.gtab{padding:8px 24px;border-radius:9px;font-size:.875rem;font-weight:600;
    cursor:pointer;transition:all .18s;border:none;
    background:transparent;color:#3B82F6;letter-spacing:.01em}
.gtab.active{background:#fff;color:#1D4ED8;
    box-shadow:0 2px 8px rgba(29,78,216,.15)}

/* ── Day selector ── */
.day-row{display:flex;gap:6px;margin-bottom:1.2rem;flex-wrap:wrap}
.daybtn{padding:6px 16px;border-radius:8px;font-size:.8rem;font-weight:600;
    cursor:pointer;transition:all .15s;border:1.5px solid #E2EAF3;
    background:#fff;color:#64748B}
.daybtn:hover{border-color:#93C5FD;color:#1D4ED8;background:#EFF6FF}
.daybtn.active{background:#1D4ED8;color:#fff;border-color:#1D4ED8;
    box-shadow:0 2px 8px rgba(29,78,216,.3)}

/* ── Period pills ── */
.ppill{display:inline-flex;align-items:center;background:#EFF6FF;color:#1E40AF;
    border:1px solid #BFDBFE;border-radius:20px;padding:4px 12px;
    font-size:.75rem;font-weight:600;margin:3px 3px 3px 0}
.ppill.brk{background:#FFF7ED;color:#C2410C;border-color:#FED7AA}

/* ── Time config form ── */
.tc-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:.8rem}
.tc-field{background:#F8FAFC;border:1.5px solid #E2EAF3;border-radius:10px;padding:12px 14px}
.tc-field label{display:block;font-size:.68rem;font-weight:700;color:#64748B;
    text-transform:uppercase;letter-spacing:.07em;margin-bottom:6px}
.tc-field input,.tc-field select{width:100%;background:#fff;border:1.5px solid #CBD5E1;
    border-radius:7px;padding:7px 10px;font-size:.875rem;color:#1E293B;
    font-family:'Inter',sans-serif;outline:none;transition:border-color .15s}
.tc-field input:focus,.tc-field select:focus{border-color:#60A5FA;
    box-shadow:0 0 0 3px rgba(96,165,250,.15)}

/* ── Save btn (JS) ── */
.save-btn-wrap{text-align:right;margin-top:10px}
.save-btn{background:#1D4ED8;color:#fff;border:none;border-radius:9px;
    padding:9px 24px;font-family:'Inter',sans-serif;font-size:.875rem;
    font-weight:700;cursor:pointer;box-shadow:0 2px 8px rgba(29,78,216,.3);
    transition:background .15s,transform .1s}
.save-btn:hover{background:#1E40AF;box-shadow:0 4px 14px rgba(30,64,175,.35)}
.save-btn:active{transform:scale(.97)}
.save-btn.saved{background:#059669}

/* ── Item rows ── */
.irow{display:flex;align-items:center;justify-content:space-between;
    padding:10px 16px;border-radius:10px;background:#F8FAFC;
    border:1.5px solid #F1F5F9;margin-bottom:7px;transition:all .15s}
.irow:hover{background:#EFF6FF;border-color:#BFDBFE}
.iname{font-size:.875rem;font-weight:500;color:#1E293B}
.itag{font-size:.68rem;font-weight:700;border-radius:20px;padding:3px 10px;
    letter-spacing:.04em}
.t-blue{background:#DBEAFE;color:#1D4ED8}
.t-green{background:#DCFCE7;color:#166534}
.t-purple{background:#EDE9FE;color:#5B21B6}
.t-orange{background:#FEF3C7;color:#92400E}
.t-indigo{background:#E0E7FF;color:#3730A3}

/* ── Inputs (Streamlit override) ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"]>div>div,
[data-testid="stNumberInput"] input{
    border-radius:9px!important;border:1.5px solid #CBD5E1!important;
    font-size:.875rem!important;color:#1E293B!important;background:#FAFCFF!important;
    transition:border-color .15s,box-shadow .15s!important}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus{
    border-color:#60A5FA!important;box-shadow:0 0 0 3px rgba(96,165,250,.15)!important}
label,.stSelectbox label,.stTextInput label,.stNumberInput label{
    font-size:.72rem!important;font-weight:700!important;color:#475569!important;
    text-transform:uppercase!important;letter-spacing:.06em!important;margin-bottom:4px!important}

/* ── Streamlit buttons ── */
.stButton>button{
    background:#1D4ED8!important;color:#fff!important;border:none!important;
    border-radius:9px!important;font-weight:700!important;font-size:.85rem!important;
    padding:.5rem 1.4rem!important;
    box-shadow:0 2px 8px rgba(29,78,216,.25)!important;
    transition:all .15s!important;letter-spacing:.01em!important}
.stButton>button:hover{background:#1E40AF!important;
    box-shadow:0 4px 14px rgba(30,64,175,.3)!important}
.stButton>button:active{transform:scale(.98)!important}

/* ── Alerts ── */
[data-testid="stInfo"]{border-radius:10px!important;background:#EFF6FF!important;
    border-left:4px solid #3B82F6!important;color:#1E40AF!important}
[data-testid="stSuccess"]{border-radius:10px!important;background:#F0FDF4!important;
    border-left:4px solid #22C55E!important}
[data-testid="stWarning"]{border-radius:10px!important;background:#FFFBEB!important;
    border-left:4px solid #F59E0B!important}
[data-testid="stError"]{border-radius:10px!important;background:#FEF2F2!important;
    border-left:4px solid #EF4444!important}

/* ── Divider ── */
hr{border:none!important;border-top:1px solid #E2EAF3!important;margin:1rem 0!important}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:#F1F5FA}
::-webkit-scrollbar-thumb{background:#CBD5E1;border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#94A3B8}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:2rem 1.5rem 1.2rem;border-bottom:1px solid rgba(255,255,255,.07)">
        <div style="display:flex;align-items:center;gap:12px">
            <div style="width:42px;height:42px;background:linear-gradient(135deg,#3B82F6,#1D4ED8);
                        border-radius:11px;display:flex;align-items:center;justify-content:center;
                        font-size:1.3rem;flex-shrink:0;box-shadow:0 4px 12px rgba(59,130,246,.4)">📅</div>
            <div>
                <div style="font-size:1rem;font-weight:800;color:#fff!important;
                            letter-spacing:-.02em;line-height:1.2">SHS Scheduler</div>
                <div style="font-size:.7rem;color:#5A7A9A!important;margin-top:1px">
                    Senior High School</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:.9rem 1.5rem .3rem;font-size:.65rem;font-weight:800;
                color:#334D66!important;text-transform:uppercase;letter-spacing:.1em">
        Main Menu</div>""", unsafe_allow_html=True)

    page = st.radio("nav", [
        "🏠  Dashboard",
        "📋  Schedule",
        "📚  Subjects",
        "👩‍🏫  Teachers",
        "🏫  Sections",
    ], label_visibility="collapsed")

    # Bottom stats
    total = sum(len(v) for v in D()["schedule"].values())
    g11_cfg = D()["time_configs"].get("Grade 11",{}).get("start_time","—")
    g12_cfg = D()["time_configs"].get("Grade 12",{}).get("start_time","—")
    st.markdown(f"""
    <div style="position:absolute;bottom:0;left:0;right:0;
                padding:.9rem 1.5rem 1.5rem;
                border-top:1px solid rgba(255,255,255,.06);
                background:rgba(0,0,0,.18)">
        <div style="font-size:.62rem;font-weight:800;color:#334D66!important;
                    text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem">
            Overview</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px">
            {"".join(f'''<div style="background:rgba(255,255,255,.05);border-radius:8px;
                padding:7px 10px;border:1px solid rgba(255,255,255,.06)">
                <div style="font-size:1.05rem;font-weight:800;color:#fff!important">{v}</div>
                <div style="font-size:.62rem;color:#5A7A9A!important;margin-top:1px">{l}</div>
            </div>''' for v,l in [
                (len(D()["subjects"]),"Subjects"),
                (len(D()["teachers"]),"Teachers"),
                (len(D()["sections"]),"Sections"),
                (total,"Entries")])}
        </div>
        <div style="margin-top:8px;display:flex;flex-direction:column;gap:3px">
            <div style="font-size:.68rem;color:#5A8AAA!important">
                ⏰ G11 starts {g11_cfg} · G12 starts {g12_cfg}</div>
        </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Helper: page top bar
# ─────────────────────────────────────────────────────────────────────────────
def topbar(title, subtitle, badges=None):
    bdg = ""
    if badges:
        bdg = "".join(f'<span class="badge-stat">{b}</span>' for b in badges)
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-left">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        <div class="topbar-right">{bdg}</div>
    </div>
    <div class="pcontent">""", unsafe_allow_html=True)

def close_content():
    st.markdown("</div>", unsafe_allow_html=True)

def card(title=""):
    t = f'<div class="card-title">{title}</div>' if title else ""
    st.markdown(f'<div class="card">{t}', unsafe_allow_html=True)

def end_card():
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Timetable HTML (combined read-only — all sections for a grade × day)
# ─────────────────────────────────────────────────────────────────────────────
def combined_timetable_html(grade, day, periods):
    secs = sections_for(grade)
    if not secs:
        return "<p style='color:#94A3B8;padding:1rem'>No sections for this grade.</p>"

    def short(s):
        name = s.split("(")[0].strip()
        return name[:14] + "…" if len(name) > 14 else name

    col_w = min(160, max(110, 740 // max(len(secs),1)))
    html = [f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Inter',sans-serif;background:#F1F5FA;
          padding:14px;font-size:12px;color:#1E293B}}
    .wrap{{overflow-x:auto;border-radius:14px;
           box-shadow:0 2px 12px rgba(15,39,68,.08);border:1px solid #E2EAF3}}
    table{{border-collapse:collapse;min-width:{110+col_w*len(secs)}px;width:100%}}
    thead th{{padding:11px 10px;text-align:center;font-size:10.5px;font-weight:700;
               letter-spacing:.04em;white-space:nowrap}}
    .corner{{background:#0F2744;color:#fff;min-width:110px;
              border-right:2px solid rgba(255,255,255,.1)}}
    .sh{{background:linear-gradient(135deg,#1D4ED8,#2563EB);color:#fff;
          min-width:{col_w}px;border-right:1px solid rgba(255,255,255,.15)}}
    td{{border:1px solid #E8EFF7;vertical-align:middle;text-align:center;
         padding:5px;height:68px}}
    td.pl{{background:linear-gradient(135deg,#EFF6FF,#DBEAFE);color:#1E3A5F;
            font-weight:700;font-size:10.5px;white-space:nowrap;padding:8px 12px;
            min-width:110px;border-right:2px solid #BFDBFE;text-align:left}}
    td.pl .pnum{{font-size:9px;font-weight:600;color:#60A5FA;display:block;margin-bottom:2px}}
    td.pl .ptime{{font-size:10px;font-weight:700;color:#1E3A5F}}
    tr:nth-child(even) td:not(.pl){{background:#F8FAFC}}
    .cc{{background:linear-gradient(145deg,#1D4ED8 0%,#3B82F6 100%);
          color:#fff;border-radius:9px;padding:7px 9px;
          font-size:10.5px;font-weight:600;line-height:1.4;
          box-shadow:0 2px 8px rgba(29,78,216,.28);margin:2px}}
    .cc .s{{font-weight:700;font-size:11px;margin-bottom:3px;
             display:flex;align-items:center;gap:4px}}
    .cc .t{{font-size:9.5px;opacity:.88;display:flex;align-items:center;gap:3px}}
    .cc .nt{{font-size:9px;opacity:.5;font-style:italic}}
    .emp{{color:#CBD5E1;font-size:22px;line-height:1}}
    </style>
    <div class="wrap"><table><thead><tr>
    <th class="corner">Period · {day}</th>"""]

    for s in secs:
        html.append(f'<th class="sh">{short(s)}</th>')
    html.append("</tr></thead><tbody>")

    for i, per in enumerate(periods):
        parts = per.split("–")
        start_t = parts[0].strip() if parts else per
        html.append(f"""<tr><td class="pl">
            <span class="pnum">Period {i+1}</span>
            <span class="ptime">{per}</span></td>""")
        for sec in secs:
            ents = D()["schedule"].get(sec, [])
            e = next((x for x in ents if x.get("day")==day and x.get("period")==per), None)
            if e:
                tch = f'<div class="t">👩‍🏫 {e["teacher"]}</div>' if e.get("teacher") \
                      else '<div class="nt">No teacher assigned</div>'
                html.append(f'<td><div class="cc"><div class="s">📚 {e["subject"]}</div>{tch}</div></td>')
            else:
                html.append('<td><span class="emp">·</span></td>')
        html.append("</tr>")

    html.append("</tbody></table></div>")
    return "".join(html)

# ─────────────────────────────────────────────────────────────────────────────
# Drag-and-drop editor HTML (single section × day)
# ─────────────────────────────────────────────────────────────────────────────
def dnd_editor_html(section, day, subjects, teachers, periods, schedule):
    sec_ents = [e for e in schedule.get(section,[]) if e.get("day")==day]
    cm = {e["period"]:{"subject":e["subject"],"teacher":e.get("teacher","")} for e in sec_ents}

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',sans-serif;background:#F1F5FA;padding:14px;
      font-size:13px;color:#1E293B}}

/* layout */
.layout{{display:grid;grid-template-columns:170px 1fr;gap:12px;align-items:start}}

/* palette */
.pal{{background:#fff;border:1.5px solid #E2EAF3;border-radius:12px;padding:12px;
      margin-bottom:10px;box-shadow:0 1px 4px rgba(15,39,68,.04)}}
.pal h4{{font-size:9px;font-weight:800;color:#475569;text-transform:uppercase;
          letter-spacing:.1em;margin-bottom:8px;padding-bottom:6px;
          border-bottom:1.5px solid #F1F5F9}}
.hint{{font-size:9px;color:#94A3B8;margin-top:5px;line-height:1.4}}

/* pills */
.pill{{display:inline-flex;align-items:center;border-radius:20px;
       padding:4px 11px;margin:2px;font-size:10.5px;font-weight:700;
       cursor:grab;user-select:none;white-space:nowrap;
       transition:opacity .15s,transform .15s,box-shadow .15s}}
.subj-pill{{background:#1D4ED8;color:#fff;box-shadow:0 1px 5px rgba(29,78,216,.3)}}
.tch-pill{{background:#059669;color:#fff;box-shadow:0 1px 5px rgba(5,150,105,.3)}}
.pill:hover{{opacity:.9;transform:translateY(-1px);
             box-shadow:0 3px 10px rgba(0,0,0,.2)!important}}
.pill:active{{opacity:.6;transform:scale(.94);cursor:grabbing}}
.pill.dragging{{opacity:.25;box-shadow:none!important}}

/* timetable */
.tt-wrap{{background:#fff;border:1.5px solid #E2EAF3;border-radius:12px;
          overflow:hidden;box-shadow:0 2px 10px rgba(15,39,68,.06)}}
table{{border-collapse:collapse;width:100%}}
thead th{{padding:11px 8px;text-align:center;font-size:10.5px;font-weight:800;
           white-space:nowrap;letter-spacing:.04em}}
th.cr{{background:#0F2744;color:#fff;min-width:105px;font-size:10px;
        border-right:1px solid rgba(255,255,255,.1)}}
th.dh{{background:linear-gradient(135deg,#1D4ED8,#3B82F6);color:#fff;width:100%}}
td{{border:1px solid #EEF2F7;vertical-align:middle;text-align:center;
    padding:5px;height:68px}}
td.pl{{background:linear-gradient(135deg,#EFF6FF,#DBEAFE);color:#1E3A5F;
        font-weight:700;font-size:10px;padding:7px 10px;
        min-width:105px;border-right:2px solid #BFDBFE;text-align:left;
        white-space:nowrap}}
td.pl .pn{{font-size:8.5px;font-weight:700;color:#60A5FA;display:block;margin-bottom:1px}}
td.pl .pt{{font-size:9.5px;font-weight:700;color:#1E3A5F}}
.drop-cell{{background:#FAFBFF;position:relative;transition:background .12s;
             min-width:200px}}
.drop-cell.drag-over{{background:#EFF6FF!important;
    outline:2px dashed #3B82F6;outline-offset:-2px}}
tr:nth-child(even) td.drop-cell{{background:#F8FAFC}}

/* empty hint */
.emp{{color:#CBD5E1;font-size:24px;user-select:none}}

/* cell card */
.cc{{background:linear-gradient(145deg,#1D4ED8,#3B82F6);color:#fff;
     border-radius:9px;padding:7px 9px;font-size:10.5px;font-weight:600;
     position:relative;cursor:grab;line-height:1.4;
     box-shadow:0 2px 8px rgba(29,78,216,.3);
     transition:box-shadow .15s,transform .15s;margin:2px}}
.cc:hover{{box-shadow:0 5px 14px rgba(29,78,216,.4);transform:translateY(-1px)}}
.cc .sub{{font-size:11px;font-weight:800;margin-bottom:3px;
           display:flex;align-items:center;gap:4px}}
.cc .tch{{font-size:9.5px;opacity:.9;display:flex;align-items:center;gap:3px}}
.cc .nt{{font-size:9px;opacity:.5;font-style:italic}}
.cc .rm{{position:absolute;top:4px;right:5px;background:rgba(255,255,255,.22);
          border:none;color:#fff;border-radius:50%;width:16px;height:16px;
          font-size:9px;cursor:pointer;display:flex;align-items:center;
          justify-content:center;transition:background .12s;line-height:1}}
.cc .rm:hover{{background:rgba(255,255,255,.5)}}

/* conflict */
@keyframes fR{{0%,100%{{background:#FEF2F2}}50%{{background:#FECACA}}}}
.conflict{{animation:fR .3s ease 2;border-radius:9px}}

/* save bar */
#sb{{position:fixed;bottom:18px;right:18px;z-index:9999;
     background:linear-gradient(135deg,#1D4ED8,#2563EB);color:#fff;
     border:none;border-radius:11px;padding:11px 26px;
     font-family:'Inter',sans-serif;font-size:13px;font-weight:800;
     cursor:pointer;box-shadow:0 4px 18px rgba(29,78,216,.4);
     transition:all .15s;letter-spacing:.01em}}
#sb:hover{{background:linear-gradient(135deg,#1E40AF,#1D4ED8);
           box-shadow:0 6px 24px rgba(30,64,175,.45);transform:translateY(-1px)}}
#sb:active{{transform:scale(.97)}}
#sb.saved{{background:linear-gradient(135deg,#059669,#10B981)}}

/* legend */
.legend{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:11px;padding:8px 12px;
          background:#fff;border-radius:10px;border:1.5px solid #E2EAF3;
          font-size:9.5px;font-weight:600;color:#475569;align-items:center}}
.ld{{display:flex;align-items:center;gap:4px}}
.ldot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
</style></head><body>

<div class="legend">
  <span class="ld"><span class="ldot" style="background:#1D4ED8"></span>Subject</span>
  <span class="ld"><span class="ldot" style="background:#059669"></span>Teacher</span>
  <span class="ld"><span class="ldot" style="background:#E2EAF3;border:1px solid #CBD5E1"></span>Empty</span>
  <span style="color:#94A3B8">|</span>
  <span>🔵 Drag subject → empty cell</span>
  <span>🟢 Drag teacher → filled cell</span>
  <span>↔ Drag card to move/swap</span>
  <span>✕ Click to clear</span>
</div>

<div class="layout">
  <!-- Palette -->
  <div>
    <div class="pal">
      <h4>📚 Subjects</h4>
      <div id="sp"></div>
      <p class="hint">Drop onto any empty period slot</p>
    </div>
    <div class="pal">
      <h4>👩‍🏫 Teachers</h4>
      <div id="tp"></div>
      <p class="hint">Drop onto a slot that already has a subject</p>
    </div>
  </div>

  <!-- Table -->
  <div class="tt-wrap">
    <table>
      <thead><tr>
        <th class="cr">Period</th>
        <th class="dh">{day} · {section.split("(")[0].strip()}</th>
      </tr></thead>
      <tbody id="tb"></tbody>
    </table>
  </div>
</div>

<button id="sb" onclick="save()">💾 Save Schedule</button>

<script>
const SUBJ={json.dumps(subjects)};
const TCHE={json.dumps(teachers)};
const PERS={json.dumps(periods)};
const SEC="{section}",DAY="{day}";
let cm={json.dumps(cm)};

// Build palette
document.getElementById('sp').append(...SUBJ.map(s=>mkPill(s,'s')));
document.getElementById('tp').append(...TCHE.map(t=>mkPill(t,'t')));

function mkPill(txt,type){{
  const p=document.createElement('span');
  p.className='pill '+(type==='s'?'subj-pill':'tch-pill');
  p.textContent=txt;p.draggable=true;
  p.dataset.type=type;p.dataset.val=txt;
  p.addEventListener('dragstart',dStart);
  p.addEventListener('dragend',  dEnd);
  return p;
}}

let drag=null;
function dStart(e){{
  drag={{type:e.currentTarget.dataset.type,val:e.currentTarget.dataset.val}};
  setTimeout(()=>e.currentTarget.classList.add('dragging'),0);
  e.dataTransfer.effectAllowed='copyMove';
}}
function dEnd(e){{e.currentTarget.classList.remove('dragging');}}

// Build table rows
function buildTable(){{
  const tb=document.getElementById('tb');
  tb.innerHTML='';
  PERS.forEach((per,i)=>{{
    const tr=tb.insertRow();
    // Period label
    const pl=tr.insertCell();
    pl.className='pl';
    pl.innerHTML=`<span class="pn">Period ${{i+1}}</span><span class="pt">${{per}}</span>`;
    // Drop cell
    const dc=tr.insertCell();
    dc.className='drop-cell';
    dc.dataset.per=per;
    dc.addEventListener('dragover', dOver);
    dc.addEventListener('dragleave',dLeave);
    dc.addEventListener('drop',     dDrop);
    render(dc,per);
  }});
}}

function render(td,per){{
  td.innerHTML='';
  const e=cm[per];
  if(!e){{td.innerHTML='<span class="emp">·</span>';return;}}
  const c=document.createElement('div');
  c.className='cc';c.draggable=true;
  c.dataset.type='mv';c.dataset.val=per;
  c.addEventListener('dragstart',dStart);
  c.addEventListener('dragend',  dEnd);
  const tl=e.teacher?`<div class="tch">👩‍🏫 ${{e.teacher}}</div>`
                     :`<div class="nt">No teacher assigned</div>`;
  c.innerHTML=`<button class="rm" onclick="rm('${{per}}')" title="Clear">✕</button>
    <div class="sub">📚 ${{e.subject}}</div>${{tl}}`;
  td.appendChild(c);
}}

function ref(per){{
  const td=document.querySelector(`td[data-per="${{per}}"]`);
  if(td) render(td,per);
}}

function dOver(e){{e.preventDefault();e.currentTarget.classList.add('drag-over');}}
function dLeave(e){{e.currentTarget.classList.remove('drag-over');}}

function dDrop(e){{
  e.preventDefault();
  const td=e.currentTarget;td.classList.remove('drag-over');
  if(!drag)return;
  const per=td.dataset.per;

  if(drag.type==='s'){{
    const ex=cm[per]||{{}};
    cm[per]={{subject:drag.val,teacher:ex.teacher||''}};
  }} else if(drag.type==='t'){{
    if(!cm[per]){{
      td.classList.add('conflict');
      setTimeout(()=>td.classList.remove('conflict'),700);
      return;
    }}
    cm[per].teacher=drag.val;
  }} else if(drag.type==='mv'){{
    const src=drag.val;
    if(src===per)return;
    if(cm[per]){{const tmp=cm[per];cm[per]=cm[src];cm[src]=tmp;ref(src);}}
    else{{cm[per]=cm[src];delete cm[src];ref(src);}}
  }}
  render(td,per);mark();
}}

function rm(per){{delete cm[per];ref(per);mark();}}

let unsaved=false;
function mark(){{
  unsaved=true;
  const b=document.getElementById('sb');
  b.textContent='💾 Save Schedule';b.classList.remove('saved');
}}

function save(){{
  const ents=Object.entries(cm)
    .filter(([k,v])=>v&&v.subject)
    .map(([per,v])=>{{return{{day:DAY,period:per,subject:v.subject,teacher:v.teacher||''}};
    }});
  window.parent.postMessage({{
    type:'shs_save',section:SEC,entries:JSON.stringify(ents)
  }},'*');
  const b=document.getElementById('sb');
  b.textContent='✅ Saved!';b.classList.add('saved');
  unsaved=false;
  setTimeout(()=>{{b.textContent='💾 Save Schedule';b.classList.remove('saved');}},2500);
}}

buildTable();
</script></body></html>"""

# ─────────────────────────────────────────────────────────────────────────────
# Time config widget (inline, inside Schedule page)
# ─────────────────────────────────────────────────────────────────────────────
def render_time_config(grade):
    cfg = D()["time_configs"].get(grade, dict(DEFAULT_TIME_CFG))
    key = grade.replace(" ","")

    with st.expander(f"⚙️ Time Configuration — {grade}", expanded=False):
        st.markdown(f"""
        <div style="background:#F8FAFC;border-radius:10px;padding:12px 14px;
                    margin-bottom:.8rem;border:1.5px solid #E2EAF3">
            <div style="font-size:.75rem;font-weight:700;color:#475569;
                        text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">
                ℹ️ About Time Setup</div>
            <div style="font-size:.8rem;color:#64748B;line-height:1.5">
                Configure when <b>{grade}</b> classes start, how long each period lasts,
                and when breaks occur. Changing this will clear the saved schedule for
                this grade to prevent period mismatches.</div>
        </div>""", unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns(4)
        with c1:
            start = st.text_input("Start Time (HH:MM)",
                value=cfg.get("start_time","07:30"),
                key=f"ts_start_{key}", help="24-hour format e.g. 07:30")
        with c2:
            dur = st.number_input("Class Duration (min)",
                min_value=30, max_value=180,
                value=int(cfg.get("class_duration",60)),
                step=5, key=f"ts_dur_{key}")
        with c3:
            n_per = st.number_input("Periods per Day",
                min_value=1, max_value=12,
                value=int(cfg.get("periods_per_day",8)),
                step=1, key=f"ts_np_{key}")
        with c4:
            brk_dur = st.number_input("Break Duration (min)",
                min_value=0, max_value=120,
                value=int(cfg.get("break_duration",60)),
                step=5, key=f"ts_bd_{key}")

        brk_raw = st.text_input(
            "Break after period(s) — comma separated, 1-based (e.g. 4 means after Period 4)",
            value=", ".join(str(x+1) for x in cfg.get("break_after",[])),
            key=f"ts_baft_{key}",
            help="Leave blank for no break")

        # Parse & validate
        time_ok, brk_ok = True, True
        try:
            datetime.strptime(start.strip(), "%H:%M")
        except:
            time_ok = False

        try:
            brk_list = [int(x.strip())-1 for x in brk_raw.split(",") if x.strip()]
            brk_list = [b for b in brk_list if 0 <= b < int(n_per)-1]
        except:
            brk_ok = False; brk_list = []

        if not time_ok:
            st.error("❌ Invalid start time. Use HH:MM (e.g. 07:30).")
        else:
            # Preview
            preview_cfg = {"start_time":start.strip(),"class_duration":int(dur),
                           "break_after":brk_list,"break_duration":int(brk_dur),
                           "periods_per_day":int(n_per)}
            try:
                preview = gen_periods(preview_cfg)
                pills = ""
                for i,p in enumerate(preview):
                    pills += f'<span class="ppill"><b>P{i+1}</b>&ensp;{p}</span>'
                    if i in brk_list:
                        pills += f'<span class="ppill brk">☕ Break {brk_dur} min</span>'
                ends = preview[-1].split("–")[-1].strip() if preview else "—"
                st.markdown(f"""
                <div style="margin:.3rem 0 .7rem">
                    <div style="font-size:.72rem;font-weight:700;color:#475569;
                                text-transform:uppercase;letter-spacing:.06em;
                                margin-bottom:6px">Preview</div>
                    {pills}
                    <div style="margin-top:6px;font-size:.78rem;color:#64748B">
                        <b>{len(preview)} periods</b> · School ends at <b>{ends}</b>
                    </div>
                </div>""", unsafe_allow_html=True)
            except:
                st.warning("Could not preview with current settings.")
                preview_cfg = None

            col_s, col_x = st.columns([2,5])
            with col_s:
                if st.button(f"✅ Apply for {grade}", key=f"save_tc_{key}"):
                    D()["time_configs"][grade] = preview_cfg
                    # Clear this grade's schedule
                    for sec in sections_for(grade):
                        if sec in D()["schedule"]:
                            del D()["schedule"][sec]
                    persist()
                    st.success(f"✅ Time config saved for {grade}. Schedule cleared.")
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ██ DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠  Dashboard":
    total_e = sum(len(v) for v in D()["schedule"].values())
    topbar("Dashboard", "Your scheduling overview at a glance",
           badges=[f"📚 {len(D()['subjects'])} Subjects",
                   f"👩‍🏫 {len(D()['teachers'])} Teachers",
                   f"🏫 {len(D()['sections'])} Sections"])

    # Stat cards
    st.markdown('<div class="stats-row">', unsafe_allow_html=True)
    for icon,lbl,val,ibg,icol in [
        ("📚","Subjects",   len(D()["subjects"]), "#EFF6FF","#1D4ED8"),
        ("👩‍🏫","Teachers",  len(D()["teachers"]), "#F0FDF4","#166534"),
        ("🏫","Sections",   len(D()["sections"]), "#F5F3FF","#5B21B6"),
        ("📋","Entries",    total_e,               "#FFFBEB","#92400E"),
    ]:
        st.markdown(f"""<div class="scard">
            <div class="scard-icon" style="background:{ibg};color:{icol}">{icon}</div>
            <div><div class="scard-v">{val}</div>
            <div class="scard-l">{lbl}</div></div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Time config summary cards
    g11c = st.columns(2)
    for ci, grade in enumerate(GRADES):
        cfg = D()["time_configs"].get(grade, DEFAULT_TIME_CFG)
        try:
            periods = gen_periods(cfg)
            end_t = periods[-1].split("–")[-1].strip()
            p_count = len(periods)
        except:
            end_t = "—"; p_count = "—"
        color = "#1D4ED8" if grade=="Grade 11" else "#5B21B6"
        with g11c[ci]:
            st.markdown(f"""<div class="card">
            <div style="display:flex;align-items:center;justify-content:space-between;
                        margin-bottom:.8rem">
                <div style="font-size:.9rem;font-weight:800;color:{color}">{grade}</div>
                <span style="font-size:.7rem;font-weight:600;background:#F1F5F9;
                             color:#475569;border-radius:20px;padding:3px 10px">
                    Time Config</span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">
                {''.join(f"""<div style="background:#F8FAFC;border-radius:9px;padding:9px 12px;
                    border:1px solid #E2EAF3">
                    <div style="font-size:.65rem;font-weight:700;color:#94A3B8;
                                text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px">{l}</div>
                    <div style="font-size:.95rem;font-weight:700;color:#1E293B">{v}</div></div>"""
                for l,v in [("Start",cfg.get("start_time","—")),
                             ("Duration",f"{cfg.get('class_duration',60)} min"),
                             ("Periods",str(p_count))])}
            </div></div>""", unsafe_allow_html=True)

    # Recent entries
    card("🕒  Recent Schedule Entries")
    rows = []
    for sec, ents in D()["schedule"].items():
        for e in ents:
            rows.append({"Section":sec,"Day":e.get("day",""),
                         "Period":e.get("period",""),"Subject":e.get("subject",""),
                         "Teacher":e.get("teacher","")})
    if rows:
        st.dataframe(pd.DataFrame(rows[-30:]), use_container_width=True, hide_index=True)
    else:
        st.markdown("<p style='color:#94A3B8;font-size:.875rem;padding:.3rem 0'>"
                    "No entries yet — go to Schedule to start.</p>", unsafe_allow_html=True)
    end_card()
    close_content()


# ─────────────────────────────────────────────────────────────────────────────
# ██ SCHEDULE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📋  Schedule":
    topbar("Schedule",
           "Per-grade timetable with drag-and-drop editing")

    if not D()["sections"]:
        st.warning("No sections yet — add them in the Sections page first.")
        close_content(); st.stop()
    if not D()["subjects"]:
        st.warning("No subjects yet — add them in the Subjects page first.")
        close_content(); st.stop()

    # Handle save from JS via query params
    qp = st.query_params
    if "save_section" in qp and "save_data" in qp:
        try:
            new_ents = json.loads(qp["save_data"])
            sec_key  = qp["save_section"]
            day_key  = qp.get("save_day","")
            # Merge: keep entries for other days, replace for this day
            old = [e for e in D()["schedule"].get(sec_key,[]) if e.get("day") != day_key]
            D()["schedule"][sec_key] = old + [dict(e,section=sec_key) for e in new_ents]
            persist()
            st.query_params.clear()
            st.success(f"✅ Saved {len(new_ents)} entries for {sec_key} — {day_key}.")
            st.rerun()
        except Exception as ex:
            st.error(f"Save error: {ex}")

    # postMessage bridge
    st.markdown("""<script>
    window.addEventListener('message',function(ev){
      if(ev.data&&ev.data.type==='shs_save'){
        const p=new URLSearchParams(window.location.search);
        p.set('save_section',ev.data.section);
        p.set('save_data',   ev.data.entries);
        // extract day from first entry
        try{const ents=JSON.parse(ev.data.entries);
            if(ents.length)p.set('save_day',ents[0].day);}catch(e){}
        window.location.search=p.toString();
      }
    });</script>""", unsafe_allow_html=True)

    # ── Grade tabs ──────────────────────────────────────────────────────────
    if "sched_grade" not in st.session_state:
        st.session_state.sched_grade = "Grade 11"
    if "sched_day" not in st.session_state:
        st.session_state.sched_day = DAYS[0]

    g11col, g12col, spacer = st.columns([1,1,4])
    with g11col:
        if st.button("📘 Grade 11", key="btn_g11",
            type="primary" if st.session_state.sched_grade=="Grade 11" else "secondary"):
            st.session_state.sched_grade = "Grade 11"; st.rerun()
    with g12col:
        if st.button("📗 Grade 12", key="btn_g12",
            type="primary" if st.session_state.sched_grade=="Grade 12" else "secondary"):
            st.session_state.sched_grade = "Grade 12"; st.rerun()

    grade = st.session_state.sched_grade
    PERIODS = get_periods(grade)
    grade_secs = sections_for(grade)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Time config (inline expander) ───────────────────────────────────────
    render_time_config(grade)

    st.markdown("<br>", unsafe_allow_html=True)

    if not grade_secs:
        st.info(f"No sections for {grade} yet. Add them in the Sections page.")
        close_content(); st.stop()

    # ── Day selector ─────────────────────────────────────────────────────────
    st.markdown("**Select Day to View / Edit:**")
    day_cols = st.columns(len(DAYS))
    for i, d in enumerate(DAYS):
        with day_cols[i]:
            if st.button(d, key=f"d_{d}_{grade}",
                type="primary" if st.session_state.sched_day==d else "secondary"):
                st.session_state.sched_day = d; st.rerun()
    sel_day = st.session_state.sched_day

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Combined read-only view ───────────────────────────────────────────────
    card(f"📊  {grade}  ·  {sel_day}  —  All Sections Overview")
    overview_h = combined_timetable_html(grade, sel_day, PERIODS)
    grid_h = max(350, 68*len(PERIODS)+100)
    components.html(overview_h, height=grid_h, scrolling=True)

    # Completion info
    total_slots = len(PERIODS) * len(grade_secs)
    filled = sum(
        1 for sec in grade_secs
        for e in D()["schedule"].get(sec,[])
        if e.get("day")==sel_day
    )
    pct = int(filled/total_slots*100) if total_slots else 0
    bar_w = max(2, pct)
    st.markdown(f"""
    <div style="margin:.6rem 0 .2rem;display:flex;align-items:center;gap:10px">
        <div style="flex:1;background:#E2EAF3;border-radius:20px;height:7px;overflow:hidden">
            <div style="width:{bar_w}%;background:linear-gradient(90deg,#3B82F6,#60A5FA);
                        height:100%;border-radius:20px;transition:width .4s"></div>
        </div>
        <div style="font-size:.75rem;font-weight:700;color:#475569;white-space:nowrap">
            {filled}/{total_slots} slots filled ({pct}%)</div>
    </div>""", unsafe_allow_html=True)
    end_card()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Per-section editor ────────────────────────────────────────────────────
    card(f"✏️  Edit Timetable  ·  {sel_day}")
    st.markdown(f"""
    <div style="margin-bottom:.9rem;font-size:.8rem;color:#475569;line-height:1.6;
                background:#F8FAFC;border-radius:9px;padding:9px 14px;
                border:1.5px solid #E2EAF3">
        Choose a section below, then drag subjects (🔵 blue pills) onto empty slots and
        teachers (🟢 green pills) onto filled slots. Drag a card to move it.
        Hit <b>Save Schedule</b> to commit.
    </div>""", unsafe_allow_html=True)

    edit_sec = st.selectbox("Section to edit", grade_secs,
                            key=f"edit_sec_{grade}", label_visibility="visible")

    dnd_h = max(300, 68*len(PERIODS)+160)
    dnd = dnd_editor_html(edit_sec, sel_day,
                          D()["subjects"], D()["teachers"],
                          PERIODS, D()["schedule"])
    components.html(dnd, height=dnd_h, scrolling=True)

    # Remove entry helper
    sec_day_ents = [e for e in D()["schedule"].get(edit_sec,[]) if e.get("day")==sel_day]
    if sec_day_ents:
        with st.expander("🗑  Remove a specific entry from this section"):
            labels = [f"P{PERIODS.index(e['period'])+1}  ·  {e['period']}  ·  "
                      f"{e['subject']}  ({e.get('teacher','—')})"
                      if e["period"] in PERIODS else
                      f"{e['period']}  ·  {e['subject']}"
                      for e in sec_day_ents]
            to_del = st.selectbox("Entry", labels, key="del_entry_sel")
            if st.button("Remove Entry", key="del_btn"):
                idx = labels.index(to_del)
                target = sec_day_ents[idx]
                D()["schedule"][edit_sec] = [
                    e for e in D()["schedule"][edit_sec]
                    if not (e.get("day")==sel_day and
                            e.get("period")==target["period"] and
                            e.get("subject")==target["subject"])
                ]
                persist(); st.success("Removed."); st.rerun()

    end_card()
    close_content()


# ─────────────────────────────────────────────────────────────────────────────
# ██ SUBJECTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📚  Subjects":
    topbar("Subjects", "Build your school's subject catalog")

    card("➕  Add New Subject")
    sc1, sc2 = st.columns([5,1])
    with sc1:
        new_sub = st.text_input("Subject name",
            placeholder="e.g. General Mathematics, Oral Communication, Earth Science…",
            label_visibility="collapsed", key="new_sub")
    with sc2:
        st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
        if st.button("Add Subject", key="add_sub"):
            n = new_sub.strip()
            if not n: st.warning("Enter a subject name.")
            elif n in D()["subjects"]: st.error("Already exists.")
            else:
                D()["subjects"].append(n); persist()
                st.success(f"✅ Added '{n}'"); st.rerun()
    end_card()

    card(f"📋  All Subjects  ({len(D()['subjects'])})")
    if D()["subjects"]:
        for i,s in enumerate(D()["subjects"]):
            c1,c2 = st.columns([6,1])
            c1.markdown(f'<div class="irow"><span class="iname">📚 {s}</span>'
                        f'<span class="itag t-blue">Subject</span></div>',
                        unsafe_allow_html=True)
            with c2:
                if st.button("🗑", key=f"ds{i}"):
                    D()["subjects"].remove(s); persist(); st.rerun()
    else:
        st.markdown("<p style='color:#94A3B8;font-size:.875rem;padding:.3rem 0'>"
                    "No subjects yet. Add your first one above.</p>", unsafe_allow_html=True)
    end_card()
    close_content()


# ─────────────────────────────────────────────────────────────────────────────
# ██ TEACHERS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "👩‍🏫  Teachers":
    topbar("Teachers", "Manage your teaching staff roster")

    card("➕  Add New Teacher")
    tc1, tc2 = st.columns([5,1])
    with tc1:
        new_tch = st.text_input("Teacher name",
            placeholder="e.g. Ms. Reyes, Mr. Santos, Mrs. Garcia…",
            label_visibility="collapsed", key="new_tch")
    with tc2:
        st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
        if st.button("Add Teacher", key="add_tch"):
            n = new_tch.strip()
            if not n: st.warning("Enter a name.")
            elif n in D()["teachers"]: st.error("Already exists.")
            else:
                D()["teachers"].append(n); persist()
                st.success(f"✅ Added '{n}'"); st.rerun()
    end_card()

    card(f"👩‍🏫  All Teachers  ({len(D()['teachers'])})")
    if D()["teachers"]:
        for i,t in enumerate(D()["teachers"]):
            c1,c2 = st.columns([6,1])
            c1.markdown(f'<div class="irow"><span class="iname">👩‍🏫 {t}</span>'
                        f'<span class="itag t-green">Teacher</span></div>',
                        unsafe_allow_html=True)
            with c2:
                if st.button("🗑", key=f"dt{i}"):
                    D()["teachers"].remove(t); persist(); st.rerun()
    else:
        st.markdown("<p style='color:#94A3B8;font-size:.875rem;padding:.3rem 0'>"
                    "No teachers yet. Add your first one above.</p>", unsafe_allow_html=True)
    end_card()
    close_content()


# ─────────────────────────────────────────────────────────────────────────────
# ██ SECTIONS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🏫  Sections":
    topbar("Sections", "Organize sections by grade level and strand")

    STRAND_TAG = {"STEM":"t-blue","ABM":"t-orange","HUMSS":"t-purple",
                  "TVL":"t-green","GAS":"t-indigo","SPORTS":"t-green"}

    card("➕  Add New Section")
    sc1,sc2,sc3,sc4 = st.columns(4)
    with sc1: sname  = st.text_input("Section name", placeholder="e.g. Einstein", key="sec_name")
    with sc2: sgrade = st.selectbox("Grade level", GRADES, key="sec_grade")
    with sc3: sstrand= st.selectbox("Strand", STRANDS, key="sec_strand")
    with sc4: st.text_input("Adviser (optional)", key="sec_adv")
    if st.button("Add Section", key="add_sec"):
        n = sname.strip()
        if not n: st.warning("Section name required.")
        else:
            display = f"{n} ({sgrade} – {sstrand})"
            if display in D()["sections"]: st.error("Already exists.")
            else:
                D()["sections"].append(display); persist()
                st.success(f"✅ Added '{display}'"); st.rerun()
    end_card()

    for grade in GRADES:
        gsecs = [s for s in D()["sections"] if grade in s]
        color = "#1D4ED8" if grade=="Grade 11" else "#5B21B6"
        card(f'<span style="color:{color}">{grade}</span>  —  {len(gsecs)} Sections')
        if gsecs:
            for sec in gsecs:
                tag = next((STRAND_TAG[s] for s in STRANDS if s in sec), "t-blue")
                strand = next((s for s in STRANDS if s in sec), "Section")
                gi = D()["sections"].index(sec)
                c1,c2 = st.columns([6,1])
                c1.markdown(f'<div class="irow"><span class="iname">🏫 {sec}</span>'
                            f'<span class="itag {tag}">{strand}</span></div>',
                            unsafe_allow_html=True)
                with c2:
                    if st.button("🗑", key=f"dsec{gi}"):
                        D()["sections"].remove(sec)
                        if sec in D()["schedule"]: del D()["schedule"][sec]
                        persist(); st.rerun()
        else:
            st.markdown(f"<p style='color:#94A3B8;font-size:.875rem;padding:.3rem 0'>"
                        f"No sections for {grade} yet.</p>", unsafe_allow_html=True)
        end_card()

    close_content()
