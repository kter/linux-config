return {
  "nvim-treesitter/nvim-treesitter",
  -- The `main` branch is the rewrite that supports Nvim 0.12. The old `master`
  -- line's query directives assume one node per capture, so on 0.12 they crash
  -- while parsing markdown injections and LSP hover (K) shows raw Markdown.
  branch = "main",
  lazy = false,
  build = ":TSUpdate",
  config = function()
    require("nvim-treesitter").install({
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
    })

    -- `main` no longer enables highlighting itself. Start it for every buffer
    -- whose filetype has an installed parser; pcall skips the rest.
    vim.api.nvim_create_autocmd("FileType", {
      group = vim.api.nvim_create_augroup("user-treesitter", { clear = true }),
      callback = function(args)
        pcall(vim.treesitter.start, args.buf)
      end,
    })
    -- Indentation stays on the runtime indenters (e.g. GetTypescriptIndent).
    -- nvim-treesitter's indentexpr is still experimental on `main`.
  end,
}
