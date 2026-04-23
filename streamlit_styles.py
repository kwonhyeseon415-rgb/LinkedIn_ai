APP_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700;900&display=swap');

:root {
    --ink: #111111;
    --paper: #FFFFFF;
    --canvas: #F0F0F0;
    --rule: #121212;
    --red: #D02020;
    --blue: #1040C0;
    --yellow: #F0C020;
}

html, body, [class*="css"]  {
    font-family: "Outfit", "Segoe UI", sans-serif;
    background: var(--canvas);
    color: var(--ink);
}

.stApp {
    background: var(--canvas);
    color: var(--ink);
}

.block-container {
    max-width: 1440px;
    padding-top: 0.95rem;
    padding-left: 0.9rem;
    padding-right: 0.9rem;
    padding-bottom: 3.2rem;
}

header[data-testid="stHeader"], #MainMenu, footer {
    visibility: hidden;
}

.hero-shell {
    display: grid;
    grid-template-columns: minmax(0, 1.12fr) minmax(300px, 0.88fr);
    gap: 0.9rem;
    align-items: stretch;
    margin-bottom: 1rem;
}

.eyebrow {
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.24em;
    margin-bottom: 0.7rem;
}

.hero-title {
    margin: 0;
    font-size: clamp(3rem, 7vw, 6.4rem);
    line-height: 0.88;
    letter-spacing: -0.06em;
    font-weight: 900;
    text-transform: uppercase;
    max-width: 9ch;
}

.hero-copy {
    margin-top: 0.7rem;
    max-width: 42rem;
    font-size: 0.95rem;
    line-height: 1.62;
    font-weight: 500;
}

.section-kicker {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 0.45rem;
}

.section-title {
    margin: 0;
    font-size: clamp(1.8rem, 3.2vw, 3rem);
    line-height: 0.94;
    letter-spacing: -0.04em;
    font-weight: 900;
    text-transform: uppercase;
}

.section-copy {
    margin-top: 0.5rem;
    margin-bottom: 0;
    max-width: 820px;
    font-size: 0.96rem;
    line-height: 1.62;
    font-weight: 500;
    color: #2f2f2f;
}

.hero-copy-card,
.hero-geometry,
.summary-panel,
.output-panel,
.form-note,
.section-marker {
    border: 4px solid var(--rule);
    box-shadow: 8px 8px 0px 0px var(--rule);
    border-radius: 0;
}

.hero-copy-card {
    background: var(--paper);
    padding: 1rem 1.1rem 1.05rem;
    position: relative;
    overflow: hidden;
}

.hero-copy-card::after {
    content: "";
    position: absolute;
    right: 1rem;
    top: 1rem;
    width: 22px;
    height: 22px;
    background: var(--red);
    border: 4px solid var(--rule);
    transform: rotate(45deg);
}

.hero-chip-row,
.summary-grid {
    display: grid;
    gap: 0.85rem;
}

.hero-chip-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    margin-top: 0.95rem;
}

.summary-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    margin-top: 0.75rem;
}

.hero-chip {
    padding: 0.78rem 0.85rem;
    border: 4px solid var(--rule);
    box-shadow: 4px 4px 0px 0px var(--rule);
    font-size: 0.76rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    text-align: center;
}

.hero-chip.red { background: var(--red); color: var(--paper); }
.hero-chip.blue { background: var(--blue); color: var(--paper); }
.hero-chip.yellow { background: var(--yellow); color: var(--ink); }

.hero-geometry {
    background: var(--blue);
    min-height: 300px;
    position: relative;
    overflow: hidden;
}

.geo-label {
    position: absolute;
    left: 1rem;
    bottom: 1rem;
    background: var(--paper);
    border: 4px solid var(--rule);
    box-shadow: 4px 4px 0px 0px var(--rule);
    padding: 0.55rem 0.7rem;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    z-index: 4;
}

.geo-circle,
.geo-square,
.geo-rotated,
.geo-square-center,
.geo-inner-dot,
.geo-triangle {
    position: absolute;
    border: 4px solid var(--rule);
}

.geo-circle {
    width: 155px;
    height: 155px;
    border-radius: 999px;
    background: var(--yellow);
    top: 1rem;
    left: 1rem;
    z-index: 1;
}

.geo-square {
    width: 132px;
    height: 132px;
    background: var(--paper);
    top: 1.55rem;
    right: 1.2rem;
    z-index: 2;
}

.geo-rotated {
    width: 96px;
    height: 96px;
    background: var(--red);
    transform: rotate(45deg);
    left: 45%;
    top: 34%;
    z-index: 1;
}

.geo-square-center {
    width: 145px;
    height: 145px;
    background: var(--paper);
    left: 27%;
    bottom: 1rem;
    z-index: 3;
}

.geo-inner-dot {
    width: 48px;
    height: 48px;
    border-radius: 999px;
    background: var(--blue);
    right: 0.85rem;
    bottom: 0.85rem;
    z-index: 5;
}

.geo-triangle {
    width: 0;
    height: 0;
    border-left: 48px solid transparent;
    border-right: 48px solid transparent;
    border-bottom: 88px solid var(--yellow);
    border-top: 0;
    left: 1rem;
    bottom: 1rem;
    z-index: 3;
}

.section-shell {
    display: grid;
    grid-template-columns: 68px minmax(0, 1fr);
    gap: 0.85rem;
    align-items: start;
    margin-top: 1.4rem;
    margin-bottom: 0.75rem;
}

.section-marker {
    min-height: 68px;
    position: relative;
    background: var(--yellow);
    overflow: hidden;
}

.section-marker.red { background: var(--red); }
.section-marker.blue { background: var(--blue); }
.section-marker.yellow { background: var(--yellow); }
.section-marker.white { background: var(--paper); }

.section-marker::before,
.section-marker::after {
    content: "";
    position: absolute;
    border: 4px solid var(--rule);
}

.section-marker::before {
    width: 30px;
    height: 30px;
    background: var(--paper);
    right: 8px;
    top: 8px;
}

.section-marker::after {
    width: 24px;
    height: 24px;
    border-radius: 999px;
    background: var(--yellow);
    left: 10px;
    bottom: 10px;
}

.summary-panel,
.form-note {
    padding: 0.85rem 0.95rem 0.9rem 0.95rem;
    position: relative;
}

.corner-shape {
    position: absolute;
    right: 12px;
    top: 12px;
    width: 18px;
    height: 18px;
    border: 4px solid var(--rule);
    background: var(--paper);
}

.corner-shape.circle { border-radius: 999px; }
.corner-shape.diamond { transform: rotate(45deg); }

.summary-panel {
    background: var(--yellow);
}

.summary-item {
    background: var(--paper);
    border: 2px solid var(--rule);
    box-shadow: 4px 4px 0px 0px var(--rule);
    padding: 0.8rem;
}

.summary-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--ink);
    font-weight: 700;
}

.summary-value {
    margin-top: 0.35rem;
    font-size: 1rem;
    line-height: 1.6;
    font-weight: 500;
}

.output-panel {
    padding: 0;
    overflow: hidden;
    margin-bottom: 0.4rem;
    background: var(--paper);
}

.output-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1rem;
    padding: 1rem 1rem 0.95rem 1rem;
    border-bottom: 4px solid var(--rule);
}

.output-head.red { background: var(--red); color: var(--paper); }
.output-head.blue { background: var(--blue); color: var(--paper); }
.output-head.yellow { background: var(--yellow); color: var(--ink); }
.output-head.white { background: var(--paper); color: var(--ink); }

.prompt-title {
    margin: 0;
    font-size: clamp(1.18rem, 2vw, 1.65rem);
    line-height: 1.04;
    font-weight: 900;
    text-transform: uppercase;
}

.status-pill {
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border: 4px solid var(--rule);
    box-shadow: 4px 4px 0px 0px var(--rule);
    padding: 0.45rem 0.6rem;
    background: var(--paper);
    color: var(--ink);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.55rem;
    margin-bottom: 0.85rem;
}

.stTabs [data-baseweb="tab"] {
    height: auto;
    padding: 0.75rem 0.95rem;
    border: 4px solid var(--rule);
    border-radius: 0;
    box-shadow: 4px 4px 0px 0px var(--rule);
    background: var(--paper);
    font-family: "Outfit", sans-serif;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

.stTabs [aria-selected="true"] {
    background: var(--yellow);
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}

.stTabs [data-baseweb="tab-panel"] {
    padding-top: 0.1rem;
}

.stTextInput label,
.stTextArea label,
.stNumberInput label,
.stSelectbox label,
.stRadio label {
    font-size: 0.76rem !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--ink) !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    border: 4px solid var(--rule) !important;
    border-radius: 0 !important;
    box-shadow: 4px 4px 0px 0px var(--rule) !important;
    background: var(--paper) !important;
    color: var(--ink) !important;
    font-family: "Outfit", sans-serif !important;
    font-weight: 500 !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="base-input"] > div {
    border-radius: 0 !important;
    border: 4px solid var(--rule) !important;
    box-shadow: 4px 4px 0px 0px var(--rule) !important;
    background: var(--paper) !important;
}

.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    border-radius: 0 !important;
    border: 4px solid var(--rule) !important;
    box-shadow: 4px 4px 0px 0px var(--rule) !important;
    font-family: "Outfit", sans-serif !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
    padding: 0.78rem 1rem !important;
    transition: transform 0.2s ease-out, box-shadow 0.2s ease-out !important;
}

.stFormSubmitButton > button {
    background: var(--red) !important;
    color: var(--paper) !important;
}

.stDownloadButton > button {
    background: var(--blue) !important;
    color: var(--paper) !important;
}

.stButton > button {
    background: var(--yellow) !important;
    color: var(--ink) !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: translate(-2px, -2px) !important;
}

.stButton > button:active,
.stDownloadButton > button:active,
.stFormSubmitButton > button:active {
    transform: translate(2px, 2px) !important;
    box-shadow: none !important;
}

.stRadio [role="radiogroup"] {
    gap: 0.5rem;
}

.stRadio [data-baseweb="radio"] {
    border: 4px solid var(--rule);
    padding: 0.45rem 0.7rem;
    box-shadow: 4px 4px 0px 0px var(--rule);
    background: var(--paper);
}

@media (max-width: 900px) {
    .hero-title {
        font-size: 2.45rem;
    }

    .hero-shell,
    .section-shell,
    .hero-chip-row,
    .summary-grid {
        grid-template-columns: 1fr;
    }

    .output-head {
        display: block;
    }

    .hero-geometry {
        min-height: 240px;
    }
}
</style>
"""


def configure_page(st_module, *, app_title):
    st_module.set_page_config(
        page_title=app_title,
        page_icon="■",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_styles(st_module):
    st_module.markdown(APP_STYLES, unsafe_allow_html=True)
