# Feature Specification: Math Review HTML Generator

**Feature Branch**: `001-math-review-generator`  
**Created**: 2026-05-20  
**Status**: Active  
**Input**: Scanned math PDF with questions and student answers, crop coordinates, AI feedback comments.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Question and Answer Chopping (Priority: P1)

As a math teacher grading student homework, I want to automatically chop each question and each step of the student's answer from the scanned PDF pages and save them as individual image files, so that I can display them sequentially.

**Why this priority**: Essential to extract the visual elements of the questions and answers from the scanned PDF.

**Independent Test**: Verify that the cropping coordinates successfully extract distinct images for questions and corresponding answer steps, and save them to the project directory.

**Acceptance Scenarios**:
1. **Given** a set of crop coordinates for the PDF pages, **When** the extraction script is run, **Then** all questions and student steps are cropped and saved to `images/` without distortion or clipping.

---

### User Story 2 - Sequential HTML Review Page (Priority: P2)

As a student reviewing my math homework, I want to see the cropped questions and my handwritten steps laid out one-by-one in an HTML page, so that I can easily follow the flow of my work.

**Why this priority**: Core presentation interface that maps the cropped visual elements to a readable layout.

**Independent Test**: Verify that the HTML page loads and correctly renders each question followed by its student answer steps in chronological order.

**Acceptance Scenarios**:
1. **Given** the cropped image assets, **When** the HTML page is rendered, **Then** each question is followed by its corresponding student answer steps in sequential order.

---

### User Story 3 - AI Feedback on Wrong Steps (Priority: P3)

As a student, I want a clear comment inserted directly below any step where I made a mathematical error, explaining why that step is wrong and what the correct step/answer should be, so that I can learn from my mistakes.

**Why this priority**: Educational value of the application to pinpoint and correct mistakes.

**Independent Test**: Verify that the AI analyzes the student steps, identifies the exact incorrect step, and displays an explanation card in the HTML right below that step.

**Acceptance Scenarios**:
1. **Given** a student's answer with an error, **When** the page is rendered, **Then** a correction comment block is visible below the exact incorrect step.
2. **Given** correct student steps, **When** the page is rendered, **Then** no error comments are displayed for those steps.

---

### User Story 4 - Premium Responsive Design (Priority: P4)

As a user, I want the HTML review page to have a premium, glassmorphic layout, clean typography, smooth hover effects, and responsive columns, so that the grading interface feels modern and professional.

**Why this priority**: Visual excellence to wow the user.

**Independent Test**: View the HTML page in the browser and verify the visual layout, typography, glassmorphism, responsive column grid, and hover micro-animations.

**Acceptance Scenarios**:
1. **Given** the HTML review page is opened in a web browser, **When** viewed on mobile or desktop, **Then** the layout adjusts dynamically, using modern typography, glassmorphic cards, and elegant error annotations.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST render PDF pages to high-resolution PNG images.
- **FR-002**: The system MUST chop PDF images into individual question images and student step images using coordinate bounding boxes.
- **FR-003**: The system MUST generate a single-page HTML application displaying the questions and student steps in chronological sequence.
- **FR-004**: The system MUST utilize an AI model to evaluate the math steps and determine which step is incorrect.
- **FR-005**: The system MUST display an explanation comment card directly beneath the incorrect step, highlighting the math error and detailing the correct step/answer.
- **FR-006**: The system HTML MUST use modern CSS (glassmorphism, CSS variables, Inter/Outfit typography, soft gradients) to provide a premium user experience.

### Key Entities

- **Question Image**: The image cropped from the PDF representing the math problem statement.
- **Student Step Image**: The image cropped from the PDF representing a single step of the student's solution.
- **Correction Comment**: An AI-generated text/formula explanation identifying the error in a step and providing the correction.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of questions and student steps are cropped and stored as high-quality PNGs.
- **SC-002**: 100% of math errors are identified, with a correction block inserted beneath the exact incorrect step.
- **SC-003**: The review page achieves 100% responsive layout parity on desktop and mobile.
- **SC-004**: Page loads in under 500ms with zero console errors.
