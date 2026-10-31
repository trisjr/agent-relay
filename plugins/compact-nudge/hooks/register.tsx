/**
 * @file register.tsx
 * @description Nhắc user compact khi context vượt ngưỡng, kèm lệnh /compact do chính session soạn sẵn
 */
import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, RenderSurface } from 'claude-code'

import type { Nudge } from '../types'

// Đổi tag khi field của Nudge đổi: giá trị bản cũ lưu lại qua reload bị bỏ.
export const nudge = atom({ plugin: 'compact-nudge', key: 'nudge' } as const, null, { shape: 'nudge-2' })
export const nextAt = atom({ plugin: 'compact-nudge', key: 'nextAt' } as const, null)

const PANE = 'compact-nudge'
const FALLBACK = '/compact '
// Auto-compact chạy ở khoảng window - 33K; nhắc trước đó để lời nhắc còn ý nghĩa.
const WINDOW_SHARE = 0.8

export function positive(value: unknown, fallback: number): number {
  const n = Number(value)
  return Number.isFinite(n) && n > 0 ? n : fallback
}

/** Mốc nhắc kế tiếp, chia đều theo step: 262K với ngưỡng 200K, step 100K cho ra 300K. */
export function nextMilestone(tokens: number, base: number, step: number): number {
  return base + step * (Math.floor((tokens - base) / step) + 1)
}

/** Có surface nào vẽ được pane/band không; không có (-p, SDK chưa attach) thì để nudge.py nhắc. */
async function canDraw($: EngineInterface): Promise<boolean> {
  return (await $.session.surfaces()).length > 0
}

// Desktop vẽ band thành card ngay trên ô chat; pane chỉ mở khi còn surface khác (terminal, VS Code, mobile).
// Session chỉ có desktop thì đóng pane còn sót (mở từ terminal, hoặc từ bản cũ trước reload) để không hiện hai lần.
async function showNudge($: EngineInterface, surfaces: readonly RenderSurface[]): Promise<void> {
  if (surfaces.some(surface => surface !== 'desktop')) {
    await openPane($)
  } else {
    await $.ui.close({ id: PANE })
  }
}

// Policy của tổ chức có thể chặn $.env.set: khi đó nudge.py vẫn nhắc, module phải đứng ngoài.
let isEnvDenied = false

// nudge.py chạy ở Stop, trước turn.complete, nên phải báo trước qua env: '1' là module này lo nhắc.
async function announce($: EngineInterface, isOwner: boolean): Promise<void> {
  const set = await $.env.set('COMPACT_NUDGE_MODULE', isOwner ? '1' : undefined)
  isEnvDenied = set.deny !== undefined
}

async function baseThreshold($: EngineInterface, threshold: number, window: number): Promise<number> {
  const capped = positive(await $.env.get('CLAUDE_CODE_AUTO_COMPACT_WINDOW'), window)
  return Math.min(threshold, Math.floor(Math.min(window, capped) * WINDOW_SHARE))
}

async function openPane($: EngineInterface): Promise<void> {
  await $.ui.open({ id: PANE, title: 'Compact', closeOnEscape: true, rows: 6 })
}

async function dismissNudge($: EngineInterface): Promise<void> {
  await update($, nudge, current => (current ? { ...current, isDismissed: true } : current))
  await $.ui.close({ id: PANE })
}

async function resetNudge($: EngineInterface): Promise<void> {
  await update($, nudge, () => null)
  await update($, nextAt, () => null)
  await $.ui.close({ id: PANE })
}

async function fillCommand($: EngineInterface, current: Nudge): Promise<void> {
  const box = await $.prompt.read()
  if (box.text.trim() !== '') {
    $.ui.toast('Ô prompt đang có nội dung: xoá đi rồi bấm Điền lệnh, hoặc bấm Tab lấy gợi ý.')
    return
  }
  const filled = await $.prompt.fill({ text: current.command ?? FALLBACK })
  if (filled.isFilled) {
    await dismissNudge($)
  }
}

const ASK = [
  'Context của session này sắp quá lớn và người dùng sẽ chạy /compact.',
  'Viết DUY NHẤT một dòng, bắt đầu bằng "/compact ", tối đa 60 từ, tiếng Việt,',
  'nói rõ cần GIỮ LẠI: task đang làm, file/hàm chính, quyết định đã chốt, các hướng đã thử và vì sao loại, lỗi hoặc việc còn dở;',
  'và có thể BỎ: output/log dài đã xử lý xong.',
  'Không giải thích, không markdown, không làm gì khác.',
].join(' ')

const MARKS = /^[\s>*_`"'“”(.]+|[\s*_`"'“”).]+$/g
// /compact có thể nằm giữa dòng, trong backtick/ngoặc kép/in đậm: "Lệnh: `/compact giữ X`".
const COMMAND = /(?:^|[\s`"'“*_(>])\/compact(?=[\s`"'”*_)]|$)(.*)$/

/** Rút dòng /compact từ câu trả lời của fork; null khi câu trả lời rỗng. */
export function toCommand(text: string): string | null {
  const lines = text
    .split('\n')
    .filter(l => !l.trim().startsWith('```'))
    .map(l => l.replace(MARKS, ''))
    .filter(l => l !== '')
  for (const [i, line] of lines.entries()) {
    const match = COMMAND.exec(line)
    if (match) {
      const rest = (match[1] ?? '').replace(MARKS, '') || (lines[i + 1] ?? '')
      return `${FALLBACK}${rest}`.trimEnd()
    }
  }
  const first = lines[0]
  return first === undefined ? null : `${FALLBACK}${first}`
}

export function formatTokens(tokens: number): string {
  return `${Math.round(tokens / 1000)}K`
}

function drawNudge($: EngineInterface, e: Parameters<EngineInterface['ui']['resolve']>[0], current: Nudge) {
  const { Box, Button, Text } = $.ui.resolve(e)
  const draft =
    current.draft === 'drafting'
      ? 'Đang soạn lệnh /compact gợi ý…'
      : current.draft === 'failed'
        ? 'Không soạn được lệnh gợi ý; Điền lệnh sẽ điền /compact để tự viết.'
        : current.command
  // Card desktop có tiêu đề đậm như notice của app; nơi khác giữ màu vàng cũ.
  const isDesktop = e.surface === 'desktop'

  // Nút native của desktop cao hơn một hàng chữ: thiếu gap thì nút đè lên dòng ngay trên. Terminal vẽ gap "sm" dọc là 0 hàng.
  return (
    <Box flexDirection="column" gap="sm">
      <Text bold={isDesktop} color={isDesktop ? undefined : 'yellow'}>
        Context {formatTokens(current.tokens)} — nên compact để giảm chi phí mỗi lượt.
      </Text>
      <Text dimColor>{draft}</Text>
      <Box>
        <Button key="fill" label="Điền lệnh" hotkey="c" variant="primary" onPress={() => fillCommand($, current)} />
        <Text> </Text>
        <Button key="dismiss" label="Bỏ qua" hotkey="x" role="dismiss" onPress={() => dismissNudge($)} />
      </Box>
    </Box>
  )
}

export const register: Register = (on, options) => {
  const threshold = positive(options.threshold, 200000)
  const step = positive(options.step, 100000)

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.isAborted || e.agentId !== undefined || isEnvDenied) {
      return result
    }
    const surfaces = await $.session.surfaces()
    if (surfaces.length === 0) {
      return result
    }

    const { context } = await $.session.usage()
    const tokens = context.tokens
    if (tokens === undefined) {
      return result
    }
    const base = await baseThreshold($, threshold, context.window)
    if (tokens < base) {
      // Context tụt mà không qua session.compact (rewind…): bỏ lời nhắc cũ, mốc về lại ngưỡng.
      if ((await read($, nextAt)) !== null || (await read($, nudge)) !== null) {
        await resetNudge($)
      }
      return result
    }
    const due = Math.max((await read($, nextAt)) ?? base, base)
    if (tokens < due) {
      return result
    }

    const id = e.turnId
    await update($, nextAt, () => nextMilestone(tokens, base, step))
    // Mở hoặc đóng pane trước khi ghi atom: band vẽ lại theo atom và phải thấy pane đã được đặt hay chưa.
    await showNudge($, surfaces)
    await update($, nudge, (): Nudge => ({ id, tokens, draft: 'drafting', command: null, isDismissed: false }))
    $.ui.toast(`Context ${formatTokens(tokens)} — nên compact`)

    void $.model
      .fork({ prompt: ASK })
      .then(reply => (reply.isAnswered ? toCommand(reply.text) : null))
      .catch(() => null)
      .then(async command => {
        await update($, nudge, (current): Nudge | null =>
          current?.id === id ? { ...current, command, draft: command === null ? 'failed' : 'ready' } : current,
        )
        const live = await read($, nudge)
        if (command !== null && live?.id === id && !live.isDismissed) {
          await $.prompt.suggest({ text: command })
        }
      })
      .catch(() => undefined)

    return result
  })

  on('session.compact', async ($, e, next) => {
    const result = await next(e)
    // precompute không cài gì, skip thì conversation giữ nguyên: chỉ compact thật mới reset mốc.
    if (e.agentId === undefined && e.trigger !== 'precompute' && result.skip === undefined) {
      await resetNudge($)
    }
    return result
  }).catch(($, e, next) => next(e))

  on('session.start', async ($, e, next) => {
    await announce($, e.surface !== null)
    await $.command.register({
      name: 'compact-nudge',
      description: 'Mở lại lời nhắc /compact cho context hiện tại',
    })
    return next(e)
  })

  on('session.attach', async ($, e, next) => {
    const result = await next(e)
    await announce($, true)
    return result
  })

  on('session.detach', async ($, e, next) => {
    const result = await next(e)
    await announce($, await canDraw($))
    return result
  })

  on('command.run', { command: 'compact-nudge' }, async $ => {
    const current = await read($, nudge)
    if (current === null) {
      return { text: 'Chưa có lời nhắc compact: context chưa chạm mốc.' }
    }
    await showNudge($, await $.session.surfaces())
    await update($, nudge, value => (value ? { ...value, isDismissed: false } : value))
    return { text: 'Đã mở lại lời nhắc compact.' }
  })

  // Đóng panel bằng tay (nút đóng, Esc) coi như bỏ qua lời nhắc; /compact-nudge mở lại được.
  on('ui.close', async ($, e, next) => {
    if (e.id === PANE && e.origin.kind === 'person') {
      await update($, nudge, current => (current ? { ...current, isDismissed: true } : current))
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e, next) => {
    const current = await read($, nudge)
    if (current === null || current.isDismissed) {
      return next(e)
    }
    return drawNudge($, e, current)
  })

  // Hiện band khi pane chưa được vẽ: terminal hẹp, hoặc session chỉ có desktop. Đọc lúc vẽ để theo kịp resize.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, nudge)
    if (e.props.hasSurvey || current === null || current.isDismissed) {
      return next(e)
    }
    const isPanePlaced = (await $.ui.panes()).some(pane => pane.id === PANE && pane.isPlaced)
    if (isPanePlaced) {
      return next(e)
    }
    return drawNudge($, e, current)
  })
}
