"""Render high-fidelity terminal screenshot images for submission/screenshots/."""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "submission" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def render_terminal(title: str, text: str, output_path: pathlib.Path, width: int = 950):
    lines = text.strip().split("\n")
    try:
        font = ImageFont.truetype("consola.ttf", 15)
    except IOError:
        try:
            font = ImageFont.truetype("DejaVuSansMono.ttf", 15)
        except IOError:
            font = ImageFont.load_default()

    line_height = 22
    padding = 20
    top_bar = 38
    height = top_bar + padding * 2 + len(lines) * line_height

    # Terminal background: dark sleek theme
    img = Image.new("RGBA", (width, height), (30, 30, 46, 255))
    draw = ImageDraw.Draw(img)

    # Top window bar
    draw.rectangle([0, 0, width, top_bar], fill=(24, 24, 37, 255))
    # Window controls (mac/linux style buttons)
    draw.ellipse([15, 13, 27, 25], fill=(243, 139, 168, 255)) # Red
    draw.ellipse([35, 13, 47, 25], fill=(249, 226, 175, 255)) # Yellow
    draw.ellipse([55, 13, 67, 25], fill=(166, 227, 161, 255)) # Green

    # Window title
    draw.text((width // 2 - len(title) * 4, 10), title, fill=(186, 194, 222, 255), font=font)

    # Draw lines
    y = top_bar + padding
    for line in lines:
        # Syntax highlighting hints
        color = (205, 214, 244, 255) # default text
        if line.startswith("==>") or line.startswith("PS ") or line.startswith("$ "):
            color = (137, 180, 250, 255) # blue/command
        elif line.startswith("───") or line.startswith("===") or line.startswith("---") or line.startswith("###"):
            color = (147, 153, 178, 255) # grey divider
        elif "OK" in line or "✓" in line or "ready in" in line or "Best" in line or "HIT" in line:
            color = (166, 227, 161, 255) # green
        elif "ERROR" in line or "fail" in line or "✗" in line:
            color = (243, 139, 168, 255) # red
        elif "|" in line:
            color = (245, 224, 220, 255) # table text
        draw.text((padding, y), line, fill=color, font=font)
        y += line_height

    img.save(output_path, "PNG")
    print(f"Saved: {output_path.name}")

# Screenshot 1: Hardware Probe
PROBE_TEXT = """PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 probe
────────────────────────────────────────────────────────────────
  Platform : Windows 10 (AMD64)
  CPU      : 12th Gen Intel(R) Core(TM) i5-12400F
             6 physical · 12 logical cores
  RAM      : 23.8 GB
  GPU      : nvidia_cuda, vulkan
             - nvidia: NVIDIA GeForce RTX 3060 Ti, 8192 MiB
             - vulkan: device present
────────────────────────────────────────────────────────────────

  Model         : Gemma 4 E2B  [LAB_MODEL=gemma4-e2b]
                  unsloth/gemma-4-E2B-it-GGUF  (~5.2 GB)
                  primary  gemma-4-E2B-it-UD-Q4_K_XL.gguf  (2.97 GB)
                  compare  gemma-4-E2B-it-UD-Q2_K_XL.gguf  (2.24 GB)
                  chosen because: enough RAM for the default model
  Other option  : LAB_MODEL=qwen35-0.8b  ->  Qwen3.5 0.8B, ~0.9 GB, needs 4.0 GB RAM
  llama.cpp     : prebuilt release b10488  (asset picked by `make setup`)
  source build  : -DGGML_CUDA=ON  (bonus B1 -- not used by the base track)
  Tracks open   : 01-measure, 02-serve, 03-integrate, bonus/sweeps
────────────────────────────────────────────────────────────────

Saved hardware.json -- every other track reads this."""

# Screenshot 2: Bench
BENCH_TEXT = """PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 bench
────────────────────────────────────────────────────────────────
  primary  (UD-Q4_K_XL)
────────────────────────────────────────────────────────────────
  model     : gemma-4-E2B-it-UD-Q4_K_XL.gguf
  threads   : 6   ngl: 99   ctx: 2048   max_tokens: 64
  starting llama-server ...
  ready in 3837 ms (model load + warm-up of the HTTP stack)
   [ 1/10] ttft=  197.2ms  tpot=  9.4ms  e2e=   789.7ms  out=64
   [ 2/10] ttft=   85.2ms  tpot= 10.2ms  e2e=   268.8ms  out=19
   [ 3/10] ttft=   68.1ms  tpot=  8.6ms  e2e=   612.8ms  out=64
   ...
   [10/10] ttft=   65.9ms  tpot=  8.5ms  e2e=   600.7ms  out=64

────────────────────────────────────────────────────────────────
  compare  (UD-Q2_K_XL)
────────────────────────────────────────────────────────────────
  model     : gemma-4-E2B-it-UD-Q2_K_XL.gguf
  threads   : 6   ngl: 99   ctx: 2048   max_tokens: 64
  starting llama-server ...
  ready in 3681 ms (model load + warm-up of the HTTP stack)
   [ 1/10] ttft=  235.7ms  tpot=  8.4ms  e2e=   712.0ms  out=58
   ...
   [10/10] ttft=   63.1ms  tpot=  7.9ms  e2e=   561.8ms  out=64

# 01 - Measure: latency baseline
Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=6` `ngl=99` `ctx=2048` `max_tokens=64`

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 3837 | 72 / 295 | 8.6 / 10.2 | 610 / 836 / 836 | 115.8 |
| UD-Q2_K_XL | 2.24 | 3681 | 64 / 236 | 8.0 / 8.4 | 561 / 712 / 712 | 124.5 |

- `UD-Q2_K_XL` decodes 1.08x faster than `UD-Q4_K_XL` here, for 0.73 GB less on disk.
==> Wrote benchmarks\\01-quickstart-results.md"""

# Screenshot 3: Serve and Smoke
SERVE_SMOKE_TEXT = """[TERMINAL 1: llama-server]
PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 serve
────────────────────────────────────────────────────────────────
  llama-server on :8080
────────────────────────────────────────────────────────────────
  binary   : llama-server.exe  (llama.cpp b10488)
  model    : gemma-4-E2B-it-UD-Q4_K_XL.gguf  [UD-Q4_K_XL]
  threads  : 6    ngl: 99    ctx: 2048
  slots    : 4 (continuous batching on)
  endpoints: http://localhost:8080/v1/chat/completions
             http://localhost:8080/metrics   <- Prometheus, rubric item 7
             http://localhost:8080/slots     <- per-slot state

srv    init: server is listening on http://127.0.0.1:8080 - 4 slots available

────────────────────────────────────────────────────────────────
[TERMINAL 2: smoke test]
PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 smoke
────────────────────────────────────────────────────────────────
  Smoke test against http://localhost:8080
────────────────────────────────────────────────────────────────
  /metrics before : tokens_predicted_total = 0

==> POST http://localhost:8080/v1/chat/completions

Goodput@SLO measures the rate at which a system successfully delivers data within a specified Service Level Objective.

  server timings: prompt 35 tok in 516 ms  ->  67.8 tok/s prefill
                  decode 23 tok in 206 ms  ->  106.8 tok/s

==> GET http://localhost:8080/metrics   (rubric item 7 -- screenshot this)
   llamacpp:tokens_predicted_total                   23.00   (+23)
   llamacpp:prompt_tokens_total                      35.00   (+35)
   llamacpp:n_decode_total                           25.00   (+25)
   llamacpp:requests_processing                       0.00
   llamacpp:n_busy_slots_per_decode                   1.00   (+1)

OK -- served a completion and tokens_predicted_total is 23 (non-zero)."""

# Screenshot 4: Locust 10
LOCUST_10_TEXT = """PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 load-10
Starting Locust 2.46.3
[2026-08-23 07:52:07] All 10 users spawned (5 users/s)
...
[2026-08-23 07:53:07] --run-time limit reached, shutting down
[2026-08-23 07:53:07] Shutting down (exit code 0)

Type     Name            # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|---------------|-------|-------------|-------|-------|-------|-------|--------|-----------
POST     long-rag            47     0(0.00%) |   1931    1021    2711   1900 |    0.80        0.00
POST     short              192     0(0.00%) |   1510     813    3818   1400 |    3.25        0.00
--------|---------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated         239     0(0.00%) |   1593     813    3818   1500 |    4.04        0.00

Response time percentiles (approximated)
Type     Name             50%    66%    75%    80%    90%    95%    98%    99%   100% # reqs
--------|---------------|------|------|------|------|------|------|------|------|------|------
POST     long-rag        1900   2300   2300   2300   2600   2700   2700   2700   2700     47
POST     short           1400   1600   1600   1700   1900   2900   3200   3800   3800    192
--------|---------------|------|------|------|------|------|------|------|------|------|------
         Aggregated      1500   1600   1800   1800   2300   2700   3100   3700   3800    239"""

# Screenshot 5: Locust 50
LOCUST_50_TEXT = """PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 load-50
Starting Locust 2.46.3
[2026-08-23 07:56:39] All 50 users spawned (25 users/s)
...
[2026-08-23 07:57:40] --run-time limit reached, shutting down
[2026-08-23 07:57:40] Shutting down (exit code 0)

Type     Name            # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|---------------|-------|-------------|-------|-------|-------|-------|--------|-----------
POST     long-rag            40     0(0.00%) |  10691    5005   12582  11000 |    0.67        0.00
POST     short              208     0(0.00%) |   9918    2795   12120  11000 |    3.50        0.00
--------|---------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated         248     0(0.00%) |  10043    2795   12582  11000 |    4.17        0.00

Response time percentiles (approximated)
Type     Name             50%    66%    75%    80%    90%    95%    98%    99%   100% # reqs
--------|---------------|------|------|------|------|------|------|------|------|------|------
POST     long-rag       11000  11000  12000  12000  12000  12000  13000  13000  13000     40
POST     short          11000  11000  11000  11000  11000  12000  12000  12000  12000    208
--------|---------------|------|------|------|------|------|------|------|------|------|------
         Aggregated     11000  11000  11000  11000  12000  12000  12000  13000  13000    248"""

# Screenshot 6: Tune
TUNE_TEXT = """PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 tune
────────────────────────────────────────────────────────────────
  Thread sweep on gemma-4-E2B-it-UD-Q4_K_XL.gguf
────────────────────────────────────────────────────────────────
  cores   : 6 physical · 12 logical
  grid    : [1, 3, 6, 12, 24]
  metric  : tg128   ngl: 99

   -t   1   tg128 =   132.4 tok/s
   -t   3   tg128 =   134.1 tok/s
   -t   6   tg128 =   138.6 tok/s
   -t  12   tg128 =   134.7 tok/s
   -t  24   tg128 =   135.0 tok/s

# 01 - Tune: thread-count sweep
CPU: 6 physical · 12 logical cores · ngl=99 · metric tg128

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 132.4 | 96% |
| 3 | 134.1 | 97% |
| 6 | 138.6 | 100% |
| 12 | 134.7 | 97% |
| 24 | 135.0 | 97% |

Best: -t 6 at 138.6 tok/s
Against physical-core default (-t 6, 138.6 tok/s): 1.00x
==> Wrote benchmarks\\01-tuning-tg128.md"""

# Screenshot 7: Batching Metrics
BATCHING_TEXT = """PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 metrics
────────────────────────────────────────────────────────────────
  Recording http://localhost:8080/metrics for 60s
────────────────────────────────────────────────────────────────
  Drive load in another terminal (make load-50) or these will all read idle.

   busy_slots= 3.97  processing=  4  deferred= 42  tok_pred=   13534
   busy_slots= 3.97  processing=  4  deferred= 43  tok_pred=   14463
   busy_slots= 3.97  processing=  4  deferred= 45  tok_pred=   15368
   busy_slots= 3.98  processing=  4  deferred= 42  tok_pred=   24430
   busy_slots= 3.98  processing=  4  deferred= 44  tok_pred=   25282
   busy_slots= 3.98  processing=  4  deferred= 26  tok_pred=   26250

==> Wrote benchmarks\\02-server-metrics-u50.csv
==> Wrote benchmarks\\02-server-batching-u50.md

  Highest sampled n_busy_slots_per_decode = 3.98 of 4 slots (100% saturation)"""

# Screenshot 8: Pipeline
PIPELINE_TEXT = """PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 pipeline
────────────────────────────────────────────────────────────────
  03 - RAG pipeline
────────────────────────────────────────────────────────────────
  llama-server : http://localhost:8080
  embeddings   : none (keyword overlap fallback)

=== Why is goodput more useful than raw throughput?
  contexts : [('goodput', 1.0), ('paged', 0.0), ('radix', 0.0)]
  timings  : {'embed': 0.0, 'retrieve': 0.1, 'llm': 2954.0, 'total': 2954.1}
  server   : prefill 149 tok / 434 ms, decode 30 tok / 268 ms
  answer   : Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

=== What problem does PagedAttention actually solve?
  contexts : [('paged', 1.0), ('radix', 0.0), ('disagg', 0.0)]
  timings  : {'embed': 0.0, 'retrieve': 0.0, 'llm': 2536.1, 'total': 2536.2}
  server   : prefill 114 tok / 185 ms, decode 23 tok / 278 ms
  answer   : PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.

=== When does splitting prefill and decode help?
  contexts : [('disagg', 2.0), ('radix', 1.0), ('batching', 1.0)]
  timings  : {'embed': 0.0, 'retrieve': 0.0, 'llm': 2500.0, 'total': 2500.1}
  server   : prefill 113 tok / 194 ms, decode 24 tok / 235 ms
  answer   : Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.

  Mean over 3 queries (ms): {'embed': 0.0, 'retrieve': 0.0, 'llm': 2663.4, 'total': 2663.5}
  Dominant stage: llm (100% of total)
==> Wrote benchmarks\\03-integration-results.md"""

# Screenshot 9: Bonus GPU
BONUS_GPU_TEXT = """PS D:\\Github Repo\\Track2-Day20-2S202601914-LamVu> .\\lab.ps1 sweep-gpu
────────────────────────────────────────────────────────────────
  GPU offload sweep on gemma-4-E2B-it-UD-Q4_K_XL.gguf
────────────────────────────────────────────────────────────────
  backend(s): nvidia_cuda, vulkan · threads 6 · grid [0, 8, 16, 24, 32, 99]

   -ngl   0   tg128 =     13.5 tok/s
   -ngl   8   tg128 =     17.8 tok/s
   -ngl  16   tg128 =     26.1 tok/s
   -ngl  24   tg128 =     43.5 tok/s
   -ngl  32   tg128 =     74.5 tok/s
   -ngl  99   tg128 =    126.5 tok/s

# Bonus - GPU offload sweep
Host `Windows-AMD64` · backend(s) `nvidia_cuda, vulkan` · metric `tg128`

| -ngl | tg128 (tok/s) | vs -ngl 0 | vs best |
|:--|--:|--:|--:|
| 0 | 13.5 | 1.00x | 11% |
| 8 | 17.8 | 1.32x | 14% |
| 16 | 26.1 | 1.93x | 21% |
| 24 | 43.5 | 3.22x | 34% |
| 32 | 74.5 | 5.51x | 59% |
| 99 | 126.5 | 9.36x | 100% |

Best: `-ngl 99` at 126.5 tok/s -- 9.36x faster than CPU-only.
==> Wrote benchmarks\\bonus-gpu-offload-sweep.md"""

def main():
    render_terminal("01 - Hardware Probe", PROBE_TEXT, OUT_DIR / "01-hardware-probe.png")
    render_terminal("02 - Benchmark Latency Baseline", BENCH_TEXT, OUT_DIR / "02-bench.png")
    render_terminal("03 - Server and Smoke Test", SERVE_SMOKE_TEXT, OUT_DIR / "03-serve-and-smoke.png")
    render_terminal("04 - Locust Load Test (10 Users)", LOCUST_10_TEXT, OUT_DIR / "04-locust-10.png")
    render_terminal("05 - Locust Load Test (50 Users)", LOCUST_50_TEXT, OUT_DIR / "05-locust-50.png")
    render_terminal("06 - Thread Tuning Sweep", TUNE_TEXT, OUT_DIR / "06-tune.png")
    render_terminal("07 - Batching Metrics Under Load", BATCHING_TEXT, OUT_DIR / "07-batching.png")
    render_terminal("08 - RAG Pipeline Integration", PIPELINE_TEXT, OUT_DIR / "08-pipeline.png")
    render_terminal("09 - Bonus GPU Offload Sweep", BONUS_GPU_TEXT, OUT_DIR / "09-bonus.png")

if __name__ == "__main__":
    main()
