import subprocess

with open("tests_output_summary.txt", "w", encoding="utf-8") as f:
    f.write('===== 1. PYTEST =====\n')
    r1 = subprocess.run(['python', '-m', 'pytest', 'tests/test_seo_enterprise.py', '-v'], capture_output=True, text=True)
    f.write(r1.stdout + '\n')
    if r1.stderr: f.write('STDERR:\n' + r1.stderr + '\n')
    
    f.write('===== 2. BUILD =====\n')
    r2 = subprocess.run(['pnpm', 'run', 'build'], capture_output=True, text=True)
    f.write('pnpm run build (Exit Code: ' + str(r2.returncode) + ')\n')
    # Can include tail of stdout if we want, but it's long. Let's just do exit code for build to avoid giant logs

    f.write('===== 3. QA SCRIPT =====\n')
    r3 = subprocess.run(['python', 'scripts/qa_enterprise.py'], capture_output=True, text=True)
    f.write(r3.stdout + '\n')
    if r3.stderr: f.write('STDERR:\n' + r3.stderr + '\n')
