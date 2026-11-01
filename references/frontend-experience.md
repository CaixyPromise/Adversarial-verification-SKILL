# Frontend Engineering & Experience Review

**When to read:** changed UI, interaction, copy, theme, client components or user-facing flows. Agent A reviews user requirements, interaction and language; Agent B reviews project components, style/design system and reuse; C reviews relevant accessibility/security/runtime risks.

## Preserve the existing visual and component system

Before evaluating a change, inspect one or two nearby production screens, current **theme, design tokens, layout/density, typography, spacing, colors, breakpoints, navigation and interaction patterns**. Prefer the **same** established design language unless the user explicitly asks for a redesign.

**Component choice:** existing project component → already-installed design-system/library component → composition of existing primitives → custom component **only with a real gap or explicit request**. Do not rebuild an existing Ant Design/MUI/Element Plus/etc. form, table, button, dialog or selector with a visually inconsistent hand-written HTML/CSS imitation. This does **not** ban semantic native HTML; it remains appropriate for accessible structure/simple content and must not be replaced by a custom inaccessible `div` control. Avoid new heavy dependencies for small tasks.

Inspect feedback states (loading, empty, error, success, disabled), real keyboard/focus behavior, responsive/overflow behavior and consistent terminology where affected.

## Interaction: simple for users, complexity for engineering

- Keep frequent operations close to the user's work; make the primary action obvious, with clear state changes and recoverability.
- For normal user journeys, **avoid more than three successive navigation/modal/drill-down levels by default**. This is a UX heuristic, **not a DOM depth rule** and not a ban on complex workflows; use clear information architecture when complexity is legitimate.
- Avoid nested dialogs, unnecessary confirmation steps, duplicate controls and walls of technical options. Use progressive disclosure only where it improves comprehension.
- Use understandable **user language**: "保存", "重试", "没有找到数据", "权限不足" instead of implementation narration ("DTO", "hydration", "RPC", "幂等性", "状态机") for nontechnical users. Developer/operator tools may legitimately retain precise technical terms.
- Where possible, review the actual rendered UI and a representative interaction, not only the source code.

## Final-artifact purity: no AI-conversation residue in the UI

**Critical rule:** The final product page must describe **the product and its user task**, never narrate temporary options, rejected designs or the AI/user discussion that led to them.

This covers **titles, subtitles, headings, badges, tabs, filter labels, tooltips, empty states, demo text, visible metadata, notifications, button labels and descriptive captions**.

| Wrong: conversation leaked into UI | Correct: clean product copy |
| --- | --- |
| `用户管理（无显示 ID 版）` | `用户管理` |
| `订单列表（已移除调试按钮）` | `订单列表` |
| `新方案 B 的工作台（按要求无侧栏）` | `工作台` |
| `数据列表（不是旧版实现）` | `数据列表` |

A user asking **not to show ID** means omit the ID where appropriate, **not** print "no-ID version" in the page title or subtitle. The clean final label should make sense to someone who never participated in design discussions. Similarly, do not turn implementation details into UI explanations merely to prove the AI listened.

**Review technique:** read modified JSX/TSX/Vue/template/i18n strings and inspect the rendered page (if available). Look for parenthetical "已去除…/不显示…/方案A/B/按要求…/不是旧版…" qualifiers, internal technical jargon and phrases addressed to the assistant. Determine whether the text communicates genuine user value or is merely commentary about design decisions. **Do not blindly blacklist words** such as "无数据", "版本" or important IDs: a real user task, safety notice, required field, version number or explicit comparison may need them.

**Avoid implementing the discussion as a feature:** A request to hide an ID usually means omit the field, not create a new `hideId` toggle or `user-without-id` component. Rejecting a modal does not justify a parallel `nonModal` component framework. Prefer the smallest existing interaction that meets the user-facing requirement; add optional modes or compatibility paths only for an actual stable use case.

**Three tests:** Would the result make sense to a user unaware of the discussion? Does the extra copy or mechanism correspond to a genuine product requirement? Can it be removed without changing requested behavior? Do not mechanically reject legitimate status labels, version identifiers, safety disclosures or explicit comparisons.

**Outside the UI:** avoid echoing rejected **session-only** alternatives into irrelevant metadata, commit or PR text and routine handoff. **Preserve** information legitimately required for security, accuracy, migrations, compatibility, audit, source attribution or authorized review reports. Do not falsify repository history or remove mandatory evidence. This is artifact cleanliness, not censorship.

## Severity and exceptions

Broken primary flows, explicit requirement violations, misleading permission messages, inaccessible essential controls or severe UX regressions can block delivery with evidence. Cosmetic wording refinements and optional layout improvements are normally non-blocking. Ask for human confirmation only when a material product/UX policy choice cannot be resolved from existing requirements.

## Official references
- [Ant Design — Customize Theme](https://ant.design/docs/react/customize-theme/)
- [W3C WAI-ARIA APG — Read Me First](https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [NN/g — Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/)
