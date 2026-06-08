# Feedback Rubric

Defines how to compute a 0–1 quality score for an extraction, and when to
emit feedback to the backend.

## Score Computation

The score is a weighted average of four signals:

| Signal | Weight | How to compute |
|---|---|---|
| Field fill rate | 0.40 | `filled_required / total_required`. If no required fields, use `filled_all / total_all`. |
| Type match rate | 0.25 | `fields_matching_expected_type / total_fields`. A "text" field returning a number is still valid; a "link" field returning plain text is not. |
| Schema match | 0.20 | 1.0 if `schema_hash` matches the recipe's current hash, 0.0 if it drifts (means field set changed). |
| Source health | 0.15 | Strategy-dependent — see Source Health table below. |

```
score = (fill_rate * 0.40)
      + (type_match * 0.25)
      + (schema_match * 0.20)
      + (source_health * 0.15)
```

### Source Health by Strategy

| Strategy | Score = 1.0 | Score = 0.0 |
|---|---|---|
| `dom_css` / `dom_xpath` | `selectors_resolved / total_selectors`. Counts every selector (including pagination, list container). | All selectors return null. |
| `api_direct` / `api_intercept` | Endpoint returns valid JSON with the expected structure matching `response_path`. | Endpoint returns non-JSON, 4xx/5xx, or response structure no longer matches `response_path`. |
| `embedded_json` | Script tag found and JSON parsed successfully at the expected `json_path`. | Script tag missing, JSON malformed, or `json_path` returns null. |
| `export_download` | Download triggered and file captured with expected format/structure. | Trigger element missing, download failed, or file format changed. |

Round to 2 decimal places.

## When to Emit Feedback

Emit a `save_extraction_feedback` call when ANY of these conditions are true:

| Condition | Severity | Notes |
|---|---|---|
| score < 1.0 | any | Any imperfection is worth recording for the refinement loop. |
| A `required` field returned null/empty | high | Add field name to `missing_fields`. |
| A selector returned elements but they were the wrong type | medium | Note in `notes`. |
| The page appeared paginated but pagination selector returned 0 | medium | Note in `notes`. |
| DOM truncation occurred during stripping | low | Note: "DOM was truncated to {n} chars". |
| Extraction used fallback selectors (not the primary CSS) | low | Note which fields used fallbacks. |

## Feedback Payload

```json
{
  "recipe_id": "uuid",
  "recipe_version": 3,
  "url": "https://example.com/page",
  "score": 0.85,
  "missing_fields": ["author", "published_date"],
  "extra_fields": ["related_links"],
  "notes": "Pagination selector returned 0 elements. Field 'author' fell back to a11y tree."
}
```

### Field Descriptions

- **missing_fields**: Field names from the recipe that returned null/empty
  despite being `required: true`, or that returned data failing type validation.
- **extra_fields**: Fields visible in the DOM (detected via the accessibility
  tree or common patterns) that the recipe doesn't capture. These hint at
  recipe expansion opportunities.
- **notes**: Free-text Claude-authored notes about what went wrong. Keep it
  factual and specific — the refinement agent will read this.

## Score Interpretation

| Score | Meaning | Action |
|---|---|---|
| 1.00 | Perfect extraction | No feedback emitted. Cache the data and move on. |
| 0.80–0.99 | Minor issues | Feedback emitted. Refinement may pick this up nightly. |
| 0.50–0.79 | Significant gaps | Feedback emitted with detailed notes. Refinement will target this recipe. |
| < 0.50 | Recipe is broken | Feedback emitted. Data is still cached (partial is better than nothing) but flagged as low-confidence. |

## Important

- Feedback writes should not block user output, but errors must be logged
  and retried once (see `references/completion-rubric.md` for the full
  verification checklist).
- Never surface the score or feedback details to the user unless they
  explicitly ask about extraction quality.
- A perfect score of 1.0 means no feedback is written — the happy path
  produces zero overhead.
