# Quy ước mã hoá Quy tắc Nghiệp vụ (Business Rules - BR)

## 1. Định dạng chuẩn
`BR-[DOMAIN]-[SEQ]`

- **DOMAIN**: Lĩnh vực hoặc nghiệp vụ cốt lõi (vd: `SEC`, `PRIC`, `PROMO`, `KYC`, `TAX`).
- **SEQ**: Số thứ tự 3 chữ số (vd: `001`, `002`).

*Ví dụ:*
- `BR-SEC-001`: Mật khẩu người dùng phải có tối thiểu 8 ký tự, gồm ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt.
- `BR-SEC-002`: Tài khoản bị tạm khóa 15 phút nếu nhập sai mật khẩu liên tiếp 5 lần.
- `BR-PROMO-001`: Mỗi đơn hàng chỉ được áp dụng tối đa 01 voucher giảm giá sản phẩm và 01 voucher freeship.

## 2. Cấu trúc mô tả Business Rule
- **Tên quy tắc**: Tóm tắt nội dung quy tắc.
- **Phạm vi áp dụng**: Áp dụng cho module, kênh, hoặc nhóm người dùng nào.
- **Logic phát biểu**:
  - **KHI (WHEN / CONDITION)**: Điều kiện kích hoạt quy tắc.
  - **THÌ (THEN / ACTION)**: Hành vi hoặc ràng buộc bắt buộc hệ thống phải tuân thủ.
  - **NGOẠI LỆ (UNLESS / EXCEPTION)**: Các trường hợp được miễn trừ (nếu có).
