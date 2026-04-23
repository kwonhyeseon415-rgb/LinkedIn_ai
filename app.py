import html
import json
import os
from textwrap import dedent

import streamlit as st
import streamlit.components.v1 as components

SKILL_IMPORT_ERROR = None

try:
    from linkedin_skill.adapters.openai_client import (
        MissingOpenAIAPIKeyError,
        OpenAIAuthenticationFailureError,
        OpenAIPipelineError,
        OpenAIQuotaError,
        OpenAIRequestError,
    )
    from linkedin_skill.config.settings import (
        CONTENT_TYPE_LABELS,
        CONTENT_TYPE_OPTIONS,
        DEFAULT_CONTENT_TYPE,
        DEMO_PLATFORM,
    )
    from streamlit_payloads import build_streamlit_payload
    from streamlit_request_adapter import run_streamlit_skill_request
except ImportError as exc:
    SKILL_IMPORT_ERROR = exc

    class OpenAIPipelineError(Exception):
        pass

    class MissingOpenAIAPIKeyError(OpenAIPipelineError):
        pass

    class OpenAIAuthenticationFailureError(OpenAIPipelineError):
        pass

    class OpenAIQuotaError(OpenAIPipelineError):
        pass

    class OpenAIRequestError(OpenAIPipelineError):
        pass

    CONTENT_TYPE_LABELS = {
        "paper": "Paper / Publication",
        "news": "News / Industry Update",
        "case_study": "Case Study / Application Story",
        "event_update": "Event Update",
    }
    CONTENT_TYPE_OPTIONS = list(CONTENT_TYPE_LABELS.keys())
    DEFAULT_CONTENT_TYPE = "paper"
    DEMO_PLATFORM = "LinkedIn"
    build_streamlit_payload = None
    run_streamlit_skill_request = None


APP_TITLE = "LinkedIn Content Skill Demo"
APP_SUBTITLE = "Skill-first 架构演示：Streamlit 只负责输入与展示，核心流程统一走 LinkedIn 内容生成 skill。"
SINGLE_RESULT_KEY = "single_mode_result"
LAST_SINGLE_PARAMS_KEY = "last_single_mode_params"


INPUT_MODE_OPTIONS = {
    "paste": "粘贴文本",
    "upload_txt": "上传 TXT",
    "upload_pdf": "上传 PDF",
}

OPENAI_ENV_SECRET_KEYS = (
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "PLANNER_MODEL",
    "TEXT_EXECUTOR_MODEL",
    "PDF_LLM_MODEL",
    "OPENAI_HTTP_REFERER",
    "OPENAI_APP_TITLE",
)

SINGLE_FORM_KEYS = {
    "title": "single_form_title",
    "content_type": "single_form_content_type",
    "target_audience": "single_form_target_audience",
    "tone": "single_form_tone",
    "post_count": "single_form_post_count",
    "language": "single_form_language",
    "input_mode": "single_form_input_mode",
    "pasted_text": "single_form_pasted_text",
}


def get_default_single_mode_params():
    return {
        "title": "",
        "content_type": DEFAULT_CONTENT_TYPE,
        "target_audience": "",
        "tone": "",
        "post_count": 3,
        "language": "English",
        "input_mode": "paste",
        "pasted_text": "",
    }


def initialize_single_mode_session_state():
    defaults = get_default_single_mode_params()
    last_params = st.session_state.get(LAST_SINGLE_PARAMS_KEY, {})
    hydrated = {**defaults, **last_params}
    for field_name, widget_key in SINGLE_FORM_KEYS.items():
        if widget_key not in st.session_state:
            st.session_state[widget_key] = hydrated[field_name]


def store_recent_single_mode_params():
    input_mode = st.session_state.get(SINGLE_FORM_KEYS["input_mode"], "paste")
    st.session_state[LAST_SINGLE_PARAMS_KEY] = {
        field_name: (
            st.session_state.get(widget_key, get_default_single_mode_params()[field_name])
            if field_name != "pasted_text" or input_mode == "paste"
            else ""
        )
        for field_name, widget_key in SINGLE_FORM_KEYS.items()
    }


def ensure_openai_api_key_ready():
    for env_key in OPENAI_ENV_SECRET_KEYS:
        if os.getenv(env_key, "").strip():
            continue
        secret_value = ""
        try:
            secret_value = str(st.secrets.get(env_key, "")).strip()
        except Exception:
            secret_value = ""
        if secret_value:
            os.environ[env_key] = secret_value

    if os.getenv("OPENAI_API_KEY", "").strip():
        return True, ""

    return (
        False,
        "未检测到 `OPENAI_API_KEY`。请在本地 `.streamlit/secrets.toml` 或 Streamlit Community Cloud 的 Secrets 中配置共享服务端 key。",
    )


def build_user_facing_error_messages(exc):
    if isinstance(exc, MissingOpenAIAPIKeyError):
        return [
            "当前没有可用的模型服务 API key。",
            "请检查 `.streamlit/secrets.toml` 或 Streamlit Community Cloud Secrets 中是否配置了 `OPENAI_API_KEY`。",
        ]
    if isinstance(exc, OpenAIAuthenticationFailureError):
        return [
            "当前共享 API key 无效，或没有访问所需模型的权限。",
            "请联系内部维护人检查 `OPENAI_API_KEY`、`OPENAI_BASE_URL` 与模型配置是否正确。",
        ]
    if isinstance(exc, OpenAIQuotaError):
        return [
            "当前共享模型服务 key 的额度不足，或请求被限流。",
            "请稍后重试，或联系内部维护人检查 billing / quota / rate limit。",
        ]
    if isinstance(exc, OpenAIRequestError):
        return [
            f"模型服务请求失败：{exc}",
            "请先检查网络连接与服务状态；如果问题持续，请联系内部维护人查看日志。",
        ]
    if isinstance(exc, ValueError):
        return [line.strip() for line in str(exc).splitlines() if line.strip()]

    message = str(exc).strip()
    lowered = message.lower()
    if "pdf" in lowered or "txt" in lowered or "read" in lowered or "decode" in lowered or "读取" in message:
        return [
            f"文件读取失败：{message or '无法解析上传文件。'}",
            "请确认文件格式正确、未损坏，并尽量使用可复制文本的 PDF 或 UTF-8 编码 TXT。",
        ]

    return [
        f"生成过程出现异常：{message or exc.__class__.__name__}",
        "请稍后重试；如果连续失败，请联系内部维护人检查服务端配置和日志。",
    ]


def render_api_key_error(message):
    if message:
        st.error(message)


def render_copy_button(label, body, key_suffix):
    button_id = f"copy_button_{key_suffix}"
    status_id = f"copy_status_{key_suffix}"
    safe_label = escape_text(label)
    payload = json.dumps(body)
    components.html(
        f"""
        <div style="padding-top: 0.15rem;">
            <button id="{button_id}" style="width: 100%; border: 3px solid #121212; box-shadow: 4px 4px 0 #121212; background: #ffffff; color: #111111; font-family: Outfit, sans-serif; font-weight: 800; padding: 0.65rem 0.8rem; cursor: pointer; text-transform: uppercase; letter-spacing: 0.08em;">
                {safe_label}
            </button>
            <div id="{status_id}" style="padding-top: 0.35rem; font-family: Outfit, sans-serif; font-size: 0.78rem; color: #2f2f2f;"></div>
        </div>
        <script>
        const copyButton = document.getElementById("{button_id}");
        const statusNode = document.getElementById("{status_id}");
        const copyText = {payload};

        copyButton.addEventListener("click", async () => {{
            try {{
                await navigator.clipboard.writeText(copyText);
                statusNode.textContent = "已复制到剪贴板";
                copyButton.textContent = "复制成功";
                window.setTimeout(() => {{
                    copyButton.textContent = "{safe_label}";
                    statusNode.textContent = "";
                }}, 1800);
            }} catch (error) {{
                statusNode.textContent = "浏览器阻止了复制，请手动复制正文（通常需要 HTTPS 或剪贴板权限）。";
            }}
        }});
        </script>
        """,
        height=74,
    )


def configure_page():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="■",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700;900&display=swap');

        :root {
            --ink: #111111;
            --paper: #FFFFFF;
            --canvas: #F0F0F0;
            --muted: #D8D8D8;
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
        .metric-panel,
        .batch-card,
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
        .summary-grid,
        .metric-grid,
        .batch-meta,
        .shape-strip {
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

        .metric-grid {
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }

        .batch-meta {
            grid-template-columns: repeat(4, minmax(0, 1fr));
            margin-top: 0.9rem;
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
        .metric-panel,
        .batch-card,
        .form-note {
            padding: 0.85rem 0.95rem 0.9rem 0.95rem;
            position: relative;
        }

        .batch-card p {
            margin: 0;
            line-height: 1.58;
            font-size: 0.95rem;
            font-weight: 500;
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
        .corner-shape.square { }
        .corner-shape.diamond { transform: rotate(45deg); }
        .corner-shape.triangle {
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-bottom: 22px solid var(--yellow);
            border-top: 0;
            background: transparent;
        }

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

        .output-body {
            background: var(--paper);
            padding: 0.9rem 0.95rem 1rem;
            white-space: pre-wrap;
            font-family: "IBM Plex Mono", "SFMono-Regular", "Consolas", "Courier New", monospace;
            font-size: 0.93rem;
            line-height: 1.68;
            max-height: 560px;
            overflow: auto;
        }

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

        .metric-number {
            margin-top: 0.45rem;
            font-size: clamp(2rem, 5vw, 4rem);
            line-height: 0.92;
            font-weight: 900;
            text-transform: uppercase;
        }

        .status-ok,
        .status-bad,
        .status-warn {
            font-weight: 700;
            letter-spacing: 0.04em;
        }

        .metric-panel.yellow { background: var(--yellow); }
        .metric-panel.blue { background: var(--blue); color: var(--paper); }
        .metric-panel.red { background: var(--red); color: var(--paper); }
        .metric-panel.white { background: var(--paper); }
        .status-ok { color: var(--blue); }
        .status-bad { color: var(--red); }
        .status-warn { color: #7A5A00; }

        .batch-card.success { background: var(--paper); }
        .batch-card.failure { background: var(--red); color: var(--paper); }
        .batch-card.partial { background: var(--yellow); color: var(--ink); }

        .mono-note {
            margin-top: 0.6rem;
            font-size: 0.82rem;
            line-height: 1.7;
            color: inherit;
            opacity: 0.92;
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
            .summary-grid,
            .metric-grid,
            .batch-meta {
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
        """,
        unsafe_allow_html=True,
    )


def escape_text(value):
    return html.escape(str(value))


def render_hero():
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-copy-card">
                <div class="eyebrow">LinkedIn Only / Skill-First / Streamlit Shell</div>
                <h1 class="hero-title">{escape_text(APP_TITLE)}</h1>
                <div class="hero-copy">{escape_text(APP_SUBTITLE)}</div>
                <div class="hero-chip-row">
                    <div class="hero-chip red">Final Drafts</div>
                    <div class="hero-chip blue">Image Prompt</div>
                    <div class="hero-chip yellow">Video Prompt</div>
                </div>
            </div>
            <div class="hero-geometry">
                <div class="geo-circle"></div>
                <div class="geo-square"></div>
                <div class="geo-rotated"></div>
                <div class="geo-square-center"></div>
                <div class="geo-triangle"></div>
                <div class="geo-inner-dot"></div>
                <div class="geo-label">Constructed for business review</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(kicker, title, copy):
    accent = "yellow"
    title_lower = title.lower()
    if "batch" in title_lower:
        accent = "blue"
    elif "prompt" in title_lower or "generated" in title_lower:
        accent = "red"
    elif "mode switch" in title_lower:
        accent = "white"

    st.markdown(
        f"""
        <div class="section-shell">
            <div class="section-marker {accent}"></div>
            <div>
                <div class="section-kicker">{escape_text(kicker)}</div>
                <h2 class="section-title">{escape_text(title)}</h2>
                <div class="section-copy">{escape_text(copy)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_panel(summary_items):
    rows = "".join(
        f"""
        <div class="summary-item">
            <div class="summary-label">{escape_text(label)}</div>
            <div class="summary-value">{escape_text(value)}</div>
        </div>
        """
        for label, value in summary_items
    )
    st.markdown(
        f"""
        <div class="summary-panel">
            <div class="corner-shape diamond"></div>
            <div class="section-kicker">Input Summary</div>
            <h3 class="prompt-title">输入摘要</h3>
            <div class="summary-grid">{rows}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_output_panel(title, caption, body, accent, kicker="Generated Output"):
    st.markdown(
        f"""
        <div class="output-panel">
            <div class="output-head {escape_text(accent)}">
                <div>
                    <div class="section-kicker">{escape_text(kicker)}</div>
                    <h3 class="prompt-title">{escape_text(title)}</h3>
                </div>
                <div class="status-pill">{escape_text(caption)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.text_area(
        title,
        value=body,
        height=420,
        disabled=True,
        key=f"{title.lower().replace(' ', '_')}_panel",
        label_visibility="collapsed",
    )


def render_preview_panel(preview_text):
    st.markdown(
        f"""
        <div class="output-panel">
            <div class="output-head yellow">
                <div>
                    <div class="section-kicker">Content Planning</div>
                    <h3 class="prompt-title">Final Draft Preview Structure</h3>
                </div>
                <div class="status-pill">Local planning view aligned to the planner/executor workflow</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.text_area(
        "Final Draft Preview Structure",
        value=preview_text,
        height=360,
        disabled=True,
        key="preview_structure_panel",
        label_visibility="collapsed",
    )


def render_result_tabs(view_payload):
    tabs = st.tabs([item["title"] for item in view_payload["tabs"]])
    for index, item in enumerate(view_payload["tabs"]):
        with tabs[index]:
            render_output_panel(
                title=item["title"],
                caption=item["caption"],
                body=item["body"],
                accent=item["accent"],
                kicker=item["kicker"],
            )
            action_cols = st.columns(2)
            with action_cols[0]:
                st.download_button(
                    label=f"下载 {item['title']}",
                    data=item["body"],
                    file_name=item["download_name"],
                    mime="text/plain",
                    key=f"download_{index}_{item['title'].lower().replace(' ', '_')}",
                    use_container_width=True,
                )
            with action_cols[1]:
                render_copy_button(
                    label=f"复制 {item['title']}",
                    body=item["body"],
                    key_suffix=f"{index}_{item['title'].lower().replace(' ', '_')}",
                )


def render_single_result():
    skill_response = st.session_state.get(SINGLE_RESULT_KEY)
    if not skill_response:
        return
    view_payload = build_streamlit_payload(skill_response)

    render_section_header(
        "Generated Result",
        "Skill Response",
        "Input Summary 保持在 tabs 外部；前端只渲染统一 SkillResponse，核心流程由 skill backend 处理。",
    )
    render_summary_panel(view_payload["summary_items"])
    if skill_response.status == "failed" and skill_response.error_message:
        st.error(f"本次生成未完成：{skill_response.error_message}")
    if view_payload["warnings"]:
        for warning in view_payload["warnings"]:
            st.warning(warning)
    st.markdown("")
    render_result_tabs(view_payload)


def render_single_mode(api_key_ready, api_key_message):
    render_section_header(
        "Single Mode",
        "单条模式｜Web Shell -> LinkedIn Skill",
        "表单只负责收集输入，随后统一调用 skill 入口；source ingestion、PDF 双通道解析、planner 与 executors 全部在 backend 内完成。",
    )

    st.markdown(
        """
            <div class="form-note">
                <div class="corner-shape circle"></div>
                <div class="summary-label">Demo Scope</div>
                <p>当前 Web Demo 只聚焦 LinkedIn，并且只作为 skill 的调用壳层。核心逻辑已下沉到统一 skill pipeline：ingestion、normalization、planner、text executor、image/video placeholder executors。</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
    initialize_single_mode_session_state()
    if not api_key_ready:
        render_api_key_error(api_key_message)

    with st.form("single_generation_form"):
        col_left, col_right = st.columns(2)

        with col_left:
            title = st.text_input(
                "标题",
                key=SINGLE_FORM_KEYS["title"],
                placeholder="请输入论文、新闻、案例或活动更新标题",
            )
            st.text_input("平台", value=DEMO_PLATFORM, disabled=True)
            content_type = st.selectbox(
                "内容类型",
                CONTENT_TYPE_OPTIONS,
                key=SINGLE_FORM_KEYS["content_type"],
                format_func=lambda key: CONTENT_TYPE_LABELS[key],
            )
            target_audience = st.text_input(
                "目标受众",
                key=SINGLE_FORM_KEYS["target_audience"],
                placeholder="例如：海外客户、潜在合作方、行业观察者",
                help="建议输入英文或中文。skill backend 会把受众信息传给 planner 与 executors。",
            )

        with col_right:
            tone = st.text_input(
                "语气风格",
                key=SINGLE_FORM_KEYS["tone"],
                placeholder="例如：professional, authoritative, insightful",
                help="建议输入英文或中文。skill backend 会把 tone 纳入 planner 与 text executor。",
            )
            post_count = st.number_input(
                "LinkedIn 帖子数量",
                min_value=1,
                key=SINGLE_FORM_KEYS["post_count"],
                step=1,
            )
            language = st.text_input("生成语言", key=SINGLE_FORM_KEYS["language"])
            input_mode = st.radio(
                "输入方式",
                list(INPUT_MODE_OPTIONS.keys()),
                key=SINGLE_FORM_KEYS["input_mode"],
                format_func=lambda key: INPUT_MODE_OPTIONS[key],
                horizontal=True,
            )

        uploaded_file = None
        pasted_text = st.session_state.get(SINGLE_FORM_KEYS["pasted_text"], "")
        if input_mode == "paste":
            pasted_text = st.text_area(
                "粘贴内容源文本",
                height=220,
                key=SINGLE_FORM_KEYS["pasted_text"],
                placeholder="请粘贴论文摘要、新闻摘要、案例信息或活动更新内容。",
            )
        elif input_mode == "upload_txt":
            uploaded_file = st.file_uploader(
                "上传 TXT 文件",
                type=["txt"],
                help="建议使用 UTF-8 编码的 TXT 文件。",
            )
        else:
            uploaded_file = st.file_uploader(
                "上传 PDF 文件",
                type=["pdf"],
                help="支持最高 400MB PDF。skill backend 会走 PDF 双通道：local structured parsing + LLM document understanding。当前保留 OCR 扩展位，但暂不接入。",
            )

        submitted = st.form_submit_button(
            "运行 LinkedIn Skill",
            use_container_width=True,
            disabled=not api_key_ready,
        )

    if submitted:
        try:
            st.session_state[SINGLE_RESULT_KEY] = run_streamlit_skill_request(
                title=title,
                content_type=content_type,
                target_audience=target_audience,
                tone=tone,
                post_count=int(post_count),
                language=language,
                input_mode=input_mode,
                uploaded_file=uploaded_file,
                pasted_text=pasted_text,
            )
            store_recent_single_mode_params()
        except OpenAIPipelineError as exc:
            st.session_state.pop(SINGLE_RESULT_KEY, None)
            for error in build_user_facing_error_messages(exc):
                st.error(error)
        except Exception as exc:
            st.session_state.pop(SINGLE_RESULT_KEY, None)
            for error in build_user_facing_error_messages(exc):
                st.error(error)

    render_single_result()


def main():
    configure_page()
    inject_styles()
    render_hero()
    st.markdown("")
    if SKILL_IMPORT_ERROR is not None:
        st.error(
            "未能导入 `linkedin_skill`。这通常表示 web repo 的依赖没有完整安装，或 vendored skill 包安装失败。请先检查 `requirements.txt` 中的 vendored package 是否存在，再查看本地/Cloud 构建日志。"
        )
        st.caption(f"Import detail: {SKILL_IMPORT_ERROR}")
        return
    api_key_ready, api_key_message = ensure_openai_api_key_ready()
    render_single_mode(api_key_ready, api_key_message)


if __name__ == "__main__":
    main()
