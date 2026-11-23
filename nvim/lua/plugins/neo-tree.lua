return {
  "nvim-neo-tree/neo-tree.nvim",
  branch = "v3.x",
  cmd = "Neotree",
  dependencies = {
    "nvim-lua/plenary.nvim",
    "nvim-tree/nvim-web-devicons",
    "MunifTanjim/nui.nvim",
  },
  keys = {
    { "<leader>E", vim.diagnostic.open_float, desc = "Line Diagnostics" },
    -- Open at position=right so it doesn't replace the file tree; edgy moves it to the left.
    { "<leader>cs", "<cmd>Neotree document_symbols position=right toggle<cr>", desc = "Symbols outline" },
  },
  opts = {
    sources = { "filesystem", "buffers", "git_status", "document_symbols" },
    document_symbols = { follow_cursor = true },
    filesystem = {
      filtered_items = {
        visible = true,
        hide_dotfiles = false,
        hide_gitignored = false,
      },
    },
  },
}
