import os
import unittest
from unittest.mock import patch

import app


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


if __name__ == "__main__":
    unittest.main()
