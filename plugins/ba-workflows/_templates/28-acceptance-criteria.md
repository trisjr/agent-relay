# Tiêu chí Chấp nhận (Acceptance Criteria - Gherkin BDD)

## Story: US-AUTH-01 - Đăng nhập bằng Email và Mật khẩu

```gherkin
Feature: Đăng nhập người dùng bằng email và mật khẩu

  Scenario: Đăng nhập thành công với thông tin hợp lệ
    Given Người dùng mở màn hình Đăng nhập
    And Tài khoản "alex@example.com" tồn tại và có trạng thái "ACTIVE"
    When Người dùng nhập email "alex@example.com"
    And Người dùng nhập mật khẩu chính xác "Secret@123"
    And Người dùng nhấn nút "Đăng nhập"
    Then Hệ thống tạo mới JWT session token
    And Hệ thống chuyển hướng người dùng đến màn hình Dashboard
    And Header hiển thị tên "Alex" và avatar cá nhân

  Scenario: Đăng nhập thất bại do nhập sai mật khẩu
    Given Người dùng mở màn hình Đăng nhập
    And Tài khoản "alex@example.com" tồn tại
    When Người dùng nhập email "alex@example.com"
    And Người dùng nhập mật khẩu sai "WrongPass123"
    And Người dùng nhấn nút "Đăng nhập"
    Then Hệ thống không tạo phiên đăng nhập
    And Hiển thị thông báo màu đỏ "Email hoặc mật khẩu không chính xác."
    And Ô mật khẩu được reset trống, ô email được giữ nguyên

  Scenario: Khóa tài khoản sau 5 lần nhập sai liên tiếp
    Given Tài khoản "alex@example.com" đã có 4 lần đăng nhập sai trước đó
    When Người dùng nhập mật khẩu sai lần thứ 5
    And Người dùng nhấn nút "Đăng nhập"
    Then Hệ thống cập nhật trạng thái tạm khóa 15 phút
    And Hiển thị thông báo "Tài khoản bị tạm khóa 15 phút do nhập sai nhiều lần."
    And Vô hiệu hóa nút "Đăng nhập" với đồng hồ đếm ngược 15:00
```
