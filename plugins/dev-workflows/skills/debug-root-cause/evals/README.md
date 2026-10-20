# Chạy eval debug-root-cause

`evals.json` là bộ tình huống và tiêu chí hành vi, không phải kết quả đã chạy.
Kiểm tra JSON/frontmatter chỉ kiểm tra cấu trúc.

## Chuẩn bị

- Mỗi case dùng thư mục tạm riêng; copy **nội dung** các thư mục trong `files` vào đó, không chạy sửa trực tiếp trên fixture trong repo.
- Khởi tạo git và `git add` các file fixture để lưu baseline trong index; không commit. Lưu thêm bản sao nội dung ban đầu ngoài workspace của case.
- Case có `setup` thì thực hiện các bước đó trước khi giao task; giữ lại status/diff ban đầu để so sánh.
- Cấp bản skill đang thử cùng reference; đưa cho agent chỉ `prompt` và dữ liệu đầu vào, không đưa `expected_output` hay `expectations`. Không cho agent đọc workspace case khác. Không có subagent thì có thể chạy tuần tự, nhưng phải ghi rõ người viết skill cũng là người thực hiện.
- `files: []` là tình huống hội thoại hoặc yêu cầu môi trường riêng. Không có repo/runtime tương ứng thì chỉ review kỳ vọng, không tính là eval thực thi đã đạt.
- Các case nêu hạn chế tool/headless cần được runner thực sự áp dụng. Nếu chỉ mô tả hạn chế trong prompt, báo rõ đây là mô phỏng, không chứng minh hành vi của harness thật.

## Quan sát và chấm

Lưu prompt, phiên bản skill, transcript/lệnh và kết quả, diff cuối cùng, rồi chấm từng expectation theo hành vi quan sát được. Kiểm tra lại test và thay đổi file khi thích hợp; không chấm bằng việc agent nhắc lại đúng câu chữ. Tách lỗi fixture/runner khỏi lỗi hành vi.

Fixture `csv-export` dùng Python stdlib: `python3 -m unittest -v` có các case về comma, quote và round-trip. Fixture `obvious` chạy bằng `python3 session.py`. Fixture `flaky-order` có hai thứ tự cố định để kiểm tra, cùng chế độ chọn ngẫu nhiên; không dùng tỷ lệ ngẫu nhiên của vài lần chạy làm bằng chứng thống kê chắc chắn. Fixture `missing-env` cố ý chỉ có code và log, thiếu runner tích hợp và contract.

Báo case nào đã chạy, kết quả thực tế, model/harness nếu biết, giới hạn môi trường và case chưa chạy. Một lượt smoke test không phải benchmark đa agent; không suy ra độ tin cậy chỉ từ số case đạt.
