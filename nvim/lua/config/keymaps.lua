local map = vim.keymap.set

map("t", "<Esc>", "<C-\\><C-n>", { desc = "Exit terminal mode" })

map("n", "<C-h>", "<C-w>h", { desc = "Move focus left" })
map("n", "<C-j>", "<C-w>j", { desc = "Move focus down" })
map("n", "<C-k>", "<C-w>k", { desc = "Move focus up" })
map("n", "<C-l>", "<C-w>l", { desc = "Move focus right" })

map("n", "<leader>wh", "<C-w>s", { desc = "Split below" })
map("n", "<leader>wv", "<C-w>v", { desc = "Split right" })
map("n", "<leader>wo", "<C-w>o", { desc = "Only window" })

map("n", "<leader>tt", "<cmd>tselect <C-R><C-W><cr>", { desc = "Select tag under cursor" })

map("n", "<leader>e", "<cmd>Neotree toggle<cr>", { desc = "Toggle file tree" })

-- Indent / outdent in visual mode, keeping the selection
map("v", "<Tab>", ">gv", { desc = "Indent selection" })
map("v", "<S-Tab>", "<gv", { desc = "Outdent selection" })

-- Insert mode: Tab/Shift+Tab indent or outdent the whole line,
-- regardless of cursor position within the line.
map("i", "<Tab>", "<C-t>", { desc = "Indent line" })
map("i", "<S-Tab>", "<C-d>", { desc = "Outdent line" })
