# Neovim 設定ガイドと利用の手引

このドキュメントは、`Sway` 上でキーボード中心にコードリーディングを行うための、最小構成の `Neovim` セットアップと日常の使い方をまとめたものです。

方針は次の 3 点です。

- 主役は `LSP`
- 検索は `Telescope + ripgrep`
- `ctags` は保険として併用

`ctags` 単体でも読めますが、定義ジャンプ中心になりやすく、参照検索や実装追跡では `LSP` に劣ります。したがって、コードリーディング用途では `LSP` を主軸に据えるのが実用的です。

## 想定環境

- Linux
- Wayland
- `Sway`
- `Neovim 0.11+`
- `git`
- `ripgrep`
- `fd` または `fdfind`
- `Universal Ctags`
- `wl-clipboard`

`wl-clipboard` を入れておくと、Wayland 上でも `clipboard=unnamedplus` が扱いやすくなります。

## まず入れるもの

ディストリビューションのパッケージマネージャーなどで、少なくとも次を入れてください。

```bash
neovim
git
ripgrep
fd
universal-ctags
wl-clipboard
```

Fedora 系なら、まずはこれで足ります。

```bash
sudo dnf install -y neovim git ripgrep fd-find ctags wl-clipboard gcc make unzip
```

この設定で使う補助ツールも合わせて入れるなら、次を追加します。

```bash
sudo dnf install -y ruff gopls nodejs nodejs-npm
npm install -g pyright typescript-language-server typescript
```

補足:

- `ctags` パッケージ名は Fedora では `ctags`
- `fd` パッケージ名は Fedora では `fd-find`
- `lua-language-server` は標準 `dnf` リポジトリでは見当たりませんでした

## 他のマシンで再現する手順

2026-03-29 時点で、Fedora 系 + `Neovim 0.11.6` で確認した手順です。

### 1. パッケージを入れる

```bash
sudo dnf install -y neovim git ripgrep fd-find ctags wl-clipboard gcc make unzip
sudo dnf install -y ruff gopls nodejs nodejs-npm
npm install -g pyright typescript-language-server typescript
```

### 2. 設定ファイルを配置する

次の構成で `~/.config/nvim` を作成します。

```text
~/.config/nvim/
├── init.lua
└── lua/
    ├── config/
    │   ├── keymaps.lua
    │   ├── lazy.lua
    │   └── options.lua
    └── plugins/
        ├── lsp.lua
        ├── oil.lua
        ├── telescope.lua
        ├── treesitter.lua
        └── trouble.lua
```

このガイドの設定例をそのまま使って構いません。

### 3. 初回同期を走らせる

初回は GUI で開く前に、先に headless で同期しておくと安定します。

```bash
nvim --headless "+Lazy! sync" "+qa"
```

### 4. Treesitter パーサを入れる

```bash
nvim --headless "+TSUpdateSync bash json lua markdown markdown_inline python query tsx typescript vim vimdoc yaml" "+qa"
```

### 5. 起動確認をする

```bash
nvim
```

Neovim 起動後:

```vim
:checkhealth
:Telescope find_files
```

## Neovim 0.11.x での Treesitter 互換条件

`Neovim 0.11.x` では、`nvim-treesitter` の `main` ブランチを使わないでください。

- 現在の `main` は互換性のない rewrite 系
- `0.11.x` では旧系の API が必要
- そのため、`treesitter.lua` では互換コミットに固定します

このガイドで使っている固定値は次です。

```lua
commit = "cf12346a3414fa1b06af75c79faebe7f76df080a"
```

将来ほかのマシンで同じ構成を再現したいなら、`branch = "master"` ではなく、上のようにコミット固定にしておくほうが安全です。

## よくあるエラーと復旧

### `module 'nvim-treesitter.configs' not found`

このエラーは、`nvim-treesitter` の新しい rewrite 系が入っているときに起きます。

復旧手順:

```bash
rm -rf ~/.local/share/nvim/lazy/nvim-treesitter
nvim --headless "+Lazy! sync" "+qa"
nvim --headless "+TSUpdateSync bash json lua markdown markdown_inline python query tsx typescript vim vimdoc yaml" "+qa"
```

その後、Neovim を再起動してください。

## ディレクトリ構成

最小構成なら、まずは `~/.config/nvim/init.lua` の 1 ファイルで十分です。

```text
~/.config/nvim/
└── init.lua
```

慣れてから、`lua/plugins/*.lua` や `lua/config/*.lua` に分割してください。

## 最小 init.lua

以下はコードリーディング用の最小構成です。

- `lazy.nvim` でプラグイン管理
- `nvim-lspconfig` で LSP 利用
- `telescope.nvim` で検索
- `nvim-treesitter` で構文理解を補強
- `trouble.nvim` で診断と参照の一覧表示
- `oil.nvim` でファイル移動
- `ctags` を fallback として併用

```lua
vim.g.mapleader = " "

vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.signcolumn = "yes"
vim.opt.cursorline = true
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.splitright = true
vim.opt.splitbelow = true
vim.opt.updatetime = 250
vim.opt.mouse = ""
vim.opt.clipboard = "unnamedplus"
vim.opt.tags = "./tags;,tags;"

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.uv.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  {
    "neovim/nvim-lspconfig",
    config = function()
      local map = vim.keymap.set

      map("n", "gd", vim.lsp.buf.definition, { desc = "Definition" })
      map("n", "gr", vim.lsp.buf.references, { desc = "References" })
      map("n", "gI", vim.lsp.buf.implementation, { desc = "Implementation" })
      map("n", "K", vim.lsp.buf.hover, { desc = "Hover" })
      map("n", "<leader>rn", vim.lsp.buf.rename, { desc = "Rename" })
      map("n", "<leader>ca", vim.lsp.buf.code_action, { desc = "Code action" })
      map("n", "<leader>e", vim.diagnostic.open_float, { desc = "Line diagnostics" })
      map("n", "[d", vim.diagnostic.goto_prev, { desc = "Prev diagnostic" })
      map("n", "]d", vim.diagnostic.goto_next, { desc = "Next diagnostic" })

      -- 使う言語だけ有効化する
      vim.lsp.enable("lua_ls")
      vim.lsp.enable("pyright")
      vim.lsp.enable("ruff")
      vim.lsp.enable("ts_ls")
      vim.lsp.enable("gopls")
    end,
  },
  {
    "nvim-telescope/telescope.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      local builtin = require("telescope.builtin")
      local map = vim.keymap.set

      map("n", "<leader>ff", builtin.find_files, { desc = "Find files" })
      map("n", "<leader>fg", builtin.live_grep, { desc = "Live grep" })
      map("n", "<leader>fb", builtin.buffers, { desc = "Buffers" })
      map("n", "<leader>fs", builtin.lsp_document_symbols, { desc = "Document symbols" })
      map("n", "<leader>fS", builtin.lsp_workspace_symbols, { desc = "Workspace symbols" })
      map("n", "<leader>fr", builtin.lsp_references, { desc = "References" })
      map("n", "<leader>fd", builtin.diagnostics, { desc = "Diagnostics" })
    end,
  },
  {
    "nvim-treesitter/nvim-treesitter",
    commit = "cf12346a3414fa1b06af75c79faebe7f76df080a",
    lazy = false,
    build = ":TSUpdate",
    config = function()
      require("nvim-treesitter.configs").setup({
        highlight = { enable = true },
        indent = { enable = true },
      })
    end,
  },
  {
    "folke/trouble.nvim",
    opts = {},
    keys = {
      { "<leader>xx", "<cmd>Trouble diagnostics toggle<cr>", desc = "Diagnostics list" },
      { "<leader>xr", "<cmd>Trouble lsp_references toggle<cr>", desc = "References list" },
      { "<leader>xq", "<cmd>Trouble qflist toggle<cr>", desc = "Quickfix list" },
    },
  },
  {
    "stevearc/oil.nvim",
    opts = {},
    keys = {
      { "-", "<cmd>Oil<cr>", desc = "Open parent directory" },
    },
  },
}, {
  ui = {
    border = "rounded",
  },
})
```

補足:

- `Neovim 0.11.x` では、`nvim-treesitter` は rewrite 前の系統に固定してください
- このガイドでは再現性のため、`branch` ではなくコミット固定にしています

## LSP サーバーについて

上の `vim.lsp.enable(...)` は、対応する言語サーバーの実行ファイルがシステムに入っている前提です。最初は自分が読む言語だけ入れてください。

このリポジトリなら、まずは次で十分です。

- `lua_ls`
- `pyright`
- `ruff`
- `ts_ls`

必要になってから `gopls` などを足すほうが管理しやすいです。

LSP サーバーの導入方法は複数あります。

- OS パッケージマネージャーで入れる
- 言語ごとの標準的な方法で入れる
- `mason.nvim` を後から追加して管理する

最初はシステム管理でも問題ありません。設定を理解してから `mason.nvim` を足すほうが挙動を掴みやすいです。

## ctags の併用

`ctags` は不要ではありません。LSP が弱いリポジトリや、雑多な言語が混ざったツリーでは保険になります。

プロジェクトルートで次を実行します。

```bash
ctags -R
```

これで `tags` ファイルができ、次の操作が使えるようになります。

- `Ctrl-]`: シンボル定義へ移動
- `Ctrl-T`: 戻る
- `g]`: 候補一覧付きでタグジャンプ
- `:tselect {name}`: タグ候補を一覧表示

`LSP` が効く言語では `gd` / `gr` を優先し、効かない箇所だけタグジャンプに逃がす運用が安定します。

## 日常の操作

最初に覚える操作はこれだけで十分です。

### 移動

- `gd`: 定義へ移動
- `gr`: 参照を表示
- `gI`: 実装へ移動
- `K`: ホバー表示
- `Ctrl-o`: ジャンプ履歴を戻る
- `Ctrl-i`: ジャンプ履歴を進む

### 検索

- `<leader>ff`: ファイル検索
- `<leader>fg`: 全文検索
- `<leader>fs`: 現在ファイルのシンボル検索
- `<leader>fS`: ワークスペース全体のシンボル検索
- `<leader>fb`: バッファ一覧

### 診断と一覧

- `[d`: 前の診断へ
- `]d`: 次の診断へ
- `<leader>e`: 現在行の診断
- `<leader>xx`: 診断一覧
- `<leader>xr`: 参照一覧
- `<leader>xq`: quickfix 一覧

### ファイル操作

- `-`: 親ディレクトリを開く

## コードリーディングの基本ループ

読むときは次の順が速いです。

1. `<leader>ff` でファイルを開く
2. `<leader>fs` でファイル内シンボルを見る
3. `gd` で定義へ飛ぶ
4. `gr` または `<leader>xr` で参照を一覧する
5. `<leader>fg` で文字列ベースの呼び出し元や設定箇所も拾う
6. `Ctrl-o` で元の地点に戻る

この流れに慣れると、サイドバー常駐型の UI がなくても十分読めます。

## Sway 前提の運用

`Sway` では、Neovim を中心に据えたほうが扱いやすいです。

- 1 ワークスペース 1 主題にする
- ファイルツリーを常駐させず、必要時だけ `Oil` を開く
- 参照や診断は `Trouble` や quickfix に集約する
- 分割は `Neovim` 内、タスク分離は `Sway` 側で行う

実運用では、次のように分けると迷いにくいです。

- workspace 1: `nvim`
- workspace 2: 開発サーバーやテスト
- workspace 3: ブラウザや設計資料

## ファイルに応じた `lcd` 自動切り替え

この設定では、ファイルを開いたときにウィンドウローカルのカレントディレクトリを最寄りの project root に自動で寄せます。

- `backend/app/*.py` を開くと `backend/`
- `frontend/src/*` を開くと `frontend/`
- それ以外は、最寄りの `.git` などを見て判断

この動作は `lcd` ベースなので、Neovim 全体のカレントディレクトリではなく、現在ウィンドウだけが切り替わります。

そのため、repo root で `nvim` を起動しても、Python の import 解決のために毎回 `:lcd backend` を打つ必要はありません。

## 最初にやる確認

設定後は次を確認してください。

```bash
nvim
```

Neovim 起動後:

```vim
:checkhealth
:Lazy
:Telescope find_files
```

さらに、TypeScript や Python のファイルを開いて `gd` と `gr` が動けば初期セットアップは概ね完了です。

## 追加候補

最初から増やしすぎないほうが良いですが、必要になったら次を検討してください。

- `mason.nvim`: LSP サーバー管理を Neovim に寄せたいとき
- `gitsigns.nvim`: Git 差分を読みながらコードを追いたいとき
- `which-key.nvim`: キーマップを可視化したいとき

ただし、コードリーディングの生産性を最初に決めるのは、プラグインの数よりも `LSP` と `grep` の運用です。

## 参考

- Neovim LSP: <https://neovim.io/doc/user/lsp>
- Neovim 本体: <https://neovim.io/>
- lazy.nvim: <https://github.com/folke/lazy.nvim>
- nvim-lspconfig: <https://github.com/neovim/nvim-lspconfig>
- telescope.nvim: <https://github.com/nvim-telescope/telescope.nvim>
- nvim-treesitter: <https://github.com/nvim-treesitter/nvim-treesitter>
- trouble.nvim: <https://github.com/folke/trouble.nvim>
- oil.nvim: <https://github.com/stevearc/oil.nvim>
- Universal Ctags: <https://docs.ctags.io/>
- GNU Global: <https://www.gnu.org/software/global/manual/global.html>
