# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=6` ·
`ngl=99`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 235 | 4.03 | 1500 | 2700 | 3700 | 6.4 | 0.0% |
| 50 | 248 | 4.17 | 11000 | 12000 | 12000 | 41.9 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **1.03x** (21% of linear) |
| P95 latency | **4.44x** |
| Effective concurrency at 50 users | 41.9 vs `--parallel 4` slots (occupancy/slot ratio 10.47) |

**Saturated.** Throughput delivered only 1.03x for 5x the offered load, and effective concurrency (41.9) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 1.03x while P95 moved 4.44x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Your reading

**1. Điểm bão hòa (Saturation Point) và Bằng chứng:**
- Server đạt điểm bão hòa ngay từ khoảng **10–12 users**:
  - Khi tăng tải (offered load) gấp **5×** (từ 10 lên 50 users), throughput thực tế chỉ tăng **1.03×** (từ 4.03 RPS lên 4.17 RPS — gần như đi ngang / plateau).
  - Trong khi đó, độ trễ P95 phình to **4.44×** (từ 2700 ms lên 12000 ms).
  - Con số thuyết phục nhất: Effective concurrency ở 50 users là **41.9**, vượt xa số slot `--parallel 4` (tỉ lệ occupancy/slot = 10.47). Khoảng chênh lệch latency ~9.3 giây giữa 10 và 50 users hoàn toàn là **queue time** (thời gian nằm chờ trong hàng đợi khi 4 slot decode bị nghẽn hoàn toàn).

**2. Đánh giá Goodput@SLO:**
- Nếu đặt mục tiêu **SLO = P95 ≤ 3.0s**:
  - Ở 10 users: P95 = 2.7s → Goodput = **4.03 RPS** (đạt 100% SLO).
  - Ở 50 users: P95 = 12.0s → Goodput = **0 RPS** (toàn bộ request vi phạm SLO do hàng đợi tích lũy).

**3. Knob sẽ thay đổi trước tiên để nâng Goodput@SLO:**
- Knob thay đổi đầu tiên là **tăng `--parallel` (từ 4 lên 8 hoặc 12 slots)**.
- **Lý do**: RTX 3060 Ti có 8 GB VRAM trong khi model UD-Q4_K_XL chỉ chiếm 2.97 GB. VRAM còn trống hơn 4.5 GB, thừa khả năng cấp phát thêm KV cache slots cho batching. Tăng slot song song cho phép xử lý đồng thời nhiều request hơn trong mỗi vòng lặp memory-bandwidth-bound decode, giảm trực tiếp queue time mà không tốn thêm chi phí phần cứng.
