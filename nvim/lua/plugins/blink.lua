return {
  "saghen/blink.cmp",
  version = "1.*",
  dependencies = { "rafamadriz/friendly-snippets" },
  opts = {
    -- Keep Tab/Shift-Tab for indentation; accept completions with Ctrl-y.
    keymap = { preset = "default" },
    completion = {
      documentation = { auto_show = true, auto_show_delay_ms = 300 },
    },
    sources = { default = { "lsp", "path", "snippets", "buffer" } },
    fuzzy = { implementation = "prefer_rust" },
    signature = { enabled = true },
  },
}
