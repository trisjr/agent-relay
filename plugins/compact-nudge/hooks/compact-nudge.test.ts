/**
 * @file compact-nudge.test.ts
 * @description Kiểm tra ngưỡng nhắc, lệnh /compact gợi ý và reset mốc sau khi compact
 */
import type { EventCalls, On } from 'claude-code'
import { describe, expect, test } from 'claude-code/testing'

import { formatTokens, toCommand } from './register.tsx'

const SUGGESTED = '/compact giữ lại: task fix pricing EUR, file pricing.service.ts; bỏ: log test cũ'
const NO_USAGE = { input_tokens: 0, output_tokens: 0, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 }

function fakeSession(on: On, tokens: { value: number }) {
  const seen = { forks: 0, suggested: [] as string[], toasts: [] as string[] }
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('prompt.suggest', (_$, e) => {
    seen.suggested.push(e.text)
    return { isShown: true } as never
  })
  on('ui.toast', (_$, e) => {
    seen.toasts.push(String((e as { text?: string }).text ?? e))
    return { value: undefined } as never
  })
  on('session.usage', () => ({
    value: { startedAt: 0, context: { tokens: tokens.value, window: 1_000_000 }, rateLimits: [] },
  }) as never)
  on('model.fork', () => {
    seen.forks += 1
    return { value: { isAnswered: true, text: SUGGESTED, usage: NO_USAGE } } as never
  })
  return seen
}

async function endTurn($: object, agentId?: string) {
  const engine = $ as { turn: Pick<EventCalls['turn'], 'complete'> }
  await engine.turn.complete({ answer: 'ok', durationMs: 1, isAborted: false, turnId: 't', reason: 'answer', agentId })
}

describe('helpers', () => {
  test('toCommand lấy dòng /compact, bỏ backtick', async () => {
    expect(toCommand('Đây là lệnh:\n`/compact giữ X`')).toBe('/compact giữ X')
    expect(toCommand('giữ X')).toBe('/compact giữ X')
    expect(formatTokens(262_400)).toBe('262K')
  })
})

describe('nudge', () => {
  test('dưới ngưỡng thì không nhắc', async ($, on) => {
    const seen = fakeSession(on, { value: 150_000 })
    await endTurn($)
    expect(seen.forks).toBe(0)
    expect(seen.suggested).toEqual([])
  })

  test('vượt ngưỡng: nhắc một lần mỗi mốc và gợi ý lệnh /compact', async ($, on) => {
    const tokens = { value: 262_000 }
    const seen = fakeSession(on, tokens)
    await endTurn($)
    await endTurn($)
    expect(seen.forks).toBe(1)
    expect(seen.suggested).toEqual([SUGGESTED])

    tokens.value = 370_000
    await endTurn($)
    expect(seen.forks).toBe(2)
  })

  test('turn của subagent thì bỏ qua', async ($, on) => {
    const seen = fakeSession(on, { value: 500_000 })
    await endTurn($, 'a1')
    expect(seen.forks).toBe(0)
  })

  test('ngưỡng lấy từ userConfig', { options: { threshold: 100_000 } }, async ($, on) => {
    const seen = fakeSession(on, { value: 120_000 })
    await endTurn($)
    expect(seen.forks).toBe(1)
  })

  test('compact xong thì reset mốc, lần sau vượt ngưỡng lại nhắc', async ($, on) => {
    const seen = fakeSession(on, { value: 262_000 })
    const messages = [{ role: 'user', text: 'tóm tắt', toolUses: [] }]
    on('session.compact', () => ({ messages }) as never)
    await endTurn($)
    await endTurn($)
    expect(seen.forks).toBe(1)

    await $.session.compact({ trigger: 'manual', messages } as never)
    await endTurn($)
    expect(seen.forks).toBe(2)
  })
})
