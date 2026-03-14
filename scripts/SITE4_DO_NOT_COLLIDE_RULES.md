# Site #4 — Do Not Collide Rules

> ⚠️ **MANDATORY — These rules apply to any new site in the ecosystem.**

## Absolute Prohibitions

### 1. Head Term Protection
Site #4 **MUST NEVER** target or compete for:
- `animatori petreceri copii` → **Superparty ONLY**
- `animatori copii bucuresti` → **Superparty ONLY**
- `animatori petreceri copii ilfov` → **Superparty ONLY**

Any page on Site #4 that starts ranking for these queries = **immediate remediation**.

### 2. Title Uniqueness
- Title overlap with ANY existing brand page: **MAX 40%**
- No two sites may have the same `<title>` format on their money pages
- No two sites may share the same H1

### 3. Meta Description Uniqueness
- Meta description overlap: **MAX 30%**
- Different value proposition angle required

### 4. Body Content Uniqueness
- Body text overlap with any brand: **MAX 40%**
- Unique examples, unique FAQ questions, unique CTA copy

### 5. FAQ Uniqueness
- At most 2 FAQ questions may overlap with another brand
- Answers must be **100% rewritten** even if the question is similar

### 6. CTA Uniqueness
- Different CTA text from all existing brands
- Different phone number or differentiating contact method

### 7. Package Structure
- Cannot copy package names from SP (Super 1/3/7), AN (Poveste/Magică/Aventură), or WP (Start/Plus/Complet/Mega)
- Must have its own naming convention
- Price points can overlap (same business), but framing must differ

## Overlap Thresholds (from Ecosystem Policy)

| Element | Max Overlap Allowed |
|---------|-------------------|
| Title tag | 40% |
| Meta description | 30% |
| Body content | 40% |
| FAQ content | 40% (max 2 shared questions) |
| CTA text | 0% (must be unique) |
| H1 | 0% (must be unique) |
| Package names | 0% (must be unique) |

## Enforcement
- Run uniqueness validator before any new page goes live
- CI check on PR must pass uniqueness thresholds
- Manual review required for any page targeting a query within 2 steps of an existing brand's primary cluster

## Collision Response Protocol
If a collision is detected after launch:
1. Identify the colliding pages and queries
2. Determine which brand has ownership priority
3. Apply the smallest safe correction to the newer/lower-priority page
4. Options: rewrite title/meta, adjust content angle, add `noindex` if unsalvageable
5. Re-verify with uniqueness validator
