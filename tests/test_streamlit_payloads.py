import unittest

from linkedin_skill.interfaces.schemas import (
    ExecutorResult,
    NormalizedSourcePackage,
    PlannerOutput,
    SkillRequest,
    SkillResponse,
)
from streamlit_payloads import build_streamlit_payload


class StreamlitPayloadTests(unittest.TestCase):
    def test_final_drafts_tab_renders_english_and_chinese_sections(self):
        request = SkillRequest(
            title="Demo",
            content_type="paper",
            target_audience="audience",
            tone="professional",
            post_count=1,
            language="English",
            source_kind="pasted_text",
            pasted_text="source material",
        )
        normalized = NormalizedSourcePackage(
            title="Demo",
            content_type="paper",
            target_audience="audience",
            tone="professional",
            post_count=1,
            language="English",
            source_kind="pasted_text",
            source_label="Pasted text",
            normalized_text="source material",
            parsed_sources=[],
            status="success",
        )
        planner = PlannerOutput(
            highlights_summary="Summary",
            text_generation_prompt="Text prompt",
            image_generation_prompt="Image prompt",
            video_generation_prompt="Video prompt",
        )
        text_result = ExecutorResult(
            executor_name="text_executor",
            status="success",
            output_text="English draft body",
            payload={
                "draft_bundle": {
                    "final_linkedin_drafts": "English draft body",
                    "chinese_translation": "中文翻译正文",
                }
            },
        )
        image_result = ExecutorResult(
            executor_name="image_executor",
            status="placeholder_not_connected",
            payload={
                "provider_connected": False,
                "placeholder_contract_version": "1.0",
                "artifact_type": "image_generation_prompt",
                "execution_mode": "prompt_only",
            },
        )
        video_result = ExecutorResult(
            executor_name="video_executor",
            status="placeholder_not_connected",
            payload={
                "provider_connected": False,
                "placeholder_contract_version": "1.0",
                "artifact_type": "video_generation_prompt",
                "execution_mode": "prompt_only",
            },
        )
        response = SkillResponse(
            request=request,
            normalized_source=normalized,
            planner_output=planner,
            text_executor_result=text_result,
            image_executor_result=image_result,
            video_executor_result=video_result,
            final_linkedin_drafts="English draft body",
            draft_bundle={
                "final_linkedin_drafts": "English draft body",
                "chinese_translation": "中文翻译正文",
            },
            status="success",
            core_status="success",
            stage_statuses={
                "source_processing": "success",
                "planner": "success",
                "text_executor": "success",
                "ocr_extension": "skipped",
                "image_executor": "placeholder_not_connected",
                "video_executor": "placeholder_not_connected",
            },
        )

        payload = build_streamlit_payload(response)
        final_tab_body = payload["tabs"][1]["body"]
        self.assertIn("English Drafts", final_tab_body)
        self.assertIn("English draft body", final_tab_body)
        self.assertIn("中文翻译", final_tab_body)
        self.assertIn("中文翻译正文", final_tab_body)


if __name__ == "__main__":
    unittest.main()
