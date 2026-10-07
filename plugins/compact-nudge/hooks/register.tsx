/**
 * @file register.tsx
 * @description Nhắc user compact khi context vượt ngưỡng, kèm lệnh /compact do chính session soạn sẵn
 */
import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Nudge } from '../types'

export const nudge = atom({ plugin: 'compact-nudge', key: 'nudge' } as const, null)
export const nextAt = atom({ plugin: 'compact-nudge', key: 'nextAt' } as const, null)

const FALLBACK = '/compact '

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
      await update($, nudge, () => null)
      await update($, nextAt, () => null)
    }
    return result
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, nudge)
    if (e.props.hasSurvey || current === null) {
      return next(e)
    }

    const { Box, Button, Text } = $.ui.resolve(e)
    const dismiss = () => update($, nudge, () => null)
    const fill = async () => {
      await $.prompt.fill({ text: current.command ?? FALLBACK })
      await dismiss()
    }

    return (
      <Box flexDirection="column">
        <Text color="yellow">
          Context {formatTokens(current.tokens)} — nên compact để giảm chi phí mỗi lượt.
        </Text>
        <Text dimColor>{current.command ?? 'Đang soạn lệnh /compact gợi ý…'}</Text>
        <Box>
          <Button key="fill" label="Điền lệnh" hotkey="c" onPress={fill} />
          <Text> </Text>
          <Button key="dismiss" label="Bỏ qua" hotkey="x" onPress={dismiss} />
        </Box>
      </Box>
    )
  })
}
