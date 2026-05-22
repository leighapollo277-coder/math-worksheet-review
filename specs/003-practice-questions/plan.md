# Implementation Plan: Circle Geometry Practice Question Generator

**Branch**: `003-practice-questions` | **Date**: 2026-05-22 | **Spec**: [spec.md](./spec.md)

## Summary

The goal of this feature is to add a dynamic "Similar Practice Questions" section to the **DSE Circle Geometry Grader** dashboard. This section will include:
1. **Three Initial Practice Questions** mapped directly to the topics of the graded worksheet (Q8: Similar Triangles, Q13: Arcs & Sectors, Q7: Angle Properties).
2. **High-Fidelity Inline SVG Diagrams** representing the geometry setup for each question.
3. **Interactive Toggleable Solution Cards** showing KaTeX-rendered step-by-step solutions and HKEAA-standard geometric reasons (e.g. `(opp. ∠s, cyclic quad.)`, `(∠ in semi-circle)`).
4. **A Dynamic "Generate More" System** that pulls additional questions with custom SVGs and solutions from a client-side JavaScript question bank when clicked.

---

## Technical Context

- **Target File**: `dse-circle-geometry/index.html`
- **Styling**: Vanilla CSS matching the glassmorphic dark theme.
- **Libraries**: KaTeX (already integrated for math rendering).
- **Diagram format**: Responsive inline SVG elements.
- **Client-Side Storage**: A JavaScript object array containing question configurations (id, topic, text, svgMarkup, solutionHtml, answer).

---

## Proposed Changes

### [MODIFY] [index.html](../../dse-circle-geometry/index.html)

- **Styles**:
  - Add practice section layout styles, toggle animations for solution cards, dynamic hover effects, and custom styles for the SVGs.
- **Sidebar**:
  - Add a navigation item `Practice Zone` pointing to `#practice-section` with an icon/badge.
- **Main Feed**:
  - Inject the practice section container `#practice-section` below the `#student-summary` section.
  - Render the 3 initial practice questions using the standard glassmorphic card style.
- **Script Block**:
  - Implement a JavaScript file-level script to:
    - Handle solution panel expand/collapse toggles with height transitions.
    - Hold the `PRACTICE_BANK` array of 6 extra questions (2 per topic).
    - Handle "Generate More" button clicks: pick the next question from the bank, render it in the DOM, call `renderMathInElement` on the new card, and update/disable the button if the bank is exhausted.

---

## Independent Auditor

### Summary of Friction
> [!WARNING]
> The primary friction is maintaining math rendering (KaTeX) and SVG responsiveness across all screen sizes for dynamically generated elements, while ensuring the mathematical correctness of the coordinates and geometric calculations in the diagrams.

### Agent Proposal
Insert the practice HTML and inline SVGs directly, write a basic toggle function, and store the extra questions in a simple JS array.

### Auditor's Challenge
1. **KaTeX Integration**: Dynamically appended HTML elements will not be parsed by the default KaTeX `auto-render` script. We must explicitly run `renderMathInElement` on the newly appended question card immediately after adding it to the DOM.
2. **SVG Text and Alignment**: SVGs containing text labels can look skewed or cut off on narrow viewports if they are not structured responsively. All SVGs must use `viewBox` attributes instead of fixed widths/heights.
3. **Geometric Accuracy**: The SVG diagrams must be mathematically plausible. For example, if an angle is labeled $90^\circ$ or $41^\circ$, the diagram lines should roughly match that geometric layout.

### Reconciled Plan
1. **Explicit KaTeX Rendering**: In the JavaScript generator function, invoke `renderMathInElement(newCard, { ... })` directly on the container of the newly appended question.
2. **Responsive viewBox SVGs**: Define all SVGs with `viewBox="0 0 400 300"` or `viewBox="0 0 400 400"`, setting width to `100%` and max-width to `400px` in CSS.
3. **Precise Coordinates**: Pre-calculate correct circle center, radius, and chord intersection coordinates for all SVGs so lines intersect precisely.

---

## Testability-First Analysis & Test Plan

### Testability Analysis
- The UI contains dynamic elements that can be tested programmatically by loading the page and checking the DOM state.
- Since we have `browser_use_agent` available, we can run browser-based checks to click the toggles, click "Generate More", and verify that everything displays cleanly.

### Test Plan

| Test Scenario | Trigger / Actions | Expected Output | Verification Method |
| --- | --- | --- | --- |
| **Verify Sidebar Navigation** | Click "Practice Zone" in sidebar | Page scrolls to `#practice-section` | Browser scrolls, URL changes to `#practice-section` |
| **Verify Solution Toggle** | Click "Show Solution" on a practice card | Solution card slides down and text is visible; button text updates to "Hide Solution" | Check DOM classes and visibility state of solution card |
| **Verify Dynamic Question Generation** | Click "Generate More Questions" | A 4th question card is added, containing its own SVG diagram | Check total question count in `#practice-container` increases to 4 |
| **Verify KaTeX Rendering of Dynamic Qs** | Generate dynamic question | Math symbols are rendered as KaTeX elements | Check for presence of `katex` classes in the newly generated card |
| **Verify Bank Exhaustion** | Click "Generate More Questions" multiple times | Button is disabled after 6 extra questions, displaying "All questions loaded!" | Check button attribute `disabled` and text content |
