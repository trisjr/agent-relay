---
name: wireframe-html
description: "Interactive grayscale HTML wireframes rendering real DOM elements. Use when you need clickable single-file HTML mockups of individual screens to validate layout and interaction with stakeholders — not for mapping screen-to-screen journeys (use /user-flow for that)."
metadata:
  phase: 05-screen-design
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /wireframe-html — Interactive Grayscale HTML Wireframe 🌟 [CORE WORKFLOW]

Interactive grayscale HTML wireframes rendering real DOM elements

## Objective
Provide expert BA guidance to execute `/wireframe-html`, creating self-contained, responsive, interactive browser wireframes. All UI copy, labels, and annotations inside the wireframe are written in Vietnamese, following the template.

## Mandatory Standards (Rules)
- `rules/13-wireframe-html-guidelines.md`
- `rules/16-ambiguity-detection-rules.md`

## Reference Template
- `_templates/31-wireframe-html.html`

## Default Storage Path
- `docs/{feature}/html-wireframe/{screen_name}.html`

## Expected Input
- Feature name and the list of screens requiring wireframes.
- Ideally the user flow output at `docs/{feature}/ui/user-flow.md` (from `/user-flow`) to derive screens and their interaction states.
- If input is missing, ask the user for it or report what is lacking — never invent requirements.

## Execution Workflow
1. Produce a single self-contained HTML file without external CDN dependencies.
2. Apply high-contrast grayscale palette per Rule 13.
3. Build semantic HTML5 forms and controls.
4. Embed minimal vanilla JavaScript to simulate UI state (modal popups, validation error highlights, submit feedbacks).
5. Save each screen to the Default Storage Path above.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Comply with the Rule 13 grayscale palette; the only permitted color exception is the error state (red `#EF4444` input borders, `#B91C1C` error text).
- [ ] Each screen is a single self-contained HTML file that opens directly in a browser.
- [ ] Wireframes cover all required UI states: Empty, Validated input, Error, and Modal popup.
- [ ] Save output at the designated repository path.
