export type Nudge = {
  /** turnId của turn đã nhắc: fork trả về muộn chỉ được ghi vào đúng lời nhắc của nó */
  id: string
  tokens: number
  draft: 'drafting' | 'ready' | 'failed'
  command: string | null
  isDismissed: boolean
}

declare module 'claude-code' {
  interface PluginState {
    'compact-nudge': { nudge: Shaped<Nudge | null>; nextAt: number | null }
  }
}
