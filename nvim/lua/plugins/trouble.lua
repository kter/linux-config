return {
  "folke/trouble.nvim",
  cmd = "Trouble",
  opts = {},
  keys = {
    {
      "<leader>xx",
      "<cmd>Trouble diagnostics toggle<cr>",
      desc = "Diagnostics list",
    },
    {
      "<leader>xr",
      "<cmd>Trouble lsp_references toggle<cr>",
      desc = "References list",
    },
    {
      "<leader>xq",
      "<cmd>Trouble qflist toggle<cr>",
      desc = "Quickfix list",
    },
  },
}
