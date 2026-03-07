import os
import subprocess

def run(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=False)

os.chdir(r"C:\Users\ursac\Superparty")

# PR A
run("git checkout agent/seo-local-intent")
with open('agent/tasks/seo.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'if m.get("county") == "Ilfov" and m.get("indexable") and m.get("place_type") in ("town", "commune"):',
    'if m.get("county", "").strip().lower() == "ilfov" and m.get("indexable") and m.get("place_type") in ("town", "commune", "city"):'
)

text = text.replace(
    'filtered_opps.sort(key=lambda x: (x.get("local_intent_score", 0), x.get("impressions", 0), -x.get("avg_position", 99)), reverse=True)',
    'filtered_opps.sort(key=lambda x: (-x.get("local_intent_score", 0), -x.get("impressions", 0), x.get("avg_position", 99)))'
)

with open('agent/tasks/seo.py', 'w', encoding='utf-8') as f:
    f.write(text)

run("git commit -am \"fix(seo): robust county parsing and explicit sort key\"")
run("git push origin agent/seo-local-intent")

# PR B
run("git checkout agent/seo-apply-real")
with open('agent/tasks/seo.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_func = """def seo_apply_task():
    import pathlib
    ga4_plans = sorted(pathlib.Path("reports/superparty").glob("seo_plan_ga4_*.json"), reverse=True)
    if ga4_plans:
        try:
            from agent.tasks.seo_ga4_patch import seo_apply_ga4_plan
            return seo_apply_ga4_plan(site_id="superparty")
        except Exception as e:
            pass
    return _orig_seo_apply_task()"""

new_func = """def seo_apply_task():
    import pathlib
    import os
    res = {}
    
    ga4_plans = sorted(pathlib.Path("reports/superparty").glob("seo_plan_ga4_*.json"), reverse=True)
    if ga4_plans:
        try:
            from agent.tasks.seo_ga4_patch import seo_apply_ga4_plan
            res["ga4"] = seo_apply_ga4_plan(site_id="superparty")
        except Exception as e:
            res["ga4_error"] = str(e)
            
    apply_mode = os.environ.get("SEO_APPLY_MODE", "report").strip()
    if apply_mode == "real" or not ga4_plans:
        res["gsc"] = _orig_seo_apply_task(apply_mode=apply_mode)
        
    if "ga4" in res and "gsc" not in res:
        return res["ga4"]
    if "gsc" in res and "ga4" not in res:
        return res["gsc"]
    return res"""

text = text.replace(old_func, new_func)

with open('agent/tasks/seo.py', 'w', encoding='utf-8') as f:
    f.write(text)

run("git commit -am \"fix(seo): allow GSC apply real mode even if GA4 plans exist\"")
run("git push origin agent/seo-apply-real")
run('gh pr create --base main --head agent/seo-apply-real --title "SEO: Apply real pentru GSC (Astro safe inject + quality gate)" --body "Apply mode=real: resolve Astro paths, inject frontmatter-safe title/desc + FAQ + links + logistică. PR-only, fără auto-index."')
