# LinkedIn Skill Web Shell

This repository is the Streamlit shell for the separately installable `linkedin_skill` package.

It is intentionally narrow:
- LinkedIn only
- Single Mode only
- current front-end fields stay simple
- text generation returns final LinkedIn drafts
- image/video remain placeholder prompts
- OCR is still not connected
- download is already supported
- copy-to-clipboard is supported in the current result tabs

## Repository Boundary

The web shell is responsible for:
- collecting user input
- converting page input into `SkillRequest`
- calling `run_linkedin_skill(...)`
- rendering `SkillResponse`

It is not the source of truth for:
- source ingestion
- parsing
- normalization
- planner logic
- executor logic
- pipeline orchestration

## Install Strategy

This repo now includes a **vendored source distribution** of `linkedin-skill` under:

```text
vendor/linkedin-skill-0.1.0.tar.gz
```

`requirements.txt` installs that packaged skill automatically, so Streamlit Community Cloud does not need a sibling repo path or a hand-written private git URL to make the app boot.

For local development, you can still override the vendored package with an editable sibling install from `../linkedin-skill` when you want live skill-side code changes.

## Local Development

### 1. Create a virtualenv and install the web repo

From the web repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

At this point, the app can already run because the vendored `linkedin-skill` package is installed from `vendor/`.

### 2. Optional: switch to editable sibling skill development

If you are working in the split workspace and want live code edits from the sibling skill repo:

```bash
python -m pip install -e ../linkedin-skill
```

`start_on_mac.sh` already does this automatically when `../linkedin-skill` exists.

### 3. Configure the shared OpenAI API key

Do not add any API key input field to the page. The app reads a shared server-side key from Streamlit secrets and maps it to `OPENAI_API_KEY` for the skill package.

Create:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-your-shared-service-key"
```

There is also a committed example file:

```text
.streamlit/secrets.toml.example
```

The real `.streamlit/secrets.toml` is ignored by git.

### 4. Upload-size configuration

This repo includes project-level Streamlit config:

```toml
# .streamlit/config.toml
[server]
maxUploadSize = 400
```

That raises the file upload limit to 400MB. The PDF uploader help text in the page matches this limit.

### 5. Run locally

```bash
streamlit run app.py
```

Or:

```bash
bash start_on_mac.sh
```

Open:

```text
http://localhost:8501
```

## Streamlit Community Cloud Deployment

### 1. Deploy the web repo only

Create a Streamlit Community Cloud app from `linkedin-skill-web`.

### 2. Let Community Cloud install the skill automatically

No sibling repo path is required in the cloud runtime.

`requirements.txt` already includes:

```text
./vendor/linkedin-skill-0.1.0.tar.gz
```

So Community Cloud installs the vendored `linkedin-skill` package as part of the normal dependency step.

### 3. Configure the shared OpenAI key in Community Cloud

In the app settings, open **Secrets** and add:

```toml
OPENAI_API_KEY = "sk-your-shared-service-key"
```

The page will automatically map that secret into the environment variable expected by `linkedin_skill`.

### 4. Upload-size config in Community Cloud

The committed `.streamlit/config.toml` travels with the web repo, so the 400MB upload limit is part of the deployed app configuration.

### 5. Refreshing the vendored skill package after backend changes

When `linkedin-skill` changes, rebuild the source distribution from the skill repo and refresh the vendored artifact:

```bash
cd ../linkedin-skill
python setup.py sdist --dist-dir ../linkedin-skill-web/vendor
```

Then commit the updated tarball in the web repo.

## What Users Will See

- No “enter your API key” field in the UI
- A clear page error if `OPENAI_API_KEY` is missing or invalid
- A clear page error if `linkedin_skill` failed to install or import
- Existing download buttons in each result tab
- A copy action in each result tab for quickly copying the current tab content
- Single-mode form values preserved in the current Streamlit session after a successful run
- No Batch Mode UI in the current web shell

## Known Limits

- LinkedIn only
- text output is the only final generated artifact
- image/video remain placeholder prompt outputs
- OCR provider is not connected
- copy-to-clipboard depends on browser clipboard permission; if blocked, users can still copy from the visible result text areas manually
