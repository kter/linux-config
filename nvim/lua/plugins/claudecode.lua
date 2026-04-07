return {
  "coder/claudecode.nvim",
  cmd = {
    "ClaudeCode",
    "ClaudeCodeFocus",
    "ClaudeCodeSend",
    "ClaudeCodeAdd",
    "ClaudeCodeDiffAccept",
    "ClaudeCodeDiffDeny",
  },
  opts = {
    terminal_cmd = "native",
  },
  keys = {
    { "<leader>ac", "<cmd>ClaudeCode<cr>",      desc = "Toggle Claude Code" },
    { "<leader>af", "<cmd>ClaudeCodeFocus<cr>", desc = "Focus Claude Code" },
    { "<leader>as", "<cmd>ClaudeCodeSend<cr>",  mode = "v", desc = "Send to Claude" },
    { "<leader>aa", "<cmd>ClaudeCodeAdd<cr>",   desc = "Add file to Claude" },
  },
}
