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
        "rust",
        "tsx",
        "typescript",
        "vim",
        "vimdoc",
        "yaml",
      },
      highlight = {
        enable = true,
      },
      -- The pinned pre-rewrite indent module crashes on Nvim 0.12
      -- (query_predicates.lua: "attempt to call method 'type'"), so indentexpr
      -- silently returns 0 and `o` lands on column 1. Fall back to the
      -- runtime indenters (e.g. GetTypescriptIndent) instead.
      indent = {
        enable = false,
      },
    })
  end,
}
