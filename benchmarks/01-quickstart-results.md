# 01 - Measure: latency baseline

Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=6` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 3837 | 72 / 295 | 8.6 / 10.2 | 610 / 836 / 836 | 115.8 |
| UD-Q2_K_XL | 2.24 | 3681 | 64 / 236 | 8.0 / 8.4 | 561 / 712 / 712 | 124.5 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.08x faster** than `UD-Q4_K_XL` here, for 0.73 GB less on disk.

## Your observation

Bản `UD-Q2_K_XL` (2.24 GB) đạt tốc độ decode 124.5 tok/s, nhanh hơn 1.08× so với `UD-Q4_K_XL` (115.8 tok/s) và tiết kiệm 0.73 GB dung lượng. Sự gia tăng tốc độ này bắt nguồn từ việc giảm lượng byte trọng số cần nạp qua bus bộ nhớ trong mỗi bước autoregressive decode (memory bandwidth bound).

Tuy nhiên, việc đánh đổi sang 2-bit **không đáng dùng** trên máy này:
1. **Dung lượng VRAM khả dụng**: GPU RTX 3060 Ti có 8 GB VRAM, thừa khả năng chứa trọn vẹn bản 4-bit (2.97 GB) cùng KV cache mà không bị tràn bộ nhớ.
2. **Chất lượng đầu ra**: Khi kiểm tra cùng câu hỏi, bản 2-bit xuất hiện hiện tượng suy giảm ngữ nghĩa rõ rệt ở các câu trả lời phức tạp và cấu trúc câu kém mạch lạc hơn. Bản UD-Q4_K_XL giữ được chất lượng suy luận gần như nguyên bản của Gemma 4 E2B với độ trễ decode vẫn cực kỳ ấn tượng (8.6 ms/token).
