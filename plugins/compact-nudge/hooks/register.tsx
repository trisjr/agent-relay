/**
 * @file register.tsx
 * @description Nhắc user compact khi context vượt ngưỡng, kèm lệnh /compact do chính session soạn sẵn
 */
import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Nudge } from '../types'

export const nudge = atom({ plugin: 'compact-nudge', key: 'nudge' } as const, null)
export const nextAt = atom({ plugin: 'compact-nudge', key: 'nextAt' } as const, null)

export const isPaneUp = atom({ plugin: 'compact-nudge', key: 'isPaneUp' } as const, false)

const PANE = 'compact-nudge'
const FALLBACK = '/compact '

async function openPane($: EngineInterface): Promise<void> {
  const opened = await $.ui.open({ id: PANE, title: 'Compact', closeOnEscape: true, rows: 6 })
  await update($, isPaneUp, () => opened.isPlaced)
}

async function dismissNudge($: EngineInterface): Promise<void> {
  await update($, nudge, () => null)
  await update($, isPaneUp, () => false)
  await $.ui.close({ id: PANE })
}

async function fillCommand($: EngineInterface, current: Nudge): Promise<void> {
  await $.prompt.fill({ text: current.command ?? FALLBACK })
  await dismissNudge($)
}

const ASK = [
  'Context của session này sắp quá lớn và người dùng sẽ chạy /compact.',
  'Viết DUY NHẤT một dòng, bắt đầu bằng "/compact ", tối đa 60 từ, tiếng Việt,',
  'nói rõ cần GIỮ LẠI: task đang làm, file/hàm chính, quyết định đã chốt, lỗi hoặc việc còn dở;',
  'và có thể BỎ: output/log dài đã xử lý xong, các hướng đã loại.',
  'Không giải thích, không markdown, không làm gì khác.',
].join(' ')

export function toCommand(text: string): string {
  const line = text
    .split('\n')
    .map(l => l.trim().replace(/^`+|`+$/g, ''))
    .find(l => l.startsWith('/compact'))
  return line ?? `${FALLBACK}${text.trim().split('\n')[0] ?? ''}`.trimEnd()
}

export function formatTokens(tokens: number): string {
  return `${Math.round(tokens / 1000)}K`
}

export const register: Register = (on, options) => {
  const threshold = Number(options.threshold ?? 200000)
  const step = Number(options.step ?? 100000)

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.isAborted || e.agentId !== undefined) {
      return result
    }

    const { context } = await $.session.usage()
    const tokens = context.tokens ?? 0
    const due = (await read($, nextAt)) ?? threshold
    if (tokens < due) {
      return result
    }

    await update($, nextAt, () => tokens + step)
    await update($, nudge, (): Nudge => ({ tokens, command: null }))
    $.ui.toast(`Context ${formatTokens(tokens)} — nên compact`)
    await openPane($)

    void $.model
      .fork({ prompt: ASK })
      .then(reply => (reply.isAnswered ? toCommand(reply.text) : FALLBACK))
      .catch(() => FALLBACK)
      .then(async command => {
        await update($, nudge, current => (current ? { ...current, command } : current))
        await $.prompt.suggest({ text: command })
      })
      .catch(() => undefined)

    return result
  })

  on('session.compact', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId === undefined) {
      await dismissNudge($)
      await update($, nextAt, () => null)
    }
    return result
  }).catch(($, e, next) => next(e))

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'compact-nudge',
      description: 'Mở panel gợi ý /compact cho context hiện tại',
    })
    return next(e)
  })

  on('command.run', { command: 'compact-nudge' }, async $ => {
    const current = await read($, nudge)
    if (current === null) {
      return { text: 'Chưa có gợi ý compact: context chưa vượt ngưỡng.' }
    }
    await openPane($)
    return { text: 'Đã mở panel compact.' }
  })

  // Đóng panel bằng tay (nút đóng, Esc) coi như bỏ qua lời nhắc.
  on('ui.close', async ($, e, next) => {
    if (e.id === PANE && e.origin.kind === 'person') {
      await update($, nudge, () => null)
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e, next) => {
    const current = await read($, nudge)
    if (current === null) {
      return next(e)
    }

    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box flexDirection="column">
        <Text color="yellow">Context {formatTokens(current.tokens)} — nên compact để giảm chi phí mỗi lượt.</Text>
        <Text dimColor>{current.command ?? 'Đang soạn lệnh /compact gợi ý…'}</Text>
        <Box>
          <Button key="fill" label="Điền lệnh" hotkey="c" onPress={() => fillCommand($, current)} />
          <Text> </Text>
          <Button key="dismiss" label="Bỏ qua" hotkey="x" onPress={() => dismissNudge($)} />
        </Box>
      </Box>
    )
  })

  // Fallback: terminal hẹp không vẽ pane thì hiện band phía trên prompt như cũ.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, nudge)
    if (e.props.hasSurvey || current === null || (await read($, isPaneUp))) {
      return next(e)
    }

    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box flexDirection="column">
        <Text color="yellow">
          Context {formatTokens(current.tokens)} — nên compact để giảm chi phí mỗi lượt.
        </Text>
        <Text dimColor>{current.command ?? 'Đang soạn lệnh /compact gợi ý…'}</Text>
        <Box>
          <Button key="fill" label="Điền lệnh" hotkey="c" onPress={() => fillCommand($, current)} />
          <Text> </Text>
          <Button key="dismiss" label="Bỏ qua" hotkey="x" onPress={() => dismissNudge($)} />
        </Box>
      </Box>
    )
  })
}
