return {
  "zbirenbaum/copilot.lua",
  cmd = "Copilot",
  event = "InsertEnter",
  opts = {
    panel = { enabled = false },
    suggestion = {
      auto_trigger = true,
      hide_during_completion = true,
      -- Let Tab fall back to indentation when no suggestion is visible.
      trigger_on_accept = false,
      keymap = {
        accept = "<Tab>",
        accept_word = "<M-w>",
        accept_line = "<M-j>",
        next = "<M-]>",
        prev = "<M-[>",
        dismiss = "<C-]>",
      },
    },
  },
  config = function(_, opts)
    require("copilot").setup(opts)

    -- Hide ghost text while blink's completion menu is open.
    local group = vim.api.nvim_create_augroup("user-copilot-completion", { clear = true })
    vim.api.nvim_create_autocmd("User", {
      group = group,
      pattern = "BlinkCmpMenuOpen",
      callback = function()
        vim.b.copilot_suggestion_hidden = true
        require("copilot.suggestion").dismiss()
      end,
    })
    vim.api.nvim_create_autocmd("User", {
      group = group,
      pattern = "BlinkCmpMenuClose",
      callback = function()
        vim.b.copilot_suggestion_hidden = false
      end,
    })
  end,
}
