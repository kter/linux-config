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
sudo dnf install -y ruff gopls rust-analyzer
mise use -g node@lts
mise use -g npm:pyright npm:typescript-language-server npm:typescript npm:vscode-langservers-extracted
```

補足:

- `ctags` パッケージ名は Fedora では `ctags`
- `fd` パッケージ名は Fedora では `fd-find`
- `lua-language-server` は標準 `dnf` リポジトリでは見当たりませんでした
- `vscode-langservers-extracted` に `vscode-eslint-language-server` が含まれています
- Node.js 系ツールは `npm install -g` ではなく `mise` で管理することを推奨します

## 他のマシンで再現する手順

2026-03-29 時点で、Fedora 系 + `Neovim 0.11.6` で確認した手順です。

### 1. パッケージを入れる

```bash
sudo dnf install -y neovim git ripgrep fd-find ctags wl-clipboard gcc make unzip
sudo dnf install -y ruff gopls rust-analyzer

# mise のインストール（未導入の場合）
curl https://mise.run | sh
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
source ~/.bashrc

# Node.js と npm パッケージを mise で管理
mise use -g node@lts
mise use -g npm:pyright npm:typescript-language-server npm:typescript npm:vscode-langservers-extracted
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
        ├── claudecode.lua
        ├── conform.lua
        ├── git.lua
        ├── lsp.lua
        ├── markdown-preview.lua
        ├── neo-tree.lua
        ├── oil.lua
        ├── surround.lua
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
nvim --headless "+TSUpdateSync bash json lua markdown markdown_inline python query rust tsx typescript vim vimdoc yaml" "+qa"
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
nvim --headless "+TSUpdateSync bash json lua markdown markdown_inline python query rust tsx typescript vim vimdoc yaml" "+qa"
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
- `Rust` を読むなら `rust-analyzer` と Treesitter `rust` を追加

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
      vim.diagnostic.config({
        severity_sort = true,
        virtual_text = { source = "if_many", prefix = "●" },
        underline = true,
        update_in_insert = false,
        float = { border = "rounded", source = "always" },
      })

      vim.api.nvim_create_autocmd("CursorHold", {
        callback = function()
          vim.diagnostic.open_float(nil, { focusable = false })
        end,
      })

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
      vim.lsp.enable("rust_analyzer")
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
      { "<leader>xx", "<cmd>Trouble diagnostics toggle<cr>", desc = "Diagnostics list (Project)" },
      { "<leader>xb", "<cmd>Trouble diagnostics toggle filter.buf=0<cr>", desc = "Diagnostics list (Buffer)" },
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
- `rust_analyzer`
- `ts_ls`

必要になってから `gopls` などを足すほうが管理しやすいです。

この構成では、現時点で次の言語を主に想定しています。

- Python: `pyright`, `ruff`
- TypeScript / TSX / React / Next.js: `ts_ls`, `eslint`
- Go: `gopls`
- Rust: `rust_analyzer`
- Lua: `lua-language-server` を入れれば有効

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
- `<leader>e`: 現在行の診断（カーソルを止めても自動表示されます）
- `<leader>xx`: プロジェクト全体の診断一覧
- `<leader>xb`: 現在バッファの診断一覧
- `<leader>xr`: 参照一覧
- `<leader>xq`: quickfix 一覧

### ファイル操作

- `<leader>E`: ファイルツリーをトグル（neo-tree）
- `-`: 親ディレクトリを開く（oil.nvim）

### テキスト囲み（nvim-surround）

囲いを追加:

- `ys{motion}{char}`: モーション範囲を囲う（例: `ysiw"` で単語を `"` で囲う）
- `yss{char}`: 行全体を囲う
- `S{char}`: ビジュアル選択範囲を囲う

囲いを削除・変更:

- `ds{char}`: 囲いを削除（例: `ds"` で `"hello"` → `hello`）
- `cs{old}{new}`: 囲い文字を変更（例: `cs"'` で `"hello"` → `'hello'`）

特殊な文字:

- `(` / `)`: スペースあり / スペースなしの `()` で囲う
- `[` / `]`: スペースあり / スペースなしの `[]` で囲う
- `{` / `}`: スペースあり / スペースなしの `{}` で囲う
- `t`: HTML タグで囲う
- `f`: 関数呼び出し形式で囲う

### Markdown プレビュー

- `<leader>mp`: プレビューをトグル（markdown ファイルのみ）

### Claude Code との連携

- `<leader>ac`: Claude Code ターミナルをトグル
- `<leader>af`: Claude Code にフォーカス
- `<leader>aa`: 現在ファイルを Claude のコンテキストに追加
- `<leader>as`: 選択テキストを Claude に送信 (visual mode)

diff が提案されたときは `:ClaudeCodeDiffAccept` / `:ClaudeCodeDiffDeny` で適用・拒否できます。

### Git（差分・履歴）

- `<leader>gd`: JetBrains 風の rich diff ビューワーを開く (Diffview)
- `<leader>gh`: 現在のファイルの変更履歴を確認
- `]c` / `[c`: ファイル内の変更箇所（hunk）へ移動 (Gitsigns)
- `<leader>gp`: 現在の変更箇所をその場でプレビュー
- `<leader>gb`: 現在行の git blame を表示

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
- ファイルツリーは `<leader>E` で neo-tree を、ファイル移動は `-` で oil.nvim を使い分ける
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

## TypeScript / React / Next.js 開発での ESLint・Prettier 連携

ESLint と Prettier の設定はリポジトリ側で管理します。Neovim はそれを読んで動くだけです。

### 前提: システムへの追加インストール

```bash
mise use -g npm:vscode-langservers-extracted
```

`vscode-eslint-language-server` がこのパッケージに含まれています。

### ESLint（`eslint` LSP）

`lsp.lua` に `eslint = "vscode-eslint-language-server"` を追加済みです。

- プロジェクトの `.eslintrc` / `eslint.config.js` を自動で読みます
- ESLint エラーが波線で表示されます
- `<leader>ca`（Code Action）で ESLint の自動修正が使えます

### Prettier（`conform.nvim`）

`conform.lua` を追加済みです。

- ファイル保存時にプロジェクトの `.prettierrc` を読んで自動フォーマットします
- Prettier がプロジェクトにない場合はスキップされます（`lsp_fallback = true`）
- 対象: `js`, `ts`, `jsx`, `tsx`, `json`, `css`

プロジェクト側での準備例:

```bash
npm install -D prettier eslint
```

## 追加候補

最初から増やしすぎないほうが良いですが、必要になったら次を検討してください。

- `mason.nvim`: LSP サーバー管理を Neovim に寄せたいとき
- `which-key.nvim`: キーマップを可視化したいとき
- `folke/snacks.nvim`: claudecode.nvim のターミナル体験を強化したいとき（現在は native provider を使用中）

`diffview.nvim` および `gitsigns.nvim` は導入済みです。JetBrains のようなリッチな Git 差分表示が可能です。

`neo-tree.nvim` は導入済みです。`<leader>E` でファイルツリーをサイドバー表示できます。Git status 表示やバッファ一覧への切り替えにも対応しています。

`nvim-surround` は導入済みです。`ysiw"` で単語を囲う、`ds"` で囲いを外す、`cs"'` で囲い文字を変換できます。

`markdown-preview.nvim` は導入済みです。markdown ファイルで `<leader>mp` を押すとブラウザでプレビューが開きます。初回インストール時は `node.js` と `npm` が必要です。

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
- neo-tree.nvim: <https://github.com/nvim-neo-tree/neo-tree.nvim>
- claudecode.nvim: <https://github.com/coder/claudecode.nvim>
- markdown-preview.nvim: <https://github.com/iamcco/markdown-preview.nvim>
- conform.nvim: <https://github.com/stevearc/conform.nvim>
- - nvim-surround: <https://github.com/kylechui/nvim-surround>
- - diffview.nvim: <https://github.com/sindrets/diffview.nvim>
- - gitsigns.nvim: <https://github.com/lewis6991/gitsigns.nvim>
- - Universal Ctags: <https://docs.ctags.io/>

- GNU Global: <https://www.gnu.org/software/global/manual/global.html>
