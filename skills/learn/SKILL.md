---
name: learn
description: Teach RaLHF something new about you. Quick way to add context — just say "/learn" followed by what you want RaLHF to remember.
---

# Learn — Teach RaLHF Something New

The user wants to save a new piece of personal context to RaLHF. This is a fast path for adding information without going through a full conversation.

## What to do

1. Read what the user provided after `/learn`. It could be anything:
   - A preference: "/learn I prefer aisle seats on flights"
   - A fact: "/learn We just adopted a golden retriever named Scout"
   - A constraint: "/learn I'm lactose intolerant"
   - A goal: "/learn I'm training for a half marathon in June"
   - A habit: "/learn I meal prep every Sunday afternoon"

2. Call `remember` with a clear, specific note. Enrich the user's input slightly:
   - Add the date: "User adopted a golden retriever named Scout, March 2026"
   - Clarify if ambiguous: If they say "/learn allergic to nuts", ask "All tree nuts, or a specific type?"
   - Keep it factual — don't embellish or infer beyond what they said

3. Confirm the save: "Saved to RaLHF: [what was saved]. I'll use this in future conversations."

## Safety-critical information

If the user is saving an allergy, medical condition, or dietary restriction:
1. Save it immediately via `remember`
2. Confirm with emphasis: "Important — saved to RaLHF: [allergy/condition]. I'll always account for this."
3. If it contradicts existing context, also call `remember` with a correction note to update the old information.

## If no content is provided

If the user just types `/learn` with nothing after it:
- Ask: "What would you like me to remember? You can tell me a preference, fact, goal, or anything else about you."

## Multiple items

If the user provides several things at once ("/learn I'm vegan, I run 3x a week, and I hate horror movies"):
- Save each as a separate `remember` call for clean categorization
- Confirm all: "Saved 3 items to RaLHF: [list]."
