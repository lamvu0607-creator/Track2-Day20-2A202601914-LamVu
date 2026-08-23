# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 15 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.98 of 4 slots (100%) |
| `requests_processing` | 4 |
| `requests_deferred` | 45 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 26250 |

Highest sampled value was **3.98 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Your observation

**Peak batch width quan sát được là 3.98 / 4 slots (xấp xỉ 100% capacity)**. Con số này chứng minh continuous batching hoạt động hiệu quả tối đa: engine đã liên tục gom các request đồng thời vào cùng một forward pass decode thay vì xử lý tuần tự.

**So sánh giữa `n_busy_slots_per_decode` (3.98) và Effective Concurrency (41.9):**
- Hai con số này phản ánh hai góc nhìn bổ trợ cho nhau và hoàn toàn nhất quán:
  1. `n_busy_slots_per_decode` (3.98) đo lường **compute utilization thực tế** bên trong llama-server: server luôn kín toàn bộ 4 slots xử lý.
  2. Effective concurrency (41.9) theo Little's Law ($L = \lambda \times W$) đo lường **tổng số request trong hệ thống (in-flight)** bao gồm cả 4 request đang được tính toán và ~40 request đang nằm chờ trong hàng đợi (`requests_deferred` đạt đỉnh 45).
- Dữ liệu `requests_deferred = 45` xác nhận độ trễ P95 tăng vọt từ 2700 ms lên 12000 ms là do **queue time (thời gian xếp hàng)** khi hệ thống vượt ngưỡng bão hòa.
