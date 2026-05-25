# Neovim キーマップ チートシート

> `<leader>` = `Space`

---

## ウィンドウ

| キー | 説明 |
|------|------|
| `<C-h>` | 左のウィンドウへ移動 |
| `<C-j>` | 下のウィンドウへ移動 |
| `<C-k>` | 上のウィンドウへ移動 |
| `<C-l>` | 右のウィンドウへ移動 |
| `<leader>wh` | 水平分割（下に開く） |
| `<leader>wv` | 垂直分割（右に開く） |
| `<leader>wo` | 現在のウィンドウのみ残す |

---

## ファイルツリー / ファイル操作

| キー | 説明 |
|------|------|
| `<leader>e` | ファイルツリーをトグル（neo-tree） |
| `-` | 親ディレクトリを開く（oil.nvim） |

---

## Telescope（検索）

| キー | 説明 |
|------|------|
| `<leader>ff` | ファイルを検索 |
| `<leader>fg` | 全文検索（live grep） |
| `<leader>fb` | バッファ一覧 |
| `<leader>fs` | ドキュメントシンボル（LSP） |
| `<leader>fS` | ワークスペースシンボル（LSP） |
| `<leader>fr` | 参照一覧（LSP） |
| `<leader>fd` | 診断一覧 |

> Telescope内: `<Esc>` で閉じる

---

## LSP

| キー | 説明 |
|------|------|
| `gd` | 定義へジャンプ |
| `gr` | 参照一覧 |
| `gI` | 実装へジャンプ |
| `K` | ホバードキュメント表示 |
| `<leader>rn` | リネーム |
| `<leader>ca` | コードアクション |
| `[d` | 前の診断へ |
| `]d` | 次の診断へ |

---

## 診断（Diagnostics）

| キー | 説明 |
|------|------|
| `<leader>E` | 現在行の診断をフロート表示 |
| `<leader>xx` | 診断リスト（プロジェクト全体） |
| `<leader>xb` | 診断リスト（現在バッファ） |
| `<leader>xr` | 参照リスト |
| `<leader>xq` | クイックフィックスリスト |

---

## Claude Code

| キー | モード | 説明 |
|------|--------|------|
| `<leader>ac` | Normal | Claude Code ターミナルをトグル |
| `<leader>af` | Normal | Claude Code にフォーカス |
| `<leader>aa` | Normal | 現在ファイルをコンテキストに追加 |
| `<leader>as` | Visual | 選択テキストを Claude に送信 |

---

## Git（差分・履歴）

### Diffview

| キー | 説明 |
|------|------|
| `<leader>gd` | Diffview を開く（現在の変更） |
| `<leader>gh` | 現在のファイルの履歴を表示 |
| `<leader>gH` | 現在のブランチの履歴を表示 |
| `<leader>gq` | Diffview を閉じる |

**PR / ブランチ差分レビュー用コマンド**

| コマンド | 説明 |
|------|------|
| `:DiffviewOpen origin/main...HEAD` | 現在のブランチが main から分岐して以降の全変更を表示 |
| `:DiffviewOpen origin/main...feature/foo` | 任意のブランチの差分を表示 |
| `:DiffviewFileHistory` | リポジトリ全体のファイル履歴 |

> Diffview内: `<tab>`/`<S-tab>` 次/前ファイル、`X` レビュー済みマーク、`-` ステージトグル、`q` 閉じる

### Gitsigns（バッファ内の差分）

| キー | 説明 |
|------|------|
| `]c` | 次の変更箇所（hunk）へ |
| `[c` | 前の変更箇所（hunk）へ |
| `<leader>gs` | 変更箇所をステージ（add） |
| `<leader>gr` | 変更箇所をリセット（戻す） |
| `<leader>gp` | 変更箇所のプレビューをフロート表示 |
| `<leader>gb` | 現在行の git blame を表示 |
| `<leader>tb` | 行ごとの blame 表示をトグル |

---

## GitHub PR レビュー（Octo）

> 前提: `gh auth login` 済み、リポジトリに GitHub remote が設定されていること

### キーマップ（`<leader>o` プレフィックス）

| キー | 説明 |
|------|------|
| `<leader>opl` | PR 一覧（Telescope） |
| `<leader>opo` | 現在のブランチを PR としてチェックアウト |
| `<leader>opr` | レビュー開始（diffview UI が開く） |
| `<leader>ops` | レビューを送信（comment / approve / request changes 選択） |
| `<leader>opc` | PR の CI チェック状況を表示 |
| `<leader>oil` | Issue 一覧（Telescope） |

### 主要 `:Octo` コマンド

| コマンド | 説明 |
|------|------|
| `:Octo pr list` | PR 一覧 |
| `:Octo pr checkout <num>` | 指定番号の PR をチェックアウト |
| `:Octo pr edit <num>` | PR バッファを開く（説明編集・コメント追加） |
| `:Octo pr checks` | CI ステータス |
| `:Octo pr merge [commit\|squash\|rebase]` | マージ |
| `:Octo review start` | レビューセッション開始 |
| `:Octo review submit` | レビュー送信 |
| `:Octo review resume` | 中断したレビューを再開 |
| `:Octo review discard` | レビュー破棄 |
| `:Octo issue list` | Issue 一覧 |
| `:Octo issue create` | Issue 作成 |

### レビューセッション中のバッファ内キーマップ（plugin デフォルト）

| キー | 説明 |
|------|------|
| `<space>ca` | 行コメント追加（normal / visual） |
| `<space>sa` | suggestion を追加（visual で範囲選択して） |
| `<space>ct` | スレッドコメント追加 |
| `]q` / `[q` | 次/前のコメント・スレッドへ |
| `]t` / `[t` | 次/前のスレッドへ |

### PR レビューのワークフロー例

1. `<leader>opl` → Telescope で PR を選択
2. `:Octo pr checkout` でローカルにチェックアウト
3. `<leader>opr` でレビュー開始（diffview UI が開く）
4. `<tab>` でファイルを巡回、コメントしたい行で `<space>ca`
5. `<leader>ops` で送信（approve / comment / request changes を選択）

---

## タグ

| キー | 説明 |
|------|------|
| `<leader>tt` | カーソル下の単語でタグ選択 |

---

## Markdown（`.md` ファイルのみ）

| キー | 説明 |
|------|------|
| `<leader>mp` | ブラウザプレビューをトグル |

---

## nvim-surround

| キー | モード | 説明 |
|------|--------|------|
| `ys{motion}{char}` | Normal | 囲みを追加（例: `ysiw"` で単語を `"` で囲む） |
| `yst;"` | Normal | カーソル位置から `;` の手前までを `"` で囲む（`import "lib/utils"` のような用途） |
| `ds{char}` | Normal | 囲みを削除（例: `ds"` で `"` を削除） |
| `cs{old}{new}` | Normal | 囲みを変更（例: `cs'"` で `'` を `"` に変更） |
| `S{char}` | Visual | 選択範囲を囲む |
