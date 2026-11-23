return {
  "folke/edgy.nvim",
  event = "VeryLazy",
  init = function()
    vim.opt.laststatus = 3
    vim.opt.splitkeep = "screen"
  end,
  opts = {
    left = {
      {
        title = "Files",
        ft = "neo-tree",
        filter = function(buf)
          return vim.b[buf].neo_tree_source == "filesystem"
        end,
        size = { height = 0.6 },
      },
      {
        title = "Symbols",
        ft = "neo-tree",
        filter = function(buf)
          return vim.b[buf].neo_tree_source == "document_symbols"
        end,
        size = { height = 0.4 },
      },
    },
  },
}
