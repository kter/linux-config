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

-- Continue markdown bullet lists onto the next line when pressing <Enter>/o
vim.api.nvim_create_autocmd("FileType", {
  pattern = "markdown",
  callback = function()
    vim.opt_local.comments = "b:- [ ],b:- [x],b:-,b:*,b:+,b:>"
    vim.opt_local.formatoptions:append("r") -- continue list in insert mode (<Enter>)
    vim.opt_local.formatoptions:append("o") -- continue list with o/O in normal mode
    -- The runtime markdown ftplugin forces these to 4; restore our 2-space indent.
    vim.opt_local.tabstop = 2
    vim.opt_local.shiftwidth = 2
    vim.opt_local.softtabstop = 2
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

vim.api.nvim_create_autocmd("TextYankPost", {
  group = vim.api.nvim_create_augroup("user-claudecode-yank-strip", { clear = true }),
  callback = function()
    if vim.v.event.operator ~= "y" then return end
    if vim.bo.buftype ~= "terminal" then return end
    local bufname = vim.api.nvim_buf_get_name(0):lower()
    if not bufname:find("claude") then return end

    local lines = vim.v.event.regcontents
    local changed = false
    for i, line in ipairs(lines) do
      local stripped = line:gsub("^\226\150\142 ?", "")
      if stripped ~= line then
        lines[i] = stripped
        changed = true
      end
    end
    if not changed then return end

    local regtype = vim.v.event.regtype
    local regname = vim.v.event.regname
    vim.fn.setreg("+", lines, regtype)
    vim.fn.setreg('"', lines, regtype)
    if regname ~= "" and regname ~= "+" and regname ~= '"' then
      vim.fn.setreg(regname, lines, regtype)
    end
  end,
})
