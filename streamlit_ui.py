import html
import json

import streamlit as st
import streamlit.components.v1 as components

from streamlit_app_config import SINGLE_FORM_KEYS, SINGLE_RESULT_KEY
from streamlit_payloads import build_streamlit_payload


INPUT_MODE_OPTIONS = {
    "paste": "粘贴文本",
    "upload_txt": "上传 TXT",
    "upload_pdf": "上传 PDF",
}


def escape_text(value):
    return html.escape(str(value))


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


def render_hero(app_title, app_subtitle):
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-copy-card">
                <div class="eyebrow">LinkedIn Only / Skill-First / Streamlit Shell</div>
                <h1 class="hero-title">{escape_text(app_title)}</h1>
                <div class="hero-copy">{escape_text(app_subtitle)}</div>
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
    if "prompt" in title_lower or "generated" in title_lower:
        accent = "red"

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
    for warning in view_payload["warnings"]:
        st.warning(warning)
    st.markdown("")
    render_result_tabs(view_payload)


def render_single_mode_page(
    *,
    api_key_ready,
    api_key_message,
    content_type_options,
    content_type_labels,
    default_content_type,
    demo_platform,
    initialize_single_mode_session_state,
    store_recent_single_mode_params,
    run_streamlit_skill_request,
    build_user_facing_error_messages,
):
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
    initialize_single_mode_session_state(default_content_type=default_content_type)
    if not api_key_ready and api_key_message:
        st.error(api_key_message)

    with st.form("single_generation_form"):
        col_left, col_right = st.columns(2)

        with col_left:
            title = st.text_input(
                "标题",
                key=SINGLE_FORM_KEYS["title"],
                placeholder="请输入论文、新闻、案例或活动更新标题",
            )
            st.text_input("平台", value=demo_platform, disabled=True)
            content_type = st.selectbox(
                "内容类型",
                content_type_options,
                key=SINGLE_FORM_KEYS["content_type"],
                format_func=lambda key: content_type_labels[key],
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
            store_recent_single_mode_params(default_content_type=default_content_type)
        except Exception as exc:
            st.session_state.pop(SINGLE_RESULT_KEY, None)
            for error in build_user_facing_error_messages(exc):
                st.error(error)

    render_single_result()
