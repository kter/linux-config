# Windows の Toshy 風キーバインド

[toshy/toshy_config.py](../toshy/toshy_config.py) の Emacs スタイル操作を、AutoHotkey v2 で Windows に移植した設定です。Toshy 全体の移植ではありません。

## 前提

- Windows 11
- [AutoHotkey v2](https://www.autohotkey.com/)（v1 は非対応。動作確認バージョン: 2.0.28）
- US キーボード
- Microsoft 日本語 IME
- Windows のハードウェアキーボードレイアウトを **英語キーボード（101/102キー）** に設定

US キーボードを日本語配列として認識させると、CapsLock が英数キー（VK_F0）として届き、キーを離した信号を取得できない場合がありました。実機ではカーソル移動が解除されず、通常の文字入力ができなくなりました。

設定 → 時刻と言語 → 言語と地域 → 日本語の「言語のオプション」→ キーボードの「レイアウトを変更する」で英語配列に変更し、Windows を再起動してください。日本語入力は Microsoft IME で引き続き利用できます。

スクリプトは通常の CapsLock（VK_CAPITAL / `vk14`）だけを修飾キーとして扱います。`SC03A` や `vkF0` に変更しないでください。JIS キーボード向けの設定ではありません。

## PC 買い替え時のセットアップ

1. 新しい PC に [AutoHotkey v2](https://www.autohotkey.com/) をインストールします。Toshy 本体のインストールは不要です。
2. US キーボードを接続し、上記のハードウェアレイアウトを英語（101/102キー）に変更して再起動します。Microsoft 日本語 IME も用意します。
3. このリポジトリの **Code → Download ZIP** から取得し、ZIP を展開します。Git を使う場合は `git clone https://github.com/kter/linux-config.git` でも構いません。
4. 展開した `windows/toshy-emacs-windows.ahk` を、例えばユーザーフォルダー内の `keymaps` フォルダーへコピーします。ZIP 内のまま実行せず、今後移動しない場所に置きます。スクリプトに旧 PC 固有のパスは含まれていません。
5. 以下の「起動と自動起動」に従って起動し、**新しい保存先を指すショートカット**を作成します。旧 PC のショートカットは流用しません。
6. メモ帳で「確認と停止」のチェック項目を試し、サインアウト・サインイン後も自動起動することを確認します。

レイアウトと自動起動の登録は Windows 側の設定なので、リポジトリをコピーするだけでは再現されません。この手順を新しい PC ごとに実施してください。

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

## 左Altを Mac の Command として使う

| キー | 動作 | 通常送信するキー |
| --- | --- | --- |
| 左Alt + F | 検索 | Ctrl + F |
| 左Alt + A | 全選択 | Ctrl + A |
| 左Alt + X / C / V | 切り取り / コピー / 貼り付け | Ctrl + X / C / V |
| 左Alt + Q | アクティブウィンドウを閉じる | WinClose（通常の終了要求） |
| 左Alt + W | タブを閉じる | Ctrl + W |
| 左Alt + N | 新規ウィンドウ | Ctrl + N |
| 左Alt + M | 最小化 | WinMinimize |
| 左Alt + T | 新規タブ | Ctrl + T |

メモ帳では N を Ctrl + Shift + N（新規ウィンドウ）、T を Ctrl + N（新規タブ）に変換します。VS Code / VSCodium の N も Ctrl + Shift + N に変換します。その他のアプリでは、そのアプリの Ctrl ショートカットに従うため、新規作成・タブ操作などの結果はアプリに依存します。ターミナルの左Alt操作にも同じ変換が適用され、例えば Ctrl + C はコピーではなく割り込みとして扱われる場合があります。

左Alt単独ではメニューを開きません。通常の Alt 操作には右Altを使ってください。CapsLock を押している間は左Altのコマンド変換を無効にしています。

実機での検出不良を解消するため、左Altは `LAlt & a` などの組み合わせで定義しています。単純な `<!a` と左Altの無効化を組み合わせる形へ戻さないでください。

## 確認と停止

2026-09-24、US 配列へ変更して再起動した環境で、利用者が次の動作を確認しました。

- メモ帳で CapsLock を使ったカーソル操作
- CapsLock を離した後の通常の文字入力
- CapsLock + Space による日本語入力 / 英字入力の切り替え
- メモ帳で左Alt + A による全選択、左Alt + F による検索（Computer Use と利用者による確認）
- 左Alt単独でメニューのアルファベットが表示されないこと

新しい PC でも、A・F の単独入力 → CapsLock + F → CapsLockを離して A・F の通常入力、IME切り替え、左Altの各操作の順で確認してください。

入力に問題がある場合は **Ctrl + Alt + F12**、または通知領域の AutoHotkey アイコンの **Suspend Hotkeys / Suspend Script** で一時停止できます。完全に終了するには同アイコンの **Exit** を選びます。自動起動も止める場合はスタートアップフォルダーから対象のショートカットを外してください。
