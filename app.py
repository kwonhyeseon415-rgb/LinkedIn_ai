import streamlit as st

from streamlit_app_config import (
    LAST_SINGLE_PARAMS_KEY,
    SINGLE_FORM_KEYS,
    SINGLE_RESULT_KEY,
    build_user_facing_error_messages as _build_user_facing_error_messages,
    ensure_openai_api_key_ready as _ensure_openai_api_key_ready,
    initialize_single_mode_session_state as _initialize_single_mode_session_state,
    store_recent_single_mode_params as _store_recent_single_mode_params,
)
from streamlit_styles import configure_page, inject_styles
from streamlit_ui import render_hero, render_single_mode_page

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
    run_streamlit_skill_request = None


APP_TITLE = "LinkedIn Content Skill Demo"
APP_SUBTITLE = "Skill-first 架构演示：Streamlit 只负责输入与展示，核心流程统一走 LinkedIn 内容生成 skill。"


def initialize_single_mode_session_state():
    _initialize_single_mode_session_state(st, default_content_type=DEFAULT_CONTENT_TYPE)


def store_recent_single_mode_params():
    _store_recent_single_mode_params(st, default_content_type=DEFAULT_CONTENT_TYPE)


def ensure_openai_api_key_ready():
    return _ensure_openai_api_key_ready(st)


def build_user_facing_error_messages(exc):
    return _build_user_facing_error_messages(
        exc,
        missing_api_key_error=MissingOpenAIAPIKeyError,
        authentication_error=OpenAIAuthenticationFailureError,
        quota_error=OpenAIQuotaError,
        request_error=OpenAIRequestError,
    )


def main():
    configure_page(st, app_title=APP_TITLE)
    inject_styles(st)
    render_hero(APP_TITLE, APP_SUBTITLE)
    st.markdown("")
    if SKILL_IMPORT_ERROR is not None:
        st.error(
            "未能导入 `linkedin_skill`。这通常表示 web repo 的依赖没有完整安装，或 vendored skill 包安装失败。请先检查 `requirements.txt` 中的 vendored package 是否存在，再查看本地/Cloud 构建日志。"
        )
        st.caption(f"Import detail: {SKILL_IMPORT_ERROR}")
        return

    api_key_ready, api_key_message = ensure_openai_api_key_ready()
    render_single_mode_page(
        api_key_ready=api_key_ready,
        api_key_message=api_key_message,
        content_type_options=CONTENT_TYPE_OPTIONS,
        content_type_labels=CONTENT_TYPE_LABELS,
        default_content_type=DEFAULT_CONTENT_TYPE,
        demo_platform=DEMO_PLATFORM,
        initialize_single_mode_session_state=initialize_single_mode_session_state,
        store_recent_single_mode_params=store_recent_single_mode_params,
        run_streamlit_skill_request=run_streamlit_skill_request,
        build_user_facing_error_messages=build_user_facing_error_messages,
    )


if __name__ == "__main__":
    main()
