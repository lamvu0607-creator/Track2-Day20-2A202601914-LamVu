# Bonus - GPU offload sweep

Host `Windows-AMD64` · backend(s) `nvidia_cuda, vulkan` ·
llama.cpp `b10488` · `threads=6` · metric `tg128`

| -ngl | tg128 (tok/s) | vs -ngl 0 | vs best |
|:--|--:|--:|--:|
| 0 | 13.5 | 1.00x | 11% |
| 8 | 17.8 | 1.32x | 14% |
| 16 | 26.1 | 1.93x | 21% |
| 24 | 43.5 | 3.22x | 34% |
| 32 | 74.5 | 5.51x | 59% |
| 99 | 126.5 | 9.36x | 100% |

Best: `-ngl 99` at 126.5 tok/s
-- 9.36x faster than CPU-only.

Where the curve flattens tells you the model ran out of layers to move. Where it
*peaks below* full offload tells you something did not fit and the accelerator
started paying to fetch weights it could not hold.

## Your finding

**Full offload (`-ngl 99`) mang lại hiệu năng cao nhất tuyệt đối (126.5 tok/s), nhanh hơn 9.36× so với CPU-only (13.5 tok/s)**.

**Phân tích cơ chế:**
1. **Dung lượng VRAM**: Toàn bộ 35 layer của Gemma 4 E2B UD-Q4_K_XL (2.97 GB) cùng KV cache hoàn toàn nằm gọn trong 8 GB VRAM của RTX 3060 Ti, không hề bị thiếu hụt bộ nhớ.
2. **Nghẽn băng thông PCIe trong Partial Offload**: Khi chỉ offload một phần (từ -ngl 8 đến 32), quá trình decode phải liên tục truyền tensor trung gian (activation tensor) qua lại giữa System RAM và VRAM qua bus PCIe ở mỗi token step. Điều này tạo ra overhead rất lớn.
3. **Băng thông bộ nhớ GPU**: Khi offload toàn bộ 100% layer lên GPU (`-ngl 99`), toàn bộ phép nhân ma trận trọng số đều diễn ra cục bộ trên VRAM với băng thông bộ nhớ cực cao (~448 GB/s trên RTX 3060 Ti so với ~50 GB/s trên RAM DDR4 của CPU), giúp tốc độ decode tăng vọt từ 13.5 lên 126.5 tok/s.
