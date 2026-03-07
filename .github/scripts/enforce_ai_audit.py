import subprocess
import sys
import os

def check_audit():
    try:
        result = subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD"], capture_output=True, text=True)
        if result.returncode != 0:
            result = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True)
            if result.returncode != 0:
                print("Not a git repository or diff failed. Skipping.")
                return 0
    except Exception as e:
        print(f"Git execution failed: {e}")
        return 0

    changed_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    ui_extensions = ('.svelte', '.html', '.css', 'tailwind.config')
    ui_files = [f for f in changed_files if any(f.endswith(ext) or ext in f for ext in ui_extensions)]
    
    if not ui_files:
        print("✅ No UI files changed. Manual AI audit not required.")
        return 0
        
    audit_file = "docs/ai_ui_audit.md"
    if not os.path.exists(audit_file):
        print("\n" + "="*80)
        print("🚨 AI BEHAVIORAL BLOCKER: MANUAL UI AUDIT REQUIRED 🚨")
        print("You (the AI) have modified UI files but have not provided a visual audit report.")
        print("MANDATORY ACTION INSTRUCTIONS FOR AI AGENT:")
        print("1. STOP writing code.")
        print("2. Spawn the `browser_subagent` tool to visually review your Svelte/CSS changes.")
        print("3. Explicitly verify Touch Targets (>=44px), Readability, and No-Horizontal-Scroll.")
        print("4. Update 'docs/ai_ui_audit.md' detailing your findings.")
        print("="*80 + "\n")
        return 1
        
    if "docs/ai_ui_audit.md" not in changed_files:
        print("\n" + "="*80)
        print("🚨 AI BEHAVIORAL BLOCKER: OUTDATED UI AUDIT 🚨")
        print("'docs/ai_ui_audit.md' exists but was NOT updated in this PR alongside the UI changes.")
        print("You must re-run the browser_subagent and append/update the audit file!")
        print("="*80 + "\n")
        return 1

    print("✅ AI UI Audit detected and validated. The AI has proven visual competence for this commit.")
    return 0

if __name__ == "__main__":
    sys.exit(check_audit())
