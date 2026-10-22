# Quy chuẩn Wireframe HTML Nguyên khối (Low-Fidelity HTML Wireframe)

Mục đích: Cung cấp giao diện bấm được trực tiếp cho khách hàng và lập trình viên kiểm tra bố cục & luồng tương tác mà không bị xao nhãng bởi màu sắc thẩm mỹ.

## Quy tắc thiết kế:
1. **Độc lập và tự chứa (Single-file HTML)**: Toàn bộ HTML và CSS nằm trong 01 file duy nhất, mở trực tiếp bằng trình duyệt.
2. **Bảng màu xám đơn sắc (Grayscale & High Contrast)**:
   - Nền: Trắng `#FFFFFF` hoặc xám nhạt `#F9FAFB`.
   - Đường viền/Khung: `#E5E7EB` / `#D1D5DB`.
   - Văn bản: Đen `#111827` và xám `#6B7280`.
   - Điểm nhấn trạng thái: Xanh trung tính hoặc viền đậm `#1E293B`.
   - **Ngoại lệ duy nhất — trạng thái lỗi (Error state)**: được phép dùng viền đỏ `#EF4444` cho input lỗi và text lỗi `#B91C1C` cho thông báo lỗi, nhằm đảm bảo người xem nhận diện rõ trạng thái lỗi. Mọi thành phần khác (bao gồm cả trạng thái success, warning, info) vẫn giữ nguyên tắc grayscale.
3. **Sử dụng Semantic HTML5**: header, nav, main, section, article, footer, form, input, button.
4. **Mô phỏng đầy đủ trạng thái UI**: Empty state, Validated input, Error state, Modal popup.
