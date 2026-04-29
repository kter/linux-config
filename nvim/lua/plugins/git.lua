return {
  -- Rich git diff viewer
  {
    "sindrets/diffview.nvim",
    cmd = { "DiffviewOpen", "DiffviewFileHistory" },
    keys = {
      { "<leader>gd", "<cmd>DiffviewOpen<cr>", desc = "Diffview Open" },
      { "<leader>gq", "<cmd>DiffviewClose<cr>", desc = "Diffview Close" },
      { "<leader>gh", "<cmd>DiffviewFileHistory %<cr>", desc = "Diffview File History" },
      { "<leader>gH", "<cmd>DiffviewFileHistory<cr>", desc = "Diffview Branch History" },
    },
    opts = {
      enhanced_diff_hl = true,
      view = {
        merge_tool = {
          layout = "diff3_mixed",
        },
      },
    },
  },

  -- Git signs in signcolumn and hunk operations
  {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    keys = {
      { "<leader>gs", function() require("gitsigns").stage_hunk() end,                                                     desc = "Stage hunk" },
      { "<leader>gs", function() require("gitsigns").stage_hunk({ vim.fn.line("."), vim.fn.line("v") }) end,               desc = "Stage hunk",        mode = "v" },
      { "<leader>gr", function() require("gitsigns").reset_hunk() end,                                                     desc = "Reset hunk" },
      { "<leader>gr", function() require("gitsigns").reset_hunk({ vim.fn.line("."), vim.fn.line("v") }) end,               desc = "Reset hunk",        mode = "v" },
      { "<leader>gS", function() require("gitsigns").stage_buffer() end,                                                   desc = "Stage buffer" },
      { "<leader>gu", function() require("gitsigns").undo_stage_hunk() end,                                                desc = "Undo stage hunk" },
      { "<leader>gR", function() require("gitsigns").reset_buffer() end,                                                   desc = "Reset buffer" },
      { "<leader>gp", function() require("gitsigns").preview_hunk() end,                                                   desc = "Preview hunk" },
      { "<leader>gb", function() require("gitsigns").blame_line({ full = true }) end,                                      desc = "Blame line" },
      { "<leader>tb", function() require("gitsigns").toggle_current_line_blame() end,                                      desc = "Toggle line blame" },
      { "<leader>hd", function() require("gitsigns").diffthis() end,                                                       desc = "Diff this" },
      { "<leader>hD", function() require("gitsigns").diffthis("~") end,                                                    desc = "Diff this ~" },
      { "<leader>td", function() require("gitsigns").toggle_deleted() end,                                                 desc = "Toggle deleted" },
    },
    opts = {
      on_attach = function(bufnr)
        local gs = package.loaded.gitsigns

        local function map(mode, l, r, opts)
          opts = opts or {}
          opts.buffer = bufnr
          vim.keymap.set(mode, l, r, opts)
        end

        -- Navigation (buffer-local expr maps required for diff mode fallback)
        map("n", "]c", function()
          if vim.wo.diff then return "]c" end
          vim.schedule(function() gs.next_hunk() end)
          return "<Ignore>"
        end, { expr = true, desc = "Next hunk" })

        map("n", "[c", function()
          if vim.wo.diff then return "[c" end
          vim.schedule(function() gs.prev_hunk() end)
          return "<Ignore>"
        end, { expr = true, desc = "Prev hunk" })

        -- Text object
        map({ "o", "x" }, "ih", ":<C-U>Gitsigns select_hunk<CR>", { desc = "Select hunk" })
      end,
    },
  },
}
