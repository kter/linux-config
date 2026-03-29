return {
  "neovim/nvim-lspconfig",
  config = function()
    vim.diagnostic.config({
      severity_sort = true,
      virtual_text = false,
      underline = true,
      update_in_insert = false,
      float = {
        border = "rounded",
      },
    })

    local group = vim.api.nvim_create_augroup("user-lsp-attach", { clear = true })
    vim.api.nvim_create_autocmd("LspAttach", {
      group = group,
      callback = function(event)
        local map = function(lhs, rhs, desc)
          vim.keymap.set("n", lhs, rhs, {
            buffer = event.buf,
            silent = true,
            desc = desc,
          })
        end

        map("gd", vim.lsp.buf.definition, "LSP Definition")
        map("gr", vim.lsp.buf.references, "LSP References")
        map("gI", vim.lsp.buf.implementation, "LSP Implementation")
        map("K", vim.lsp.buf.hover, "LSP Hover")
        map("<leader>rn", vim.lsp.buf.rename, "LSP Rename")
        map("<leader>ca", vim.lsp.buf.code_action, "LSP Code Action")
        map("<leader>e", vim.diagnostic.open_float, "Line Diagnostics")
        map("[d", vim.diagnostic.goto_prev, "Prev Diagnostic")
        map("]d", vim.diagnostic.goto_next, "Next Diagnostic")
      end,
    })

    local servers = {
      lua_ls = "lua-language-server",
      pyright = "pyright-langserver",
      ruff = "ruff",
      ts_ls = "typescript-language-server",
      gopls = "gopls",
    }

    for server, executable in pairs(servers) do
      if vim.fn.executable(executable) == 1 then
        vim.lsp.enable(server)
      end
    end
  end,
}
