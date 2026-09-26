# jev-dispatch

Plugin route task tới đúng **harness / model / effort** khi điều phối agent (Orca, swarm, DAG…). Mỗi task được chấm qua một **battery phán đoán TypeSafe Jev**, rồi một **policy thuần trong code** quyết định: Jev chỉ chấm, code mới route.

## Bối cảnh

Plugin có hai lớp:

- **MCP server** `mcp/server.py`: expose tool `ask(battery, task, context)`. Chỉ có một battery là `task_dispatch`, gồm 5 câu hỏi trong **một** request: `complexity` (Score, 0..4), `risk` (Score, 0..2), `needs_web`, `needs_long_context`, `needs_planning` (Noul). `needs_planning` vẫn được chấm và trả về, nhưng policy chưa dùng.
- **Skill** `dispatch-routing`: hướng dẫn flow gọi `ask` trước khi dispatch, cách đọc response, và cách vận hành (shadow mode, golden dataset, pin model). Cursor dùng rule `.cursor/rules/jev-dispatch.mdc` với cùng các quy tắc.

Server chạy bằng `uv run --script <PLUGIN_ROOT>/mcp/server.py`. Dependency khai báo trong block PEP 723 ở đầu `server.py` (`mcp[cli]>=2.2,<3`, `typesafe-sdk>=0.7.1,<0.8`, Python >= 3.10), `uv` tự cài vào env riêng của nó.

## Các skill

| Skill | Dùng khi | Làm gì |
| --- | --- | --- |
| `dispatch-routing` | Điều phối hoặc dispatch agent worker và cần chọn harness/model/effort cho task | Gọi `ask` trước khi dispatch, làm theo `routing` (`act`, `requires_approval`, `error`), log response để tích golden dataset, chạy shadow mode trước khi cho auto-route |

Skill kèm `evals/evals.json`: bộ prompt mẫu kèm kỳ vọng hành vi, dùng cho vòng đánh giá/iterate của skill-creator.

## Nguyên tắc dùng chung

- **Shadow mode trước, auto-route sau.** Chưa chạy lại golden set với policy hiện tại thì `routing` chỉ để log và tham khảo; coordinator vẫn tự quyết.
- **Fail-closed.** ESCALATE và error không bao giờ dẫn tới dispatch tự động. Task rủi ro cao luôn phải được user duyệt (`requires_approval`), kể cả khi Jev rất chắc.
- **Không đổi battery khi chưa re-eval.** Wording câu hỏi, state builder, hay `TYPESAFE_JEV_MODEL` đổi thì phải chạy lại golden set trước khi dùng kết quả để route.
- **Gửi đi tối thiểu.** `task` chỉ là mô tả ngắn, `context` chỉ có `repo`/`budget`, không có secret hay preamble (xem Data egress).

## Policy routing

Biến dùng trong bảng: `c` = `judgments.complexity`, `r` = `judgments.risk`, `tail` = `risk_tail` (xác suất risk rơi vào criterion index 2), `FLOOR_ROUTE` mặc định 0.35, `FLOOR_RISK` mặc định 0.85. Policy chạy từ trên xuống, **gặp rule đầu tiên khớp thì dừng**:

| # | Điều kiện | `routing` |
| --- | --- | --- |
| 1 | `r >= 1.5` hoặc `tail >= 0.2` | `ESCALATE`, `act=false`, `requires_approval=true`, `suggested={"harness":"claude","model":"opus","effort":"high"}` |
| 2 | `confidence.risk < FLOOR_ROUTE` | `ESCALATE`, `act=false` (risk unknown) |
| 3 | `confidence.complexity < FLOOR_ROUTE` | `ESCALATE`, `act=false` (complexity unknown) |
| 4 | `c >= 3.2` | `claude` / `opus` / `high` |
| 5 | `needs_web > 0.7` hoặc `needs_long_context > 0.7` | `codex` / `sol` / `medium` |
| 6 | `c < 1.2` và `r < 0.6` và `confidence.risk >= FLOOR_RISK` | `gemini` / `flash` / `high` |
| 7 | Còn lại | `codex` / `luna` / `max` |

`ESCALATE` luôn có dạng `{"harness":"ESCALATE","model":"orchestrator-llm","effort":"-","act":false,"why":...}`. Chỉ rule 1 thêm `requires_approval` và `suggested`. Các rule route thật (4–7) trả `act=true`.

Thứ tự đánh giá:

- Gate high-risk/tail chạy **đầu tiên** và không cần confidence floor: task chắc chắn rủi ro cao không bao giờ bị auto-dispatch.
- Sau đó cả hai confidence của Score phải `>= FLOOR_ROUTE`.
- `FLOOR_RISK` chỉ gate nhánh rẻ `gemini/flash`.
- Nhánh Noul (`> 0.7`) không có field confidence.

**Response thành công:** `{"model", "battery", "judgments", "confidence", "risk_tail", "score_scale", "routing", "usage"}`, thêm `context_ignored` khi có key context bị bỏ.

**Error contract.** Mọi lỗi đều trả về một dict, server không crash và không ném exception trần. Dạng: `{"error": str, "kind": ..., "routing": <ESCALATE với why = error>}`, có thể kèm `error_type`, `status`, `request_id`, `available`. Routing của error không bao giờ có `requires_approval`.

| `kind` | Khi nào |
| --- | --- |
| `config` | Thiếu `TYPESAFE_API_KEY` hoặc key sai định dạng; floor không hợp lệ |
| `input` | Battery lạ (kèm `available`); `task` rỗng, không phải string, hoặc dài quá 8000 ký tự; `context` không phải object |
| `api` | TypeSafe API trả lỗi (kèm `status`, `request_id` nếu có). Key đúng định dạng nhưng sai hoặc đã revoke sẽ ra ở đây với `status` 401 |
| `timeout` | Request quá thời gian chờ |
| `connection` | Không kết nối được API |
| `response` | Response thiếu answer, thiếu xác suất cho risk criterion 2, hoặc có giá trị không hữu hạn |

**Consumer phải xử lý như sau:**

- `act=false`: không dispatch theo `routing`.
- `requires_approval=true`: hỏi user trước khi dispatch, có thể đưa `suggested` ra làm đề xuất.
- Có field `error`: coi như `act=false`.
- `act=false` không kèm `requires_approval` (rule 2/3 và mọi error): coordinator tự quyết bằng reasoning model, hoặc hỏi user.

> **Policy này đã khác bản prototype từng được đo.** Gate risk/tail được đưa lên đầu và có thêm `requires_approval`, `FLOOR_RISK` giờ chỉ gate nhánh flash. Vì vậy phải **chạy lại golden set** (shadow mode) trước khi bật auto-routing.

## Biến môi trường

Server chỉ đọc 4 biến sau:

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `TYPESAFE_API_KEY` | — | Bắt buộc. Claude Code lấy từ `userConfig` sensitive của plugin (lưu trong keychain), Gemini CLI lấy từ extension setting (lưu dạng sensitive); harness khác truyền từ env của host. Không bao giờ ghi literal vào file. Server vẫn khởi động khi thiếu key, nhưng mọi `ask` đều trả `kind: "config"` cho tới khi host khởi động lại server với key trong env |
| `TYPESAFE_JEV_MODEL` | `jev-1.13.0` | Model đã pin. Chỉ bump sau khi re-eval golden set; để rỗng thì dùng mặc định |
| `JEV_DISPATCH_FLOOR_ROUTE` | `0.35` | Confidence tối thiểu của `risk` và `complexity` để route |
| `JEV_DISPATCH_FLOOR_RISK` | `0.85` | Confidence tối thiểu của `risk` cho nhánh rẻ `gemini/flash` |

- Floor phải thỏa `0 <= FLOOR_ROUTE <= FLOOR_RISK <= 1`. Sai định dạng hoặc ngoài khoảng thì mọi `ask` trả `kind: "config"`.
- Ngưỡng tail `0.2` là hằng số trong code, không cấu hình qua env.

## Data egress

- Mỗi lần gọi `ask` mà qua được bước validate local, server gửi lên TypeSafe API (mặc định `https://api.typesafe.ai`) các dữ liệu sau:
  - `task`
  - `context.repo` và `context.budget` đã qua allowlist (thiếu thì gửi giá trị mặc định)
  - chuỗi `harnesses` cố định trong code
- Giới hạn input:
  - `task`: string không rỗng, tối đa 8000 ký tự.
  - `context`: chỉ giữ key `repo` và `budget` có giá trị string tối đa 500 ký tự. Mọi thứ khác (kể cả `harnesses`) bị bỏ và liệt kê trong `context_ignored`.
- **Không bao giờ** đưa vào `task`/`context`: secret, credential, PII, dump source code/diff/log dài, preamble điều phối, capability token hay terminal handle. Chỉ mô tả task trong vài câu.
- `TYPESAFE_LOG_LEVEL=debug` (biến của SDK) ghi **toàn bộ** request/response body (gồm task và context) ra stderr của server; host thường lưu stderr vào log MCP. SDK chỉ redact header, không redact body. Chỉ bật khi debug, xong thì tắt.
- `TYPESAFE_BASE_URL` (biến của SDK) đổi host nhận request **kèm API key**. Chỉ đặt khi tin endpoint đó, và kiểm tra env của host không có biến này ngoài ý muốn.

## Dispatch log

Golden dataset là một file JSONL duy nhất: `~/.local/state/jev-dispatch/dispatch-log.jsonl`.

- Server không ghi file này. Coordinator ghi theo hướng dẫn của skill `dispatch-routing` (Cursor thì theo rule).
- File chỉ append:
  - Mỗi dòng là một JSON object, append qua `jq -c . <<'EOF' >> <log>` chứ không dùng `echo`. JSON sai thì `jq` không ghi gì.
  - Không sửa hay xoá dòng cũ.
- File nằm ngoài mọi repo nhưng chứa text của task, nên cũng áp quy tắc không có secret như `task`.

Có hai loại record, nối với nhau bằng `id`: task id của orchestrator nếu có (vd task id của Orca), không có thì tự sinh, vd UTC timestamp kèm slug ngắn.

| `event` | Ghi khi nào | Field |
| --- | --- | --- |
| `route` | Sau **mỗi** lần gọi `ask`, kể cả khi error, ESCALATE hay không dispatch gì | `id`, `ts` (UTC ISO 8601), `task` và `context` đúng như đã gửi, `response` là nguyên response của `ask`, `used` = `{harness, model, effort}` thực sự dispatch |
| `outcome` | Một lần khi task kết thúc, sau mọi lần retry | `id`, `ts`, `outcome` (`ok` \| `retried` \| `failed` \| `cancelled`), `note` (tùy chọn, một dòng) |

- `used.model`/`used.effort` là `null` khi để mặc định của harness.
- `used` là `null` khi không dispatch gì; khi đó không ghi `outcome`.
- `cancelled` là task dừng vì lý do không liên quan tới worker, không tính vào metric routing.

Phải log `task` và `context` vì response của `ask` không chứa hai field này, mà chấm lại golden set sau khi đổi wording hoặc model thì cần cả hai. Thay đổi chỉ nằm ở policy thì replay qua `route()` là đủ, không tốn API call.

## Cơ sở thiết kế

- **Jev chấm, code route:** Jev trả xác suất đã calibrate kèm confidence cho các phán đoán hẹp. Policy nằm trong code nên đọc được, test được, và đổi ngưỡng không cần đổi model. Structured output của LLM chỉ đảm bảo đúng shape, không có confidence đáng tin để đặt ngưỡng.
- **Chi phí:** 5 câu hỏi dùng chung state trong một request, khoảng 740 input token, tức khoảng $0.00003/task ($0.042/1M input token, output free). Fallback sang reasoning model đắt hơn 2–3 bậc, nên đặt escalation budget khoảng 5–10% số dispatch.
- **Đọc đúng tín hiệu:**
  - Score là vị trí có trọng số **0-based**.
  - Noul gần 0.5 nghĩa là "không chắc", không phải "mức trung bình", và Noul không có confidence.
  - Confidence đo độ tập trung của phân phối, không phải xác suất đúng.
  - Kết quả không deterministic tuyệt đối giữa các lần chạy, nên regression test cần tolerance.
- **Điểm yếu đã công bố của Jev:** toán/ngày tháng, suy luận nhiều bước, nội dung adversarial trong state (text trong `task` có thể lái điểm risk). Jev chạy tốt nhất với tiếng Anh; tiếng Việt cho kết quả hợp lý trên mẫu nhỏ, cần tự đo trên golden set.
- **Pin model:** alias `jev-latest` có thể đổi version bất cứ lúc nào, nên pin `jev-1.13.0` và log field `model` mỗi lần gọi. Đổi wording câu hỏi, state builder hay model đều bắt buộc re-run golden set, vì Jev đọc instruction theo nghĩa đen.
- **Shadow mode và golden dataset:** gọi `ask` ở mọi dispatch nhưng coordinator vẫn tự quyết. Log response cùng outcome của worker theo [Dispatch log](#dispatch-log). Tune floor trên một phần log, kiểm lại trên phần còn lại (ưu tiên ca biên), rồi mới bật auto-route.

## Cài đặt

1. Cài plugin qua marketplace `agent-relay`: xem mục "Cài từ bản local" (và đoạn "Cài từ GitHub") trong README gốc của repo.
2. Chuẩn bị:
   - `uv` có trên `PATH`.
   - API key TypeSafe:
     - Claude Code: nhập vào dialog `TypeSafe API Key` khi cài/enable plugin qua `/plugin`. Đổi key bằng `/plugin configure jev-dispatch@agent-relay`. Cài bằng CLI `claude plugin install` thì không có dialog, nên phải truyền `--config typesafe_api_key=...` hoặc chạy `/plugin configure` sau đó.
     - Gemini CLI: nhập khi cài extension.
     - Harness khác: `TYPESAFE_API_KEY` phải có trong môi trường khởi chạy harness.
     - Không commit key, không ghi key vào file config.
   - Chạy `uv run --script <PLUGIN_ROOT>/mcp/server.py` một lần trước khi mở harness, thấy server chờ stdin thì Ctrl+C. Lần launch đầu trên máy mới phải tải dependency và có thể vượt timeout khởi động MCP của harness; sau đó uv dùng cache.
3. Kiểm tra MCP server theo từng harness:

| Harness | Wiring | Ghi chú |
| --- | --- | --- |
| Claude Code | Tự động (`.mcp.json`, `${CLAUDE_PLUGIN_ROOT}`) | Key lấy từ `userConfig.typesafe_api_key` (sensitive, lưu trong keychain) nên không phụ thuộc vào cách mở Claude Code. Đặt key qua `/plugin configure`, đừng dựa vào `export TYPESAFE_API_KEY` trong shell. Các biến tùy chọn vẫn kế thừa env của process Claude Code |
| Gemini CLI | Tự động (`mcpServers` trong `gemini-extension.json`, `${extensionPath}`) | Extension không kế thừa env của shell. Lúc cài sẽ hỏi `TypeSafe API Key` (lưu dạng sensitive). Các biến tùy chọn không tới được server nên dùng mặc định |
| Codex | Tự động (`mcp.json`) nhưng **fail-closed** | Key không tới được server, nên mọi `ask` trả `kind: "config"`. Cần cấu hình tay như bên dưới |
| Kimi Code | Tự động (`mcpServers` trong `.kimi-plugin/plugin.json`, `cwd: "./mcp"`) | **Unverified** ở runtime; docs không nói có kế thừa env hay không |
| Qoder | Tự load `.mcp.json` của plugin | **Unverified**: chưa rõ Qoder có expand `${CLAUDE_PLUGIN_ROOT}` và `${user_config.*}` không. Nếu server không start hoặc `ask` báo lỗi key, cấu hình tay |
| Cursor | **Chỉ cấu hình tay** | Plugin chỉ ship rule `.cursor/rules/jev-dispatch.mdc` |

Trong các snippet cấu hình tay, thay `/ABS/PATH/jev-dispatch` bằng đường dẫn tuyệt đối tới bản plugin đã cài (hoặc bản clone).

**Codex:** thêm vào `~/.codex/config.toml`, rồi tắt bản do plugin cung cấp để khỏi trùng tool. Plugin id lấy theo marketplace.

```toml
[mcp_servers.jev-dispatch]
command = "uv"
args = ["run", "--script", "/ABS/PATH/jev-dispatch/mcp/server.py"]
env_vars = ["TYPESAFE_API_KEY"]

[plugins."jev-dispatch@<marketplace>".mcp_servers.jev-dispatch]
enabled = false
```

**Qoder:** thêm vào `~/.qoder/settings.json`, và để `TYPESAFE_API_KEY` trong shell khởi chạy Qoder.

```json
{
  "mcpServers": {
    "jev-dispatch": {
      "command": "uv",
      "args": ["run", "--script", "/ABS/PATH/jev-dispatch/mcp/server.py"]
    }
  }
}
```

**Cursor:** thêm vào `~/.cursor/mcp.json` (global) hoặc `.cursor/mcp.json` (project).

```json
{
  "mcpServers": {
    "jev-dispatch": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--script", "/ABS/PATH/jev-dispatch/mcp/server.py"],
      "env": { "TYPESAFE_API_KEY": "${env:TYPESAFE_API_KEY}" }
    }
  }
}
```

**Debug:**

- `uv run --script <PLUGIN_ROOT>/mcp/server.py`: chính là lệnh launch mà harness dùng. Server chạy stdio và chờ client, nên lỗi cài dependency hay lỗi import sẽ hiện ngay ở đây.
- `uv run --with "mcp[cli]>=2.2,<3" --with "typesafe-sdk>=0.7.1,<0.8" mcp dev <PLUGIN_ROOT>/mcp/server.py`: mở MCP Inspector.
  - `mcp dev` import `server.py` ngay trong interpreter hiện tại, nên cần cả `mcp[cli]` lẫn `typesafe-sdk`.
  - Cần Node/`npx`; Inspector được kéo từ npm và không pin version.
  - Mỗi lần gọi `ask` từ Inspector là một request **tính phí** tới TypeSafe API.
