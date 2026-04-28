from linkedin_skill.interfaces.schemas import SkillResponse


def slugify_filename(value):
    cleaned = "".join(char.lower() if char.isalnum() else "_" for char in str(value).strip())
    compact = "_".join(part for part in cleaned.split("_") if part)
    return compact or "linkedin_skill"


def build_download_filename(title, content_type, suffix):
    return f"{slugify_filename(title)}_{content_type}_{suffix}.txt"


def safe_text_preview(text, limit=320):
    normalized = " ".join(str(text).split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit].rstrip()}..."


def build_final_drafts_body(response: SkillResponse):
    draft_bundle = dict(getattr(response, "draft_bundle", {}) or {})
    english_drafts = draft_bundle.get("final_linkedin_drafts") or response.final_linkedin_drafts
    chinese_translation = draft_bundle.get("chinese_translation", "")
    sections = ["English Drafts", english_drafts]
    if chinese_translation:
        sections.extend(["中文翻译", chinese_translation])
    return "\n\n".join(section for section in sections if section).strip()


def build_preview_structure(response: SkillResponse):
    lines = [
        "Skill Preview Structure｜统一技能执行结构预览",
        "平台：LinkedIn",
        f"内容类型：{response.normalized_source.content_type}",
        f"标题：{response.request.title}",
        f"整体状态：{response.status}",
        f"核心主链状态：{response.core_status}",
        "说明：planner 基于 NormalizedSourcePackage 生成三个下游 prompts，text executor 生成最终 LinkedIn drafts，image/video executors 当前保留 placeholder 结构。",
        "",
        "Parsed Sources",
    ]
    for parsed in response.normalized_source.parsed_sources:
        lines.append(f"- {parsed.channel_name}: {parsed.status}")
    lines.extend(
        [
            "",
            "Stage Statuses",
            f"- source_processing: {response.stage_statuses.get('source_processing', response.normalized_source.status)}",
            f"- planner: {response.stage_statuses.get('planner', response.planner_output.status)}",
            f"- ocr_extension: {response.stage_statuses.get('ocr_extension', response.normalized_source.ocr_extension.get('status', 'skipped'))}",
            "",
            "Executors",
            f"- text_executor: {response.text_executor_result.status}",
            f"- image_executor: {response.image_executor_result.status}",
            f"- video_executor: {response.video_executor_result.status}",
        ]
    )
    if response.capability_gaps:
        lines.extend(["", "Capability Gaps"])
        for item in response.capability_gaps:
            lines.append(f"- {item.get('stage')}: {item.get('status')}｜{item.get('note')}")
    if response.error_message:
        lines.extend(["", "Pipeline Error", f"- {response.error_message}"])
    return "\n".join(lines).strip()


def build_image_generation_body(response: SkillResponse):
    result = response.image_executor_result
    payload = dict(result.payload or {})
    sections = []
    image_prompt = payload.get("image_prompt") or response.planner_output.image_generation_prompt
    if image_prompt:
        sections.extend(["Image prompt", image_prompt])
    if payload.get("image_url"):
        sections.extend(["Generated image URL", payload["image_url"]])
    if payload.get("image_base64"):
        sections.extend(["Generated image", "Base64 image content is available in the structured payload and rendered by the web preview."])
    if payload.get("revised_prompt"):
        sections.extend(["Revised prompt", payload["revised_prompt"]])
    if not sections and result.output_text:
        sections.append(result.output_text)
    return "\n\n".join(str(section) for section in sections if str(section).strip()).strip()


def build_summary_items(response: SkillResponse):
    items = [
        ("平台范围", "LinkedIn only"),
        ("内容类型", response.request.content_type),
        ("标题", response.request.title),
        ("目标受众", response.request.target_audience),
        ("语气风格", response.request.tone),
        ("计划帖子数", str(response.request.post_count)),
        ("生成语言", response.request.language),
        ("输入来源", response.normalized_source.source_label),
        ("标准化状态", response.normalized_source.status),
        ("Planner 状态", response.planner_output.status),
        ("整体状态", response.status),
        ("核心主链状态", response.core_status),
        ("源文本预览", safe_text_preview(response.normalized_source.normalized_text) or "N/A"),
    ]
    if response.capability_gaps:
        items.append(
            (
                "Capability Gaps",
                "; ".join(f"{item['stage']}={item['status']}" for item in response.capability_gaps),
            )
        )
    if response.error_message:
        items.append(("错误摘要", response.error_message))
    return items


def build_streamlit_payload(response: SkillResponse):
    preview_structure = build_preview_structure(response)
    title = response.request.title
    content_type = response.request.content_type
    image_payload = dict(response.image_executor_result.payload or {})
    tabs = [
        {
            "title": "Highlights Summary",
            "caption": "Planner output from the unified skill pipeline.",
            "body": response.planner_output.highlights_summary,
            "accent": "white",
            "kicker": "Planner Output",
            "download_name": build_download_filename(title, content_type, "highlights_summary"),
        },
        {
            "title": "Final LinkedIn Drafts",
            "caption": f"Text executor status: {response.text_executor_result.status}",
            "body": build_final_drafts_body(response),
            "accent": "red",
            "kicker": "Executor Output",
            "download_name": build_download_filename(title, content_type, "final_linkedin_drafts"),
        },
        {
            "title": "Text Generation Prompt",
            "caption": "Planner prompt prepared for the text executor.",
            "body": response.planner_output.text_generation_prompt,
            "accent": "white",
            "kicker": "Planner Output",
            "download_name": build_download_filename(title, content_type, "text_generation_prompt"),
        },
        {
            "title": "Image Generation Prompt",
            "caption": f"Image executor status: {response.image_executor_result.status}",
            "body": build_image_generation_body(response),
            "accent": "blue",
            "kicker": "Image Executor" if response.image_executor_result.status == "success" else "Placeholder Executor",
            "download_name": build_download_filename(title, content_type, "image_generation_prompt"),
            "image_url": image_payload.get("image_url", ""),
            "image_base64": image_payload.get("image_base64", ""),
        },
        {
            "title": "Video Generation Prompt",
            "caption": f"Video executor status: {response.video_executor_result.status}",
            "body": response.video_executor_result.output_text,
            "accent": "yellow",
            "kicker": "Placeholder Executor",
            "download_name": build_download_filename(title, content_type, "video_generation_prompt"),
        },
        {
            "title": "Preview Structure",
            "caption": "Unified skill response preview.",
            "body": preview_structure,
            "accent": "yellow",
            "kicker": "Pipeline Overview",
            "download_name": build_download_filename(title, content_type, "preview_structure"),
        },
    ]

    return {
        "summary_items": build_summary_items(response),
        "tabs": tabs,
        "warnings": list(response.warnings),
        "status": response.status,
        "preview_structure": preview_structure,
    }
