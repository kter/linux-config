return {
  "nvim-treesitter/nvim-treesitter",
  -- Neovim 0.11.x needs the pre-rewrite line. Pin the known-good commit.
  commit = "cf12346a3414fa1b06af75c79faebe7f76df080a",
  lazy = false,
  build = ":TSUpdate",
  config = function()
    require("nvim-treesitter.configs").setup({
      ensure_installed = {
        "bash",
        "json",
        "lua",
        "markdown",
        "markdown_inline",
        "python",
        "query",
        "tsx",
        "typescript",
        "vim",
        "vimdoc",
        "yaml",
      },
      highlight = {
        enable = true,
      },
      indent = {
        enable = true,
      },
    })
  end,
}
