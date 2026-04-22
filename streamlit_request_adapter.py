import tempfile
from pathlib import Path

from linkedin_skill.adapters.python_api import run_linkedin_skill
from linkedin_skill.interfaces.schemas import SkillRequest


def create_temp_binary_file(file_bytes, suffix, prefix):
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, delete=False)
    try:
        temp_file.write(file_bytes)
        return temp_file.name
    finally:
        temp_file.close()


def cleanup_temp_files(file_paths):
    for file_path in file_paths:
        if not file_path:
            continue
        try:
            Path(file_path).unlink(missing_ok=True)
        except OSError:
            pass


def build_streamlit_skill_request(
    *,
    title,
    content_type,
    target_audience,
    tone,
    post_count,
    language,
    input_mode,
    uploaded_file,
    pasted_text,
):
    temp_files = []
    try:
        if input_mode == "paste":
            return SkillRequest(
                title=title.strip(),
                content_type=content_type,
                target_audience=target_audience.strip(),
                tone=tone.strip(),
                post_count=int(post_count),
                language=language.strip(),
                source_kind="pasted_text",
                pasted_text=pasted_text.strip(),
            ), temp_files

        if uploaded_file is None:
            raise ValueError("请先上传文件。")

        original_name = uploaded_file.name or "uploaded_file"
        file_bytes = uploaded_file.getvalue()
        suffix = Path(original_name).suffix.lower() or (".txt" if input_mode == "upload_txt" else ".pdf")
        temp_path = create_temp_binary_file(
            file_bytes,
            suffix if input_mode == "upload_txt" else ".pdf",
            "linkedin_skill_upload_",
        )
        temp_files.append(temp_path)

        return SkillRequest(
            title=title.strip(),
            content_type=content_type,
            target_audience=target_audience.strip(),
            tone=tone.strip(),
            post_count=int(post_count),
            language=language.strip(),
            source_kind="txt" if input_mode == "upload_txt" else "pdf",
            source_path=temp_path,
        ), temp_files
    except Exception:
        cleanup_temp_files(temp_files)
        raise


def run_streamlit_skill_request(**kwargs):
    request, temp_files = build_streamlit_skill_request(**kwargs)
    try:
        return run_linkedin_skill(request)
    finally:
        cleanup_temp_files(temp_files)
