# Tiêu chuẩn Thiết kế Hợp đồng API (API Contract Specification)

## 1. Nguyên tắc thiết kế RESTful
- Sử dụng danh từ số nhiều cho resource URL: `/api/v1/orders`, `/api/v1/users/{user_id}`.
- Sử dụng chuẩn HTTP Verbs:
  - `GET`: Truy vấn dữ liệu (Idempotent, Safe).
  - `POST`: Tạo mới tài nguyên.
  - `PUT`: Cập nhật toàn bộ tài nguyên (Idempotent).
  - `PATCH`: Cập nhật một phần trường dữ liệu.
  - `DELETE`: Xóa tài nguyên (Idempotent).

## 2. Chuẩn định dạng Response Body
```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": { "page": 1, "limit": 20, "total": 150 },
  "timestamp": "2026-10-15T10:30:00Z"
}
```

## 3. Cơ chế Webhook / Callback
- Đăng ký callback URL:
  - Mỗi consumer đăng ký một callback URL riêng, bắt buộc HTTPS (TLS 1.2 trở lên), nhận request `POST` từ hệ thống lõi.
  - Mỗi callback URL được cấp một `secret` riêng, độ dài tối thiểu 32 ký tự, rotate định kỳ 90 ngày.
- Payload event chuẩn:
  ```json
  {
    "event": "order.status_updated",
    "event_id": "evt_8842",
    "occurred_at": "2026-10-22T11:00:00Z",
    "data": {}
  }
  ```
  - `event`: tên sự kiện dạng `<resource>.<action>` (vd `order.status_updated`, `payment.completed`).
  - `event_id`: định danh duy nhất của sự kiện, dùng làm khóa idempotency.
  - `occurred_at`: thời điểm phát sinh sự kiện, định dạng ISO 8601 UTC.
  - `data`: dữ liệu nghiệp vụ đi kèm sự kiện.
- Xác thực chữ ký (Signature Verification):
  - Mọi request webhook bắt buộc mang header `X-Webhook-Signature` và `X-Webhook-Timestamp`.
  - Chữ ký là chuỗi `HMAC-SHA256(secret, timestamp + "." + raw_body)` mã hóa hex; consumer bắt buộc tính lại và so sánh bằng thuật toán constant-time.
  - Consumer từ chối request có `X-Webhook-Timestamp` lệch quá 300 giây so với giờ hệ thống (chống replay attack).
- Chính sách Retry:
  - Chỉ HTTP response 2xx từ consumer được coi là nhận thành công; mọi mã khác hoặc timeout 10 giây kích hoạt retry.
  - Retry tối đa 5 lần theo backoff lũy tiến: 1 phút, 5 phút, 30 phút, 2 giờ, 6 giờ; hết số lần retry thì chuyển event vào Dead Letter Queue và cảnh báo SRE.
- Idempotency:
  - Consumer bắt buộc xử lý idempotent dựa trên `event_id`: một `event_id` chỉ được xử lý đúng 1 lần trong vòng 72 giờ.
