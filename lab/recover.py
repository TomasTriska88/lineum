import os
import re

user_profile = os.environ.get('USERPROFILE')
log_path = os.path.join(user_profile, '.gemini', 'antigravity', 'brain', '79a43cc7-a559-4fa6-b78e-376d8edea203', '.system_generated', 'logs', 'overview.txt')

print("Reading log from:", log_path)

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

lines_map = {}

block_pattern = re.compile(r"Showing lines (\d+) to (\d+)\n.*?<original_line>.*?\n(.*?)(?=\nThe above content)", re.DOTALL)
matches = list(block_pattern.finditer(text))
print(f"Found {len(matches)} view_file blocks in log.")

for match in matches:
    pre_text = text[max(0, match.start() - 500):match.start()]
    if "ValidationDashboard.svelte" in pre_text:
        content = match.group(3)
        for line in content.split('\n'):
            if ': ' in line:
                parts = line.split(': ', 1)
                if parts[0].isdigit():
                    num = int(parts[0])
                    lines_map[num] = parts[1]

print(f"Recovered {len(lines_map)} unique lines from view_file calls.")

diff_pattern = re.compile(r"\[diff_block_start\]\n(.*?)\n\[diff_block_end\]", re.DOTALL)
diff_matches = list(diff_pattern.finditer(text))
for match in diff_matches:
    diff_text = match.group(1)
    pre_text = text[max(0, match.start() - 500):match.start()]
    if "ValidationDashboard.svelte" in pre_text:
        hunks = re.split(r"@@ -(\d+),\d+ \+(\d+),\d+ @@", diff_text)
        if len(hunks) > 1:
            i = 1
            while i < len(hunks):
                old_start = int(hunks[i])
                new_start = int(hunks[i+1])
                hunk_lines = hunks[i+2].lstrip('\n').split('\n')
                
                curr_line = new_start
                for ln in hunk_lines:
                    if ln.startswith('+') or ln.startswith(' '):
                        lines_map[curr_line] = ln[1:]
                        curr_line += 1
                i += 3

print(f"Recovered {len(lines_map)} unique lines total.")

if len(lines_map) > 0:
    max_line = max(lines_map.keys())
    out = []
    missing = 0
    for i in range(1, max_line + 1):
        if i in lines_map:
            out.append(lines_map[i])
        else:
            out.append(f"/* MISSING LINE {i} */")
            missing += 1
    
    with open("ValidationDashboard_recovered.svelte", "w", encoding="utf-8") as f:
        f.write('\n'.join(out))
    
    print(f"Saved to ValidationDashboard_recovered.svelte. Missing {missing} lines.")
