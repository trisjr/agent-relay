# spec-readiness-gate

Plugin chấm **độ sẵn sàng của task spec** trước khi coordinator dispatch cho worker (`worker-start --spec`, `task-create` của Orca). Mỗi spec được chấm qua một **battery phán đoán TypeSafe Jev** trong một request, rồi một **policy thuần trong code** ra verdict: `dispatch`, `clarify` (chỉ rõ trường nào yếu) hoặc `escalate`. Jev chỉ chấm, code mới quyết. Plugin không viết hay vá spec thay coordinator.

Plugin là **add-on**: `orca-workflows` chạy bình thường khi vắng plugin. Không có API key thì skill dùng checklist thủ công 5 trường.

## Bối cảnh

Mọi fan-out có giám sát trong `orca-workflows` dispatch worker bằng spec theo contract 5 trường: **Target / Change / Constraints / Ownership / Observable acceptance**. Spec mơ hồ làm worker fail, đi lệch hoặc phải escalate giữa chừng, tốn trọn một lần dispatch. Plugin cho coordinator một thang đo nhất quán trước khi dispatch, và một log để học xem spec kiểu nào hay gây fail.

Plugin có hai lớp:

- **MCP server** `mcp/server.py`: expose tool `ask(battery, task, context)`, battery duy nhất `spec_readiness`.
- **Skill** `spec-readiness`: khi nào gọi, cách đọc verdict, clarify loop, checklist thủ công, format log, tiêu chí bật enforce. Cursor dùng rule `.cursor/rules/spec-readiness-gate.mdc`.

## Các skill

| Skill | Dùng khi | Làm gì |
| --- | --- | --- |
| `spec-readiness` | Coordinator sắp dispatch spec cho worker (dag-build, research-swarm, parallel-review), hoặc worker xong và cần log outcome | Gọi `ask` trước `worker-start`/`task-create`, theo `verdict` (enforce) hoặc chỉ báo một dòng (shadow), clarify đúng trường yếu, log verdict + downstream |

Skill kèm `evals/evals.json`: 11 ca mẫu kèm kỳ vọng hành vi (có ca spec tiếng Việt, injection, thiếu key, shadow không chặn).

## Battery `spec_readiness`

Sáu câu hỏi trong **một** request (~$0.00003/lần):

| Câu hỏi | Loại | Hỏi gì |
| --- | --- | --- |
| `target_specific` | Noul | Target có chỉ đúng một đối tượng cụ thể (git ref, path, module) không |
| `change_scoped` | Noul | Change có nói rõ làm gì **và** ranh giới không làm gì |
| `constraints_stated` | Noul | Constraints có liệt kê các điều cấm thật sự |
| `ownership_clear` | Noul | Ownership có chỉ rõ file/thư mục, không chồng lấn với `context.siblings` |
| `acceptance_testable` | Noul | Acceptance kiểm được bằng lệnh hoặc quan sát cụ thể |
| `overall_readiness` | Score 0..4 | 0 placeholder … 2 đủ 5 trường hình thức … 4 dispatch-ready |

Server còn gửi kèm một chuỗi `contract` cố định mô tả 5 trường, để Jev hiểu ngữ cảnh. `round` **không** gửi cho Jev: nó chỉ là input của policy.

## Policy

Chạy từ trên xuống, **gặp rule đầu tiên khớp thì dừng**:

| # | Điều kiện | `verdict` |
| --- | --- | --- |
| 1 | Floor/mode không hợp lệ | error `kind: "config"` |
| 2 | `confidence.overall_readiness < SPECGATE_FLOOR_CONF` | `escalate` (readiness unknown) |
| 3 | `overall_readiness >= SPECGATE_FLOOR_SCORE` và không Noul nào `< SPECGATE_FLOOR_FIELD` | `dispatch` |
| 4 | `round = "1"` | `clarify`, `missing_fields` = các Noul dưới floor, hoặc `["overall"]` nếu chỉ điểm tổng thấp |
| 5 | `round = "2"` | `clarify` + `exhausted: true`: coordinator tự quyết, dispatch thì ghi `readiness_override` vào spec |

Mọi verdict có `act`, `why`, `round`. Rule escalate đứng trước nên confidence thấp vẫn escalate ở round 2.

**Response thành công:** `{"model", "battery", "mode", "spec_hash", "judgments", "confidence", "score_scale", "verdict", "latency_ms", "usage"}`, thêm `context_ignored` khi có key context bị bỏ. `spec_hash` = `sha256:` + hash của `task`, dùng để join log.

**Error contract.** Mọi lỗi đều trả về dict, không crash: `{"error", "kind", "mode", "verdict": {"act": "escalate", "why"}}`, có thể kèm `error_type`, `status`, `request_id`, `available`.

| `kind` | Khi nào |
| --- | --- |
| `config` | Thiếu `TYPESAFE_API_KEY` (rỗng hoặc placeholder `${...}` chưa expand), key sai định dạng, floor ngoài khoảng, mode lạ |
| `input` | Battery lạ (kèm `available`); `task` rỗng hoặc > 8000 ký tự; `context` không phải object; `context.round` khác `"1"`/`"2"` |
| `api` | TypeSafe API trả lỗi (kèm `status`, `request_id`); key sai sẽ ra đây với `status` 401 |
| `timeout` | Request quá thời gian chờ |
| `connection` | Không kết nối được API |
| `response` | Response thiếu answer hoặc có giá trị không hữu hạn (NaN/Inf) |

Gate chỉ sai theo hướng an toàn: clarify thừa hoặc escalate, không bao giờ tự `dispatch` khi không chắc. `dispatch` chỉ nói spec **rõ**, không nói việc đó **an toàn**.

## Shadow và enforce

- `shadow` (mặc định): chấm, báo verdict một dòng cho user, ghi log, **không chặn** dispatch.
- `enforce`: theo `verdict.act`.
- Server chỉ **echo** `mode` trong mọi response, không bao giờ đổi verdict theo mode, nên log shadow ghi đúng điều enforce sẽ làm.
- Chỉ **user** đổi mode: Claude Code qua `/plugin configure spec-readiness-gate@agent-relay` (option `mode`), harness khác qua env `SPECGATE_MODE`. Tiêu chí gợi ý để bật enforce nằm trong SKILL.md (≥ 50 spec có downstream, tương quan rõ với outcome, clarify precision ≥ 80%, p95 latency < 2s).

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `TYPESAFE_API_KEY` | — | Optional. Thiếu thì mọi `ask` trả `kind: "config"` và skill dùng checklist thủ công. Không bao giờ ghi literal vào file |
| `TYPESAFE_JEV_MODEL` | `jev-1.13.0` | Model đã pin, chỉ bump sau khi re-eval |
| `SPECGATE_FLOOR_FIELD` | `0.5` | Noul của trường nào dưới floor thì trường đó vào `missing_fields`. Khoảng [0, 1] |
| `SPECGATE_FLOOR_SCORE` | `2.0` | `overall_readiness` tối thiểu để `dispatch`. Khoảng [0, 4] |
| `SPECGATE_FLOOR_CONF` | `0.35` | Confidence tối thiểu của `overall_readiness`, dưới floor thì `escalate`. Khoảng [0, 1] |
| `SPECGATE_MODE` | `shadow` | `shadow` \| `enforce` |

Giá trị rỗng hoặc placeholder chưa expand (`${user_config.x}`) được coi như chưa đặt.

## Data egress

- Mỗi lần `ask` qua được validate local, server gửi lên TypeSafe API: `task` (toàn văn spec), `context.repo` (≤ 500 ký tự), `context.siblings` (≤ 1000 ký tự) và chuỗi `contract` cố định. Key khác hoặc giá trị quá dài bị bỏ, liệt kê trong `context_ignored`.
- **Không bao giờ** đưa vào `task`/`context`: secret, credential, PII, preamble điều phối, capability token hay terminal handle.
- `TYPESAFE_LOG_LEVEL=debug` (biến của SDK) ghi toàn bộ request body ra stderr của server; chỉ bật khi debug.

## Readiness log

Golden dataset: `~/.local/state/spec-readiness-gate/readiness-log.jsonl`, append-only, do coordinator ghi (server không ghi) qua `jq -c . <<'EOF' >> <log>`.

| `event` | Ghi khi nào | Field chính |
| --- | --- | --- |
| `verdict` | Sau mỗi `ask` trả judgments (error không log) | `ts`, `mode`, `run_id`, `worker`, `lang`, `spec_hash`, `model`, `judgments`, `confidence`, `verdict`, `latency_ms` |
| `downstream` | Khi worker của spec đã dispatch kết thúc | `ts`, `run_id`, `worker`, `spec_hash` của spec **thực sự dispatch**, `downstream.worker_outcome` (`succeeded` \| `failed` \| `escalated`), `reworked`, `fields_at_fault` |
| `label` | Khi user xác nhận trường bị flag có thật sự thiếu | `ts`, `spec_hash`, `flagged`, `confirmed` |

Log **không chứa raw spec**, chỉ `spec_hash`: spec có thể chứa nội dung nhạy cảm, còn tune floor chỉ cần replay `verdict()` trên judgments đã log (không tốn API call). Đổi wording câu hỏi hoặc model thì re-eval bằng `evals/evals.json`.

## Cài đặt

1. Cài plugin qua marketplace `agent-relay` (xem README gốc của repo).
2. Cần `uv` trên `PATH`. Chạy `uv run --script <PLUGIN_ROOT>/mcp/server.py` một lần trước khi mở harness để uv cache dependency (lần đầu có thể vượt timeout khởi động MCP), thấy server chờ stdin thì Ctrl+C.
3. API key TypeSafe (optional):
   - Claude Code: nhập ở dialog `TypeSafe API Key` khi cài/enable, hoặc `/plugin configure spec-readiness-gate@agent-relay`. Option `mode` cũng đổi ở đây.
   - Gemini CLI: nhập khi cài extension (bỏ trống được). Extension không kế thừa env của shell nên `SPECGATE_MODE` và floor giữ mặc định.
   - Harness khác: `TYPESAFE_API_KEY` trong môi trường khởi chạy harness.

| Harness | Wiring | Ghi chú |
| --- | --- | --- |
| Claude Code | Tự động (`.mcp.json`, `${CLAUDE_PLUGIN_ROOT}`) | Key và mode lấy từ `userConfig` |
| Gemini CLI | Tự động (`gemini-extension.json`, `${extensionPath}`) | Key từ extension setting |
| Codex | Tự động (`mcp.json`, `${PLUGIN_ROOT}`) | Key không tới server nên mọi `ask` trả `kind: "config"` (skill vẫn chạy bằng checklist). Muốn dùng Jev thì cấu hình tay như dưới |
| Kimi Code | Tự động (`.kimi-plugin/plugin.json`, `cwd: "./mcp"`) | **Unverified** ở runtime |
| Qoder, Cursor | Cấu hình tay | Cursor chỉ nhận rule `.cursor/rules/spec-readiness-gate.mdc` |

**Codex** (`~/.codex/config.toml`), thay `/ABS/PATH` bằng đường dẫn plugin:

```toml
[mcp_servers.spec-readiness-gate]
command = "uv"
args = ["run", "--script", "/ABS/PATH/spec-readiness-gate/mcp/server.py"]
env_vars = ["TYPESAFE_API_KEY", "SPECGATE_MODE"]

[plugins."spec-readiness-gate@<marketplace>".mcp_servers.spec-readiness-gate]
enabled = false
```

**Qoder / Cursor** (`~/.qoder/settings.json`, `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "spec-readiness-gate": {
      "command": "uv",
      "args": ["run", "--script", "/ABS/PATH/spec-readiness-gate/mcp/server.py"],
      "env": { "TYPESAFE_API_KEY": "${env:TYPESAFE_API_KEY}" }
    }
  }
}
```

Qoder bỏ `env` và để `TYPESAFE_API_KEY` trong shell khởi chạy Qoder.

## Kiểm tra

Test offline với fake client, không gọi mạng (`python` trần không có SDK nên chạy qua `uv`):

```sh
cd plugins/spec-readiness-gate/mcp
uv run --with "mcp[cli]>=2.2,<3" --with "typesafe-sdk>=0.7.1,<0.8" python test_server.py
```

## Tích hợp (PR follow-up)

Chưa nằm trong bản đầu, mỗi mục là một PR nhỏ, revert được: bước "nếu có tool thì chấm spec" trong `orca-workflows/dag-build`; chế độ nhận `missing_fields` làm input targeted trong `clarify-requirements`; một dòng nhắc gate trong coordinator rules của `orca-router`.
