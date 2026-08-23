# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** Lâm Vũ
**Cohort:** A20-K4
**Ngày submit:** 2026-08-23

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** Windows 10 (AMD64)
- **CPU:** 12th Gen Intel(R) Core(TM) i5-12400F
- **Cores:** 6 physical / 12 logical
- **CPU extensions:** AVX2
- **RAM:** 23.8 GB
- **Accelerator:** NVIDIA GeForce RTX 3060 Ti, 8192 MiB (CUDA / Vulkan)
- **llama.cpp asset đã tải:** llama-b10488-bin-win-cuda-12.4-x64.zip
- **Model đã dùng:** Gemma 4 E2B (`LAB_MODEL=gemma4-e2b`)
- **Quantization:** UD-Q4_K_XL (2.97 GB) + UD-Q2_K_XL (2.24 GB) (từ `models/active.json`)

**Chạy ở đâu:** laptop của tôi
_(Nếu dùng cloud fallback: nói rõ vì sao — RAM < 8 GB, setup fail, v.v. Không mất điểm.)_

**Setup story** (≤ 80 chữ): điều gì cần thay đổi để lab chạy trên máy bạn? Có bước
nào fail rồi phải workaround không?

Lab chạy mượt mà trên Windows với script `lab.ps1` và prebuilt CUDA runtime b10488 mà không cần compiler. Khi probe trên PowerShell, cần thiết lập cờ UTF-8 cho Python output để hiển thị chuẩn xác ký tự giao diện.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 3837 | 72 / 295 | 8.6 / 10.2 | 610 / 836 / 836 | 115.8 |
| UD-Q2_K_XL | 2.24 | 3681 | 64 / 236 | 8.0 / 8.4 | 561 / 712 / 712 | 124.5 |

**Quan sát** (≤ 60 chữ): 2-bit nhanh hơn bao nhiêu, và **có đáng không**? Bạn đã thử
hỏi cùng một câu trên cả hai (`make serve` vs `.venv/bin/python labs/02-serve/serve.py --compare`)
chưa? Chất lượng khác nhau thế nào?

2-bit decode nhanh hơn 1.08× (124.5 vs 115.8 tok/s) và nhẹ hơn 0.73 GB nhưng không đáng dùng. Thử nghiệm cho thấy bản 2-bit giảm độ mạch lạc, trong khi 8GB VRAM thừa sức chạy bản 4-bit chất lượng cao.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|---|--:|--:|--:|--:|--:|--:|
| 10 | 4.03 | 1500 | 2700 | 3700 | 6.4 | 0.0% |
| 50 | 4.17 | 11000 | 12000 | 12000 | 41.9 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 1.03×
- **P95 tăng:** 4.44×
- **Effective concurrency ở 50 users:** 41.9 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang
chạy): 3.98 / 4 slots

**Saturation reading** (≤ 80 chữ): server của bạn bão hoà ở đâu, và **bằng chứng nào**
thuyết phục bạn? Nếu P95 tăng nhanh hơn RPS thì phần latency thêm đó là queue time hay
compute time — bạn biết bằng cách nào? Nếu bạn phải nâng goodput@SLO, bạn sẽ đổi knob
nào **trước**, và vì sao knob đó?

Server bão hòa ở ~10 users khi throughput đi ngang (~4.1 RPS) và P95 tăng 4.44× do queue time (deferred reqs = 45). Sẽ tăng `--parallel` trước vì VRAM còn trống nhiều, giúp mở rộng slot decode song song.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Local Windows host | stub |
| N17 Data pipeline | In-memory toy docs | stub |
| N18 Lakehouse | Local Python dictionary | stub |
| N19 Vector + features | Keyword overlap search | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0.0 ms
- retrieve: 0.0 ms
- llm: 2663.4 ms
- **stage chiếm nhiều nhất:** llm (100% của total)

**Reflection** (≤ 60 chữ): bottleneck ở đâu? Có khớp với kỳ vọng của bạn không? Nếu
phải giảm latency của pipeline này 2×, bạn sẽ tấn công vào đâu?

LLM generation là bottleneck tuyệt đối (100%). Để giảm 2× latency, cần tối ưu TTFT bằng Prompt Caching và tăng tốc độ phát sinh token qua Speculative Decoding (MTP head).

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Tối ưu hóa số luồng xử lý từ 1 lên 6 threads (`-t 1` -> `-t 6`)

```
before:  132.4 tok/s
after:   138.6 tok/s
speedup: 1.05×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

Kết quả khảo sát thread count cho thấy điểm uốn (knee) đạt đỉnh tại đúng **`-t 6`** (138.6 tok/s), trùng khớp với số lượng **6 nhân vật lý (physical cores)** của CPU Intel Core i5-12400F. Từ 1 luồng lên 6 luồng, mỗi worker thread độc lập quản lý một core vật lý với bộ nhớ đệm L1/L2 riêng biệt, giúp quá trình chuẩn bị dữ liệu và điều phối kernel sang GPU diễn ra nhanh nhất.

Khi tăng số luồng lên 12 (hyperthreading) và 24 (oversubscription), tốc độ giảm nhẹ xuống ~134.7–135.0 tok/s. Điều này xảy ra do các logical hyperthreads phải chia sẻ tài nguyên tính toán và cache trong cùng một physical core, dẫn đến xung đột bộ nhớ cache (cache contention) và chi phí chuyển đổi ngữ cảnh (context switching overhead) của hệ điều hành. Do đó, thiết lập `-t` bằng đúng số physical core là điểm cân bằng lý tưởng nhất.

---

## 6. Bonus  *(optional — tối đa 20 điểm)*

> Bỏ trống nếu không làm. Xem `bonus/README.md`. Đừng làm hết — **một** finding sâu
> ăn điểm hơn năm bảng nông.

**Đã làm:** B2 (GPU offload sweep) & B4/B5 (C8 Semantic Cache & C9 Embedding Serving)

**Numbers:**

```
before:  13.5 tok/s
after:   126.5 tok/s
speedup: 9.36×
```

**Điều này nói lên gì mà deck chưa nói:**

Trong quá trình partial offload (`-ngl 8` đến `32`), tốc độ tăng rất chậm do hệ thống bị nghẽn băng thông truyền tensor trung gian qua bus PCIe giữa Host RAM và GPU VRAM tại mỗi bước autoregressive decode. Chỉ khi đạt full offload (`-ngl 99`), toàn bộ phép tính ma trận và KV cache đều nằm trọn trên VRAM, tận dụng tối đa băng thông 448 GB/s của RTX 3060 Ti để tạo ra mức speedup nhảy vọt 9.36× so với CPU thuần.

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

_(1–2 câu. Không bắt buộc, nhưng grader đọc hết.)_

Khả năng nén batching của continuous batching trong llama.cpp đạt tới 3.98/4 slots (99.5%) rất ổn định, giữ cho server không bị crash hay drop request ngay cả khi chịu tải gấp 5 lần công suất phục vụ.

---

## 8. Self-check trước khi push

- [x] `hardware.json` committed
- [x] `models/active.json` committed
- [x] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [x] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [x] `benchmarks/02-server-results.md` committed (`make load-report`)
- [x] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [x] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [x] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [x] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [x] 5 screenshots trong `submission/screenshots/`
- [x] `make verify` → **exit 0**
- [x] Repo GitHub ở chế độ **public**
- [x] Đã paste public URL vào VinUni LMS
- [x] **Không** commit `models/*.gguf` hay `runtime/` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.
