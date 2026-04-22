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
            "body": response.final_linkedin_drafts,
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
            "body": response.image_executor_result.output_text,
            "accent": "blue",
            "kicker": "Placeholder Executor",
            "download_name": build_download_filename(title, content_type, "image_generation_prompt"),
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
