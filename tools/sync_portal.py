import json
import re
import os
import sys

# Paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARAMS_PATH = os.path.join(ROOT, "portal", "static", "portal_params.json")
SHADER_PATH = os.path.join(ROOT, "portal", "src", "lib", "components", "FieldShader.svelte")

def check_sync():
    """
    Checks if the GLSL #define constants in FieldShader.svelte match 
    the exported parameters from lineum.py.
    """
    if not os.path.exists(PARAMS_PATH):
        print(f"❌ portal_params.json not found at {PARAMS_PATH}.")
        print("   Run 'python lineum.py' to generate parameters.")
        return False
    
    try:
        with open(PARAMS_PATH, "r", encoding="utf-8") as f:
            params = json.load(f)
    except Exception as e:
        print(f"❌ Failed to parse portal_params.json: {e}")
        return False
        
    if not os.path.exists(SHADER_PATH):
        print(f"❌ FieldShader.svelte not found at {SHADER_PATH}.")
        return False
        
    try:
        with open(SHADER_PATH, "r", encoding="utf-8") as f:
            shader_content = f.read()
    except Exception as e:
        print(f"❌ Failed to read FieldShader.svelte: {e}")
        return False
        
    # Mapping between GLSL defines and JSON parameter keys
    mapping = {
        "DISSIPATION_RATE": "dissipation_rate",
        "REACTION_STRENGTH": "reaction_strength",
        "PSI_PHI_COUPLING": "psi_phi_coupling",
        "PHI_INTERACTION_STRENGTH": "phi_interaction_strength",
        "PHI_DIFFUSION": "phi_diffusion",
        "PSI_DIFFUSION": "psi_diffusion",
        "VACUUM_FLUCTUATION": "noise_strength"
    }
    
    mismatches = []
    
    print(f"🔍 Checking synchronicity (Core v{params.get('version', 'unknown')})...")
    
    for glsl_name, json_name in mapping.items():
        # Match #define NAME VALUE (handling scientific notation and trailing semicolons/comments)
        pattern = rf"#define\s+{glsl_name}\s+([\d\.e\-]+)"
        match = re.search(pattern, shader_content)
        
        if match:
            glsl_val = float(match.group(1))
            json_val = float(params[json_name])
            
            # Tolerance to allow for slight rounding or precision differences
            tolerance = max(abs(json_val) * 0.01, 1e-7)
            
            if abs(glsl_val - json_val) > tolerance:
                mismatches.append(f"{glsl_name}: Shader={glsl_val}, Core={json_val}")
            else:
                # print(f"  ✅ {glsl_name} is in sync.")
                pass
        else:
            mismatches.append(f"{glsl_name}: NOT FOUND in shader GLSL.")
            
    if mismatches:
        print("\n🚨 [VISUAL DRIFT DETECTED] Portal visuals are out of sync with Lineum Core!")
        for m in mismatches:
            print(f"  - {m}")
        print("\n👉 To fix: Update #define values in FieldShader.svelte to match portal_params.json.")
        return False
    
    print("\n✨ [SUCCESS] Portal visuals are perfectly synchronized with Lineum Core.")
    return True

if __name__ == "__main__":
    success = check_sync()
    sys.exit(0 if success else 1)
