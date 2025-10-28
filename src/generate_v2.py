import os, json, datetime as dt, re, random, requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

def load_keywords(path: str):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        items = [x.strip() for x in f.read().splitlines() if x.strip()]
    return items

def fetch_meta(url: str):
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0 (Miori-v2)"})
        r.raise_for_status()
        html = r.text
    except Exception:
        html = ""
    soup = BeautifulSoup(html, "lxml") if html else BeautifulSoup("", "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    ogd = soup.find("meta", attrs={"property":"og:description"}) or soup.find("meta", attrs={"name":"description"})
    desc = ogd["content"].strip() if ogd and ogd.get("content") else ""
    ogi = soup.find("meta", attrs={"property":"og:image"})
    img = ogi["content"].strip() if ogi and ogi.get("content") else ""
    return {"title":title, "description":desc, "image":img}

def build_variables(meta: dict, rakuten_link: str, keyword: str):
    today = dt.datetime.now().strftime("%Y/%m/%d")
    raw_title = meta.get("title","")
    product = re.sub(r"【.*?】|\|.*$", "", raw_title).strip()[:60] or "サンプル商品"
    sneak = "無理なく続ければ体感しやすいポイントがいくつかありました"
    return {
        "商品名": product,
        "ブランド名": "",
        "特集キーワード": keyword or "スキンケア",
        "悩みキーワード": keyword or "肌荒れ",
        "更新日": today,
        "継続日数": "14日",
        "推奨期間": "14日〜4週間",
        "主成分": "",
        "形状": "サプリ/美容液/クリーム など",
        "内容量": "",
        "使用タイミング": "朝/夜",
        "用量": "",
        "併用スキンケア": "",
        "失敗回避": "飲み忘れアラーム/パッチテスト など",
        "変化_日": "7",
        "感じた変化_日": "",
        "変化_週": "2",
        "感じた変化_週": "",
        "変化_月": "1",
        "感じた変化_月": "",
        "結論チラ見せ": sneak,
        "学術メモ本文": "",
        "豆知識1": "",
        "豆知識2": "",
        "豆知識3": "",
        "特徴_本品": "",
        "価格_本品": "¥◯◯◯〜（ポイント◯倍時）",
        "比較商品A_名称": "",
        "比較商品A_特徴": "",
        "比較商品A_成分量": "",
        "比較商品A_価格": "",
        "比較商品B_名称": "",
        "比較商品B_特徴": "",
        "比較商品B_成分量": "",
        "比較商品B_価格": "",
        "良い口コミ1": "",
        "良い口コミ1_属性": "",
        "良い口コミ2": "",
        "良い口コミ2_属性": "",
        "悪い口コミ1": "",
        "悪い口コミ2": "",
        "レビュー件数": "",
        "目安期間": "14日〜4週間",
        "注意成分": "ビタミンA/ピーリング/薬の飲み合わせ など",
        "商品画像URL1": meta.get("image",""),
        "商品画像URL2": meta.get("image",""),
        "楽天_最安候補": rakuten_link,
        "楽天_販売ページA": rakuten_link,
        "楽天_比較A": rakuten_link,
        "楽天_比較B": rakuten_link,
        "楽天_レビュー多い店舗": rakuten_link,
        "楽天_価格比較まとめ": rakuten_link
    }

def build_prompt(template_html: str, variables: dict):
    with open(os.path.join(os.path.dirname(__file__), "prompt_master.txt"), "r", encoding="utf-8") as f:
        master = f.read()
    return master.replace("{{TEMPLATE_HTML}}", template_html)\
                 .replace("{{VARIABLES_JSON}}", json.dumps(variables, ensure_ascii=False))

def call_openai(prompt: str, model: str, max_tokens: int = 3600) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system","content":"指定以外の文字を出さず、HTML本文のみを返します。本文が2000〜3000字になるように調整し、豆知識×3と学術メモを必ず含めてください。"},
            {"role":"user","content":prompt}
        ],
        temperature=0.5,
        max_tokens=max_tokens
    )
    return resp.choices[0].message.content.strip()

def main(url: str, keyword_override: str = ""):
    # Load env
    from dotenv import load_dotenv
    load_dotenv()

    # Meta
    meta = fetch_meta(url)

    # Keyword rotation
    kw = keyword_override.strip()
    if not kw:
        pool = load_keywords(os.path.join(os.path.dirname(__file__), "..", "data", "keywords.txt"))
        if pool:
            kw = random.choice(pool)

    # Variables
    rakuten = os.getenv("DEFAULT_RAKUTEN_LINK","")
    variables = build_variables(meta, rakuten, kw)

    # Prompt
    with open(os.path.join(os.path.dirname(__file__), "template_wp.html"), "r", encoding="utf-8") as f:
        template_html = f.read()
    prompt = build_prompt(template_html, variables)

    # OpenAI
    model = os.getenv("OPENAI_MODEL","gpt-4.1-mini")
    html = call_openai(prompt, model)

    # Save
    out_dir = os.path.join(os.path.dirname(__file__), "..", "dist")
    os.makedirs(out_dir, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M")
    path = os.path.join(out_dir, f"{ts}_miori.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] saved:", path)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--keyword", default="")
    a = p.parse_args()
    main(a.url, a.keyword)
