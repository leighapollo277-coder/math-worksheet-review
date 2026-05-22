# Feature Specification: Circle Geometry Practice Question Generator

**Feature Branch**: `003-practice-questions`  
**Created**: 2026-05-22  
**Status**: Draft (Ready for Review)  
**Input**: Interactive UI on the "DSE Circle Geometry Grader" page.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accessing Practice Questions (Priority: P1)

As a student studying for the HKDSE Mathematics exam, I want to see a list of similar practice questions right after reviewing my graded worksheet, so that I can practice the concepts where I made mistakes.

**Why this priority**: Helps students apply feedback immediately. Without this, the feedback is passive; with practice questions, the portal becomes an active learning environment.

**Independent Test**: Verify that a new section named "Similar Practice Questions" appears at the bottom of the grader page, and is linked in the sidebar for quick navigation.

**Acceptance Scenarios**:
1. **Given** the grader page is loaded, **When** I scroll to the bottom or click the sidebar link "Practice & Reinforcement", **Then** the page smooth-scrolls to a dedicated practice section with a title and brief instructions.

---

### User Story 2 - Inline High-Fidelity SVG Diagrams (Priority: P1)

As a student, I want each practice question to include a clear, clean, and accurate geometry diagram showing the circle, lines, angles, and given values, so that I can visualize the problem.

**Why this priority**: Geometry questions cannot be solved without a diagram. Standard HTML text is insufficient; clean inline SVG elements ensure the diagram is sharp, scalable, and loads instantly.

**Independent Test**: Verify that every practice question displays a responsive, high-resolution SVG diagram depicting the geometric setup.

**Acceptance Scenarios**:
1. **Given** a practice question is displayed, **When** I look at the diagram, **Then** I see a circle with labeled points (e.g., $A$, $B$, $C$), chords, and angles corresponding to the values specified in the question text.

---

### User Story 3 - Interactive Toggleable Solutions with HKDSE Reasons (Priority: P1)

As a student, I want to attempt the question first and then click a button to view the correct answer and a step-by-step solution that includes standard HKEAA geometric reasons (such as `(opp. ∠s, cyclic quad.)`), so that I can verify my steps and learn the correct formatting.

**Why this priority**: Helps students self-assess and learn the specific justification phrases required to earn reason marks in the DSE.

**Independent Test**: Verify that clicking the "Show Solution" button for a question reveals a step-by-step breakdown using KaTeX formatting and official abbreviations in parentheses.

**Acceptance Scenarios**:
1. **Given** a practice question, **When** I click "Show Solution", **Then** the button text changes to "Hide Solution", and a detailed solution card slides down showing KaTeX math expressions and standard reasons.

---

### User Story 4 - Dynamic "Generate More" Practice Questions (Priority: P1)

As a student who wants more practice, I want to click a button to load more similar questions, so that I can continue practicing with different numbers and scenarios.

**Why this priority**: Students need repetitive practice to master geometry theorems. Static pages limit practice; dynamic loading offers a richer pool of questions.

**Independent Test**: Verify that clicking "Generate More Questions" dynamically appends new, distinct circle geometry questions with SVGs and solutions.

**Acceptance Scenarios**:
1. **Given** 3 initial practice questions are loaded, **When** I click "Generate More Questions", **Then** the page dynamically instantiates one or more new questions from a client-side question pool, maintaining the same visual design.

---

### Edge Cases

- **Missing KaTeX rendering**: Ensure dynamically generated/appended equations are processed by KaTeX's auto-render script so they display as formatted math.
- **Responsive SVGs**: Ensure SVGs scale down cleanly on narrow mobile viewports without cropping the label text.
- **Exhausted Pool**: When all questions in the client-side bank are exhausted, the "Generate More" button should either randomize values of existing questions or disable itself gracefully with a polite message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST display a dedicated section titled "Similar Practice Questions" at the bottom of the dashboard page.
- **FR-002**: The system MUST render 3 initial practice questions, one corresponding to each of the primary grader questions:
  - **PQ1 (Similar to Q8)**: Circle geometry with similar triangles (requiring proofs/ratios of corresponding sides).
  - **PQ2 (Similar to Q13)**: Circle geometry with sector perimeter/arcs (requiring arc length calculations).
  - **PQ3 (Similar to Q7)**: Circle geometry with angle properties (angles in semicircle, cyclic quadrilaterals, etc.).
- **FR-003**: Each question MUST include an inline, highly-styled SVG graphic displaying the geometric scenario (e.g. circle, labeled points, given angles, and segment lengths).
- **FR-004**: Each question MUST have a toggle button that expands/collapses a "Model Answer & Solution" panel.
- **FR-005**: All mathematical expressions in solutions MUST be written in LaTeX and rendered using KaTeX.
- **FR-006**: Model solutions MUST include HKEAA-approved geometric reasons in parentheses (e.g., `(opp. ∠s, cyclic quad.)`, `(∠ in semi-circle)`).
- **FR-007**: The system MUST provide a "Generate More Questions" button. Clicking this button dynamically adds questions to the feed from a client-side question pool.
- **FR-008**: The client-side question bank MUST contain at least 6 distinct additional questions (2 variations for each of the 3 topics) to support multiple clicks of the generation button.
- **FR-009**: The sidebar navigation MUST be updated to include a "Practice & Reinforcement" link that scrolls to the practice section.

### Key Entities

- **Practice Question**: An object containing ID, topic, question text, inline SVG representation, final answer, and step-by-step solution.
- **SVG Diagram**: SVG markup containing drawing elements (circle, path, text) that represents the geometric structure.
- **Solution Card**: A collapseable UI container displaying KaTeX math and text.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 3 practice questions are rendered immediately on page load.
- **SC-002**: Clicking "Show Solution" displays the step-by-step solution with KaTeX rendered math within 100ms.
- **SC-003**: The "Generate More Questions" button appends a new question with a distinct SVG diagram on each click until the bank is exhausted.
- **SC-004**: SVG coordinates, labels, and geometry lines are perfectly aligned and visible on all viewport widths down to 320px.
