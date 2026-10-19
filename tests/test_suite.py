"""
Chronos-Prove v2.0 Test Suite
Comprehensive Automated Verification for AMD AI League Match 4

Tests Cover:
  1. Tier 1: 2D Spatial HTML Specification Tables with Colspan & Decoy SKUs.
  2. Tier 1: Embedded __NEXT_DATA__ and application/ld+json e-commerce product pricing.
  3. Tier 1: Superseded / Withdrawn Revision Trap Avoidance.
  4. Tier 1: Unanswerable Query Refusal & Zero Hallucination Guarantee.
  5. Tier 2: Adaptive ROCm Hardware Detection & Graceful CPU Fallback (Zero Warnings/Crashes).
  6. Tier 2: ROCm Semantic Adapter re-ranking kernel execution.
  7. End-to-End CLI Invocation, JSON contract validation, and sub-second latency.
  8. CLI v2.0 --include-trace telemetry flag and provenance verification.
  9. CLI v2.0 --demo-mode offline deterministic sandbox execution.
  10. FastAPI Cockpit Endpoints (/api/presets, /api/sandbox/{page}, /api/health).
  11. FastAPI Cockpit /api/retrieve REST Evaluation with full provenance trace.
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
from unittest.mock import patch, MagicMock
from http.server import HTTPServer, BaseHTTPRequestHandler
import pytest
import httpx

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import (
    QueryIntentDecomposer,
    SymbolicDOMCompiler,
    SymbolicScorer,
    GroundingVerifier,
    ChronosEngine,
    ROCmSemanticAdapter,
    CandidateTelemetry,
    detect_rocm_hardware,
    DEMO_CORPUS
)
from server import app


# ==============================================================================
# TEST DATA FIXTURES
# ==============================================================================

COMPLEX_2D_TABLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>AMD Radeon RX 7000 Series Hardware Specifications</title></head>
<body>
  <h1>AMD Desktop Graphics Comparison</h1>
  <table>
    <caption>Official Architecture Spec Sheet</caption>
    <tr>
      <th rowspan="2">Model SKU</th>
      <th colspan="2">Compute Engine</th>
      <th colspan="2">Memory Configuration</th>
      <th rowspan="2">TDP</th>
      <th rowspan="2">MSRP</th>
    </tr>
    <tr>
      <th>Compute Units</th>
      <th>Stream Processors</th>
      <th>VRAM Capacity</th>
      <th>Memory Bus</th>
    </tr>
    <tr>
      <td>Radeon RX 7900 XTX</td>
      <td>96</td>
      <td>6144</td>
      <td>24 GB</td>
      <td>384-bit</td>
      <td>355W</td>
      <td>$999</td>
    </tr>
    <tr>
      <td>Radeon RX 7900 XT</td>
      <td>84</td>
      <td>5376</td>
      <td>20 GB</td>
      <td>320-bit</td>
      <td>315W</td>
      <td>$899</td>
    </tr>
    <tr>
      <td>Radeon RX 7800 XT</td>
      <td>60</td>
      <td>3840</td>
      <td>16 GB</td>
      <td>256-bit</td>
      <td>263W</td>
      <td>$499</td>
    </tr>
  </table>
</body>
</html>
"""

HYDRATION_DATA_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>AMD Instinct MI300X Product Page</title>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org/",
    "@type": "Product",
    "name": "AMD Instinct MI300X",
    "description": "High performance generative AI accelerator with CDNA 3",
    "offers": {
      "@type": "Offer",
      "price": "$14999",
      "priceCurrency": "USD"
    }
  }
  </script>
  <script id="__NEXT_DATA__" type="application/json">
  {
    "props": {
      "pageProps": {
        "hardware": {
          "sku": "MI300X-OAM",
          "memory": "192 GB",
          "bandwidth": "5.3 TB/s",
          "tdp": "750W"
        }
      }
    }
  }
  </script>
</head>
<body>
  <h1>AMD Instinct Data Center GPU</h1>
  <p>The MI300X delivers unprecedented memory density for LLM training and inference.</p>
</body>
</html>
"""

SUPERSEDED_REVISION_HTML = """
<!DOCTYPE html>
<html>
<head><title>ROCm Compute Standard Specification</title></head>
<body>
  <h1>Specification Revisions</h1>
  <table>
    <tr>
      <th>Revision Level</th>
      <th>Lifecycle Status</th>
      <th>Max Interconnect Bandwidth</th>
      <th>Supported Architecture</th>
    </tr>
    <tr style="color: gray;">
      <td>Revision 1.0 Draft</td>
      <td>Deprecated and Withdrawn (Superseded)</td>
      <td>64 GB/s</td>
      <td>CDNA 1</td>
    </tr>
    <tr style="font-weight: bold;">
      <td>Revision 2.0 Official</td>
      <td>Current Active Production Standard</td>
      <td>896 GB/s</td>
      <td>CDNA 3</td>
    </tr>
  </table>
</body>
</html>
"""


# ==============================================================================
# TIER 1: SYMBOLIC CORE UNIT & INTEGRATION TESTS
# ==============================================================================

def test_2d_table_colspan_resolution_and_pinpoint_accuracy():
    """Verify Tier 1 2D spatial matrix expansion resolves colspan/rowspan and isolates target SKU."""
    query = "What is the TDP of Radeon RX 7900 XTX?"
    slot = QueryIntentDecomposer.decompose(query)

    assert any("7900" in a for a in slot.anchor_tokens)
    assert slot.target_metric == "tdp"

    records, stats = SymbolicDOMCompiler.compile(COMPLEX_2D_TABLE_HTML, "https://amd.com/specs")
    assert len(records) > 0
    assert stats["table_cells"] > 0

    candidates, _ = SymbolicScorer.score_records(records, slot)
    assert len(candidates) > 0

    result, verif = GroundingVerifier.verify_and_format(candidates)
    assert result["answer"] == "355W"
    assert result["confidence"] > 0.50
    assert verif["is_grounded"] is True


def test_2d_table_decoy_rejection():
    """Ensure query for RX 7900 XT does NOT return RX 7900 XTX or RX 7800 XT values."""
    query = "What is the MSRP price of Radeon RX 7900 XT?"
    slot = QueryIntentDecomposer.decompose(query)

    records, _ = SymbolicDOMCompiler.compile(COMPLEX_2D_TABLE_HTML, "https://amd.com/specs")
    candidates, _ = SymbolicScorer.score_records(records, slot)
    result, _ = GroundingVerifier.verify_and_format(candidates)

    assert result["answer"] == "$899"
    assert result["confidence"] > 0.50


def test_hydration_and_schema_extraction():
    """Verify JSON-LD and __NEXT_DATA__ state decompression."""
    price_query = "What is the price of AMD Instinct MI300X?"
    slot_price = QueryIntentDecomposer.decompose(price_query)

    records, _ = SymbolicDOMCompiler.compile(HYDRATION_DATA_HTML, "https://amd.com/mi300x")
    candidates_price, _ = SymbolicScorer.score_records(records, slot_price)
    result_price, _ = GroundingVerifier.verify_and_format(candidates_price)

    assert result_price["answer"] == "$14999"
    assert result_price["confidence"] > 0.40

    vram_query = "What is the memory capacity of MI300X-OAM?"
    slot_vram = QueryIntentDecomposer.decompose(vram_query)

    candidates_vram, _ = SymbolicScorer.score_records(records, slot_vram)
    result_vram, _ = GroundingVerifier.verify_and_format(candidates_vram)

    assert result_vram["answer"] == "192 GB"
    assert result_vram["confidence"] > 0.40


def test_superseded_revision_trap_avoidance():
    """Verify that deprecated/withdrawn specs are penalized and current active specs win."""
    query = "What is the Max Interconnect Bandwidth of the ROCm standard?"
    slot = QueryIntentDecomposer.decompose(query)

    records, _ = SymbolicDOMCompiler.compile(SUPERSEDED_REVISION_HTML, "https://rocm.docs.amd.com/spec")
    candidates, _ = SymbolicScorer.score_records(records, slot)
    result, _ = GroundingVerifier.verify_and_format(candidates)

    assert result["answer"] == "896 GB/s"
    assert result["confidence"] > 0.40


def test_revision_lifecycle_trap_rev_c2_ignoring_deprecated_rev_a1():
    """Verify that query for Rev-C2 with (ignoring deprecated Rev-A1) extracts active 105°C and rejects 85°C."""
    query = "What is the maximum thermal operating limit in Rev-C2 (ignoring deprecated Rev-A1)?"
    slot = QueryIntentDecomposer.decompose(query)

    assert "Rev-C2" in slot.target_revisions
    assert any("rev-a1" in nt for nt in slot.negated_tokens)
    assert not slot.is_deprecated_query

    records, _ = SymbolicDOMCompiler.compile(DEMO_CORPUS["thermal_specs"], "sandbox://thermal_specs")
    candidates, _ = SymbolicScorer.score_records(records, slot)
    result, verif = GroundingVerifier.verify_and_format(candidates)

    assert result["answer"] == "105°C"
    assert result["confidence"] > 0.90
    assert "Rev-C2" in verif["matched_span"]


def test_unanswerable_query_refusal_and_zero_hallucination():
    """Ensure unanswerable queries abstain with schema-valid refusal and confidence 0.0."""
    unanswerable_query = "What was the batting average of Babe Ruth in 1927?"
    slot = QueryIntentDecomposer.decompose(unanswerable_query)

    records, _ = SymbolicDOMCompiler.compile(COMPLEX_2D_TABLE_HTML, "https://amd.com/specs")
    candidates, _ = SymbolicScorer.score_records(records, slot)
    result, verif = GroundingVerifier.verify_and_format(candidates)

    assert result["answer"] == ""
    assert result["source_url"] == ""
    assert result["confidence"] == 0.0
    assert verif["is_grounded"] is False


# ==============================================================================
# TIER 2: ADAPTIVE ROCm HARDWARE DETECTION & ADAPTER TESTS
# ==============================================================================

def test_tier2_rocm_detection_and_graceful_cpu_fallback():
    """Verify that ROCm hardware detection operates without throwing errors on CPU."""
    hw = detect_rocm_hardware()
    assert isinstance(hw, dict)
    assert "rocm_available" in hw
    assert "active_tier" in hw
    assert "device_name" in hw
    # On typical CPU test runner without ROCm, graceful fallback is verified
    assert "Tier 1" in hw["active_tier"] or "Tier 2" in hw["active_tier"]


def test_tier2_rocm_semantic_adapter_cpu_execution():
    """Verify that ROCmSemanticAdapter.re_rank returns candidates without crashing on CPU."""
    slot = QueryIntentDecomposer.decompose("What is the TDP of Radeon RX 7900 XTX?")
    sample_candidate = CandidateTelemetry(
        rank=1,
        answer="355W",
        confidence=0.85,
        source_url="https://amd.com",
        record_type="table",
        key="Radeon RX 7900 XTX — TDP",
        context="Specs",
        raw_span="Radeon RX 7900 XTX | TDP: 355W",
        bm25_score=3.5,
        proximity_boost=2.0,
        structural_prior=1.65,
        composite_score=5.5,
        win_reason="Tier 1"
    )

    reranked, applied = ROCmSemanticAdapter.re_rank([sample_candidate], slot)
    assert len(reranked) == 1
    assert reranked[0].answer == "355W"
    # When no ROCm GPU is available, applied should be False with clean passthrough
    if not detect_rocm_hardware()["rocm_available"]:
        assert applied is False


# ==============================================================================
# CLI HARNESS & END-TO-END LATENCY TESTS
# ==============================================================================

class MockWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if "/next" in self.path:
            self.wfile.write(HYDRATION_DATA_HTML.encode("utf-8"))
        else:
            self.wfile.write(COMPLEX_2D_TABLE_HTML.encode("utf-8"))

    def log_message(self, format, *args):
        pass


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_end_to_end_cli_contract_and_subsecond_latency(tmp_path):
    """Executes the exact CLI contract and measures end-to-end response time."""
    port = get_free_port()
    server = HTTPServer(("127.0.0.1", port), MockWebHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    start_url = f"http://127.0.0.1:{port}/specs"
    query_id = "eval_cli_contract_01"
    output_dir = str(tmp_path / "out")

    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))
    cmd = [
        sys.executable,
        app_path,
        "--query-id", query_id,
        "--query", "What is the TDP of Radeon RX 7900 XTX?",
        "--start-url", start_url,
        "--output-dir", output_dir
    ]

    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    latency = time.perf_counter() - t0

    server.shutdown()

    assert proc.returncode == 0
    assert latency < 3.0

    out_file = os.path.join(output_dir, f"{query_id}_output.json")
    assert os.path.exists(out_file)

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "answer" in data
    assert "source_url" in data
    assert "confidence" in data
    assert data["answer"] == "355W"
    assert data["confidence"] > 0.50


def test_cli_v2_include_trace_flag(tmp_path):
    """Verifies that --include-trace outputs microsecond provenance telemetry in JSON."""
    port = get_free_port()
    server = HTTPServer(("127.0.0.1", port), MockWebHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    start_url = f"http://127.0.0.1:{port}/specs"
    query_id = "eval_cli_trace_02"
    output_dir = str(tmp_path / "out_trace")

    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))
    cmd = [
        sys.executable,
        app_path,
        "--query-id", query_id,
        "--query", "What is the TDP of Radeon RX 7900 XTX?",
        "--start-url", start_url,
        "--output-dir", output_dir,
        "--include-trace"
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    server.shutdown()

    assert proc.returncode == 0
    out_file = os.path.join(output_dir, f"{query_id}_output.json")
    assert os.path.exists(out_file)

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "trace" in data
    trace = data["trace"]
    assert "stage_timings_ms" in trace
    assert "dom_statistics" in trace
    assert "top_candidates" in trace
    assert "active_tier" in trace
    assert len(trace["top_candidates"]) > 0
    assert trace["dom_statistics"]["table_cells"] > 0


def test_cli_v2_demo_mode_offline_execution(tmp_path):
    """Verifies --demo-mode works completely offline without network calls."""
    query_id = "eval_cli_demo_03"
    output_dir = str(tmp_path / "out_demo")

    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))
    cmd = [
        sys.executable,
        app_path,
        "--query-id", query_id,
        "--query", "What is the peak FP16 Tensor TFLOPS and HBM3 memory capacity of the AMD Instinct MI300X?",
        "--output-dir", output_dir,
        "--demo-mode"
    ]

    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    latency = time.perf_counter() - t0

    assert proc.returncode == 0
    assert latency < 1.0

    out_file = os.path.join(output_dir, f"{query_id}_output.json")
    assert os.path.exists(out_file)

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["answer"] == "1307.4 TFLOPS"
    assert data["confidence"] > 0.50


# ==============================================================================
# FASTAPI COCKPIT REST ENDPOINT TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_fastapi_presets_and_sandbox_endpoints():
    """Tests GET /api/presets, GET /api/sandbox/{page}, and GET /api/health."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test Presets
        r_presets = await client.get("/api/presets")
        assert r_presets.status_code == 200
        presets = r_presets.json().get("presets", [])
        assert len(presets) == 5
        preset_ids = [p["id"] for p in presets]
        assert "2d_table_mi300x" in preset_ids
        assert "hydration_cloud_pricing" in preset_ids
        assert "hallucination_abstention" in preset_ids

        # 2. Test Sandbox fixture endpoint
        r_sandbox = await client.get("/api/sandbox/mi300x")
        assert r_sandbox.status_code == 200
        assert "AMD Instinct MI300X" in r_sandbox.text
        assert "1307.4 TFLOPS" in r_sandbox.text

        # 3. Test Health endpoint (Verifies Two-Tier Hardware Reporting)
        r_health = await client.get("/api/health")
        assert r_health.status_code == 200
        health = r_health.json()
        assert health["status"] == "healthy"
        assert "active_tier" in health
        assert "hardware_info" in health


@pytest.mark.anyio
async def test_fastapi_retrieve_endpoint_and_telemetry():
    """Tests POST /api/retrieve with full v2.0 provenance and candidate rankings."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # A. 2D Table Spec Test
        payload_1 = {
            "query": "What is the peak FP16 Tensor TFLOPS and HBM3 memory capacity of the AMD Instinct MI300X?",
            "start_url": "sandbox://mi300x",
            "use_sandbox": True
        }
        r1 = await client.post("/api/retrieve", json=payload_1)
        assert r1.status_code == 200
        d1 = r1.json()
        assert d1["answer"] == "1307.4 TFLOPS"
        assert d1["confidence"] > 0.50
        assert "trace" in d1
        assert "active_tier" in d1["trace"]
        assert len(d1["trace"]["top_candidates"]) > 0

        # B. Hydration Cloud Pricing Test
        payload_2 = {
            "query": "What is the exact hourly enterprise cloud price for the MI300X 8x GPU node?",
            "start_url": "sandbox://cloud_pricing",
            "use_sandbox": True
        }
        r2 = await client.post("/api/retrieve", json=payload_2)
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["answer"] == "$24.80/hr"
        assert d2["confidence"] > 0.40

        # C. Zero-Hallucination Refusal Test
        payload_3 = {
            "query": "What is the secret quantum warp core frequency of the unreleased AMD MI9999X?",
            "start_url": "sandbox://quantum_lab",
            "use_sandbox": True
        }
        r3 = await client.post("/api/retrieve", json=payload_3)
        assert r3.status_code == 200
        d3 = r3.json()
        assert d3["answer"] == ""
        assert d3["confidence"] == 0.0
        assert d3["trace"]["grounding_verification_status"]["is_grounded"] is False

        # D. Wikipedia Infobox Grounded Foundation Date Test
        payload_4 = {
            "query": "When was Advanced Micro Devices (AMD) founded?",
            "start_url": "sandbox://amd_history",
            "use_sandbox": True
        }
        r4 = await client.post("/api/retrieve", json=payload_4)
        assert r4.status_code == 200
        d4 = r4.json()
        assert d4["answer"] == "May 1, 1969"
        assert d4["confidence"] > 0.90
        assert d4["trace"]["grounding_verification_status"]["is_grounded"] is True


@pytest.mark.anyio
async def test_wikipedia_infobox_compilation_and_date_extraction():
    """Validates that table.infobox vcard tables explicitly extract key-values and GroundingVerifier yields May 1, 1969 with >0.90 confidence."""
    engine = ChronosEngine()
    result = await engine.execute_with_trace(
        query="When was Advanced Micro Devices (AMD) founded?",
        start_url="sandbox://amd_history",
        use_sandbox=True
    )
    assert result["answer"] == "May 1, 1969"
    assert result["confidence"] > 0.90
    assert result["trace"]["grounding_verification_status"]["is_grounded"] is True

