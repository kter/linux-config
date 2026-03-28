# Sway 設定メモ

## 環境

- OS: Fedora 43
- WM: Sway 1.11
- GPU: Intel UHD 620 (Kaby Lake / i915)
- ノートPC: Dell Latitude 7290
- ディスプレイ:
  - 内蔵: `eDP-1` 1920x1080 @ 60Hz
  - 外部: `HDMI-A-1` LG ULTRAFINE 5K2K
    - 現在の固定モード: `3440x1440@49.987Hz`（HDMI接続時、21:9維持）

---

## セットアップ時に修正した内容

### 1. modifierキーの設定（`~/.config/sway/config`）

`Super_L` はSwayのmodifier名として無効。`Mod4` に変更が必要。

```
# 誤り
set $mod Super_L

# 正しい
set $mod Mod4
```

### 2. ターミナルとランチャー（`~/.config/sway/config`）

`alacritty` と `dmenu_run` は未インストールのため、利用可能なものに変更。

```
set $term foot          # Wayland専用の軽量ターミナル
set $menu wofi --show run  # Wayland対応ランチャー
```

インストール:
```bash
sudo dnf install wofi
```

### 3. 日本語入力（fcitx5 + mozc）

#### `~/.config/environment.d/fcitx5.conf`

systemdのenvironment.dファイルには変数定義のみ記述可能。`exec` コマンドは無効なため削除。

```ini
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
SDL_IM_MODULE=fcitx
```

#### `~/.bash_profile`

`GLFW_IM_MODULE` が `ibus` になっていたため `fcitx` に修正。

```bash
export GLFW_IM_MODULE=fcitx
```

#### `~/.config/sway/config`

- fcitx5 を起動
- DBus / systemd user service に Wayland セッション変数を伝える
- `for_window` の `class=` はX11の概念。Waylandでは `app_id=` を使用

```
exec_always --no-startup-id systemctl --user import-environment XDG_SESSION_TYPE XDG_CURRENT_DESKTOP WAYLAND_DISPLAY SWAYSOCK
exec_always --no-startup-id dbus-update-activation-environment --systemd XDG_SESSION_TYPE XDG_CURRENT_DESKTOP WAYLAND_DISPLAY SWAYSOCK
exec_always --no-startup-id systemctl --user restart toshy-wlroots-dbus.service toshy-config.service
exec fcitx5 -d
for_window [app_id="fcitx"] floating enable, border none
```

日本語/英語の切り替えキー: `Ctrl+Space` または `Zenkaku_Hankaku`

### 4. キーボードレイアウト（`~/.config/sway/config`）

物理キーボードが US 配列のため `xkb_layout` を `jp` から `us` に変更。

```
input type:keyboard {
  xkb_layout us
  xkb_options caps:ctrl_modifier
}
```

※ `xkb_layout` は物理キー配列の設定。日本語IME（fcitx5）とは独立している。

### 4.1 Toshy 連携

`Toshy` を `sway` で使う場合は、systemd user service に
Wayland セッション変数を渡さないと起動に失敗することがある。

`~/.config/sway/config` で以下を実行しておく:

```conf
exec_always --no-startup-id systemctl --user import-environment XDG_SESSION_TYPE XDG_CURRENT_DESKTOP WAYLAND_DISPLAY SWAYSOCK
exec_always --no-startup-id dbus-update-activation-environment --systemd XDG_SESSION_TYPE XDG_CURRENT_DESKTOP WAYLAND_DISPLAY SWAYSOCK
exec_always --no-startup-id systemctl --user restart toshy-wlroots-dbus.service toshy-config.service
```

この構成では `Mod4` は変えず、物理 `Win` キーをそのまま `sway` の modifier として維持する。
`CapsLock -> Ctrl` は維持しつつ、GUI アプリでは `Toshy` 側で
物理 `Alt` を使った Mac 風ショートカット（`Alt+C/V/T/W/F...`）を使えるようにしている。

ターミナル（`foot` など）は `Toshy` の変換対象から外しているため、
`Win+C/V` よりもアプリ本来のショートカットを優先する。

`Win+d` は `Toshy` の `Super-d -> Delete` と衝突するため、
`wofi` ランチャーは `Win+/` に割り当てている。

### 4.2 トラックパッド

タップでクリック扱いにするには `touchpad` 入力ブロックで `tap enabled`
を指定する。

```conf
input type:touchpad {
  tap enabled
}
```

### 5. フォント（`~/.config/sway/config`）

Sway 側で明示的に日本語フォントを使う場合は `font` を指定する。

```conf
font pango:Noto Sans CJK JP 10
```

Fedora では `google-noto-sans-cjk-fonts` に含まれる `Noto Sans CJK JP` を利用できる。

---

## コピペ

### GUIアプリ（Chromium, Firefox など）
- コピー: `Ctrl+C`
- ペースト: `Ctrl+V`
- Toshy有効時: `Alt+C` / `Alt+V` も利用可
- ページ内検索: `Ctrl+F` または `Alt+F`

### ターミナル（foot）
- コピー: `Ctrl+Shift+C`
- ペースト: `Ctrl+Shift+V`
- `Alt+C` / `Alt+V` は使わない前提（Toshyの変換対象外）

### プライマリ選択（Linuxの「選択してそのままペースト」）
- テキストを選択するだけでクリップボードに入る
- 中クリックでペースト

### コマンドライン
```bash
wl-copy < ファイル        # ファイル内容をコピー
echo "text" | wl-copy    # テキストをコピー
wl-paste                 # クリップボードの内容を出力
```

---

## WiFi接続

### TUI（ターミナル画面）で接続する（推奨）

```bash
nmtui
```

`NetworkManager-tui` パッケージが必要:
```bash
sudo dnf install NetworkManager-tui
```

### コマンドラインで接続する

```bash
# 利用可能なWifiを一覧表示
nmcli device wifi list

# 接続（パスワードありの場合）
nmcli device wifi connect "SSID名" password "パスワード"

# 接続済みネットワーク一覧
nmcli connection show

# 切断
nmcli connection down "SSID名"
```

---

## ディスプレイ

### 内蔵ディスプレイ（eDP-1）

1920x1080 のみ対応。解像度変更は不可。リフレッシュレートのみ変更可能。

```bash
swaymsg "output eDP-1 mode 1920x1080@60Hz"   # 60Hz（デフォルト）
swaymsg "output eDP-1 mode 1920x1080@48Hz"   # 48Hz
```

### 外部ディスプレイ（LG ULTRAFINE 5K2K）

### 現状（HDMI接続）

LG ULTRAFINE 5K2K のネイティブ解像度は **5120x2160（21:9）** だが、
HDMIはその帯域をサポートしないため 5120x2160 では接続不可。

21:9 アスペクト比を維持した最適モード:

```bash
swaymsg "output HDMI-A-1 mode 3440x1440@49.987Hz scale 1"
```

※ 3440x1440 は 5120x2160 の整数倍ではないため、ディスプレイ側の
ハードウェアスケーラーによる若干のぼやけが生じる。

`~/.config/sway/config` でも以下を固定しておく:

```conf
output eDP-1 mode 1920x1080@60.049Hz position 0 0 scale 1
output HDMI-A-1 mode 3440x1440@49.987Hz position 1920 0 scale 1
```

### Thunderbolt 接続について

このPCには Thunderbolt 3（JHL6340）および Thunderbolt 5（JHL9480）が搭載されている。
USB-C/Thunderbolt ケーブルで接続すれば 5120x2160 ネイティブで使用可能（未解決）。

接続時のカーネルエラー:
```
thunderbolt: failed to find route string for switch at 1.1
thunderbolt: no switch exists at 1.1, ignoring
```

現在調査中。BIOSのThunderboltセキュリティ設定は確認済み（問題なし）。

---

## 明るさ調整

`brightnessctl` が必要:
```bash
sudo dnf install brightnessctl
```

### キーボードショートカット（sway config に設定済み）

| キー | 動作 |
|------|------|
| `XF86MonBrightnessUp` | 明るさ +5% |
| `XF86MonBrightnessDown` | 明るさ -5% |

（ノートPCの明るさキー）

### コマンドで直接変更

```bash
brightnessctl set 50%     # 50%に設定
brightnessctl set +10%    # 10%上げる
brightnessctl set 10%-    # 10%下げる
brightnessctl get         # 現在の値を確認
```

---

## Waybar

### バーが二重に表示される問題（修正済み）

**原因**: `bar {}` ブロック（swaybar）と `exec waybar` が両方動いていた。

**修正**: `bar {}` ブロックを削除し、`exec waybar` のみ残した。

### カスタマイズ

`~/.config/waybar/config.jsonc` と `~/.config/waybar/style.css` を作成。

**テーマ**: Catppuccin Mocha ベースのダーク・ミニマル

| 要素 | 色 |
|------|----|
| 背景 | `#1e1e2e` |
| 文字 | `#cdd6f4` |
| 選択中ワークスペース（アンダーライン） | `#89b4fa`（青） |
| 時計 | `#89b4fa`（青） |
| 明るさ表示 | `#f9e2af`（黄） |
| バッテリー警告 | `#f9e2af` → `#f38ba8`（赤） |

**表示モジュール（左→右）**:
- 左: ワークスペース番号、モード
- 中央: アクティブなウインドウタイトル
- 右: WiFi、明るさ、電源プロファイル、バッテリー、時計、トレイ

**バックライトのスクロール操作**: バックライト表示上でマウスホイールを回すと明るさ調整可能。

**電源プロファイル**: `power-profiles-daemon` モジュールを表示。左クリックで `power-saver` → `balanced` → `performance` を切り替え。

**必要パッケージ**:
```bash
sudo dnf install fontawesome-fonts brightnessctl
```

---

## キーボードショートカット一覧

`$mod` = Super（Windowsキー）、`$alt` = Alt

### ウインドウ操作

| キー | 動作 |
|------|------|
| `Shift+$mod+m` | クリップボードの内容を `mpv` で開く |
| `$mod+Enter` | ターミナル（foot）起動 |
| `$mod+/` | ランチャー（wofi）起動 |
| `$mod+Shift+Delete` | スクラッチパッドに送る |
| `$mod+Delete` | スクラッチパッド表示 |
| `$mod+Shift+minus` | スクラッチパッドに送る |
| `$mod+minus` | スクラッチパッド表示 |
| `$alt+h/j/k/l` | フォーカス移動（左/下/上/右） |
| `$alt+z/c` | フォーカス移動（前/次） |
| `Shift+$alt+h/j/k/l` | ウインドウ移動 |
| `Shift+$alt+0` | ウインドウサイズ均等化（50%x50%） |
| `$alt+t` | フロート切り替え |
| `$mod+Space` | タイル層とフロート層のフォーカス切り替え |
| `Shift+$mod+Space` | フロートウインドウへフォーカス |
| `$alt+s` | スティッキー切り替え |
| `$alt+o` | フロート＋スティッキー（最前面） |
| `Shift+$alt+f` | フルスクリーン切り替え |
| `$alt+p` | ボーダー切り替え（PiP風） |
| `$alt+e` | 分割方向切り替え |

### フロートウインドウ配置

| キー | 動作 |
|------|------|
| `Shift+$alt+Up` | 全画面配置 |
| `Shift+$alt+Left` | 左半分配置 |
| `Shift+$alt+Right` | 右半分配置 |

### レイアウト

| キー | 動作 |
|------|------|
| `Ctrl+$alt+a` | デフォルトレイアウト |
| `Ctrl+$alt+s` | 分割レイアウト切り替え |
| `Ctrl+$alt+d` | フロート化 |
| `$alt+r` | タブレイアウト |
| `$alt+y` | スタックレイアウト |
| `$alt+x` | 分割切り替え |
| `$alt+a` | ギャップ切り替え |

### ワークスペース

| キー | 動作 |
|------|------|
| `$mod+$alt+1/2/3` | ワークスペース番号移動 |
| `$mod+$alt+w` | 前のワークスペース |
| `$mod+$alt+x` | 前後切り替え |
| `$mod+$alt+z/c` | 同じモニターの前/次 |

### モニター間

| キー | 動作 |
|------|------|
| `Ctrl+$mod+z/c` | ウインドウを左/右モニターへ移動 |
| `Ctrl+$mod+Left/Right` | ウインドウを左/右モニターへ移動 |
| `Ctrl+$alt+z/c` | 左/右モニターにフォーカス |
| `Ctrl+$alt+Left/Right` | 左/右モニターにフォーカス |

`Toshy` の `Alt+C` / `Alt+Z` と衝突するアプリでは、
`Ctrl+$mod+Left/Right` の方を使う。

現在の配置は `eDP-1` が左、`HDMI-A-1` が右。

### スクラッチパッド

`move scratchpad` は効いていても `show` だけ特定キーで拾われないことがある。
その場合は `Delete` 系ではなく `minus` 系のバインドを使う。

### ウインドウサイズ調整

| キー | 動作 |
|------|------|
| `Shift+$alt+a/d` | 幅を縮小/拡大 |
| `Shift+$alt+w/s` | 高さを縮小/拡大 |
| `Shift+$mod+a/d` | 幅を拡大/縮小（逆方向） |
| `Shift+$mod+w/s` | 高さを拡大/縮小（逆方向） |
| `Shift+Ctrl+a/s/w/d` | ウインドウを相対移動（20px） |

### 明るさ

| キー | 動作 |
|------|------|
| `XF86MonBrightnessUp` | 明るさ +5% |
| `XF86MonBrightnessDown` | 明るさ -5% |
