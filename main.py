import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import time

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="Crypto Scanner Pro", layout="wide")

st.title("🛡️ رادار اختراق البولينجر باند (950/2)")
st.markdown("---")

# القائمة الجانبية للإعدادات
st.sidebar.header("⚙️ إعدادات الفحص")
timeframe = st.sidebar.selectbox("اختر الفريم الزمني", ['1h', '4h', '1d'], index=0)
limit_coins = st.sidebar.slider("عدد العملات للفحص", 10, 200, 100)

# دالة جلب البيانات والحساب
def fetch_and_analyze():
    exchange = ccxt.binance({'enableRateLimit': True})
    try:
        markets = exchange.load_markets()
        # اختيار أزواج USDT النشطة فقط
        symbols = [s for s in markets if '/USDT' in s and markets[s]['active']]
        symbols = symbols[:limit_coins] # تحديد العدد لتسريع الفحص
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, symbol in enumerate(symbols):
            try:
                status_text.text(f"🔍 جاري فحص: {symbol}")
                # جلب 1000 شمعة للحصول على دقة في مؤشر 950
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=1000)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # حساب البولينجر باند
                bb = ta.bbands(df['close'], length=950, std=2)
                
                last_price = df['close'].iloc[-1]
                lower_band = bb.iloc[-1][0] # Lower Band
                
                if last_price < lower_band:
                    diff = ((lower_band - last_price) / lower_band) * 100
                    results.append({
                        "العملة": symbol,
                        "السعر الحالي": f"{last_price:.4f}",
                        "خط البولينجر": f"{lower_band:.4f}",
                        "نسبة الكسر": f"{diff:.2f}%"
                    })
                
                # تحديث شريط التقدم
                progress_bar.progress((i + 1) / len(symbols))
                time.sleep(0.05) # لتجنب حظر بينانس (Rate Limit)
            except:
                continue
        
        status_text.empty()
        return results
    except Exception as e:
        st.error(f"خطأ في الاتصال ببينانس: {e}")
        return []

# زر التشغيل
if st.button("🚀 ابدأ فحص السوق الآن"):
    data = fetch_and_analyze()
    
    if data:
        st.success(f"✅ تم العثور على {len(data)} فرصة!")
        df_final = pd.DataFrame(data)
        # عرض الجدول بشكل أنيق
        st.dataframe(df_final, use_container_width=True)
    else:
        st.info("ℹ️ لا توجد عملات مخترقة للبولينجر 950 حالياً على هذا الفريم.")

st.sidebar.markdown("---")
st.sidebar.info("هذا الرادار يبحث عن العملات التي يتداول سعرها حالياً تحت خط البولينجر 950، وهي استراتيجية تعتمد على الارتداد القوي.")
