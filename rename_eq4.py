import os
import glob

def replace_in_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We only want to replace imports and the names
    new_content = content.replace('Eq4Config', 'CoreConfig')
    new_content = new_content.replace('step_eq4', 'step_core')
    
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {path}")

dirs_to_search = ['lineum_core', 'tests', 'scripts', 'portal', 'lab']

for d in dirs_to_search:
    for root, _, files in os.walk(d):
        for file in files:
            if file.endswith('.py') or file.endswith('.js') or file.endswith('.ts') or file.endswith('.svelte'):
                replace_in_file(os.path.join(root, file))

for f in os.listdir('.'):
    if os.path.isfile(f) and f.endswith('.py') and f != 'rename_eq4.py':
        replace_in_file(f)

print("Done.")
