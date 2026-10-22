# Quy trình Phân tích Tác động Yêu cầu Thay đổi (CR Impact Matrix)

Khi khách hàng hoặc PO yêu cầu thay đổi nghiệp vụ giữa chừng, BA tuyệt đối không sửa tài liệu ngay mà phải tiến hành Phân tích Tác động (Impact Analysis).

## 4 Góc độ đánh giá tác động:
1. **Tác động Tài liệu (Documentation Drift)**: Cập nhật lại những file nào: SRS, FR, BR, User Story, Wireframe, Diagram nào?
2. **Tác động Kỹ thuật (Technical & Architecture)**: Có phải thay đổi schema CSDL không? Có breaking change API không?
3. **Tác động Kiểm thử (QA & Test Cases)**: Bao nhiêu test case cũ bị vô hiệu hoặc phải viết lại?
4. **Tác động Kế hoạch & Rủi ro (Cost & Schedule)**: Ước tính story point phát sinh, rủi ro trễ hạn sprint.
