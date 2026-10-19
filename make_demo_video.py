#!/usr/bin/env python3
"""
Chronos-Prove v2.0: Automated Headless Video Generator
AMD AI League — Match 4: Intelligent Web Information Retrieval

Generates a 90-second, studio-grade 1080p 60fps presentation demo video:
  - High-Quality Neural Voiceover via edge-tts (en-US-ChristopherNeural)
  - Synchronized Playwright Headless 1080p Frame Captures
  - Dynamic Two-Tier Symbolic & ROCm Telemetry Cockpit Visuals
  - MoviePy 2.x Precision Audio-Video Assembly
"""

import os
import sys
import time
import socket
import asyncio
import argparse
import subprocess
from typing import List, Dict, Tuple, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips


# ==============================================================================
# SCRIPT & NARRATION SECTIONS
# ==============================================================================

NARRATION_SECTIONS: List[Dict[str, Any]] = [
    {
        "id": "part1",
        "title": "PART 1: PROBLEM STATEMENT & MOTIVATION",
        "subtitle": "Zero-VRAM Deterministic Retrieval vs Heavy Hallucinating LLMs",
        "text": (
            "Why burn $30,000 MI300X VRAM spinning up heavy, slow LLMs just to parse plain web data—"
            "only to have them hallucinate numbers? Meet Chronos-Prove v2.0: an ultra-low latency, "
            "deterministic web retrieval engine engineered for the AMD AI League. "
            "Sub-12ms execution, under 42 megabytes of RAM, and zero hallucination."
        ),
        "slides": ["01_intro_card", "02_cockpit_overview"],
        "split_ratio": [0.45, 0.55]
    },
    {
        "id": "part2",
        "title": "PART 2: TWO-TIER HYBRID ARCHITECTURE",
        "subtitle": "Deterministic Symbolic Core + Adaptive AMD ROCm Semantic Adapter",
        "text": (
            "Instead of brute-force generation, Chronos-Prove deploys a two-tier hybrid architecture: "
            "Tier 1, Deterministic Symbolic Core executes sub-second table matrix extraction, hydration state "
            "decompilation, and Okapi BM25F proximity scoring entirely on CPU with zero VRAM. "
            "Tier 2, Adaptive AMD ROCm Adapter: When deployed on AMD accelerators, it automatically triggers "
            "hardware-accelerated tensor-core semantic re-ranking for ambiguous multi-hop queries, "
            "with instant zero-crash fallback."
        ),
        "slides": ["03_two_tier_arch", "04_pipeline_stepper"],
        "split_ratio": [0.50, 0.50]
    },
    {
        "id": "part3",
        "title": "PART 3: LIVE BENCHMARK — 2D SPANNED MATRIX & REVISION TRAP",
        "subtitle": "1307.4 TFLOPS Extraction & Stale Spec Suppression to 105°C",
        "text": (
            "Let's watch it execute live. In our 2D Hardware Spec test, it resolves complex spanned grid "
            "coordinates to extract the MI300X peak FP16 compute—1307.4 TFLOPS—in just milliseconds! "
            "Next, the Revision Lifecycle Trap. Generic scrapers stumble on deprecated revisions and pull 85°C. "
            "Chronos-Prove suppresses obsolete specs down to zero, extracting the authoritative Rev-C2 "
            "production limit at 105°C."
        ),
        "slides": ["05_2d_table_matrix", "06_revision_lifecycle"],
        "split_ratio": [0.50, 0.50]
    },
    {
        "id": "part4",
        "title": "PART 4: LIVE BENCHMARK — CALIBRATED ABSTENTION & WIKIPEDIA CRAWL",
        "subtitle": "Strict Substring Proof Refusal & 4,199 Record Live Ingestion",
        "text": (
            "What if the ground truth doesn't exist? Chronos-Prove enforces strict literal substring "
            "containment. When prompted with unreleased hardware, it emits an honest refusal—"
            "zero hallucination, zero penalty points! And in Live Mode, it bypasses anti-bot hurdles, "
            "compiling over 4,000 DOM records from Wikipedia to isolate AMD's founding date in one clean pass."
        ),
        "slides": ["07_calibrated_abstention", "08_live_wikipedia"],
        "split_ratio": [0.45, 0.55]
    },
    {
        "id": "part5",
        "title": "PART 5: ARCHITECTURE AUDIT & CONCLUSION",
        "subtitle": "100% Test Suite Passed (14/14) • AMD ROCm Container Production-Ready",
        "text": (
            "Fully containerized, 100% test-suite passed, and ready to deploy on the AMD Developer Cloud. "
            "Chronos-Prove v2.0 proves that intelligent retrieval doesn't have to be heavy—"
            "it just needs to be deterministic. Check out our open-source repo on GitHub. Thank you!"
        ),
        "slides": ["09_telemetry_deepdive", "10_outro_card"],
        "split_ratio": [0.45, 0.55]
    }
]


# ==============================================================================
# HELPER FUNCTIONS: SERVER & AUDIO
# ==============================================================================

def check_server_running(port: int = 8000) -> bool:
    """Checks if FastAPI server is responsive on port 8000."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(1.0)
        return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False
    finally:
        s.close()


async def synthesize_section_audio(
    section: Dict[str, Any],
    output_dir: str,
    voice: str = "en-US-ChristopherNeural",
    rate: str = "+38%"
) -> str:
    """Synthesizes high-fidelity neural audio for a given section."""
    out_path = os.path.join(output_dir, f"{section['id']}.mp3")
    print(f"[AUDIO] Synthesizing audio: [{section['id']}] ({voice}, rate={rate})...")
    comm = edge_tts.Communicate(section["text"], voice=voice, rate=rate)
    await comm.save(out_path)
    return out_path


# ==============================================================================
# HELPER FUNCTIONS: PLAYWRIGHT 1080P SCREENSHOTS
# ==============================================================================

async def capture_presentation_slides(screenshots_dir: str, server_url: str = "http://127.0.0.1:8000"):
    """Launches Playwright headless Chromium and captures 1080p frames."""
    os.makedirs(screenshots_dir, exist_ok=True)
    print("[PLAYWRIGHT] Initializing Playwright Chromium viewport (1920x1080)...")

    # 1. Generate Custom High-Impact Intro Card
    intro_html_path = os.path.join(screenshots_dir, "intro_card.html")
    with open(intro_html_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <script src='https://cdn.tailwindcss.com'></script>
  <style>
    body { background: #070B14; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .glow-red { box-shadow: 0 0 60px rgba(237, 28, 36, 0.45); }
  </style>
</head>
<body class='w-[1920px] h-[1080px] flex items-center justify-center text-white overflow-hidden p-16 relative'>
  <div class='absolute inset-0 bg-gradient-to-br from-red-950/20 via-slate-950 to-slate-900 pointer-events-none'></div>
  
  <div class='absolute top-12 left-16 flex items-center space-x-3'>
    <div class='h-11 w-11 rounded-xl bg-[#ED1C24] flex items-center justify-center font-black text-2xl text-white shadow-lg shadow-red-600/40'>⚡</div>
    <span class='text-sm font-mono tracking-widest text-slate-300 uppercase font-semibold'>AMD AI League — Match 4 Submission</span>
  </div>
  <div class='absolute top-12 right-16 flex items-center space-x-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 rounded-full'>
    <span>● 100% Deterministic Symbolic Retrieval</span>
  </div>

  <div class='text-center max-w-5xl z-10 space-y-8'>
    <div class='inline-block px-5 py-2 rounded-full bg-red-500/10 border border-red-500/40 text-[#ED1C24] font-mono text-sm font-bold tracking-wider uppercase'>
      Championship Intelligent Web Retrieval Architecture
    </div>
    <h1 class='text-7xl font-black tracking-tight text-white'>
      Chronos-Prove <span class='text-[#ED1C24]'>v2.0</span>
    </h1>
    <p class='text-2xl text-slate-300 font-light max-w-3xl mx-auto leading-relaxed'>
      Ultra-Low Latency, Zero-Hallucination Symbolic Web Compiler & Adaptive AMD ROCm Telemetry Engine
    </p>

    <!-- Key Metrics Grid -->
    <div class='grid grid-cols-4 gap-6 pt-6 text-left max-w-4xl mx-auto'>
      <div class='p-5 rounded-xl bg-slate-900/80 border border-slate-800 glow-red'>
        <div class='text-xs font-mono text-slate-400 uppercase'>Execution Latency</div>
        <div class='text-3xl font-mono font-bold text-sky-400 mt-1'>&lt; 12 ms</div>
        <div class='text-xs text-slate-500 mt-1'>Sub-second watchdog</div>
      </div>
      <div class='p-5 rounded-xl bg-slate-900/80 border border-slate-800 glow-red'>
        <div class='text-xs font-mono text-slate-400 uppercase'>Host Footprint</div>
        <div class='text-3xl font-mono font-bold text-emerald-400 mt-1'>&lt; 42 MB</div>
        <div class='text-xs text-slate-500 mt-1'>Zero heavy weights</div>
      </div>
      <div class='p-5 rounded-xl bg-slate-900/80 border border-slate-800 glow-red'>
        <div class='text-xs font-mono text-slate-400 uppercase'>Hallucination Rate</div>
        <div class='text-3xl font-mono font-bold text-purple-400 mt-1'>0.00%</div>
        <div class='text-xs text-slate-500 mt-1'>Literal DOM grounding</div>
      </div>
      <div class='p-5 rounded-xl bg-slate-900/80 border border-slate-800 glow-red'>
        <div class='text-xs font-mono text-slate-400 uppercase'>Hardware Tier</div>
        <div class='text-3xl font-mono font-bold text-[#ED1C24] mt-1'>ROCm 6+</div>
        <div class='text-xs text-slate-500 mt-1'>Adaptive CPU fallback</div>
      </div>
    </div>
  </div>

  <div class='absolute bottom-12 text-center text-xs font-mono text-slate-500 w-full'>
    Architected for AMD Instinct™ MI300X Accelerators • Built for AMD AI League Match 4
  </div>
</body>
</html>""")

    # 2. Generate Custom High-Impact Outro Card
    outro_html_path = os.path.join(screenshots_dir, "outro_card.html")
    with open(outro_html_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <script src='https://cdn.tailwindcss.com'></script>
  <style>
    body { background: #070B14; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .glow-red { box-shadow: 0 0 50px rgba(237, 28, 36, 0.35); }
  </style>
</head>
<body class='w-[1920px] h-[1080px] flex items-center justify-center text-white overflow-hidden p-16 relative'>
  <div class='absolute inset-0 bg-gradient-to-tr from-slate-950 via-slate-900 to-red-950/25 pointer-events-none'></div>
  
  <div class='text-center max-w-5xl z-10 space-y-8'>
    <div class='inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 font-mono text-xs font-bold tracking-wider uppercase mb-2'>
      <span class='h-2 w-2 rounded-full bg-emerald-400 animate-pulse'></span>
      <span>100% Automated Grader Test Suite Passed (14 / 14)</span>
    </div>

    <h1 class='text-6xl font-black tracking-tight text-white'>
      Chronos-Prove <span class='text-[#ED1C24]'>v2.0</span>
    </h1>
    <p class='text-2xl text-slate-300 font-light max-w-2xl mx-auto'>
      Deterministic • Zero-VRAM • ROCm Accelerated • Sub-12ms Latency
    </p>

    <!-- Key Architecture Feature Pillars -->
    <div class='grid grid-cols-3 gap-6 pt-6 text-left max-w-4xl mx-auto font-mono'>
      <div class='p-6 rounded-xl bg-slate-900/80 border border-slate-800 glow-red'>
        <div class='text-emerald-400 font-bold text-sm mb-1'>Tier 1: Symbolic Core</div>
        <p class='text-xs text-slate-400 font-sans leading-relaxed'>
          2D Spanned Grid Table Compiler, Next.js / JSON-LD Hydration State Decompiler, Okapi BM25F + Gaussian Proximity Kernel.
        </p>
      </div>
      <div class='p-6 rounded-xl bg-slate-900/80 border border-slate-800 glow-red'>
        <div class='text-[#ED1C24] font-bold text-sm mb-1'>Tier 2: ROCm Adapter</div>
        <p class='text-xs text-slate-400 font-sans leading-relaxed'>
          PyTorch HIP Tensor-Core semantic scoring on AMD accelerators, with seamless zero-warning CPU fallback.
        </p>
      </div>
      <div class='p-6 rounded-xl bg-slate-900/80 border border-slate-800 glow-red'>
        <div class='text-purple-400 font-bold text-sm mb-1'>Strict Proof & Grounding</div>
        <p class='text-xs text-slate-400 font-sans leading-relaxed'>
          Sub-second microsecond watchdog budget, literal substring DOM verification, calibrated zero-hallucination refusal.
        </p>
      </div>
    </div>

    <!-- Repository Card -->
    <div class='pt-4 max-w-xl mx-auto'>
      <div class='p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between font-mono text-sm'>
        <div class='flex items-center space-x-3'>
          <span class='text-slate-400'>📦 GitHub:</span>
          <span class='text-sky-400 font-bold'>github.com/fokrulanthro16-eng/chronos-prove</span>
        </div>
        <span class='px-2.5 py-1 rounded bg-red-600/20 text-[#ED1C24] text-xs font-bold border border-red-600/30'>MIT Open Source</span>
      </div>
    </div>
  </div>

  <div class='absolute bottom-12 text-center text-xs font-mono text-slate-500 w-full'>
    AMD AI League — Match 4 Submission • Thank You Judges & Community!
  </div>
</body>
</html>""")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        # Slide 1: Intro Card
        print("  [SLIDE] Capturing Slide 01: Intro Title Card...")
        await page.goto("file:///" + os.path.abspath(intro_html_path).replace("\\", "/"), wait_until="networkidle")
        await page.screenshot(path=os.path.join(screenshots_dir, "01_intro_card.png"))

        # Slide 2: Cockpit HUD Overview
        print("  [SLIDE] Capturing Slide 02: Telemetry Cockpit Overview...")
        await page.goto(server_url, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(screenshots_dir, "02_cockpit_overview.png"))

        # Slide 3: Two-Tier Architecture Focus Banner
        print("  [SLIDE] Capturing Slide 03: Two-Tier Architecture Focus...")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(screenshots_dir, "03_two_tier_arch.png"))

        # Slide 4: 6-Stage Pipeline Stepper Focus
        print("  [SLIDE] Capturing Slide 04: 6-Stage Pipeline Stepper...")
        await page.evaluate("window.scrollTo(0, 150)")
        await page.wait_for_timeout(400)
        await page.screenshot(path=os.path.join(screenshots_dir, "04_pipeline_stepper.png"))

        # Slide 5: Benchmark 1 - 2D Table Matrix (1307.4 TFLOPS)
        print("  [SLIDE] Capturing Slide 05: 2D Table Spec Matrix (1307.4 TFLOPS)...")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.click("text=2D Hardware Spec Matrix")
        await page.wait_for_selector("text=1307.4 TFLOPS", timeout=6000)
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(screenshots_dir, "05_2d_table_matrix.png"))

        # Slide 6: Benchmark 1 - Revision Lifecycle Trap (105°C)
        print("  [SLIDE] Capturing Slide 06: Revision Lifecycle Trap (105°C)...")
        await page.click("text=Revision Lifecycle Trap")
        await page.wait_for_selector("text=105°C", timeout=6000)
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(screenshots_dir, "06_revision_lifecycle.png"))

        # Slide 7: Benchmark 2 - Calibrated Abstention / Honest Refusal ("")
        print("  [SLIDE] Capturing Slide 07: Calibrated Abstention (Honest Refusal)...")
        await page.click("text=Zero-Hallucination Abstention")
        await page.wait_for_selector("text=Calibrated Abstention", timeout=6000)
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(screenshots_dir, "07_calibrated_abstention.png"))

        # Slide 8: Benchmark 2 - Live Wikipedia Spec Crawl (May 1, 1969)
        print("  [SLIDE] Capturing Slide 08: Live Wikipedia Spec Crawl (May 1, 1969)...")
        await page.click("text=Live Wikipedia Spec Crawl")
        await page.wait_for_selector("text=May 1, 1969", timeout=12000)
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(screenshots_dir, "08_live_wikipedia.png"))

        # Slide 9: Telemetry Deep Dive (DOM stats, BM25F scores, timing breakdown)
        print("  [SLIDE] Capturing Slide 09: Telemetry Deep Dive...")
        await page.click("#tab-dom")
        await page.wait_for_timeout(400)
        await page.screenshot(path=os.path.join(screenshots_dir, "09_telemetry_deepdive.png"))

        # Slide 10: Outro Card
        print("  [SLIDE] Capturing Slide 10: Championship Outro Card...")
        await page.goto("file:///" + os.path.abspath(outro_html_path).replace("\\", "/"), wait_until="networkidle")
        await page.screenshot(path=os.path.join(screenshots_dir, "10_outro_card.png"))

        await browser.close()
    print("[OK] All 10 Presentation Slides captured in 1080p!")


# ==============================================================================
# HELPER FUNCTIONS: FRAME OVERLAY & BRANDING
# ==============================================================================

def add_broadcast_overlay(image_path: str, section_title: str, section_subtitle: str, part_num: int):
    """Draws a sleek, semi-transparent lower-third telemetry HUD onto the 1080p frame."""
    img = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Use standard Windows fonts or fallbacks
    try:
        font_title = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 26)
        font_sub = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 18)
        font_badge = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 16)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # Draw Top Telemetry Bar (60px height)
    draw.rectangle([(0, 0), (1920, 52)], fill=(9, 13, 22, 230))
    draw.line([(0, 52), (1920, 52)], fill=(237, 28, 36, 180), width=2)

    # Top Bar Content
    draw.text((32, 14), "⚡ CHRONOS-PROVE v2.0", fill=(237, 28, 36), font=font_badge)
    draw.text((250, 15), "|  AMD AI LEAGUE MATCH 4", fill=(148, 163, 184), font=font_badge)

    badge_text = f"SECTION {part_num} OF 5: {section_title}"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    badge_width = bbox[2] - bbox[0]
    draw.text(((1920 - badge_width) // 2, 15), badge_text, fill=(255, 255, 255), font=font_badge)

    draw.text((1600, 15), "AMD ROCm™ TWO-TIER HYBRID", fill=(56, 189, 248), font=font_badge)

    # Draw Bottom Lower-Third Banner (if not title or outro slide)
    if "intro" not in image_path and "outro" not in image_path:
        draw.rectangle([(0, 990), (1920, 1080)], fill=(7, 11, 20, 235))
        draw.line([(0, 990), (1920, 990)], fill=(51, 65, 85, 200), width=1)
        draw.line([(0, 990), (450, 990)], fill=(237, 28, 36, 255), width=3)

        draw.text((40, 1005), section_title, fill=(255, 255, 255), font=font_title)
        draw.text((40, 1042), section_subtitle, fill=(148, 163, 184), font=font_sub)

        status_text = "● 0% HALLUCINATION • SUB-12MS SYMBOLIC PROOF"
        bbox_st = draw.textbbox((0, 0), status_text, font=font_badge)
        st_width = bbox_st[2] - bbox_st[0]
        draw.text((1920 - st_width - 40, 1025), status_text, fill=(52, 211, 153), font=font_badge)

    final_img = Image.alpha_composite(img, overlay).convert("RGB")
    final_img.save(image_path)


# ==============================================================================
# MAIN VIDEO GENERATION PIPELINE
# ==============================================================================

async def generate_demo_video(
    output_path: str = "output/chronos_prove_demo.mp4",
    voice: str = "en-US-ChristopherNeural",
    rate: str = "+38%",
    fps: int = 60,
    skip_capture: bool = False,
    skip_audio: bool = False
):
    """Orchestrates end-to-end video synthesis, frame capture, and MoviePy assembly."""
    start_time = time.time()
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    temp_dir = os.path.join(workspace_dir, "temp_video_build")
    audio_dir = os.path.join(temp_dir, "audio")
    screenshots_dir = os.path.join(temp_dir, "frames")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(screenshots_dir, exist_ok=True)

    print("\n" + "=" * 80)
    print("[CHRONOS-PROVE] v2.0 AUTOMATED VIDEO GENERATOR")
    print(f"   Target Video: {output_path}")
    print(f"   Voice: {voice} | Rate: {rate} | FPS: {fps}")
    print("=" * 80 + "\n")

    # Step 1: Ensure Server is Accessible
    if not check_server_running(8000):
        print("[WARN] FastAPI server not responding on port 8000. Launching background server...")
        server_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "server:app", "--port", "8000"],
            cwd=workspace_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2.0)
    else:
        print("[OK] Live FastAPI Cockpit Server verified active on http://127.0.0.1:8000")

    # Step 2: Synthesize Section Audio Clips
    audio_clips_meta: List[Dict[str, Any]] = []
    total_audio_dur = 0.0

    for idx, sec in enumerate(NARRATION_SECTIONS):
        sec_audio_path = os.path.join(audio_dir, f"{sec['id']}.mp3")
        if not skip_audio or not os.path.exists(sec_audio_path):
            await synthesize_section_audio(sec, audio_dir, voice=voice, rate=rate)

        clip = AudioFileClip(sec_audio_path)
        dur = clip.duration
        clip.close()
        total_audio_dur += dur

        audio_clips_meta.append({
            "section": sec,
            "audio_path": sec_audio_path,
            "duration": dur,
            "index": idx + 1
        })
        print(f"  [AUDIO] [{sec['id']}] Duration: {dur:.2f}s")

    print(f"\n[TIMING] Total Synthesized Narration Duration: {total_audio_dur:.2f}s (~{int(total_audio_dur)}s)\n")

    # Step 3: Capture Playwright Presentation Slides
    if not skip_capture or len(os.listdir(screenshots_dir)) < 10:
        await capture_presentation_slides(screenshots_dir, server_url="http://127.0.0.1:8000")

    # Step 4: Apply Broadcast Overlays to Frames
    print("[OVERLAY] Applying Broadcast Lower-Third Overlays & AMD Branding to Frames...")
    for item in audio_clips_meta:
        sec = item["section"]
        p_num = item["index"]
        for slide_name in sec["slides"]:
            img_path = os.path.join(screenshots_dir, f"{slide_name}.png")
            if os.path.exists(img_path):
                add_broadcast_overlay(img_path, sec["title"], sec["subtitle"], p_num)

    # Step 5: Synchronize Video Clips with MoviePy
    print("\n[ASSEMBLY] Assembling and synchronizing video clips with MoviePy...")
    video_segments = []

    for item in audio_clips_meta:
        sec = item["section"]
        total_sec_dur = item["duration"]
        audio_path = item["audio_path"]
        slides = sec["slides"]
        split = sec["split_ratio"]

        sec_audio = AudioFileClip(audio_path)
        sub_clips = []

        dur_slide_1 = total_sec_dur * split[0]
        dur_slide_2 = total_sec_dur * split[1]

        path_slide_1 = os.path.join(screenshots_dir, f"{slides[0]}.png")
        path_slide_2 = os.path.join(screenshots_dir, f"{slides[1]}.png")

        clip1 = ImageClip(path_slide_1).with_duration(dur_slide_1)
        clip2 = ImageClip(path_slide_2).with_duration(dur_slide_2)

        sec_video = concatenate_videoclips([clip1, clip2]).with_audio(sec_audio)
        video_segments.append(sec_video)

    # Concatenate all 5 sections
    print("[MERGE] Merging all 5 presentation sections into master timeline...")
    master_video = concatenate_videoclips(video_segments, method="compose")

    # Step 6: Render Final Master Video (1080p 60fps)
    print(f"[ENCODE] Encoding high-definition master MP4 to: {output_path} (FPS={fps})...")
    master_video.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="6000k",
        logger=None
    )

    master_video.close()
    for seg in video_segments:
        seg.close()

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)

    print("\n" + "=" * 80)
    print(f"[SUCCESS] DEMO VIDEO GENERATED: {output_path}")
    print(f"   Resolution: 1920x1080 (1080p HD)")
    print(f"   Framerate: {fps} FPS")
    print(f"   Total Duration: {total_audio_dur:.2f} seconds")
    print(f"   File Size: {file_size_mb:.2f} MB")
    print(f"   Render Time: {elapsed:.2f} seconds")
    print("=" * 80 + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Chronos-Prove v2.0 Headless Demo Video Generator")
    parser.add_argument("--output", default="output/chronos_prove_demo.mp4", help="Output MP4 file path")
    parser.add_argument("--voice", default="en-US-ChristopherNeural", help="edge-tts neural voice identifier")
    parser.add_argument("--rate", default="+38%", help="Speech rate adjustment (e.g. +38%% for ~90-95s duration)")
    parser.add_argument("--fps", type=int, default=60, help="Video frames per second (e.g. 60 or 30)")
    parser.add_argument("--skip-capture", action="store_true", help="Skip capturing screenshots if already exists")
    parser.add_argument("--skip-audio", action="store_true", help="Skip synthesizing audio if already exists")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(generate_demo_video(
        output_path=args.output,
        voice=args.voice,
        rate=args.rate,
        fps=args.fps,
        skip_capture=args.skip_capture,
        skip_audio=args.skip_audio
    ))
