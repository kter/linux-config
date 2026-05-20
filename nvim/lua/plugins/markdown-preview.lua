return {
  "iamcco/markdown-preview.nvim",
  cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
  ft = { "markdown" },
  build = function(plugin)
    vim.fn.system({ "npm", "install", "--prefix", plugin.dir .. "/app" })
  end,
  init = function()
    vim.g.mkdp_auto_close = 0
    vim.api.nvim_create_autocmd("FileType", {
      pattern = "markdown",
      callback = function()
        vim.keymap.set("n", "<leader>mp", "<cmd>MarkdownPreviewToggle<cr>", { buffer = true, desc = "Markdown Preview Toggle" })
      end,
    })
  end,
}
