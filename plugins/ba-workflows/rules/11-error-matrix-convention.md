# Quy chuẩn Ma trận Lỗi Tổng hợp (Consolidated Error Matrix)

Một tài liệu SRS hoàn chỉnh bắt buộc phải có Ma trận Lỗi tổng hợp:
1. **Error Code**: Mã định danh duy nhất (`ERR-xxx`).
2. **HTTP Code**: 4xx/5xx mapping.
3. **Trigger Condition**: Nguyên nhân cụ thể dẫn đến lỗi này.
4. **Localization Key**: Key đa ngôn ngữ dùng trong source code frontend/backend.
5. **UI Display Message**: Nội dung văn bản thân thiện hiển thị cho End-user (tiếng Việt/tiếng Anh).
6. **Severity**: Critical (Ngừng hệ thống), High (Chặn luồng chính), Medium (Lỗi validation form), Low (Cảnh báo phụ).
7. **Next Action**: Hướng dẫn bước xử lý tiếp theo của người dùng.
