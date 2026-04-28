import os
import unittest
from unittest.mock import patch

import app
import streamlit_app_config


class FakeSecrets(dict):
    def get(self, key, default=""):
        return super().get(key, default)


class StreamlitSecretsEnvMappingTests(unittest.TestCase):
    def test_secrets_map_openai_compatible_environment_variables(self):
        secrets = FakeSecrets(
            {
                "OPENAI_API_KEY": "sk-openrouter-test",
                "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
                "PLANNER_MODEL": "openai/gpt-5.2",
                "TEXT_EXECUTOR_MODEL": "openai/gpt-5.2",
                "PDF_LLM_MODEL": "openai/gpt-5.2-mini",
                "IMAGE_GENERATOR_MODEL": "gpt-image-1",
                "IMAGE_GENERATION_SIZE": "1024x1024",
                "ENABLE_IMAGE_GENERATION": "true",
                "OPENAI_HTTP_REFERER": "https://example.com/demo",
                "OPENAI_APP_TITLE": "LinkedIn Skill Demo",
            }
        )

        with patch.object(app.st, "secrets", secrets, create=True), patch.dict(os.environ, {}, clear=True):
            ready, message = app.ensure_openai_api_key_ready()
            self.assertTrue(ready)
            self.assertEqual(message, "")
            self.assertEqual(os.environ["OPENAI_API_KEY"], "sk-openrouter-test")
            self.assertEqual(os.environ["OPENAI_BASE_URL"], "https://openrouter.ai/api/v1")
            self.assertEqual(os.environ["PLANNER_MODEL"], "openai/gpt-5.2")
            self.assertEqual(os.environ["TEXT_EXECUTOR_MODEL"], "openai/gpt-5.2")
            self.assertEqual(os.environ["PDF_LLM_MODEL"], "openai/gpt-5.2-mini")
            self.assertEqual(os.environ["IMAGE_GENERATOR_MODEL"], "gpt-image-1")
            self.assertEqual(os.environ["IMAGE_GENERATION_SIZE"], "1024x1024")
            self.assertEqual(os.environ["ENABLE_IMAGE_GENERATION"], "true")
            self.assertEqual(os.environ["OPENAI_HTTP_REFERER"], "https://example.com/demo")
            self.assertEqual(os.environ["OPENAI_APP_TITLE"], "LinkedIn Skill Demo")

    def test_existing_environment_values_take_precedence_over_secrets(self):
        secrets = FakeSecrets(
            {
                "OPENAI_API_KEY": "secret-key",
                "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
            }
        )

        with patch.object(app.st, "secrets", secrets, create=True), patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "env-key",
                "OPENAI_BASE_URL": "https://custom.example/v1",
            },
            clear=True,
        ):
            ready, _ = app.ensure_openai_api_key_ready()
            self.assertTrue(ready)
            self.assertEqual(os.environ["OPENAI_API_KEY"], "env-key")
            self.assertEqual(os.environ["OPENAI_BASE_URL"], "https://custom.example/v1")


class StreamlitWrapperCompatibilityTests(unittest.TestCase):
    @patch("app._initialize_single_mode_session_state")
    def test_initialize_single_mode_session_state_accepts_default_override(self, initialize_mock):
        app.initialize_single_mode_session_state(default_content_type="news")
        initialize_mock.assert_called_once_with(app.st, default_content_type="news")

    @patch("app._initialize_single_mode_session_state")
    def test_initialize_single_mode_session_state_falls_back_to_existing_default(self, initialize_mock):
        app.initialize_single_mode_session_state()
        initialize_mock.assert_called_once_with(app.st, default_content_type=app.DEFAULT_CONTENT_TYPE)

    @patch("app._store_recent_single_mode_params")
    def test_store_recent_single_mode_params_accepts_default_override(self, store_mock):
        app.store_recent_single_mode_params(default_content_type="news")
        store_mock.assert_called_once_with(app.st, default_content_type="news")


class FakeStreamlitModule:
    def __init__(self):
        self.session_state = {}


class StreamlitSessionStateInitializationTests(unittest.TestCase):
    def test_initialize_single_mode_session_state_uses_override_for_content_type(self):
        st_module = FakeStreamlitModule()

        streamlit_app_config.initialize_single_mode_session_state(
            st_module,
            default_content_type="news",
        )

        self.assertEqual(
            st_module.session_state[streamlit_app_config.SINGLE_FORM_KEYS["content_type"]],
            "news",
        )
        self.assertEqual(
            st_module.session_state[streamlit_app_config.SINGLE_FORM_KEYS["language"]],
            "English",
        )

    def test_initialize_single_mode_session_state_falls_back_when_override_is_none(self):
        st_module = FakeStreamlitModule()

        streamlit_app_config.initialize_single_mode_session_state(
            st_module,
            default_content_type=None,
        )

        self.assertEqual(
            st_module.session_state[streamlit_app_config.SINGLE_FORM_KEYS["content_type"]],
            streamlit_app_config.DEFAULT_SINGLE_CONTENT_TYPE,
        )


if __name__ == "__main__":
    unittest.main()
