# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **6 physical · 12 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 132.4 | 96% |
| 3 | 134.1 | 97% |
| 6 | 138.6 | 100% |
| 12 | 134.7 | 97% |
| 24 | 135.0 | 97% |

**Best**: `-t 6` at 138.6 tok/s
**Slowest tested**: `-t 1` at 132.4 tok/s (1.05x spread)
**Against the physical-core default** (`-t 6`, 138.6 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=6 make bench
```

## Your explanation

Điểm uốn (knee) nằm chính xác tại **`-t 6`** đạt đỉnh 138.6 tok/s, trùng khớp hoàn hảo với số **physical cores (6 cores)** của CPU Intel Core i5-12400F.

**Cơ chế giải thích:**
1. **Physical Cores vs Hyperthreading**: Từ `-t 1` đến `-t 6`, throughput tăng dần khi mỗi luồng vật lý được phân bổ trọn vẹn tài nguyên ALU, L1/L2 Cache và memory controller. Khi vượt qua 6 luồng lên 12 (logical hyperthreads) và 24 (oversubscription), tốc độ giảm xuống ~134.7–135.0 tok/s. Nguyên nhân là các logical hyperthreads chia sẻ chung execution units và cache trong cùng physical core, làm tăng cache pollution (xung đột L1/L2 cache), tranh chấp bộ nhớ và độ trễ do context switching/thread synchronization.
2. **Tương quan với GPU Offload (`ngl=99`)**: Với toàn bộ layer chạy trên GPU RTX 3060 Ti, CPU đóng vai trò điều phối batching và token transfer. Số luồng `-t 6` cung cấp năng lực điều phối tối ưu mà không gây quá tải scheduler của hệ điều hành. Do đó, thiết lập chuẩn là `LAB_N_THREADS=6`.
