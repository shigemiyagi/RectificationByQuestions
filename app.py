import streamlit as st
import swisseph as swe
from datetime import datetime, time, timezone, timedelta
import os

# --- 定数データ ---

# 天体暦ファイルのパス
EPHE_PATH = 'ephe'
# サイン名
SIGN_NAMES = ["牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座", "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"]
# エレメント
ELEMENTS = {'火': ["牡羊座", "獅子座", "射手座"], '地': ["牡牛座", "乙女座", "山羊座"], '風': ["双子座", "天秤座", "水瓶座"], '水': ["蟹座", "蠍座", "魚座"]}
# クオリティ
QUALITIES = {'活動': ["牡羊座", "蟹座", "天秤座", "山羊座"], '不動': ["牡牛座", "獅子座", "蠍座", "水瓶座"], '柔軟': ["双子座", "乙女座", "射手座", "魚座"]}
# 天体ID
PLANET_IDS = {'太陽': swe.SUN, '月': swe.MOON, '水星': swe.MERCURY, '金星': swe.VENUS, '火星': swe.MARS, '木星': swe.JUPITER, '土星': swe.SATURN, '天王星': swe.URANUS, '海王星': swe.NEPTUNE}

# 都道府県の緯度経度データ
PREFECTURE_DATA = {
    "北海道": {"lat": 43.064, "lon": 141.348}, "青森県": {"lat": 40.825, "lon": 140.741},
    "岩手県": {"lat": 39.704, "lon": 141.153}, "宮城県": {"lat": 38.269, "lon": 140.872},
    "秋田県": {"lat": 39.719, "lon": 140.102}, "山形県": {"lat": 38.240, "lon": 140.364},
    "福島県": {"lat": 37.750, "lon": 140.468}, "茨城県": {"lat": 36.342, "lon": 140.447},
    "栃木県": {"lat": 36.566, "lon": 139.884}, "群馬県": {"lat": 36.391, "lon": 139.060},
    "埼玉県": {"lat": 35.857, "lon": 139.649}, "千葉県": {"lat": 35.605, "lon": 140.123},
    "東京都": {"lat": 35.690, "lon": 139.692}, "神奈川県": {"lat": 35.448, "lon": 139.643},
    "新潟県": {"lat": 37.902, "lon": 139.023}, "富山県": {"lat": 36.695, "lon": 137.211},
    "石川県": {"lat": 36.594, "lon": 136.626}, "福井県": {"lat": 36.065, "lon": 136.222},
    "山梨県": {"lat": 35.664, "lon": 138.568}, "長野県": {"lat": 36.651, "lon": 138.181},
    "岐阜県": {"lat": 35.391, "lon": 136.722}, "静岡県": {"lat": 34.977, "lon": 138.383},
    "愛知県": {"lat": 35.180, "lon": 136.907}, "三重県": {"lat": 34.730, "lon": 136.509},
    "滋賀県": {"lat": 35.005, "lon": 135.869}, "京都府": {"lat": 35.021, "lon": 135.756},
    "大阪府": {"lat": 34.686, "lon": 135.520}, "兵庫県": {"lat": 34.691, "lon": 135.183},
    "奈良県": {"lat": 34.685, "lon": 135.833}, "和歌山県": {"lat": 34.226, "lon": 135.168},
    "鳥取県": {"lat": 35.504, "lon": 134.238}, "島根県": {"lat": 35.472, "lon": 133.051},
    "岡山県": {"lat": 34.662, "lon": 133.934}, "広島県": {"lat": 34.396, "lon": 132.459},
    "山口県": {"lat": 34.186, "lon": 131.471}, "徳島県": {"lat": 34.066, "lon": 134.559},
    "香川県": {"lat": 34.340, "lon": 134.043}, "愛媛県": {"lat": 33.842, "lon": 132.765},
    "高知県": {"lat": 33.560, "lon": 133.531}, "福岡県": {"lat": 33.607, "lon": 130.418},
    "佐賀県": {"lat": 33.249, "lon": 130.299}, "長崎県": {"lat": 32.745, "lon": 129.874},
    "熊本県": {"lat": 32.790, "lon": 130.742}, "大分県": {"lat": 33.238, "lon": 131.613},
    "宮崎県": {"lat": 31.911, "lon": 131.424}, "鹿児島県": {"lat": 31.560, "lon": 130.558},
    "沖縄県": {"lat": 26.212, "lon": 127.681}
}

# ▼▼▼ 変更点1：QUESTIONSのデータ構造を変更。「reason」を「trait」に。▼▼▼
QUESTIONS = [
    {
        "q": "質問1：新しいプロジェクトを始める時、あなたのスタイルに最も近いのは？",
        "a": {
            "a": "「まずやってみよう！」と、すぐに行動を開始する。",
            "b": "成功までの道のりを詳細に計画し、準備を固めてから始める。",
            "c": "周囲の意見を聞きながら、柔軟にやり方を変えていく。",
            "d": "なぜそれが必要なのか、という理念や目的が明確になるまで動かない。"
        },
        "map": {
            "a": {"type": "quality", "value": "活動", "target": "全体", "weight": 2, "trait": "物事を率先して始める主導性"},
            "b": {"type": "quality", "value": "不動", "target": "全体", "weight": 2, "trait": "一度決めたことを粘り強く続ける持続力"},
            "c": {"type": "quality", "value": "柔軟", "target": "全体", "weight": 2, "trait": "状況に応じて対応を変える順応性"},
            "d": {"type": "emphasis", "value": "太陽", "target": "天体", "weight": 1, "trait": "行動の基盤となる理念や目的意識"}
        }
    },
    {
        "q": "質問2：大きな問題に直面した時、最初にとる行動は？",
        "a": {
            "a": "信頼できる友人数人に相談し、意見を求める。",
            "b": "誰にも話さず、一人でじっくりと考え、解決策を探す。",
            "c": "感情的になり、まずはその気持ちを誰かに聞いてもらいたくなる。",
            "d": "問題から一旦離れ、趣味や別の作業に没頭して気分転換する。"
        },
        "map": {
            "a": {"type": "element", "value": "風", "target": "月", "weight": 3, "trait": "客観的な意見を求めるコミュニケーション重視の性質"},
            "b": {"type": "element", "value": "地", "target": "月", "weight": 3, "trait": "現実的な解決策を求める自己完結的な性質"},
            "c": {"type": "element", "value": "水", "target": "月", "weight": 3, "trait": "感情の共有と共感を求める情緒的な性質"},
            "d": {"type": "element", "value": "火", "target": "月", "weight": 3, "trait": "行動を通じてストレスを解消する直情的な性質"}
        }
    },
        {
        "q": "質問3：理想的な休日の過ごし方は？",
        "a": {
            "a": "大勢の友人と集まり、賑やかにパーティーやイベントを楽しむ。",
            "b": "ごく親しい友人やパートナーと、二人きりで深い語らいをする。",
            "c": "一人で趣味に没頭したり、家でゆっくりと過ごしたりする。",
            "d": "新しい場所へ出かけたり、セミナーに参加したりして知的な刺激を求める。"
        },
        "map": {
            "a": {"type": "element", "value": "火", "target": "ASC", "weight": 2, "trait": "エネルギッシュで社交的な第一印象"},
            "b": {"type": "sign_emphasis", "value": "蠍座", "target": "ASC", "weight": 2, "trait": "深く限定的な人間関係を好む性質"},
            "c": {"type": "element", "value": "地", "target": "ASC", "weight": 2, "trait": "穏やかで落ち着いた第一印象"},
            "d": {"type": "sign_emphasis", "value": "射手座", "target": "ASC", "weight": 2, "trait": "知的好奇心が旺盛で自由を好む性質"}
        }
    },
    {
        "q": "質問4：人生の大きな決断をする時、最終的な決め手は？",
        "a": {
            "a": "論理的なメリット・デメリットを比較検討した上での結論。",
            "b": "「なんとなくこちらの方が良い気がする」という直感やフィーリング。",
            "c": "将来の安定や経済的な安心感が得られるかどうか。",
            "d": "自分の理想や「こうありたい」という夢に近づけるかどうか。"
        },
        "map": {
            "a": {"type": "emphasis", "value": "水星", "target": "天体", "weight": 2, "trait": "論理と思考を重んじる性質"},
            "b": {"type": "emphasis", "value": "月", "target": "天体", "weight": 2, "trait": "感情や直感を信頼する性質"},
            "c": {"type": "emphasis", "value": "土星", "target": "天体", "weight": 2, "trait": "現実と安定を最優先する性質"},
            "d": {"type": "emphasis", "value": "海王星", "target": "天体", "weight": 2, "trait": "夢や理想を追い求める性質"}
        }
    },
    {
        "q": "質問5：あなたが最も「許せない」と感じることは？",
        "a": {
            "a": "裏切られること、秘密を軽々しく扱われること。",
            "b": "不誠実な態度、その場しのぎの嘘をつかれること。",
            "c": "優柔不断な態度で、物事をなかなか決めないこと。",
            "d": "非効率で、無駄が多いやり方を強要されること。"
        },
        "map": {
            "a": {"type": "sign_emphasis", "value": "蠍座", "target": "太陽/月/ASC", "weight": 3, "trait": "深い信頼関係を裏切られることへの強い反発"},
            "b": {"type": "sign_emphasis", "value": "山羊座", "target": "太陽/月/ASC", "weight": 3, "trait": "誠実さと責任感を重んじる価値観"},
            "c": {"type": "sign_emphasis", "value": "牡羊座", "target": "太陽/月/ASC", "weight": 3, "trait": "迅速な決断と行動を尊重する価値観"},
            "d": {"type": "sign_emphasis", "value": "乙女座", "target": "太陽/月/ASC", "weight": 3, "trait": "効率性と完璧さを求める価値観"}
        }
    },
    {
        "q": "質問6：他人との意見対立が起きた時、あなたの態度は？",
        "a": {
            "a": "自分の正しさを主張し、相手を説得しようと試みる。",
            "b": "その場の調和を優先し、自分の意見を一旦抑える。",
            "c": "冷静に議論し、お互いの妥協点を探る。",
            "d": "感情的になり、その場から離れたくなる。"
        },
        "map": {
            "a": {"type": "element", "value": "火", "target": "火星", "weight": 2, "trait": "自己主張が強く、闘争を恐れない性質"},
            "b": {"type": "sign_emphasis", "value": "天秤座", "target": "火星", "weight": 2, "trait": "対立を避け、調和的な解決を望む性質"},
            "c": {"type": "element", "value": "風", "target": "火星", "weight": 2, "trait": "言葉による論理的な議論で解決しようとする性質"},
            "d": {"type": "element", "value": "水", "target": "火星", "weight": 2, "trait": "対立において感情が優先される繊細な性質"}
        }
    },
    {
        "q": "質問7：あなたにとって「美しさ」とは？",
        "a": {
            "a": "機能的で洗練された、無駄のないデザイン。",
            "b": "自然の素材や、手仕事の温かみが感じられるもの。",
            "c": "華やかで、人の心を高揚させるドラマティックなもの。",
            "d": "儚さや、不完全さの中に宿る趣。"
        },
        "map": {
            "a": {"type": "sign_emphasis", "value": "乙女座", "target": "金星", "weight": 2, "trait": "完璧で機能的な美を好む感性"},
            "b": {"type": "sign_emphasis", "value": "牡牛座", "target": "金星", "weight": 2, "trait": "五感に心地よい自然な美を好む感性"},
            "c": {"type": "sign_emphasis", "value": "獅子座", "target": "金星", "weight": 2, "trait": "ドラマティックで自己表現豊かな美を好む感性"},
            "d": {"type": "sign_emphasis", "value": "魚座", "target": "金星", "weight": 2, "trait": "幻想的で情緒的な美を好む感性"}
        }
    },
    {
        "q": "質問8：仕事において、最もやりがいを感じる瞬間は？",
        "a": {
            "a": "チームで一体となり、大きな目標を達成した時。",
            "b": "自分の専門スキルや知識を深め、完璧な仕事ができた時。",
            "c": "誰かの役に立っている、社会に貢献していると実感した時。",
            "d": "高い評価を得て、自分の地位や収入が上がった時。"
        },
        "map": {
            "a": {"type": "house_emphasis", "value": 11, "target": "MC", "weight": 2, "trait": "仲間との連帯感を重視する価値観"},
            "b": {"type": "sign_emphasis", "value": "乙女座", "target": "MC", "weight": 2, "trait": "専門性を極める職人気質の価値観"},
            "c": {"type": "sign_emphasis", "value": "魚座", "target": "MC", "weight": 2, "trait": "奉仕と貢献を重視する価値観"},
            "d": {"type": "sign_emphasis", "value": "山羊座", "target": "MC", "weight": 2, "trait": "社会的な成功と評価を重視する価値観"}
        }
    },
    {
        "q": "質問9：あなたの人生観に最も近い考え方は？",
        "a": {
            "a": "人生は一度きり。常に新しいことに挑戦し、自分を成長させたい。",
            "b": "運命や見えない力は存在する。流れに身を任せることも大切だ。",
            "c": "努力は必ず報われる。地道な積み重ねが確かな未来を創る。",
            "d": "人生は楽しむためにある。ユーモアと楽観性を忘れたくない。"
        },
        "map": {
            "a": {"type": "emphasis", "value": "木星", "target": "天体", "weight": 2, "trait": "自己成長と挑戦を求める人生観"},
            "b": {"type": "emphasis", "value": "海王星", "target": "天体", "weight": 2, "trait": "運命や精神性を重んじる人生観"},
            "c": {"type": "emphasis", "value": "土星", "target": "天体", "weight": 2, "trait": "努力と現実を重んじる人生観"},
            "d": {"type": "sign_emphasis", "value": "射手座", "target": "全体", "weight": 2, "trait": "楽観性と自由を求める人生観"}
        }
    },
    {
        "q": "質問10：大きな失敗をした時、どう乗り越えますか？",
        "a": {
            "a": "自分の力不足を痛感し、原因を徹底的に分析して次に活かす。",
            "b": "信頼できる人に話を聞いてもらい、励ましてもらうことで立ち直る。",
            "c": "「これも経験だ」と気持ちを切り替え、あまり引きずらない。",
            "d": "しばらく落ち込むが、時間が経てば自然と忘れていく。"
        },
        "map": {
            "a": {"type": "emphasis", "value": "土星", "target": "天体", "weight": 2, "trait": "失敗を分析し、教訓を得ようとする回復スタイル"},
            "b": {"type": "emphasis", "value": "月", "target": "天体", "weight": 2, "trait": "他者との共感を通じて回復するスタイル"},
            "c": {"type": "emphasis", "value": "木星", "target": "天体", "weight": 2, "trait": "楽観的に気持ちを切り替えて回復するスタイル"},
            "d": {"type": "quality", "value": "柔軟", "target": "全体", "weight": 2, "trait": "状況を受け入れ、自然に立ち直っていく回復スタイル"}
        }
    },
    {
        "q": "質問11：あなたの体型や第一印象について、人からよく言われることに最も近いものは？",
        "a": {
            "a": "スラリとして中性的、シャープな印象",
            "b": "がっしりしていて、落ち着いた印象",
            "c": "ふっくらとして、優しく親しみやすい印象",
            "d": "筋肉質で、エネルギッシュな印象"
        },
        "map": {
            "a": {"type": "multi_sign_emphasis", "value": ["双子座", "乙女座", "水瓶座"], "target": "ASC", "weight": 3, "trait": "知的でシャープな第一印象"},
            "b": {"type": "multi_sign_emphasis", "value": ["牡牛座", "山羊座"], "target": "ASC", "weight": 3, "trait": "落ち着きと安定感のある第一印象"},
            "c": {"type": "multi_sign_emphasis", "value": ["蟹座", "魚座"], "target": "ASC", "weight": 3, "trait": "優しく親しみやすい第一印象"},
            "d": {"type": "multi_sign_emphasis", "value": ["牡羊座", "獅子座"], "target": "ASC", "weight": 3, "trait": "活発でエネルギッシュな第一印象"}
        }
    }
]

# --- 占星術計算関数 ---

def get_jd(dt_obj):
    dt_utc = dt_obj.replace(tzinfo=timezone(timedelta(hours=9))).astimezone(timezone.utc)
    return swe.utc_to_jd(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second, 1)[1]

def get_sign(degree):
    return SIGN_NAMES[int(degree / 30)]

def calculate_chart(jd, lat, lon):
    chart = {'planets': {}, 'angles': {}, 'elements': {'火': 0, '地': 0, '風': 0, '水': 0}, 'qualities': {'活動': 0, '不動': 0, '柔軟': 0}}
    iflag = swe.FLG_SWIEPH
    for name, pid in PLANET_IDS.items():
        pos = swe.calc_ut(jd, pid, iflag)[0][0]
        sign = get_sign(pos)
        chart['planets'][name] = sign
        for el, signs in ELEMENTS.items():
            if sign in signs: chart['elements'][el] += 1
        for q, signs in QUALITIES.items():
            if sign in signs: chart['qualities'][q] += 1
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')
    chart['angles']['ASC'] = get_sign(ascmc[0])
    chart['angles']['MC'] = get_sign(ascmc[1])
    return chart

# ▼▼▼ 変更点2：根拠を詳細に生成するようscore_chart関数を全面的に改修 ▼▼▼
def score_chart(chart, answers):
    score = 0
    reasons = []

    for i, ans_key in enumerate(answers):
        if not ans_key: continue
        
        q_map = QUESTIONS[i]["map"][ans_key]
        map_type = q_map["type"]
        map_value = q_map["value"]
        map_target = q_map["target"]
        map_weight = q_map["weight"]
        trait_desc = q_map["trait"]

        reason_text = ""
        is_match = False

        # --- マッチングロジックと根拠生成 ---
        if map_type == "quality":
            if chart['qualities'][map_value] >= 4:
                is_match = True
                reason_text = f"あなたの「{trait_desc}」という回答は、物事への取り組み方における**{map_value}宮**の性質を強く示唆します。この時間帯のホロスコープでは、天体の多くが{map_value}宮に集中しており、あなたの性格と一致します。"
        
        elif map_type == "element":
            target_planet_sign = chart['planets'].get(map_target) or chart['angles'].get(map_target)
            if target_planet_sign and target_planet_sign in ELEMENTS[map_value]:
                is_match = True
                if map_target == "月":
                    reason_text = f"あなたの「{trait_desc}」という回答は、感情の核である**月**の性質を反映します。この時間帯の月は**{map_value}のエレメント**に属する**{target_planet_sign}**にあり、あなたの情緒的な特徴と強く結びつきます。"
                else: #火星やASCなど
                    reason_text = f"あなたの「{trait_desc}」という回答は、**{map_target}**が象徴する性質と関連します。この時間帯の{map_target}は**{map_value}のエレメント**に属する**{target_planet_sign}**にあり、あなたの行動様式と一致します。"

        elif map_type == "sign_emphasis" or map_type == "multi_sign_emphasis":
            target_signs = map_value if isinstance(map_value, list) else [map_value]
            # ターゲット（太陽、月、ASCなど）をチェック
            matched_targets = []
            if "太陽" in map_target and chart['planets']['太陽'] in target_signs: matched_targets.append(f"太陽が{chart['planets']['太陽']}にあること")
            if "月" in map_target and chart['planets']['月'] in target_signs: matched_targets.append(f"月が{chart['planets']['月']}にあること")
            if "ASC" in map_target and chart['angles']['ASC'] in target_signs: matched_targets.append(f"アセンダントが{chart['angles']['ASC']}にあること")
            if "MC" in map_target and chart['angles']['MC'] in target_signs: matched_targets.append(f"MCが{chart['angles']['MC']}にあること")
            if "金星" in map_target and chart['planets']['金星'] in target_signs: matched_targets.append(f"金星が{chart['planets']['金星']}にあること")
            if "火星" in map_target and chart['planets']['火星'] in target_signs: matched_targets.append(f"火星が{chart['planets']['火星']}にあること")
            if "全体" in map_target and (chart['angles']['ASC'] in target_signs or chart['planets']['太陽'] in target_signs): matched_targets.append(f"太陽またはアセンダントが{'/'.join(target_signs)}にあること")
            
            if matched_targets:
                is_match = True
                reason_text = f"あなたの「{trait_desc}」という回答は、**{'/'.join(target_signs)}**の価値観を強く反映しています。この時間帯のホロスコープでは、{'、'.join(matched_targets)}が、その性質を裏付けています。"
        
        elif map_type == "emphasis" or map_type == "house_emphasis":
             # 簡略化ロジック：ここでは特定の天体・テーマの重要性を示す根拠として記述
             is_match = True # このタイプは常に加点
             reason_text = f"あなたの「{trait_desc}」という回答は、占星術で**「{map_value}」**が象徴するテーマが、あなたの人生で重要であることを示唆しています。この時間帯のホロスコープは、そのテーマを強調する配置を持っています。"


        if is_match:
            score += map_weight
            reasons.append(reason_text)
            
    return score, reasons

# --- Streamlit UI ---

st.set_page_config(page_title="心理占星術レクティフィケーション", page_icon="🔮")
st.title("🔮 心理占星術レクティフィケーション")
st.write("11の質問に答えることで、あなたの性格から最も可能性の高い出生時刻を推定します。")

st.header("1. 基本情報を入力してください")
col1, col2 = st.columns(2)
birth_date = col1.date_input("📅 生年月日", min_value=datetime(1900, 1, 1), max_value=datetime(2099, 12, 31), value=datetime(1990, 1, 1))
birth_pref = col2.selectbox("📍 出生都道府県", options=list(PREFECTURE_DATA.keys()), index=12)

st.header("2. 心理テスト")
st.info("深く考えず、直感的にお答えください。")

answers = []
for i, q_data in enumerate(QUESTIONS):
    st.subheader(q_data["q"])
    ans = st.radio("選択肢:", list(q_data["a"].values()), key=f"q{i}", index=None, horizontal=True)
    ans_key = next((key for key, value in q_data["a"].items() if value == ans), None)
    answers.append(ans_key)

st.markdown("---")

if st.button("鑑定する 🚀", type="primary"):
    if None in answers:
        st.warning("すべての質問に回答してください。")
    else:
        if not os.path.exists(EPHE_PATH):
            st.error(f"天体暦ファイルが見つかりません。`{EPHE_PATH}` フォルダを配置してください。")
            st.stop()
        swe.set_ephe_path(EPHE_PATH)

        coords = PREFECTURE_DATA[birth_pref]
        lat, lon = coords["lat"], coords["lon"]
        
        candidate_times = []
        
        progress_text = "出生時刻の候補を検証中... (00:00)"
        bar = st.progress(0, text=progress_text)

        total_steps = 24 * 4
        for i, minute_of_day in enumerate(range(0, 24 * 60, 15)):
            hour = minute_of_day // 60
            minute = minute_of_day % 60
            candidate_time = time(hour, minute)
            bar.progress((i + 1) / total_steps, text=f"出生時刻の候補を検証中... ({candidate_time.strftime('%H:%M')})")
            birth_dt = datetime.combine(birth_date, candidate_time)
            jd = get_jd(birth_dt)
            chart = calculate_chart(jd, lat, lon)
            score, reasons = score_chart(chart, answers)
            if score > 0:
                candidate_times.append({"time": candidate_time, "score": score, "reasons": reasons})

        bar.empty()

        st.header("鑑定結果")
        if not candidate_times:
            st.warning("回答に一致する有力な出生時刻の候補は見つかりませんでした。")
        else:
            sorted_candidates = sorted(candidate_times, key=lambda x: x['score'], reverse=True)
            max_score = sorted_candidates[0]['score'] if sorted_candidates else 1
            
            st.success(f"あなたの性格に最も一致する可能性の高い出生時刻は以下の通りです。")

            for i, candidate in enumerate(sorted_candidates[:5]):
                percentage = (candidate['score'] / max_score * 100)
                
                with st.container(border=True):
                    st.subheader(f"第 {i+1} 位： **{candidate['time'].strftime('%H:%M')} ごろ**")
                    st.progress(int(percentage), text=f"可能性: {percentage:.0f}%")
                    st.markdown("**▼ 西洋占星術の観点からの根拠**")
                    unique_reasons = sorted(list(set(candidate['reasons'])))
                    for reason in unique_reasons:
                        st.markdown(f"- {reason}")
