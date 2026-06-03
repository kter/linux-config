# Thunderbolt外部ディスプレイ出力 調査レポート

---

## [2026-05-30 追記] 新マシンでの動作確認

- マシン: (新マシン)
- OS: Fedora 44 (kernel 7.0.10-201.fc44.x86_64)
- GPU: Intel Iris Xe (Alder Lake-P)
- Thunderboltコントローラ: Intel Thunderbolt 4 (Alder Lake / JHL8xxx)

**結果: Thunderbolt経由でLG 40U990Aへの映像出力に成功。**

TB4はUSB4/TB5デバイス (Barlow Ridge) のスイッチ列挙に正常に対応しており、DPトンネルが確立される。下記の旧マシン (TB3) での問題はこのマシンでは発生しない。

接続時のカーネルログ（正常動作）:
```
thunderbolt 1-1: new device found, vendor=0x1e device=0x111d
thunderbolt 1-1: LG Electronics 40U990A
thunderbolt 1-0:1.1: new retimer found, vendor=0x8087 device=0x15ee
rc rc0: DP-4 as /devices/pci0000:00/0000:00:02.0/rc/rc0
```

PCIeスイッチ (bus 50-78)、USBハブ、Ethernet、オーディオ、モニターコントロール等すべて正常認識。

---

## [旧マシン: Dell Latitude 7290] 調査記録 (2026-04-03)

- 調査日: 2026-04-03
- マシン: Dell Latitude 7290
- OS: Fedora 43 (kernel 6.19.9-200.fc43.x86_64)
- WM: sway (Wayland)

## ハードウェア構成

| コンポーネント | 詳細 |
|---|---|
| GPU | Intel Kaby Lake-R GT2 UHD Graphics 620 |
| Thunderboltコントローラ | Intel JHL6340 Alpine Ridge 2C (TB3, 2レーン) |
| NHIファームウェア | v40.00 (fwupd確認済み、最新) |
| モニター | LG Electronics 40U990A (USB4世代) |
| モニター内蔵コントローラ | Intel JHL9480 Barlow Ridge (TB5/USB4) |

## 症状

- Thunderbolt経由で外部ディスプレイに映像が出力されない
- HDMI接続では正常に出力可能
- 同じケーブルでMacBookからは出力可能

## 調査結果

### 動作しているもの

- **PCIeトンネル**: Barlow Ridge TB5コントローラがPCIデバイスとして正常に列挙 (bus 06-08)
- **USBトンネル**: モニター内蔵USBハブ、ヘッドセット/マイク、Ethernetアダプター等すべて認識
- **Thunderbolt Alt Mode**: USB Type-Cポートで有効 (SVID 8087, active=yes)
- **boltd**: セキュリティレベル `none`、ホストデバイス (Latitude 7290) は authorized

### 動作していないもの

- **DPトンネル**: 確立されない
- **DRM DP出力**: `card1-DP-1`, `card1-DP-2` ともに `disconnected`
- **DisplayPort Alt Mode**: パートナーデバイス側で `active=no` (SVID ff01)
- **Thunderboltスイッチ列挙**: 失敗

### 根本原因

カーネルログに以下のエラーが一貫して記録される:

```
thunderbolt 0000:05:00.0: failed to find route string for switch at 1.1
thunderbolt 0000:05:00.0: no switch exists at 1.1, ignoring
```

Alpine Ridge 2C (TB3) のNHIファームウェアが、ダウンストリームのBarlow Ridge (USB4/TB5) デバイスをThunderboltスイッチとして列挙できない。DPトンネルはスイッチ列挙後に確立されるため、この段階で失敗するとDP出力は不可能。

USB Billboard デバイス (VIA Labs 2109:0100) も検出されており、DP Alt Modeの交渉が失敗したことを示している。

### USB Type-C Alt Mode状態

| パス | SVID | 説明 | active |
|---|---|---|---|
| port0-partner.0 | 8087 | Thunderbolt3 | yes |
| port0-partner.1 | ff01 | DisplayPort | **no** |

TB Alt Modeが優先され、DP Alt Modeは有効化されない。UCSIコントローラはsysfs経由でのモード切替を拒否 (`Operation not supported`)。

## 試行した対策と結果

| 対策 | 結果 |
|---|---|
| ケーブル抜き差し (複数回) | 変化なし。同じエラー再現 |
| PCI バス再スキャン (`echo 1 > /sys/bus/pci/rescan`) | 変化なし |
| boltctl authorize (UUID指定) | デバイスが disconnected のため認証不可 |
| DP Alt Mode 直接有効化 (sysfs書き込み) | UCSI が拒否 (`Operation not supported`) |
| TB Alt Mode 無効化 → DP 有効化 | UCSI が拒否 (`Operation not supported`) |
| コールドブート (電源オフ→モニター接続状態で起動) | 変化なし。起動時に同じエラー |
| カーネルパラメータ `thunderbolt.start_icm=true` | 変化なし |

## カーネルブートパラメータ (調査時)

```
intel_iommu=off i915.enable_dc=0 thunderbolt.start_icm=true
```

※ `thunderbolt.start_icm=true` は効果がなかったため削除推奨。

## 結論

**Alpine Ridge 2C (JHL6340, TB3) ファームウェアがUSB4/TB5 (Barlow Ridge) デバイスのThunderboltスイッチ列挙に対応しておらず、DPトンネルを確立できない。** これはハードウェア/ファームウェアレベルの互換性問題であり、カーネルパラメータやソフトウェア設定では解決できない。

## 代替案

1. **HDMI接続** - 動作確認済み。最も確実
2. **USB-C → DisplayPort変換アダプター** - DP Alt Modeで接続 (TB経由ではない)。モニターのDP入力に接続
3. **Thunderbolt 3対応ドック** (DP/HDMI出力付き) - ドック側でDPトンネルを処理
