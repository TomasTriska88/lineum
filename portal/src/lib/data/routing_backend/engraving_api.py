import os
import uuid
import json
import hashlib
import zipfile
import asyncio
import numpy as np
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import shutil

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import CoreConfig, step_core
from routing_backend.text_to_wave_encoder import TextToWaveEncoder

router = APIRouter()

STAGING_DIR = "artifacts/staging"
JOBS_DIR = "artifacts/jobs"
IDENTITIES_DIR = "artifacts/identities"

os.makedirs(STAGING_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)
os.makedirs(IDENTITIES_DIR, exist_ok=True)

# In-memory job state for SSE streaming and cancellation
active_jobs: Dict[str, Dict] = {}

def _chunk_text(text: str, target_tokens: int = 600) -> List[Dict]:
    target_chars = target_tokens * 4
    paragraphs = text.split("\\n\\n")
    chunks = []
    current_chunk = ""
    start_offset = 0
    current_offset = 0
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < target_chars:
            if not current_chunk:
                start_offset = current_offset
            current_chunk += p + "\\n\\n"
            current_offset += len(p) + 2
        else:
            if current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "offsets": [start_offset, current_offset]
                })
            start_offset = current_offset
            current_chunk = p + "\\n\\n"
            current_offset += len(p) + 2
            
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "offsets": [start_offset, current_offset]
        })
        
    return chunks

def _classify_chunk(text: str) -> Dict:
    physics_keywords = [
        "physics", "ontology", "hypothesis", "equation", "mechanics", 
        "lineum", "tensor", "gradient", "manifold", "thermodynamics",
        "psi", "phi", "mu", "kappa", "determinism", "emergence", "fluid"
    ]
    text_lower = text.lower()
    
    hits = [kw for kw in physics_keywords if kw in text_lower]
    score = len(hits)
    
    if score >= 2:
        return {"category": "A", "why": {"score": score, "hits": hits}}
    elif score == 1:
        return {"category": "UNCERTAIN", "why": {"score": score, "hits": hits}}
    else:
        return {"category": "B", "why": {"score": score, "hits": hits}}

@router.post("/api/engraving/preview")
async def engrave_preview(file: UploadFile = File(...)):
    staging_id = str(uuid.uuid4())
    stage_path = os.path.join(STAGING_DIR, staging_id)
    os.makedirs(stage_path, exist_ok=True)
    
    file_path = os.path.join(stage_path, "upload.zip")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    blocks = []
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            for filename in zf.namelist():
                if not filename.endswith(('.txt', '.md')):
                    continue
                content = zf.read(filename).decode('utf-8')
                chunks = _chunk_text(content)
                
                for chunk in chunks:
                    block_id = f"blk_{uuid.uuid4().hex[:8]}"
                    sha256 = hashlib.sha256(chunk["text"].encode('utf-8')).hexdigest()
                    classification = _classify_chunk(chunk["text"])
                    
                    blocks.append({
                        "block_id": block_id,
                        "source_file": filename,
                        "text": chunk["text"],
                        "offsets": chunk["offsets"],
                        "sha256": sha256,
                        "category": classification["category"],
                        "why": classification["why"]
                    })
                    
        # Save blocks to staging for the run phase
        with open(os.path.join(stage_path, "blocks.json"), "w") as f:
            json.dump(blocks, f)
            
        return {"staging_id": staging_id, "blocks": blocks}
        
    except Exception as e:
        shutil.rmtree(stage_path, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(e))

class RunConfigRequest(BaseModel):
    stencil_type: str = "LAP4"
    encoder_version: str = "v1"
    personalization_depth: float = 1.0

class RunProcessRequest(BaseModel):
    staging_id: str
    overrides: Dict[str, str]  # block_id -> "A"|"B"
    config: RunConfigRequest
    identity_name: str = "anonymous"

async def offline_run_job(job_id: str, req: RunProcessRequest):
    try:
        stage_path = os.path.join(STAGING_DIR, req.staging_id)
        job_dir = os.path.join(JOBS_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        out_dir = os.path.join(IDENTITIES_DIR, f"identity_{req.identity_name}_{job_id[:8]}")
        os.makedirs(out_dir, exist_ok=True)
        
        with open(os.path.join(stage_path, "blocks.json"), "r") as f:
            blocks = json.load(f)
            
        audit_log = []
        context_chunks = []
        classification_report = []
        
        cfg = CoreConfig(
            use_mode_coupling=True, 
            use_mu=True,
            stencil_type=req.config.stencil_type
        )
        
        GRID_SIZE = 64
        state = {
            "psi": np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128),
            "phi": np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64),
            "kappa": np.ones((GRID_SIZE, GRID_SIZE), dtype=np.float64),
            "mu": np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64),
        }
        
        encoder = TextToWaveEncoder(grid_size=GRID_SIZE, plasticity_tau=200)

        total_blocks = len(blocks)
        current_block = None
        for i, block in enumerate(blocks):
            current_block = block
            if active_jobs[job_id]["cancel_requested"]:
                active_jobs[job_id]["status"] = "cancelled"
                return
                
            active_jobs[job_id]["progress"] = int((i / total_blocks) * 80)
            
            # Apply overrides or fallback to original
            final_cat = req.overrides.get(block["block_id"], block["category"])
            
            classification_report.append({
                "block_id": block["block_id"],
                "sha256": block["sha256"],
                "original_cat": block["category"],
                "final_cat": final_cat,
                "why": block["why"]
            })
            
            entry = {
                "block_id": block["block_id"],
                "category": final_cat,
                "sha256": block["sha256"]
            }
            
            if final_cat == "A":
                state, metrics = encoder.encode(
                    text=block["text"],
                    state=state,
                    cfg=cfg,
                    step_fn=step_core,
                    mode="identity_burn",
                    personalization_depth=req.config.personalization_depth
                )
                
                entry["auc_phi"] = metrics.get("auc_phi", 0.0)
                entry["auc_psi"] = metrics.get("auc_psi", 0.0)
                active_jobs[job_id]["logs"].append(f"Block {block['block_id'][:8]} baked into Mu. AUC(phi): {entry['auc_phi']:.2f}, AUC(psi): {entry['auc_psi']:.4f}")
                
            else:
                context_chunks.append({
                    "id": block["block_id"],
                    "content": block["text"],
                    "sha256": block["sha256"]
                })
                active_jobs[job_id]["logs"].append(f"Block {block['block_id'][:8]} appended to Context Library.")
                
            audit_log.append(entry)
            await asyncio.sleep(0.01)  # Yield explicitly for non-blocking Event Loop

        active_jobs[job_id]["progress"] = 85
        active_jobs[job_id]["logs"].append("Cooling Phase (200 ticks)...")
        state["delta"] = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
        for _ in range(200):
            state = step_core(state, cfg)
            
        active_jobs[job_id]["progress"] = 95
        
        # Output Bundling
        cfg_dict = {
            "encoder_version": req.config.encoder_version,
            "stencil": cfg.stencil_type,
            "dt": cfg.dt,
            "grid_size": GRID_SIZE,
            "personalization_depth": req.config.personalization_depth
        }
        cfg_dict["cfg_hash"] = hashlib.sha256(json.dumps(cfg_dict, sort_keys=True).encode()).hexdigest()
        
        np.savez_compressed(os.path.join(out_dir, f"identity_seed_{req.identity_name}.npz"), 
                            kappa=state["kappa"], mu=state["mu"], phi=state["phi"], 
                            psi_real=state["psi"].real, psi_imag=state["psi"].imag)
                            
        with open(os.path.join(out_dir, "cfg.json"), "w") as f:
            json.dump(cfg_dict, f, indent=2)
            
        with open(os.path.join(out_dir, "context.json"), "w", encoding="utf-8") as f:
            json.dump(context_chunks, f, indent=2, ensure_ascii=False)
            
        with open(os.path.join(out_dir, "audit_trace.log"), "w") as f:
            json.dump(audit_log, f, indent=2)
            
        with open(os.path.join(out_dir, "classification_report.json"), "w") as f:
            json.dump(classification_report, f, indent=2)

        active_jobs[job_id]["progress"] = 100
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["output_dir"] = out_dir
        active_jobs[job_id]["logs"].append("Memory Engraving Complete.")
        
    except Exception as e:
        import traceback
        err_str = traceback.format_exc()
        try:
            # Deterministic Crash Bundling
            crash_dir = os.path.join(JOBS_DIR, job_id, "crash_bundle")
            os.makedirs(crash_dir, exist_ok=True)
            
            with open(os.path.join(crash_dir, "crash_debug.log"), "w") as f:
                f.write(err_str)
                
            # 1. input_id + failing chunk
            with open(os.path.join(crash_dir, "failing_block.json"), "w") as f:
                json.dump(current_block if current_block else {"error": "Failed before block processing start"}, f, indent=2)
                
            # 2. cfg snapshot
            with open(os.path.join(crash_dir, "cfg_snapshot.json"), "w") as f:
                try:
                    from dataclasses import asdict
                    json.dump(asdict(cfg), f, indent=2)
                except Exception:
                    f.write(str(cfg))
                    
            # 3. Last 200 logs
            with open(os.path.join(crash_dir, "last_200_logs.log"), "w") as f:
                f.write("\\n".join(active_jobs[job_id]["logs"][-200:]))
                
            # 4. mu/phi SHAs
            with open(os.path.join(crash_dir, "physics_fingerprint.json"), "w") as f:
                json.dump({
                    "mu_sha": encoder._hash_array(state.get("mu", np.zeros_like(state["phi"]))),
                    "phi_sha": encoder._hash_array(state.get("phi")),
                    "psi_sha": encoder._hash_array(state.get("psi")),
                    "kappa_sha": encoder._hash_array(state.get("kappa"))
                }, f, indent=2)
        except Exception as bundle_err:
            print(f"Failed to create crash bundle: {bundle_err}")
            
        print("BACKGROUND JOB ERROR:")
        print(err_str)
        
        active_jobs[job_id]["status"] = "error"
        active_jobs[job_id]["logs"].append(f"Error: {str(e)}")

@router.post("/api/engraving/run")
async def engrave_run(req: RunProcessRequest, background_tasks: BackgroundTasks):
    try:
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        active_jobs[job_id] = {
            "status": "running",
            "progress": 0,
            "logs": ["Job started..."],
            "cancel_requested": False
        }
        
        background_tasks.add_task(offline_run_job, job_id, req)
        return {"job_id": job_id}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

@router.get("/api/engraving/stream/{job_id}")
async def stream_engraving(job_id: str):
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    async def event_generator():
        last_log_idx = 0
        while True:
            job = active_jobs.get(job_id)
            if not job:
                yield f"data: {json.dumps({'error': 'Job disappeared'})}\\n\\n"
                break
                
            logs_to_send = job["logs"][last_log_idx:]
            last_log_idx = len(job["logs"])
            
            payload = {
                "status": job["status"],
                "progress": job["progress"],
                "logs": logs_to_send
            }
            if "output_dir" in job:
                payload["output_dir"] = job["output_dir"]
                
            yield f"data: {json.dumps(payload)}\\n\\n"
            
            if job["status"] in ["completed", "error", "cancelled"]:
                break
                
            await asyncio.sleep(0.5)
            
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@router.post("/api/engraving/cancel/{job_id}")
async def cancel_job(job_id: str):
    if job_id in active_jobs:
        active_jobs[job_id]["cancel_requested"] = True
        return {"status": "cancelling"}
    raise HTTPException(status_code=404, detail="Job not found")

@router.delete("/api/engraving/job/{job_id}")
async def delete_job(job_id: str):
    if job_id in active_jobs:
        del active_jobs[job_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Job not found")
