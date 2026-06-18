# Building & publishing rapidrouge

This repo ships **one PyPI distribution**:

| Distribution | Built by | Artifact | Role |
|---|---|---|---|
| `rapidrouge` | hatchling | one `py3-none-any` wheel + sdist | pure-Python, the public import |

The wheel is platform-independent (`py3-none-any`), so a single build works
everywhere.

There are two ways to publish. Pick based on where you are:

- **[Path A — GitHub Actions](#path-a--release-via-github-actions-recommended)**: the real
  release. Needs the repo on GitHub. Publishes tokenlessly via PyPI Trusted
  Publishing. **Use this for any real release.**
- **[Path B — manual from your machine](#path-b--manual-publish-from-your-machine)**: works
  right now with no git. Good for TestPyPI dry-runs.

---

## 0. Prerequisites

- **uv** ≥ 0.11 (`uv --version`).
- A **PyPI account** (and optionally a **TestPyPI** account for dry-runs).
- For Path A: a **GitHub repo** for this project.

---

## 1. Build & inspect locally (do this first, every time)

```bash
cd ~/developer/rapidrouge

# Dev environment: installs test deps into .venv
uv sync --group test
uv run pytest          # full suite incl. the rouge_score parity gate
```

Build the distributable artifacts:

```bash
# pure base -> rapidrouge-0.1.0-py3-none-any.whl  +  rapidrouge-0.1.0.tar.gz
uv build --out-dir dist
```

Sanity-check the artifact before uploading anything:

```bash
# wheel MUST be pure (no compiled file):
unzip -l dist/rapidrouge-0.1.0-py3-none-any.whl | grep -E '\.so$|\.pyd$' && echo "BAD: not pure" || echo "OK: pure"
```

---

## 2. Cut a version (both paths)

The version lives in **two** places that must move in lockstep (the distribution
version and the package `__version__`). One command updates both:

```bash
uvx bump-my-version bump patch     # or: minor / major   (config in ./pyproject.toml)
# equivalently, the no-tool path:
# ./scripts/release.sh 0.2.0

uv lock                            # refresh the shared lockfile to the new version
```

Guard before publishing — both versions MUST agree:

```bash
grep '^version'     pyproject.toml                 # version = "0.2.0"
grep '^__version__' rapidrouge/__init__.py         # __version__ = "0.2.0"
```

---

## Path A — release via GitHub Actions (recommended)

### A1. One-time: push to GitHub

```bash
cd ~/developer/rapidrouge
git init -b main
git add -A
git commit -m "rapidrouge 0.1.0"
git remote add origin git@github.com:williambrach/rapidrouge.git
git push -u origin main
```

Then enable auto-tagging on bump (optional but handy): in `pyproject.toml`
under `[tool.bumpversion]`, set `commit = true` and `tag = true`.

### A2. One-time: PyPI Trusted Publisher (no API tokens, ever)

Register a Trusted Publisher on the `rapidrouge` PyPI project pointing at this
repo and `release.yml`.

The project name doesn't exist on PyPI yet, so register a **pending publisher**
(PyPI → *Your account* → *Publishing* → *Add a pending publisher*):

| For project | Owner | Repository | Workflow | Environment |
|---|---|---|---|---|
| `rapidrouge` | `williambrach` | `rapidrouge` | `release.yml` | `pypi-rapidrouge` |

Then in **GitHub → repo Settings → Environments**, create the environment
`pypi-rapidrouge` (optionally add a required-reviewer rule to gate the upload). No
secrets are stored — the workflow already requests `id-token: write` on the
publish job.

### A3. Release: tag and push

```bash
uvx bump-my-version bump minor      # writes versions; with commit/tag=true also tags v0.2.0
uv lock && git add -A && git commit -m "release: v0.2.0"   # if bump didn't commit
git tag v0.2.0                                              # if bump didn't tag
git push --follow-tags
```

Pushing the `v*` tag fires `.github/workflows/release.yml`, which builds the pure
`rapidrouge` sdist + wheel (and re-asserts it is pure), then publishes it.

Watch it under the repo's **Actions** tab.

---

## Path B — manual publish from your machine

Use this with **no git** (TestPyPI dry-run). Auth is via an **API token** (Trusted
Publishing only works inside GitHub Actions).

### B1. Get tokens

- TestPyPI: https://test.pypi.org/manage/account/token/
- PyPI: https://pypi.org/manage/account/token/ (start with an account-scoped
  token; after the first upload, replace it with a project-scoped one).

### B2. Dry-run on TestPyPI first (highly recommended)

```bash
cd ~/developer/rapidrouge
rm -rf dist && uv build --out-dir dist

uv publish --publish-url https://test.pypi.org/legacy/ --token <TESTPYPI_TOKEN> dist/rapidrouge-*

# verify an install from TestPyPI (pull normal deps from real PyPI):
uv venv /tmp/rr-test && \
uv pip install --python /tmp/rr-test \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  "rapidrouge==0.1.0"
/tmp/rr-test/bin/python -c "import rapidrouge; print(rapidrouge.__version__)"
```

### B3. Real PyPI

Same as B2 but drop `--publish-url` (defaults to PyPI) and use the PyPI token:

```bash
uv publish --token <PYPI_TOKEN> dist/rapidrouge-*
```

> `twine upload dist/rapidrouge-*` works identically if you prefer twine.

---

## 3. Verify after publishing

```bash
curl -fsSL https://pypi.org/pypi/rapidrouge/0.2.0/json >/dev/null && echo OK
uv venv /tmp/rr && uv pip install --python /tmp/rr "rapidrouge==0.2.0"
/tmp/rr/bin/python -c "import rapidrouge; print(rapidrouge.__version__)"
```

---

## 4. Troubleshooting

- **First upload rejected (project not found)**: register the pending publisher
  (Path A) or do the first upload with an API token (Path B) to create the name.
- **Wrong version somewhere**: re-run `uvx bump-my-version bump` / `scripts/release.sh`;
  never hand-edit one file — the two locations must stay identical.
- **Need to undo a bad release**: you cannot overwrite a version on PyPI; bump to
  the next patch and re-release (optionally *yank* the bad one in the PyPI UI).
