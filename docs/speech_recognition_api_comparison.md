# 音声認識APIサービス比較分析 (2024-2025)

## 主要サービス概要

### 1. AssemblyAI
**料金体系**
- **無料枠**: $50クレジット（約185時間の録音音声または333時間のストリーミング音声）
- **Nano tier**: $0.12/時間（速度重視）
- **Best tier**: $0.37/時間（精度重視、デフォルト）
- **リアルタイム**: $0.47/時間

**特徴**
- 精度: >93.3%
- 多言語対応
- 話者分離機能
- 感情分析、要約機能
- 企業向けセキュリティ対応（HIPAA、SOC2）

### 2. Deepgram
**料金体系**
- **無料枠**: $200クレジット
- **Standard**: $0.0043/分（$0.258/時間）
- **Growth Plan**: $4,000-10,000/年（前払い）
- **Nova-3**: $4.30/1000分

**特徴**
- 高速処理（低レイテンシ）
- リアルタイム対応
- カスタムモデル対応
- 50+言語対応
- エンタープライズ向け機能

### 3. Gladia
**料金体系**
- **無料枠**: 利用可能
- **Pay-as-you-go**: $0.00017/秒（$0.612/時間）
- **Enterprise**: カスタム価格

**特徴**
- Whisper ASR最適化版
- 話者分離
- 単語レベルタイムスタンプ
- バッチ処理対応
- 多言語対応

### 4. OpenAI Whisper API
**料金体系**
- **標準**: $0.006/分（$0.36/時間）

**特徴**
- 高精度
- 99言語対応
- オープンソースベース
- シンプルなAPI

## 詳細比較表

| サービス | 料金/時間 | 精度 | 言語数 | リアルタイム | 特殊機能 |
|---------|-----------|------|--------|-------------|----------|
| **AssemblyAI** | $0.12-0.47 | >93% | 多数 | ✅ | 感情分析、要約 |
| **Deepgram** | $0.258 | 高 | 50+ | ✅ | カスタムモデル |
| **Gladia** | $0.612 | 高 | 多数 | ✅ | Whisper最適化 |
| **OpenAI Whisper** | $0.36 | 最高 | 99 | ❌ | シンプル |

## コストパフォーマンス分析

### 1時間の音声処理コスト比較
1. **Deepgram**: $0.258（最安）
2. **OpenAI Whisper**: $0.36
3. **AssemblyAI Nano**: $0.12（速度重視）
4. **AssemblyAI Best**: $0.37（精度重視）
5. **Gladia**: $0.612（最高価格）

### 月間1000時間処理の場合
- **Deepgram**: $258
- **OpenAI Whisper**: $360
- **AssemblyAI**: $120-370
- **Gladia**: $612

## 精度・品質比較

### Word Error Rate (WER)
1. **OpenAI Whisper**: 最低WER（最高精度）
2. **AssemblyAI**: >93.3%精度
3. **Deepgram**: 高精度
4. **Gladia**: Whisper最適化版

### 言語対応
1. **OpenAI Whisper**: 99言語（最多）
2. **Deepgram**: 50+言語
3. **AssemblyAI**: 多言語対応
4. **Gladia**: 多言語対応

## 機能比較

### リアルタイム処理
- **AssemblyAI**: ✅ ($0.47/時間)
- **Deepgram**: ✅ (低レイテンシ)
- **Gladia**: ✅
- **OpenAI Whisper**: ❌

### 話者分離
- **AssemblyAI**: ✅
- **Deepgram**: ✅
- **Gladia**: ✅
- **OpenAI Whisper**: ❌

### 感情分析・要約
- **AssemblyAI**: ✅（LeMUR機能）
- **Deepgram**: 限定的
- **Gladia**: 限定的
- **OpenAI Whisper**: ❌

## 実装の複雑さ

### 簡単さランキング
1. **OpenAI Whisper**: 最もシンプル
2. **AssemblyAI**: 豊富なSDK
3. **Deepgram**: 中程度
4. **Gladia**: 中程度

### SDK・ライブラリ対応
- **AssemblyAI**: Python, JavaScript, Go, Java
- **Deepgram**: Python, JavaScript, Go, .NET
- **Gladia**: Python, JavaScript
- **OpenAI Whisper**: Python, JavaScript

## 用途別推奨

### 個人・小規模プロジェクト
**推奨**: AssemblyAI（無料枠$50）
- 理由: 豊富な無料枠、高機能

### コスト重視
**推奨**: Deepgram
- 理由: 最安価格、高品質

### 最高精度重視
**推奨**: OpenAI Whisper
- 理由: 業界最高精度、99言語対応

### リアルタイム処理
**推奨**: Deepgram
- 理由: 低レイテンシ、安定性

### 企業・大規模システム
**推奨**: AssemblyAI または Deepgram
- 理由: エンタープライズ機能、セキュリティ対応

## YouTube文字起こしでの適用

### 既存字幕なし動画への対応
1. **音声ダウンロード**: yt-dlp等を使用
2. **音声認識API呼び出し**: 上記サービスを利用
3. **結果整形**: タイムスタンプ付きテキスト生成

### 推奨フロー
```
1. youtube-transcript-api (無料)
   ↓ 失敗時
2. InnerTube API (無料)
   ↓ 失敗時
3. 音声認識API (有料)
   - 短時間動画: OpenAI Whisper
   - 長時間動画: Deepgram
   - 高機能要求: AssemblyAI
```

## 実装コスト試算

### 月間処理量別コスト（1000時間/月）

#### 小規模（100時間/月）
- **Deepgram**: $25.8
- **OpenAI Whisper**: $36
- **AssemblyAI**: $12-37
- **Gladia**: $61.2

#### 中規模（1000時間/月）
- **Deepgram**: $258
- **OpenAI Whisper**: $360
- **AssemblyAI**: $120-370
- **Gladia**: $612

#### 大規模（10000時間/月）
- **Deepgram**: $2,580（ボリューム割引あり）
- **OpenAI Whisper**: $3,600
- **AssemblyAI**: $1,200-3,700（ボリューム割引あり）
- **Gladia**: $6,120

## 結論・推奨事項

### 総合評価
1. **AssemblyAI**: バランス型、豊富な機能
2. **Deepgram**: コスト効率、高速処理
3. **OpenAI Whisper**: 最高精度、多言語
4. **Gladia**: 高価格だが高品質

### YouTube文字起こしでの推奨戦略

#### フォールバック順序
1. **無料手法**: youtube-transcript-api → InnerTube API
2. **有料手法**: Deepgram（コスト重視）または OpenAI Whisper（精度重視）

#### 実装優先度
1. **プロトタイプ**: AssemblyAI（無料枠活用）
2. **本格運用**: Deepgram（コスト効率）
3. **高品質要求**: OpenAI Whisper（最高精度）

### 注意事項
- 音声認識APIは音声ファイルが必要（YouTube音声ダウンロードが前提）
- 著作権・利用規約の確認が必要
- 処理時間は字幕取得より長い（数秒〜数分）
- ネットワーク帯域の考慮が必要

