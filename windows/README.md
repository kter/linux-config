# Windows の Toshy 風キーバインド

[toshy/toshy_config.py](../toshy/toshy_config.py) の Emacs スタイル操作を、AutoHotkey v2 で Windows に移植した設定です。Toshy 全体の移植ではありません。

## 前提

- Windows 11
- [AutoHotkey v2](https://www.autohotkey.com/)（v1 は非対応）
- US キーボード
- Microsoft 日本語 IME
- Windows のハードウェアキーボードレイアウトを **英語キーボード（101/102キー）** に設定

US キーボードを日本語配列として認識させると、CapsLock が英数キー（VK_F0）として届き、キーを離した信号を取得できない場合がありました。実機ではカーソル移動が解除されず、通常の文字入力ができなくなりました。

設定 → 時刻と言語 → 言語と地域 → 日本語の「言語のオプション」→ キーボードの「レイアウトを変更する」で英語配列に変更し、Windows を再起動してください。日本語入力は Microsoft IME で引き続き利用できます。

スクリプトは通常の CapsLock（VK_CAPITAL / `vk14`）だけを修飾キーとして扱います。`SC03A` や `vkF0` に変更しないでください。JIS キーボード向けの設定ではありません。

## 起動と自動起動

1. AutoHotkey v2 をインストールします。
2. [toshy-emacs-windows.ahk](toshy-emacs-windows.ahk) を固定の場所に置き、ダブルクリックして実行します。
3. 自動起動する場合は、このファイルのショートカットを作成します。
4. エクスプローラーのアドレス欄に `shell:startup` を入力し、開いたフォルダーへショートカットを置きます。

スクリプトの変更後は同じファイルをもう一度実行すると再読み込みされます。ファイルを移動した場合は、自動起動ショートカットの参照先も更新してください。

## キー操作

CapsLock を押している間だけ次の操作になります。CapsLock 単独では大文字固定を切り替えません。

| キー | 通常の GUI アプリでの動作 |
| --- | --- |
| CapsLock + A / E | 行頭 / 行末 |
| CapsLock + F / B | 右 / 左 |
| CapsLock + P / N | 上 / 下 |
| CapsLock + D / H | Delete / Backspace |
| CapsLock + Space | 日本語入力 / 英字入力の切り替え |
| Ctrl + Alt + F12 | スクリプトの一時停止 / 再開 |

CapsLock + Space は、US 配列の Microsoft IME が提供する **Alt + バッククォート** を送ります。Space を離すまで待つことで、長押しによる連続切り替えを防ぎます。参考：[Microsoft 日本語 IME のショートカット](https://support.microsoft.com/ja-jp/windows/hardware/input-devices/microsoft-japanese-ime)。

ターミナルでは、CapsLock + `A E F B P N D H C Z L U W K R V` を対応する Ctrl + 文字へ変換します。対象は Windows Terminal、PowerShell、cmd、WezTerm、Alacritty、kitty、Ghostty の各プロセスです。実際の動作はシェルやターミナルのキー設定に依存します。

VS Code / VSCodium ではカーソル・削除操作の変換を除外しています。CapsLock + Space はターミナル・エディターでも有効です。

## 確認と停止

2026-09-24、US 配列へ変更して再起動した環境で、利用者が次の動作を確認しました。

- メモ帳で CapsLock を使ったカーソル操作
- CapsLock を離した後の通常の文字入力
- CapsLock + Space による日本語入力 / 英字入力の切り替え

入力に問題がある場合は **Ctrl + Alt + F12**、または通知領域の AutoHotkey アイコンの **Suspend Hotkeys / Suspend Script** で一時停止できます。完全に終了するには同アイコンの **Exit** を選びます。自動起動も止める場合はスタートアップフォルダーから対象のショートカットを外してください。
