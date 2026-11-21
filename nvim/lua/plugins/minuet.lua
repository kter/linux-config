-- Local inline completion via Ollama (replaces Copilot; see copilot.lua).
return {
  "milanglacier/minuet-ai.nvim",
  event = "InsertEnter",
  dependencies = { "nvim-lua/plenary.nvim" },
  opts = {
    provider = "openai_fim_compatible",
    n_completions = 1,
    context_window = 1024,
    -- Default 3s cuts off local 7B responses (esp. cold model load); empty result = no ghost text.
    request_timeout = 10,
    provider_options = {
      openai_fim_compatible = {
        api_key = "TERM", -- Ollama needs no key; minuet just requires a non-empty env var name.
        name = "Ollama",
        end_point = "http://localhost:11434/v1/completions",
        -- 7b was ~2s/request on M4 Pro; 1.5b trades accuracy for speed.
        model = "qwen2.5-coder:1.5b",
        optional = { max_tokens = 32, top_p = 0.9 },
      },
    },
    virtualtext = {
      auto_trigger_ft = { "*" },
      keymap = {
        -- <Tab> is mapped below so it can fall back to indentation.
        accept_line = "<M-j>",
        next = "<M-]>",
        prev = "<M-[>",
        dismiss = "<C-]>",
      },
    },
  },
  config = function(_, opts)
    require("minuet").setup(opts)
    local vt = require("minuet.virtualtext").action
    vim.keymap.set("i", "<Tab>", function()
      if vt.is_visible() then
        vt.accept()
      else
        vim.api.nvim_feedkeys(vim.keycode("<Tab>"), "n", false)
      end
    end, { desc = "Accept minuet suggestion or indent" })
  end,
}
