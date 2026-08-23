# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.1 | 2954.0 | 2954.1 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 2536.1 | 2536.2 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.0 | 2500.0 | 2500.1 |

Mean per stage (ms): embed **0.0** · retrieve **0.0** ·
llm **2663.4** · total **2663.5**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Which N16-N19 pieces are real

**1. Khai báo trạng thái các thành phần (Real / Stub):**
- **N16 Cloud/IaC**: **Stub** (chạy trực tiếp trên máy local Windows thay vì cloud provisioning).
- **N17 Data pipeline**: **Stub** (dùng tập tài liệu mẫu `TOY_DOCS` in-memory).
- **N18 Lakehouse**: **Stub** (dữ liệu lưu dạng Python dictionary cục bộ).
- **N19 Vector + features**: **Stub** (thuật toán lọc keyword overlap thay vì vector database như Milvus/Qdrant).
- **N20 Serving**: **REAL** (`llama-server` chạy Gemma 4 E2B trên backend CUDA/GPU).

**2. Đánh giá Bottleneck và Giải pháp:**
- Giai đoạn chiếm ưu thế tuyệt đối là **LLM generation (2663.4 ms ~ 100% tổng thời gian)**, hoàn toàn khớp với kỳ vọng vì retrieval in-memory chỉ tốn < 0.1 ms.
- **Nếu cần giảm latency pipeline đi 2×**: Cần tấn công trực tiếp vào tầng LLM Serving bằng cách:
  1. **Prompt Caching / Prefix Caching**: Tận dụng prefix cache cho `SYSTEM_PROMPT` và cấu trúc context để giảm thiểu TTFT (prefill time).
  2. **Speculative Decoding / Giới hạn generation**: Tối ưu số token decode tối đa và áp dụng Multi-Token Prediction (MTP) của Gemma 4 để tăng tốc độ phát sinh token.
