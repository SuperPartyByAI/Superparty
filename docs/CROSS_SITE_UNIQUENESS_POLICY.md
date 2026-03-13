# CROSS-SITE UNIQUENESS POLICY

## 1. Core Principle
Every page intended for indexation MUST provide unique value. Swapping ONLY the location, keyword, or brand name is strictly forbidden and constitutes "Thin Content / Doorway Pages".

## 2. Thresholds
Based on our `uniqueness.config.json`:
- **Full Page Similarity**: Must be **< 55%** overlap with any other page across `Superparty`, `WowParty`, and `Animatopia`.
- **Title Similarity**: Must be **< 70%** (some pattern repetition is expected, but must contain modifiers).
- **Meta Description**: Must be **< 75%**.
- **FAQ / CTA Blocks**: Must be **< 50-60%**. Exact copy-pasted FAQs across different cities are blocked.

## 3. Allowed Overlap (Allowlist)
The following elements are ignored by the similarity validator:
- Brand names (`Superparty`, `WowParty`, `Animatopia`).
- Geo-modifiers (`Bucuresti`, `Ilfov`, `Cluj`, sector numbers).
- Target keywords (e.g., `animatori copii`, `petreceri tematice`).
- Legal boilerplate, GDPR text.
- Contact primitives (Phone, Email, Address).

## 4. Enforcement (Fail-Closed)
If a page violates uniqueness:
1. It is **denied indexation** (`robots="noindex, follow"`).
2. It is **stripped from `sitemap.xml`**.
3. It triggers a warning in the build logs.
4. It requires editorial intervention to inject unique paragraphs, local testimonials, or specific venue details before it can be unlocked for Googlebot.
