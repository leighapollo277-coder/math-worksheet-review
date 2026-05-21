# Feature Specification: Dynamic PDF Review Pipeline Automation

**Feature Branch**: `002-pdf-review-pipeline`  
**Created**: 2026-05-20  
**Status**: Draft (Ready for Review)  
**Input**: Local PDF file path containing student math worksheets, crop coordinates, AI feedback comments.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic PDF Page Extraction (Priority: P1)

As a math teacher grading student homework, I want to specify a PDF file path and have the system automatically extract all pages as high-resolution PNG images, so that I do not need to convert pages manually.

**Why this priority**: Core entry point of the pipeline; without automatic extraction, users are forced to perform manual, error-prone conversion steps.

**Independent Test**: Verify that providing a multi-page PDF path correctly extracts all pages as high-resolution PNG images into the project's source page directory.

**Acceptance Scenarios**:
1. **Given** a valid local PDF file path, **When** the extraction is executed, **Then** all pages are converted into individual PNG files named sequentially (e.g., `page_01.png`, `page_02.png`, etc.) without quality loss.

---

### User Story 2 - Dynamic Multi-Page Analysis (Priority: P1)

As a math teacher, I want the system to dynamically detect the page count of the input PDF and run the AI grading/layout analysis on all pages without any hardcoded page limits, so that any worksheet can be analyzed.

**Why this priority**: Hardcoded page ranges limit the utility of the application to a specific document. Dynamic page handling makes the system reusable.

**Independent Test**: Verify that the analysis script reads the actual page count of the generated images and loops through all pages to produce analysis JSONs.

**Acceptance Scenarios**:
1. **Given** a converted page folder containing $N$ pages, **When** the analysis script is run, **Then** it processes exactly $N$ pages, requesting Gemini visual analysis for each and saving the cache JSONs.

---

### User Story 3 - Unified Pipeline Command (Priority: P2)

As a grading administrator, I want to execute a single command that runs the entire workflow (extraction, resizing, AI analysis, cropping, HTML rendering), so that the processing is fully automated and simple.

**Why this priority**: Streamlines the operator workflow from several manual CLI steps to a single command.

**Independent Test**: Verify that running the entry-point script with a PDF path runs all pipeline components in sequence, ending with a successfully generated `index.html`.

**Acceptance Scenarios**:
1. **Given** a raw student PDF file, **When** the unified command is run, **Then** the scripts execute in order (PDF to PNG -> resize -> analyze -> crop -> generate HTML) and complete with a success status.

---

### Edge Cases

- **File missing/invalid**: How does the system handle an invalid or non-existent PDF path? (The system must abort gracefully with a clear error message).
- **Corrupted PDF/Extraction Failure**: What if page extraction fails for a page? (The pipeline must log the failure and stop before requesting AI analysis, to prevent API token waste).
- **Gemini Rate Limits/Transient Errors**: How do we handle API transient failures during the multi-page analysis? (The system should support robust error recovery or skip/cache successfully completed pages to allow resuming).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a PDF file path as a CLI argument.
- **FR-002**: The system MUST use `PyMuPDF` (`fitz`) to extract pages as PNG files at a high resolution (minimum 150 DPI).
- **FR-003**: The system MUST dynamically determine the number of pages from the PDF or output directory.
- **FR-004**: The system MUST resize the extracted pages to a standard width (e.g., 1000px) for consistent crop box scaling.
- **FR-005**: The system MUST call Gemini API for each page to determine question/step bounding boxes and feedback.
- **FR-006**: The system MUST crop individual question and step images based on the percentage-based y-coordinate boxes returned by the AI.
- **FR-007**: The system MUST compile all page reviews into `analysis_report.json` and generate a single-page interactive HTML review portal.
- **FR-008**: The system MUST provide a unified executable script (e.g., `run_pipeline.py`) that orchestrates all sub-steps.

### Key Entities

- **PDF Document**: The input document containing student math work.
- **Raw Page Image**: A high-resolution PNG image rendered from a PDF page.
- **Resized Page Image**: A page image scaled to standard dimensions.
- **Page Analysis Schema**: JSON data structure representing the crop boxes and grading comments for a single page.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of pages in the input PDF are extracted and processed.
- **SC-002**: The system executes end-to-end with a single command (e.g. `python run_pipeline.py --pdf <path>`).
- **SC-003**: All questions and student steps are cropped and correctly displayed side-by-side with feedback in the final HTML report.
- **SC-004**: Total pipeline execution logs are written to a central log file for debugging.
