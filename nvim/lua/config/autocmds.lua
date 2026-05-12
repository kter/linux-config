vim.api.nvim_create_autocmd("ColorScheme", {
  pattern = "*",
  callback = function()
    vim.api.nvim_set_hl(0, "CursorLine", { bg = "#2d3a5a" })
  end,
})
vim.api.nvim_set_hl(0, "CursorLine", { bg = "#2d3a5a" })

local project_root_markers = {
  "pyrightconfig.json",
  "pyproject.toml",
  "package.json",
  "go.mod",
  "Cargo.toml",
  ".git",
}

local group = vim.api.nvim_create_augroup("user-project-root", { clear = true })

vim.api.nvim_create_autocmd("FileType", {
  pattern = "json",
  callback = function()
    vim.opt_local.equalprg = "npx prettier --parser json --tab-width 2"
  end,
})

vim.api.nvim_create_autocmd("BufEnter", {
  group = group,
  callback = function(event)
    local bufname = vim.api.nvim_buf_get_name(event.buf)
    if bufname == "" or vim.bo[event.buf].buftype ~= "" then
      return
    end

    local root = vim.fs.root(bufname, project_root_markers)
    if not root or root == "" then
      return
    end

    vim.cmd("lcd " .. vim.fn.fnameescape(root))
  end,
})
