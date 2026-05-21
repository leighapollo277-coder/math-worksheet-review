# Implementation Plan: Dynamic PDF Review Pipeline Automation

**Branch**: `002-pdf-review-pipeline` | **Date**: 2026-05-20 | **Spec**: [spec.md](file:///Users/kenyim/.gemini/antigravity/scratch/math-answer-review/specs/002-pdf-review-pipeline/spec.md)
**Input**: Feature specification from `/specs/002-pdf-review-pipeline/spec.md`

## Summary

The goal of this feature is to support dynamic multi-page PDF files, converting them programmatically to high-resolution PNGs, resizing them, analyzing their layout via Gemini API, cropping them, and generating a responsive glassmorphic HTML review portal. All sub-steps will be orchestrated through a single unified CLI runner `run_pipeline.py`.

## Technical Context

- **Language/Version**: Python 3.11
- **Primary Dependencies**: PyMuPDF (`fitz`), Pillow (`PIL`), Gemini CLI (`/usr/local/bin/gemini`)
- **Storage**: JSON cache files (`analysis_cache/page_XX_raw.json`) and compiled `analysis_report.json`
- **Testing**: Python `unittest` framework
- **Target Platform**: macOS/Linux CLI
- **Performance Goals**: End-to-end execution of a typical 10-page PDF in under 60 seconds (excluding AI latency), page conversion under 100ms per page.
- **Constraints**: Offline-capable for non-AI tasks, graceful rate-limit handling, robust cache verification.
- **Scale/Scope**: Support PDFs with any arbitrary number of pages.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No local `CONSTITUTION.md` exists. The following default quality gates are applied:
1. **Clean Code**: Standard formatting, no inline logic duplication, clean separation of concerns.
2. **Robustness**: Proper error checking at every boundary (file existence, directory creation, subprocess failure).
3. **No Hardcoded Absolute Paths**: All paths must be relative to the workspace root or configurable via parameters/arguments.

---

## Project Structure

### Documentation

```text
specs/002-pdf-review-pipeline/
├── plan.md              # This file
└── checklists/
    └── requirements.md  # Specification Checklist (completed)
```

### Source Code

The pipeline will be integrated into the existing structure with new modules and a unified runner:

```text
/Users/kenyim/.gemini/antigravity/scratch/math-answer-review/
├── run_pipeline.py      # [NEW] Unified pipeline runner
├── pdf_extractor.py     # [NEW] PyMuPDF-based PDF page extractor
├── analyze_all.py       # [MODIFY] Dynamic page analyzer with cache checks
├── crop_images.py       # [MODIFY] Parameterized image cropper
├── generate_review.py   # [MODIFY] Parameterized review generator
├── resize_and_preview.py# [MODIFY] Parameterized resizer
└── test_pipeline.py     # [NEW] End-to-end and component tests
```

---

## Independent Auditor

### Summary of Friction
> [!WARNING]
> The primary risks are Gemini API rate-limiting/token cost on large PDFs, and fragile subprocess execution of `/usr/local/bin/gemini`. Caching and dependency injection are critical to prevent command-line execution failures.

### Agent Proposal
Implement a pipeline runner script `run_pipeline.py` that invokes PyMuPDF to extract pages, resizes pages, loops through pages invoking `/usr/local/bin/gemini` via subprocess, saves page JSON outputs to a cache, crops elements, and generates the final HTML file.

### Auditor's Challenge
1. **Fragility of Subprocess**: Directly spawning `/usr/local/bin/gemini` is hard to test and mock. If the binary is missing or if the environment changes, tests will fail.
2. **API Quota & Cost**: Large PDFs will exceed Gemini rate limits if we process all pages sequentially in one run without delay or if we re-analyze already-cached pages. Caching must be smart (skipping already-analyzed pages based on image checksums or timestamps).
3. **Hardcoded Directories**: The existing scripts have hardcoded absolute paths like `/Users/kenyim/...`. This prevents executing the pipeline from different directories or on different machines.

### Reconciled Plan
1. **Encapsulate and Mock**: Create an abstract `GeminiClient` wrapper interface for the AI queries. In testing, we inject a mock `GeminiClient` that reads from static fixture files.
2. **State-of-the-Art Caching**: Use the existing page-based JSON cache directory. Before calling the AI for a page, check if `analysis_cache/page_XX_raw.json` exists. Implement a `--force` flag in the pipeline to bypass cache.
3. **Path Parameterization**: Update all scripts to accept a `--workspace` or `--output-dir` argument, defaulting to the directory containing the script. Eliminate all absolute hardcoded paths.

---

## Testability-First Analysis & Test Plan

### Testability Analysis

The current scripts are hard-to-test for three main reasons:
1. **Tight Coupling to File System Paths**: Scripts reference hardcoded `/Users/kenyim/.gemini/antigravity/...` strings.
2. **Subprocess Side Effects**: `analyze_all.py` spawns a real shell process running `/usr/local/bin/gemini`, which makes testing offline or verification of JSON parsing logic impossible without hitting the real API.
3. **State Side Effects**: Modules write output files directly to disk without configurable source/destination targets.

### Proposed Refactor

We will restructure the scripts to follow the **Dependency Injection** pattern:
1. **Parameterize Input/Output Paths**: Functions like `crop_page_assets` and `generate_html_content` will accept the paths of the target directories as arguments.
2. **Isolate AI Subprocess**: Wrap `/usr/local/bin/gemini` calls inside an `analyze_page_content(image_path, prompt_runner=None)` function. If `prompt_runner` is provided, it handles executing the prompt (facilitating test stubbing).
3. **PDF Page Reader**: Extract `extract_pdf_pages(pdf_path, dest_dir)` to a standalone testable utility in `pdf_extractor.py`.

### Test Plan

| Test Scenario | Input | Expected Output | Verification Method |
| --- | --- | --- | --- |
| **Test_PDF_Extraction** | Standard multi-page PDF | List of generated page image files | Call `extract_pdf_pages` on a sample 2-page PDF, verify output file count is 2 |
| **Test_Resizing_Standardization** | Image of size 2000x3000 | Image of size 1000x1500 | Verify resized image width is exactly 1000px and ratio is preserved |
| **Test_Gemini_Output_Parsing_Valid** | Raw JSON string from model | Parsed Python dictionary | Verify correct mapping of crops and correctness status |
| **Test_Gemini_Output_Parsing_Markdown_Wrap** | Markdown-wrapped JSON (e.g., ` ```json ... ``` `) | Parsed Python dictionary | Verify parser successfully strips backticks and handles JSON conversion |
| **Test_HTML_Compilation** | Mock list of page analysis dictionaries | HTML string containing matching elements | Verify KaTeX imports and matching question/step containers exist in HTML |

### Mocking Guide

- **API Subprocess Mock**: We will create a `MockPromptRunner` class that returns pre-determined JSON strings for given pages, preventing subprocess execution during unit test runs.

```python
class MockPromptRunner:
    def __init__(self, mock_responses):
        self.mock_responses = mock_responses
        self.calls = []

    def run(self, prompt):
        self.calls.append(prompt)
        # Return a mock JSON response based on prompt context
        return self.mock_responses.get(prompt, '{"page": 1, "questions": []}')
```
