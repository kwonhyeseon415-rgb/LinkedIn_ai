import os


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

LAST_SINGLE_PARAMS_KEY = "last_single_mode_params"
SINGLE_RESULT_KEY = "single_mode_result"


def get_default_single_mode_params(default_content_type):
    return {
        "title": "",
        "content_type": default_content_type,
        "target_audience": "",
        "tone": "",
        "post_count": 3,
        "language": "English",
        "input_mode": "paste",
        "pasted_text": "",
    }


def initialize_single_mode_session_state(st_module, *, default_content_type):
    defaults = get_default_single_mode_params(default_content_type)
    last_params = st_module.session_state.get(LAST_SINGLE_PARAMS_KEY, {})
    hydrated = {**defaults, **last_params}
    for field_name, widget_key in SINGLE_FORM_KEYS.items():
        if widget_key not in st_module.session_state:
            st_module.session_state[widget_key] = hydrated[field_name]


def store_recent_single_mode_params(st_module, *, default_content_type):
    defaults = get_default_single_mode_params(default_content_type)
    input_mode = st_module.session_state.get(SINGLE_FORM_KEYS["input_mode"], "paste")
    st_module.session_state[LAST_SINGLE_PARAMS_KEY] = {
        field_name: (
            st_module.session_state.get(widget_key, defaults[field_name])
            if field_name != "pasted_text" or input_mode == "paste"
            else ""
        )
        for field_name, widget_key in SINGLE_FORM_KEYS.items()
    }


def ensure_openai_api_key_ready(st_module):
    for env_key in OPENAI_ENV_SECRET_KEYS:
        if os.getenv(env_key, "").strip():
            continue
        secret_value = ""
        try:
            secret_value = str(st_module.secrets.get(env_key, "")).strip()
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


def build_user_facing_error_messages(
    exc,
    *,
    missing_api_key_error,
    authentication_error,
    quota_error,
    request_error,
):
    if isinstance(exc, missing_api_key_error):
        return [
            "当前没有可用的模型服务 API key。",
            "请检查 `.streamlit/secrets.toml` 或 Streamlit Community Cloud Secrets 中是否配置了 `OPENAI_API_KEY`。",
        ]
    if isinstance(exc, authentication_error):
        return [
            "当前共享 API key 无效，或没有访问所需模型的权限。",
            "请联系内部维护人检查 `OPENAI_API_KEY`、`OPENAI_BASE_URL` 与模型配置是否正确。",
        ]
    if isinstance(exc, quota_error):
        return [
            "当前共享模型服务 key 的额度不足，或请求被限流。",
            "请稍后重试，或联系内部维护人检查 billing / quota / rate limit。",
        ]
    if isinstance(exc, request_error):
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
