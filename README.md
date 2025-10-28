# みおりのブログ自動更新 — v2（OpenAI Only）

- **2000〜3000字** の本文目標
- **豆知識×3** と **学術メモ** を追加（やさしい説明＋研究名/年の軽い言及）
- “みおり”の世界観を維持した丁寧口調
- **キーワード自動ローテーション**（`data/keywords.txt` からランダム）／ `--keyword` で上書き

## 使い方
```bash
pip install -r requirements.txt
cp .env.example .env
python run.py --url "https://example.com"              # 自動キーワード
# or
python run.py --url "https://example.com" --keyword "ビタミンC"
```
出力: `dist/YYYYMMDD_HHMM_miori.html`

## 既存プロジェクトからの乗り換え
- `src/template_wp.html` / `src/prompt_master.txt` / `src/generate_v2.py` / `run.py` を置換
- `data/keywords.txt` を同梱

## .env
- `OPENAI_API_KEY` / `OPENAI_MODEL=gpt-4.1-mini`
- `DEFAULT_RAKUTEN_LINK`（任意）
- `TIMEZONE=Asia/Tokyo`
