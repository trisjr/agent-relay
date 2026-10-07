export type Nudge = {
  tokens: number
  command: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'compact-nudge': { nudge: Nudge | null; nextAt: number | null }
  }
}
