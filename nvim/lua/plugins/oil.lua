return {
  "stevearc/oil.nvim",
  opts = {
    default_file_explorer = false,
    view_options = {
      show_hidden = true,
    },
  },
  keys = {
    {
      "-",
      "<cmd>Oil<cr>",
      desc = "Open parent directory",
    },
  },
}
