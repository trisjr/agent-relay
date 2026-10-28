/**
 * @file compact-nudge.test.tsx
 * @description Kiểm tra mốc nhắc, lệnh /compact gợi ý, reset sau compact, phối hợp với nudge.py và panel/band
 */
import type { EventCalls, On } from 'claude-code'
import { describe, expect, test } from 'claude-code/testing'

import { formatTokens, nextMilestone, positive, toCommand } from './register.tsx'

const SUGGESTED = '/compact giữ lại: task fix pricing EUR, file pricing.service.ts; bỏ: log test cũ'
const NO_USAGE = { input_tokens: 0, output_tokens: 0, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 }

type Fake = {
  tokens: number
  window?: number
  surfaces?: string[]
  fork?: () => Promise<{ isAnswered: boolean; text: string }>
  draft?: string
  isPanePlaced?: boolean
}

function fakeSession(on: On, fake: Fake) {
  const seen = {
    forks: 0,
    suggested: [] as string[],
    toasts: [] as string[],
    opened: [] as string[],
    closed: [] as string[],
    filled: [] as string[],
    env: [] as (string | undefined)[],
  }
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('command.register', () => ({ value: { command: 'compact-nudge' } }) as never)
  on('session.surfaces', () => ({ value: fake.surfaces ?? ['terminal'] }) as never)
  on('env.get', () => ({ value: undefined }) as never)
  on('env.set', (_$, e) => {
    seen.env.push((e as { value?: string }).value)
    return { value: {} } as never
  })
  on('ui.open', (_$, e) => {
    seen.opened.push(e.id)
    return { value: { isPlaced: true } } as never
  })
  on('ui.close', (_$, e) => {
    seen.closed.push(e.id)
    return { value: undefined } as never
  })
  on('ui.panes', () => ({ value: [{ id: 'compact-nudge', title: 'Compact', isShown: true, isFocused: false, isPlaced: fake.isPanePlaced ?? false }] }) as never)
  on('prompt.suggest', (_$, e) => {
    seen.suggested.push(e.text)
    return { isShown: true } as never
  })
  on('prompt.read', () => ({ value: { text: fake.draft ?? '', cursor: 0 } }) as never)
  on('prompt.fill', (_$, e) => {
    seen.filled.push(e.text)
    return { isFilled: true, text: e.text, cursor: e.text.length } as never
  })
  on('ui.toast', (_$, e) => {
    seen.toasts.push(String((e as { text?: string }).text ?? e))
    return { value: undefined } as never
  })
  on('session.usage', () => ({
    value: { startedAt: 0, context: { tokens: fake.tokens, window: fake.window ?? 1_000_000 }, rateLimits: [] },
  }) as never)
  on('model.fork', async () => {
    seen.forks += 1
    const reply = fake.fork ? await fake.fork() : { isAnswered: true, text: SUGGESTED }
    return { value: { ...reply, usage: NO_USAGE } } as never
  })
  return seen
}

let turn = 0

async function endTurn($: object, agentId?: string) {
  const engine = $ as { turn: Pick<EventCalls['turn'], 'complete'> }
  turn += 1
  await engine.turn.complete({ answer: 'ok', durationMs: 1, isAborted: false, turnId: `t${turn}`, reason: 'answer', agentId })
}

/** Cho các promise fork chạy ngầm (void) chạy xong. */
async function settle() {
  for (let i = 0; i < 20; i += 1) await Promise.resolve()
}

const PANE = {
  plugin: 'compact-nudge',
  component: 'Pane',
  requestId: 'compact-nudge',
  props: { title: 'Compact', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 6 }, view: {} },
} as const

const BAND = {
  plugin: 'compact-nudge',
  component: 'AbovePrompt',
  props: { hasSurvey: false, isWorking: false, maxRows: 6, bodyColumns: 60, scroll: { offset: 0, bodyRows: 6 }, view: {} },
} as const

describe('helpers', () => {
  test('toCommand lấy dòng /compact, bỏ backtick, ngoặc, tiền tố', async () => {
    expect(toCommand('Đây là lệnh:\n`/compact giữ X`')).toBe('/compact giữ X')
    expect(toCommand('giữ X')).toBe('/compact giữ X')
    expect(toCommand('Lệnh: /compact giữ X')).toBe('/compact giữ X')
    expect(toCommand('"/compact giữ X"')).toBe('/compact giữ X')
    expect(toCommand('**/compact giữ X**')).toBe('/compact giữ X')
    expect(toCommand('> /compact giữ X')).toBe('/compact giữ X')
    expect(toCommand('```\n/compact\ngiữ X\n```')).toBe('/compact giữ X')
    expect(toCommand('Lệnh: `/compact giữ X`')).toBe('/compact giữ X')
    expect(toCommand('Lệnh: **/compact giữ X**')).toBe('/compact giữ X')
    expect(toCommand('Lệnh: "/compact giữ X".')).toBe('/compact giữ X')
    expect(toCommand('```text\ngiữ X\n```')).toBe('/compact giữ X')
    expect(toCommand('   ')).toBe(null)
  })

  test('mốc chia đều theo step, option không hợp lệ dùng mặc định', async () => {
    expect(nextMilestone(262_000, 200_000, 100_000)).toBe(300_000)
    expect(nextMilestone(200_000, 200_000, 100_000)).toBe(300_000)
    expect(nextMilestone(399_999, 200_000, 100_000)).toBe(400_000)
    expect(positive(0, 5)).toBe(5)
    expect(positive(-1, 5)).toBe(5)
    expect(positive('abc', 5)).toBe(5)
    expect(positive(Infinity, 5)).toBe(5)
    expect(positive(7, 5)).toBe(7)
    expect(formatTokens(262_400)).toBe('262K')
  })
})

describe('nudge', () => {
  test('dưới ngưỡng thì không nhắc', async ($, on) => {
    const seen = fakeSession(on, { tokens: 150_000 })
    await endTurn($)
    expect(seen.forks).toBe(0)
    expect(seen.suggested).toEqual([])
  })

  test('vượt ngưỡng: nhắc một lần mỗi mốc 200K → 300K và gợi ý lệnh /compact', async ($, on) => {
    const fake: Fake = { tokens: 262_000 }
    const seen = fakeSession(on, fake)
    await endTurn($)
    await settle()
    await endTurn($)
    expect(seen.forks).toBe(1)
    expect(seen.suggested).toEqual([SUGGESTED])
    expect(seen.opened).toEqual(['compact-nudge'])

    fake.tokens = 299_000
    await endTurn($)
    expect(seen.forks).toBe(1)
    fake.tokens = 301_000
    await endTurn($)
    expect(seen.forks).toBe(2)
  })

  test('turn của subagent thì bỏ qua', async ($, on) => {
    const seen = fakeSession(on, { tokens: 500_000 })
    await endTurn($, 'a1')
    expect(seen.forks).toBe(0)
  })

  test('không có surface (-p, SDK) thì để nudge.py nhắc, không fork', async ($, on) => {
    const seen = fakeSession(on, { tokens: 500_000, surfaces: [] })
    await endTurn($)
    expect(seen.forks).toBe(0)
    expect(seen.opened).toEqual([])
  })

  test('ngưỡng lấy từ userConfig', { options: { threshold: 100_000 } }, async ($, on) => {
    const seen = fakeSession(on, { tokens: 120_000 })
    await endTurn($)
    expect(seen.forks).toBe(1)
  })

  test('step <= 0 không làm nhắc mỗi turn', { options: { step: 0 } }, async ($, on) => {
    const fake: Fake = { tokens: 262_000 }
    const seen = fakeSession(on, fake)
    await endTurn($)
    fake.tokens = 263_000
    await endTurn($)
    expect(seen.forks).toBe(1)
  })

  test('window 200K: nhắc trước auto-compact (80% window)', async ($, on) => {
    const seen = fakeSession(on, { tokens: 165_000, window: 200_000 })
    await endTurn($)
    expect(seen.forks).toBe(1)
  })

  test('compact xong thì reset mốc, lần sau vượt ngưỡng lại nhắc', async ($, on) => {
    const seen = fakeSession(on, { tokens: 262_000 })
    const messages = [{ role: 'user', text: 'tóm tắt', toolUses: [] }]
    on('session.compact', () => ({ messages }) as never)
    await endTurn($)
    await endTurn($)
    expect(seen.forks).toBe(1)

    await $.session.compact({ trigger: 'manual', messages } as never)
    expect(seen.closed).toEqual(['compact-nudge'])
    await endTurn($)
    expect(seen.forks).toBe(2)
  })

  test('precompute hoặc compact bị skip thì không reset mốc', async ($, on) => {
    const seen = fakeSession(on, { tokens: 262_000 })
    const messages = [{ role: 'user', text: 'tóm tắt', toolUses: [] }]
    let skip = false
    on('session.compact', () => (skip ? { skip: 'blocked by PreCompact' } : { messages }) as never)
    await endTurn($)
    await $.session.compact({ trigger: 'precompute', messages } as never)
    await endTurn($)
    skip = true
    await $.session.compact({ trigger: 'manual', messages } as never)
    await endTurn($)
    expect(seen.forks).toBe(1)
    expect(seen.closed).toEqual([])
  })

  test('context tụt không qua compact (rewind) thì reset mốc', async ($, on) => {
    const fake: Fake = { tokens: 262_000 }
    const seen = fakeSession(on, fake)
    await endTurn($)
    fake.tokens = 20_000
    await endTurn($)
    expect(seen.closed).toEqual(['compact-nudge'])
    fake.tokens = 210_000
    await endTurn($)
    expect(seen.forks).toBe(2)
  })

  test('bỏ qua trong lúc fork đang soạn thì không gợi ý lệnh nữa', async ($, on) => {
    let release: () => void = () => undefined
    const gate = new Promise<void>(resolve => {
      release = resolve
    })
    const seen = fakeSession(on, {
      tokens: 262_000,
      fork: async () => {
        await gate
        return { isAnswered: true, text: SUGGESTED }
      },
    })
    await endTurn($)
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    await ui.press({ key: 'dismiss' })
    await ui.unmount()
    release()
    await settle()
    expect(seen.suggested).toEqual([])
  })

  test('fork lỗi thì không gợi ý "/compact " trống', async ($, on) => {
    const seen = fakeSession(on, { tokens: 262_000, fork: async () => ({ isAnswered: false, text: '' }) })
    await endTurn($)
    await settle()
    expect(seen.suggested).toEqual([])
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect((await ui.find({ type: 'Text', text: /Không soạn được/ }))?.text).toBeDefined()
    await ui.unmount()
  })
})

describe('coordination', () => {
  test('session có surface thì báo nudge.py đứng ngoài; -p thì để nudge.py nhắc', async ($, on) => {
    const seen = fakeSession(on, { tokens: 0 })
    await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
    await $.session.start({ cwd: '/', surface: null, isInteractive: false })
    expect(seen.env).toEqual(['1', undefined])
  })
})

describe('ui', () => {
  for (const surface of ['terminal', 'desktop'] as const) {
    test(`panel trên ${surface}: hiện lệnh, Điền lệnh đưa vào ô prompt`, async ($, on) => {
      const seen = fakeSession(on, { tokens: 262_000 })
      await endTurn($)
      await settle()
      const ui = await $.ui.mount({ ...PANE, surface })
      expect((await ui.find({ type: 'Text', text: /giữ lại/ }))?.text).toBe(SUGGESTED)
      await ui.press({ key: 'fill' })
      expect(seen.filled).toEqual([SUGGESTED])
      expect(seen.closed).toEqual(['compact-nudge'])
      await ui.unmount()
    })
  }

  test('ô prompt đang có chữ thì Điền lệnh không ghi đè', async ($, on) => {
    const seen = fakeSession(on, { tokens: 262_000, draft: 'đang gõ dở' })
    await endTurn($)
    await settle()
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    await ui.press({ key: 'fill' })
    expect(seen.filled).toEqual([])
    expect(seen.toasts.some(t => /đang có nội dung/.test(t))).toBe(true)
    await ui.unmount()
  })

  test('band chỉ hiện khi pane chưa được vẽ', async ($, on) => {
    const fake: Fake = { tokens: 262_000, isPanePlaced: false }
    fakeSession(on, fake)
    // Hook này đứng thay engine: plugin trả next(e) thì engine vẽ band của nó.
    on('ui.render', ($, e) => {
      const { Text } = $.ui.resolve(e)
      return <Text>engine</Text>
    })
    await endTurn($)
    await settle()
    let ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
    expect(await ui.find({ type: 'Text', text: /262K/ })).toBeDefined()
    await ui.unmount()

    fake.isPanePlaced = true
    ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
    expect(await ui.find({ type: 'Text', text: /262K/ })).toBeUndefined()
    expect((await ui.find({ type: 'Text', text: /engine/ }))?.text).toBe('engine')
    await ui.unmount()
  })

  test('/compact-nudge mở lại lời nhắc đã bỏ qua', async ($, on) => {
    const seen = fakeSession(on, { tokens: 262_000 })
    await endTurn($)
    await settle()
    let ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    await ui.press({ key: 'dismiss' })
    await ui.unmount()

    const answer = await $.command.run({ command: 'compact-nudge', args: '' } as never)
    expect((answer as { text: string }).text).toBe('Đã mở panel compact.')
    expect(seen.opened).toEqual(['compact-nudge', 'compact-nudge'])
    ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect((await ui.find({ type: 'Text', text: /giữ lại/ }))?.text).toBe(SUGGESTED)
    await ui.unmount()
  })
})
