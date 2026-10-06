import time

import streamlit as st

from src.rag import CRISIS_MSG, EMERGENCY_MSG, answer, chunks, cited_sources

# ---- Update these after re-running eval/run_eval.py ----
EVAL_HIT1 = "93.5%"
# --------------------------------------------------------

st.set_page_config(
    page_title="Jarvis | Medical Information Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FIXES = {
    "commen cold": "Common Cold",
    "heart deseases": "Heart Disease",
    "chronic kidney desease": "Chronic Kidney Disease",
    "copd": "COPD",
    "foodallergy": "Food Allergy",
}


def pretty(source):
    name = source.replace("medlineplus_", "").replace("_", " ")
    return FIXES.get(name.lower(), name.title())


topics = sorted({pretty(c["source"]) for c in chunks})

GLOBAL_CSS = """
<style>
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stSidebar"],
[data-testid="collapsedControl"] {display: none !important;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1100px 600px at 85% -10%, #1d3a94 0%, transparent 60%),
    radial-gradient(900px 500px at -10% 25%, #123a7a 0%, transparent 55%),
    #0a1230;
}
[data-testid="stBottom"] > div {background: transparent;}
.block-container {max-width: 1100px; padding-top: 1.2rem; padding-bottom: 6rem;}

@keyframes float {0%,100% {transform: translateY(0);} 50% {transform: translateY(-14px);}}
@keyframes pulse {0% {box-shadow: 0 0 0 0 rgba(91,141,239,.55);} 70% {box-shadow: 0 0 0 18px rgba(91,141,239,0);} 100% {box-shadow: 0 0 0 0 rgba(91,141,239,0);}}
@keyframes fadeUp {from {opacity: 0; transform: translateY(18px);} to {opacity: 1; transform: translateY(0);}}
@keyframes draw {0% {stroke-dashoffset: 700;} 60%,100% {stroke-dashoffset: 0;}}
@keyframes blink {0%,92%,100% {transform: scaleY(1);} 96% {transform: scaleY(0.1);}}
@keyframes pop {from {opacity: 0; transform: scale(.6) translateY(10px);} to {opacity: 1; transform: scale(1) translateY(0);}}
@keyframes bob {0%,100% {transform: translateY(0);} 50% {transform: translateY(-5px);}}
@keyframes drift {0%,100% {transform: translate(0,0);} 50% {transform: translate(18px,-22px);}}

.eye {transform-box: fill-box; transform-origin: center; animation: blink 4.5s infinite;}

.hero {
  position: relative; overflow: hidden; display: flex; align-items: center; justify-content: space-between;
  gap: 2rem; padding: 2.8rem 3rem; border-radius: 28px;
  background: linear-gradient(135deg, rgba(20,40,110,.85) 0%, rgba(10,22,64,.9) 100%);
  border: 1px solid rgba(140,175,255,.18); box-shadow: 0 30px 80px rgba(0,0,0,.35);
}
.orb {position: absolute; border-radius: 50%; filter: blur(40px); opacity: .55; animation: drift 9s ease-in-out infinite;}
.o1 {width: 260px; height: 260px; background: #2f63e0; top: -80px; right: 120px;}
.o2 {width: 200px; height: 200px; background: #17a2b8; bottom: -90px; left: 30%; animation-delay: 2s;}
.hero-text {position: relative; z-index: 2; max-width: 560px; animation: fadeUp .8s ease both;}
.eyebrow {font-size: .75rem; letter-spacing: .18em; color: #8fb4ff; font-weight: 700;}
.hero h1 {font-size: 3.4rem; line-height: 1.05; margin: .5rem 0 .8rem 0; color: #fff; font-weight: 800;}
.grad {background: linear-gradient(90deg, #7cc4ff, #9b8cff); -webkit-background-clip: text; background-clip: text; color: transparent;}
.hero p {color: #c5d6fb; font-size: 1.08rem; line-height: 1.6; margin: 0 0 1.4rem 0;}
.cta-row {display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;}
a.cta {
  display: inline-block; padding: .85rem 1.5rem; border-radius: 999px; font-weight: 700; font-size: 1rem;
  color: #0a1230 !important; text-decoration: none !important;
  background: linear-gradient(90deg, #8ec5ff, #b6a8ff); transition: transform .2s, box-shadow .2s;
}
a.cta:hover {transform: translateY(-3px); box-shadow: 0 12px 30px rgba(120,160,255,.45);}
.note {color: #8fa6d6; font-size: .85rem;}
.ecg {margin-top: 1.4rem; display: block; opacity: .9;}
.ecg path {stroke-dasharray: 700; stroke-dashoffset: 700; animation: draw 3.6s linear infinite;}
.hero-art {position: relative; z-index: 2; animation: float 5s ease-in-out infinite; filter: drop-shadow(0 20px 40px rgba(60,110,230,.55));}

.stats {display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin: 1.4rem 0 .4rem 0;}
.stat {text-align: center; padding: 1rem; border-radius: 18px; background: rgba(255,255,255,.04); border: 1px solid rgba(140,175,255,.14); animation: fadeUp .8s ease both;}
.stat b {display: block; font-size: 1.7rem; color: #9fc3ff;}
.stat span {font-size: .82rem; color: #9db0d8;}

h2.sec {font-size: 1.6rem; margin: 2.6rem 0 .3rem 0; color: #fff;}
p.sub {color: #9db0d8; margin: 0 0 1rem 0;}
.grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(235px, 1fr)); gap: 1rem;}
.card {
  padding: 1.3rem; border-radius: 20px; background: linear-gradient(160deg, rgba(30,52,130,.55), rgba(14,26,72,.7));
  border: 1px solid rgba(140,175,255,.16); animation: fadeUp .7s ease both; transition: transform .25s, border-color .25s, box-shadow .25s;
}
.card:hover {transform: translateY(-6px); border-color: #6f9cff; box-shadow: 0 18px 40px rgba(20,50,160,.45);}
.card .icon {width: 52px; height: 52px; border-radius: 16px; display: grid; place-items: center; font-size: 1.6rem; margin-bottom: .7rem; background: rgba(110,150,255,.18);}
.card h3 {margin: 0 0 .35rem 0; font-size: 1.08rem; color: #fff;}
.card p {margin: 0; color: #b6c6ea; font-size: .92rem; line-height: 1.5;}
.grid .card:nth-child(1) {animation-delay: .05s;} .grid .card:nth-child(2) {animation-delay: .12s;}
.grid .card:nth-child(3) {animation-delay: .19s;} .grid .card:nth-child(4) {animation-delay: .26s;}
.grid .card:nth-child(5) {animation-delay: .33s;} .grid .card:nth-child(6) {animation-delay: .40s;}
.grid .card:nth-child(7) {animation-delay: .47s;} .grid .card:nth-child(8) {animation-delay: .54s;}

.pill {display: inline-block; padding: .3rem .8rem; margin: .2rem .3rem .2rem 0; border-radius: 999px; font-size: .82rem; color: #cfdcff; background: rgba(110,150,255,.12); border: 1px solid rgba(140,175,255,.25);}
.footer {margin-top: 2.6rem; padding: 1rem 1.2rem; border-radius: 14px; font-size: .85rem; color: #fde68a; background: rgba(250,204,21,.07); border: 1px solid rgba(250,204,21,.28);}

a.fab {position: fixed; right: 26px; bottom: 26px; z-index: 9999; display: flex; align-items: center; gap: 12px; text-decoration: none !important;}
.fab-bubble {
  background: #fff; color: #0a1230; padding: 10px 15px; border-radius: 16px 16px 4px 16px; font-size: .9rem; font-weight: 700;
  box-shadow: 0 12px 30px rgba(0,0,0,.4); animation: pop .6s ease 1.4s both, bob 3s ease-in-out 2.2s infinite;
}
.fab-btn {width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center; background: linear-gradient(135deg, #3e74f0, #1c3fa8); border: 2px solid rgba(255,255,255,.35); animation: pulse 2.4s infinite;}

.chat-head {display: flex; align-items: center; gap: .9rem; padding: .9rem 1.1rem; border-radius: 18px; background: rgba(255,255,255,.04); border: 1px solid rgba(140,175,255,.16);}
.chat-logo {width: 46px; height: 46px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, #2f63e0, #1a2f86);}
.chat-title {font-weight: 800; font-size: 1.15rem; color: #fff; line-height: 1.1;}
.chat-sub {font-size: .78rem; color: #9db0d8;}
a.back {margin-left: auto; color: #9fc3ff !important; text-decoration: none !important; font-size: .9rem; padding: .35rem .8rem; border-radius: 999px; border: 1px solid rgba(140,175,255,.3);}
a.back:hover {background: rgba(110,150,255,.15);}
.mini-banner {margin: .7rem 0 1rem 0; font-size: .8rem; color: #fde68a; opacity: .9; text-align: center;}
.empty {text-align: center; padding: 1.5rem 0 .5rem 0; animation: fadeUp .7s ease both;}
.empty h3 {color: #fff; margin: .6rem 0 .2rem 0;}
.empty p {color: #9db0d8; margin: 0 0 1rem 0;}
.chip {display: inline-block; padding: .25rem .75rem; margin: .15rem .35rem .15rem 0; border-radius: 999px; font-size: .8rem; text-decoration: none !important; color: #9fc3ff !important; background: rgba(110,150,255,.14); border: 1px solid rgba(140,175,255,.4);}
.chip:hover {background: rgba(110,150,255,.28);}
.meta {font-size: .75rem; color: #8fa6d6; margin-top: .4rem;}

[data-testid="stChatMessage"] {background: rgba(255,255,255,.035); border: 1px solid rgba(140,175,255,.12); border-radius: 18px; padding: .9rem 1rem;}
[data-testid="stChatMessageAvatarAssistant"] {background: linear-gradient(135deg, #2f63e0, #1a2f86) !important;}
[data-testid="stChatMessageAvatarUser"] {background: #3b4a7a !important;}
[data-testid="stChatInput"] {border-radius: 18px;}
div.stButton > button {border-radius: 14px; border: 1px solid rgba(140,175,255,.3); background: rgba(255,255,255,.03); padding: .65rem .9rem; white-space: normal; height: auto; transition: all .2s;}
div.stButton > button:hover {border-color: #6f9cff; color: #b8d0ff; transform: translateY(-2px);}

@media (max-width: 800px) {
  .hero {flex-direction: column; padding: 2rem 1.4rem;}
  .hero h1 {font-size: 2.5rem;}
  .fab-bubble {display: none;}
}
@media (prefers-reduced-motion: reduce) {* {animation: none !important; transition: none !important;}}
</style>
"""


def bot_svg(size=120):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Jarvis bot">
<defs><linearGradient id="jg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8ac8ff"/><stop offset="1" stop-color="#3b6fe0"/></linearGradient></defs>
<line x1="60" y1="10" x2="60" y2="24" stroke="#9cc9ff" stroke-width="4" stroke-linecap="round"/>
<circle cx="60" cy="8" r="6" fill="#ffd166"/>
<rect x="22" y="24" width="76" height="62" rx="20" fill="url(#jg)"/>
<rect x="30" y="34" width="60" height="42" rx="14" fill="#0a1634"/>
<circle class="eye" cx="47" cy="55" r="7" fill="#7cf0ff"/>
<circle class="eye" cx="73" cy="55" r="7" fill="#7cf0ff"/>
<path d="M50 68 Q60 75 70 68" stroke="#7cf0ff" stroke-width="3" fill="none" stroke-linecap="round"/>
<rect x="12" y="46" width="8" height="20" rx="4" fill="#5c8fee"/>
<rect x="100" y="46" width="8" height="20" rx="4" fill="#5c8fee"/>
<rect x="38" y="90" width="44" height="20" rx="10" fill="url(#jg)"/>
<rect x="58" y="94" width="4" height="12" rx="1" fill="#fff"/>
<rect x="54" y="98" width="12" height="4" rx="1" fill="#fff"/>
</svg>"""


ECG = """<svg class="ecg" width="300" height="56" viewBox="0 0 300 56" xmlns="http://www.w3.org/2000/svg">
<path d="M0 30 L70 30 L84 30 L94 8 L108 52 L120 30 L190 30 L204 30 L212 16 L222 40 L230 30 L300 30" stroke="#7cc4ff" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

FEATURES = [
    ("🔎", "Grounded answers", "Jarvis searches NIH MedlinePlus pages and answers only from what it finds."),
    ("📄", "Sources you can open", "Every answer links to the pages it used, so you can read the original."),
    ("🛡️", "Knows its limits", "No diagnoses and no doses. If the documents don't cover it, Jarvis says so."),
]

HABITS = [
    ("💧", "Stay hydrated", "Keep water within reach and drink regularly through the day."),
    ("😴", "Sleep well", "Most adults do best with 7 or more hours and a steady bedtime."),
    ("🏃", "Move daily", "Aim for about 150 minutes of moderate activity a week. Short walks count."),
    ("🥗", "Eat balanced", "Fill your plate with vegetables, fruit and whole grains. Go easy on salt."),
    ("🧘", "Manage stress", "Short breaks, deep breathing or a talk with a friend ease everyday stress."),
    ("🧼", "Wash your hands", "Soap and water for at least 20 seconds helps stop colds and flu spreading."),
    ("🚭", "Avoid tobacco", "Not smoking is one of the best things you can do for your lungs and heart."),
    ("🩺", "Check in early", "Regular checkups catch problems sooner. See a doctor if something feels off."),
]


def cards(items):
    return "".join(
        f"<div class='card'><div class='icon'>{i}</div><h3>{t}</h3><p>{d}</p></div>" for i, t, d in items
    )


def home():
    hero = (
        "<div class='hero'><div class='orb o1'></div><div class='orb o2'></div>"
        "<div class='hero-text'><div class='eyebrow'>AI HEALTH INFORMATION ASSISTANT</div>"
        "<h1>Meet <span class='grad'>Jarvis</span></h1>"
        "<p>Your calm, careful guide to health information. Ask a question and Jarvis answers from "
        "trusted NIH MedlinePlus pages, with sources you can open.</p>"
        "<div class='cta-row'><a class='cta' href='/chat' target='_self'>Chat with Jarvis →</a>"
        "<span class='note'>No sign-up needed</span></div>"
        + ECG
        + "</div><div class='hero-art'>"
        + bot_svg(230)
        + "</div></div>"
    )
    st.markdown(hero, unsafe_allow_html=True)

    st.markdown(
        f"<div class='stats'>"
        f"<div class='stat'><b>{len(topics)}</b><span>health topics</span></div>"
        f"<div class='stat'><b>{len(chunks)}</b><span>searchable passages</span></div>"
        f"<div class='stat'><b>NIH</b><span>trusted source</span></div>"
        f"<div class='stat'><b>{EVAL_HIT1}</b><span>retrieval hit rate</span></div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<h2 class='sec'>What Jarvis does</h2><p class='sub'>Built to be helpful, honest and careful.</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='grid'>{cards(FEATURES)}</div>", unsafe_allow_html=True)

    st.markdown("<h2 class='sec'>Everyday habits for good health</h2><p class='sub'>Simple, widely recommended habits. General wellness tips, not personal medical advice.</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='grid'>{cards(HABITS)}</div>", unsafe_allow_html=True)

    st.markdown("<h2 class='sec'>Topics Jarvis knows</h2>", unsafe_allow_html=True)
    st.markdown("".join(f"<span class='pill'>{t}</span>" for t in topics), unsafe_allow_html=True)

    st.markdown(
        "<div class='footer'>⚠️ Jarvis shares general information from public health sources. It is <b>not medical advice</b> "
        "and cannot diagnose or treat. In an emergency, call your local emergency number.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<a class='fab' href='/chat' target='_self' aria-label='Chat with Jarvis'>"
        "<div class='fab-bubble'>👋 Hi! Chat with Jarvis for health info</div>"
        "<div class='fab-btn'>" + bot_svg(40) + "</div></a>",
        unsafe_allow_html=True,
    )


EXAMPLES = [
    "What triggers an asthma attack?",
    "What are the symptoms of low blood sugar?",
    "How is high blood pressure treated?",
    "What is the F.A.S.T. test for stroke?",
]


def set_pending(q):
    st.session_state["pending"] = q


def render(m):
    avatar = ":material/person:" if m["role"] == "user" else ":material/smart_toy:"
    with st.chat_message(m["role"], avatar=avatar):
        kind = m.get("kind", "answer")
        if kind == "emergency":
            st.error(m["content"], icon="🚨")
        elif kind == "refusal":
            st.info(m["content"], icon="ℹ️")
        else:
            st.markdown(m["content"])
        if m.get("sources"):
            chips = "".join(
                f"<a class='chip' href='{url}' target='_blank'>📄 {label}</a>" for label, url in m["sources"]
            )
            st.markdown("<div class='meta'>Sources</div>" + chips, unsafe_allow_html=True)
        if m.get("hits"):
            with st.expander("How Jarvis found this"):
                for label, score, snippet in m["hits"]:
                    st.markdown(f"**{label}**  ·  similarity {score:.2f}")
                    st.text(snippet)
        if m.get("elapsed"):
            st.markdown(f"<div class='meta'>Answered in {m['elapsed']:.1f}s</div>", unsafe_allow_html=True)


def chat():
    st.markdown("<style>.block-container {max-width: 800px !important;}</style>", unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.markdown(
        "<div class='chat-head'><div class='chat-logo'>" + bot_svg(34) + "</div>"
        "<div><div class='chat-title'>Jarvis</div>"
        "<div class='chat-sub'>Medical information assistant · NIH MedlinePlus</div></div>"
        "<a class='back' href='/' target='_self'>← Home</a></div>"
        "<div class='mini-banner'>General information only, not medical advice. In an emergency, call your local emergency number.</div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.markdown(
            "<div class='empty'>" + bot_svg(84) + "<h3>How can I help today?</h3>"
            "<p>Ask a health question, or try one of these.</p></div>",
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        for i, q in enumerate(EXAMPLES):
            cols[i % 2].button(q, key=f"ex{i}", on_click=set_pending, args=(q,), use_container_width=True)

    for m in st.session_state.messages:
        render(m)

    typed = st.chat_input("Ask a health question...")
    question = st.session_state.pop("pending", None) or typed

    if question:
        user_msg = {"role": "user", "content": question}
        st.session_state.messages.append(user_msg)
        render(user_msg)

        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            with st.spinner("Searching medical documents..."):
                start = time.time()
                text, hits = answer(question)
                elapsed = time.time() - start

        if text in (EMERGENCY_MSG, CRISIS_MSG):
            kind = "emergency"
        elif text.startswith("I don't have enough information") or text.startswith("I do not have enough information"):
            kind = "refusal"
        else:
            kind = "answer"

        sources = [(pretty(n), url) for n, url in cited_sources(text, hits)] if kind == "answer" else []
        hit_info = [(pretty(c["source"]), s, c["text"][:240] + "...") for c, s in hits] if kind == "answer" else []
        st.session_state.messages.append(
            {"role": "assistant", "content": text, "kind": kind, "sources": sources, "hits": hit_info, "elapsed": elapsed}
        )
        st.rerun()

    if st.session_state.messages:
        if st.button("Clear chat", key="clear"):
            st.session_state.messages = []
            st.rerun()


home_page = st.Page(home, title="Home", icon=":material/home:", url_path="home", default=True)
chat_page = st.Page(chat, title="Chat", icon=":material/chat:", url_path="chat")
pg = st.navigation([home_page, chat_page], position="hidden")

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
pg.run()