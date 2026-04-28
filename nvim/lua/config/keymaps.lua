local map = vim.keymap.set

map("n", "<C-h>", "<C-w>h", { desc = "Move focus left" })
map("n", "<C-j>", "<C-w>j", { desc = "Move focus down" })
map("n", "<C-k>", "<C-w>k", { desc = "Move focus up" })
map("n", "<C-l>", "<C-w>l", { desc = "Move focus right" })

map("n", "<leader>wh", "<C-w>s", { desc = "Split below" })
map("n", "<leader>wv", "<C-w>v", { desc = "Split right" })
map("n", "<leader>wo", "<C-w>o", { desc = "Only window" })

map("n", "<leader>tt", "<cmd>tselect <C-R><C-W><cr>", { desc = "Select tag under cursor" })

map("n", "<leader>e", "<cmd>Neotree toggle<cr>", { desc = "Toggle file tree" })
