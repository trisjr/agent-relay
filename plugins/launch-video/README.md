# launch-video

Biến project vừa làm xong (hoặc một website URL) thành một **launch video** ngắn, chỉn chu, sẵn để chia sẻ — render bằng HyperFrames. Agent đọc code project trực tiếp, không cần URL live hay screenshot.

Plugin này là bản vendor của [latent-spaces/brag](https://github.com/latent-spaces/brag) (MIT, tác giả Shunit Haviv Hakimi), clone từ upstream **v0.4.0**, commit `d06a77f`. Nội dung workflow giữ nguyên; chỉ đổi định danh cho khớp quy ước tên của AgentRelay (`brag` → `launch-video`, `brag-slim` → `launch-video-slim`) và đóng gói lại theo chuẩn marketplace.

## Skill

| Skill | Khi nào dùng |
| --- | --- |
| `launch-video` | Bản đầy đủ: chọn tone, lên plan cảnh, compose HyperFrames, mix nhạc + SFX có sẵn trong `assets/`, render video |
| `launch-video-slim` | Bản gọn một file, không asset kèm theo — model tự dựng toàn bộ bằng tool có sẵn trên máy. `launch-video` tự hand-off sang đây khi chạy trên Opus 5.5 (trừ khi có `--full` hoặc `--voice`) |

Trigger: `/launch-video`, `/launch-video-slim`, "show off this project", "make a launch video", "make a launch video for <url>".

Output ghi vào `launch-video-output/` (hoặc `launch-video-output-<timestamp>/` nếu đã tồn tại): `launch-video.mp4`, `launch-video.jpg` (poster), `launch-video-plan.md`, `share-copy.txt`.

## Yêu cầu

- Node.js (`npx hyperframes`), `ffmpeg` để cắt poster.
- `uv` nếu muốn chạy lại `skills/launch-video/scripts/analyze_music_cues.py` (phân tích beat nhạc).

## Cài đặt

```text
/plugin marketplace add trisjr/agent-relay
/plugin install launch-video@agent-relay
```

Nếu đã cài bản gốc từ marketplace upstream, nên gỡ một bản để hai skill không tranh nhau trigger "make a launch video".

## Đồng bộ với upstream

| Upstream | Ở đây |
| --- | --- |
| `skills/brag/` | `skills/launch-video/` |
| `skills/brag-slim/` | `skills/launch-video-slim/` |

Khi upstream ra bản mới: copy đè hai thư mục theo bảng trên, rồi đổi lại mọi chỗ còn chữ "brag" (`name` trong frontmatter, slash command, tên skill slim, tên file output, câu chữ, `sourceRoot` trong `assets/sfx/sfx-analysis.json`, tên package trong `scripts/pyproject.toml` và `uv.lock`). Kiểm tra bằng `grep -rni brag plugins/launch-video` (chỉ còn link nguồn upstream), cập nhật commit ở trên và bump version cả 5 manifest.

## License

MIT — xem [`LICENSE`](./LICENSE) (giữ nguyên copyright của tác giả gốc). Nhạc trong `skills/launch-video/assets/music/` lấy từ series "Happy Beats / Business Moves" của [ende.app](https://ende.app/en) (xem `assets/music/README.md`); dùng lại ngoài plugin thì kiểm tra điều khoản của nguồn.
