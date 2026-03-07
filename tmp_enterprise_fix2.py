import os
import re

os.chdir(r"C:\Users\ursac\Superparty")

with open('agent/tasks/seo.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update titles in get_deterministic_payload
text = text.replace(
    '        "title": f"Animatori copii în {location_label} | Superparty",\n',
    '        "title": f"Animatori petreceri copii în {location_label} | Superparty",\n'
)
text = text.replace(
    '        elif page_type == "sector":\n            payload["title"] = f"Animatori copii Sector {slug.replace(\'sector-\', \'\')} București | Superparty"\n',
    '        elif page_type == "sector":\n            payload["title"] = f"Animatori petreceri copii Sector {slug.replace(\'sector-\', \'\')} București | Superparty"\n'
)

# 2. Update gate logic
# Find: min_chars = agent.common.env.getenv_int("SEO_REAL_MIN_TEXT_CHARS", 1000)
# Replace with 2500 default
text = text.replace(
    'min_chars = agent.common.env.getenv_int("SEO_REAL_MIN_TEXT_CHARS", 1000)',
    'min_chars = agent.common.env.getenv_int("SEO_REAL_MIN_TEXT_CHARS", 2500)'
)

# Update links count to absolute checks
old_gate = """        links_count = new_text.count('href="/')

        min_chars = agent.common.env.getenv_int("SEO_REAL_MIN_TEXT_CHARS", 2500)
        
        gate_passed = text_delta > min_chars and faq_count >= 4 and links_count >= 3"""

new_gate = """        links_count = new_text.count('href="/')

        min_chars = agent.common.env.getenv_int("SEO_REAL_MIN_TEXT_CHARS", 2500)
        
        required_links_present = (
            'href="/animatori-petreceri-copii"' in new_text and
            'href="/arie-acoperire"' in new_text and
            f'href="{payload["hub_url"]}"' in new_text
        )
        gate_passed = text_delta > min_chars and faq_count >= 4 and required_links_present"""

text = text.replace(old_gate, new_gate)

# 3. Update branch naming
old_pr = """        pr_url = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}",
            commit_msg=f"feat(seo): gsc apply real {date.today()}","""

new_pr = """        import time
        run_id = time.strftime("%H%M%S")
        pr_url = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}T{run_id}Z",
            commit_msg=f"feat(seo): gsc apply real {date.today()}T{run_id}Z","""
            
text = text.replace(old_pr, new_pr)

with open('agent/tasks/seo.py', 'w', encoding='utf-8') as f:
    f.write(text)

# Also update the tests
with open('tests/test_seo_enterprise.py', 'r', encoding='utf-8') as f:
    test_text = f.read()

test_text += """
def test_payload_types():
    manifest_data = {"ilfov_town": {"county": "Ilfov", "name": "Ilfov Town"}}
    pay_hub = get_deterministic_payload("ilfov", manifest_data)
    assert pay_hub["page_type"] == "hub_ilfov"
    
    pay_sec = get_deterministic_payload("sector-3", manifest_data)
    assert pay_sec["page_type"] == "sector"
    
    pay_loc = get_deterministic_payload("ilfov_town", manifest_data)
    assert pay_loc["page_type"] == "localitate_ilfov"
    
def test_insert_when_no_marker():
    text = "<Layout>\\n<h1>Hi</h1>\\n</Layout>"
    block = "<!-- SEO_INJECT_START:v1 -->\\nSEO BLOCK\\n<!-- SEO_INJECT_END:v1 -->"
    res = replace_or_insert_seo_block(text, block)
    assert "SEO BLOCK" in res
    assert res.endswith("</Layout>")
    
def test_required_links_present():
    html = '<a href="/animatori-petreceri-copii">Pilon</a> <a href="/arie-acoperire">Arie</a> <a href="/petreceri/ilfov">Hub</a>'
    assert 'href="/animatori-petreceri-copii"' in html
    assert 'href="/arie-acoperire"' in html
    assert 'href="/petreceri/ilfov"' in html
"""

with open('tests/test_seo_enterprise.py', 'w', encoding='utf-8') as f:
    f.write(test_text)
