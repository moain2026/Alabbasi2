# WebviewActivity — شاشة العرض المختلطة

> **المصدر:** `com.egy.webpaymentapp.Screens.web.WebviewActivity`
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/Screens/web/WebviewActivity.java`
> **عدد الأسطر:** 461 سطر
> **الـ Layout:** `R.layout.activity_web_view` (مُتوقَّع)
> **الدور:** WebView يعرض صفحات HTML من الخادم أو من الـ assets المحلية، مع جسر JavaScript (`mobile`) للتواصل مع Android.

---

## 1. مكوّنات الواجهة

| المتغير | View ID | النوع | الوظيفة |
|---------|---------|-------|---------|
| `u` (static) | `R.id.webview` | `WebView` | العرض الرئيسي |
| `x` (static) | — | `WebView` | WebView ثانوي للطباعة (يُنشَأ في `b/c.java`) |
| `y` (static) | `R.id.savePdfBtn` | `Button` | حفظ كـ PDF (يظهر فقط لـ OP_TYP=3 + URL يحوي `&action=prntInv`) |
| `v` (static) | — | `String` | الـ URL المُحمَّل |
| `w` (static) | — | `String` | إستخدام غير واضح (cache؟) |
| `r` | — | `int` | `OP_TYP` (1/2/3) |
| `q` | — | `com.egy.webpaymentapp.BixlonPrinterManger.a` | مدير الطابعة (فقط لـ OP_TYP=1) |
| `s` | — | `PrintJob` | مهمة الطباعة الحالية |
| `t` | — | `boolean` | علم: هل يجب تتبع PrintJob في onResume |

⚠️ **استخدام `static` بكثرة** ⇒ مشاكل في الـ memory leak و في multi-instance.

---

## 2. الـ Intent Extras المُتوقَّعة

من السطور 424-427:

```java
public void y() {
  // ...
  v = getIntent().getExtras().getString("page");       // الـ URL أو إسم صفحة محلية
  r().n(getIntent().getExtras().getString("title"));  // عنوان الـ ActionBar
  this.r = getIntent().getExtras().getInt("OP_TYP");  // 1/2/3
}
```

| Extra | الإستخدام |
|-------|-----------|
| `page` | URL يُحمَّل (مثل `file:///android_asset/web/paymentList.html` أو `https://abbasiy.yedns.org:.../reports`) |
| `title` | يُعرَض في الـ ActionBar |
| `OP_TYP` | يُحدِّد سلوك الطباعة + Bridge methods |

---

## 3. ⚠️ إعدادات WebView الخطرة (السطور 431-440)

```java
u = (WebView) findViewById(R.id.webview);
u.getSettings().setDomStorageEnabled(true);
u.getSettings().setAllowFileAccess(true);                  // ⚠️
u.getSettings().setAllowContentAccess(true);
u.clearCache(true);
u.getSettings().setDatabaseEnabled(true);
u.getSettings().setDomStorageEnabled(true);
u.getSettings().setAllowUniversalAccessFromFileURLs(true); // 🔴🔴🔴
u.getSettings().setJavaScriptEnabled(true);                // ⚠️
u.addJavascriptInterface(new i(this, this), "mobile");    // 🔴 الجسر
```

### تحليل كل إعداد:

| الإعداد | القيمة | الخطر |
|---------|--------|------|
| `setDomStorageEnabled(true)` | ✅ | لازم لـ localStorage |
| `setAllowFileAccess(true)` | 🟡 | يسمح بقراءة `file://` URIs |
| `setAllowContentAccess(true)` | 🟡 | يسمح بـ content:// |
| `setDatabaseEnabled(true)` | 🟡 | يفعِّل WebSQL (deprecated) |
| **`setAllowUniversalAccessFromFileURLs(true)`** | 🔴🔴🔴 | يسمح لـ `file://` page بـ XHR إلى أي origin ⇒ **CSRF + Data exfiltration** |
| `setJavaScriptEnabled(true)` | 🟡 | لازم لكن خطر |
| **`addJavascriptInterface(..., "mobile")`** | 🔴🔴 | يفتح 6 طرق Android إلى JavaScript |
| `clearCache(true)` | ✅ | بدلاً من خفي ⇒ يضمن آخر نسخة لكن لا يوفر offline |

### السيناريو الإستغلالي (Exploit)
1. مهاجم يصل إلى الخادم (MITM ممكن لأن `c.b.a.f.d` empty TrustManager).
2. يحقن HTML/JS في صفحة `paymentList.html` أو `reports`.
3. الـ JS يستدعي `mobile.ShareReport(...)`, `mobile.printPdfReport(...)`, إلخ.
4. الـ JS يستدعي `XMLHttpRequest` إلى `file:///data/data/com.egy.webpaymentapp/databases/...` ⇒ يقرأ SharedPreferences + ينقلها لخادم خارجي.
5. ⇒ سرقة Token + معلومات الزبائن.

⇒ راجع `05_webview_bridge/01_bridge_overview.md` للجسر الكامل.

---

## 4. WebChromeClient (السطور 48-130 تقريباً)

```java
public class a extends WebChromeClient {
  // 1. Geolocation: يوافق تلقائياً
  public void onGeolocationPermissionsShowPrompt(String origin, Callback cb) {
    cb.invoke(origin, true, false);  // ⚠️ يعطي صلاحية GPS لأي origin بدون سؤال!
  }
  
  // 2. JS alert: AlertDialog مع زر OK
  public boolean onJsAlert(WebView v, String url, String msg, JsResult result) {
    show AlertDialog with "alert_title" + msg + OK button
    result.confirm();
    return true;
  }
  
  // 3. JS confirm: AlertDialog مع OK/Cancel
  public boolean onJsConfirm(...) {
    show AlertDialog with confirm/cancel
    onConfirm → result.confirm(); onCancel → result.cancel()
  }
  
  // 4. JS prompt: غير مُعالَج → fallback
  public boolean onJsPrompt(...) { /* … */ }
}
```

⚠️ **مخاطر:**
- **Geolocation auto-allow:** أي صفحة تطلب موقع GPS تحصل عليه ⇒ tracking.
- **JS alerts غير سياقية:** عنوان "تنبيه" دائماً ⇒ مهاجم يستطيع تنفيذ phishing.

---

## 5. WebViewClient (الكلاس `h` — ملف منفصل)

من السطور 451-452:
```java
u.setWebViewClient(new h(this, u, null));
u.setWebChromeClient(new a());
```

⇒ `h` معرَّف في `web/h.java` (151 سطر) — يحوي **التجاوز الحرج للـ SSL** (الأسطر 134-137 — راجع `04_screens_flow/05_webview_screen.md` لكن **هنا** في `WebviewActivity`):

```java
// في h.java
public void onReceivedSslError(WebView v, SslErrorHandler handler, SslError error) {
  handler.proceed();   // 🔴 يقبل أي شهادة SSL — حتى المُزيَّفة
}
```

⇒ **MITM ممكن** لأي WebView page.

---

## 6. الدوال الأساسية

### 6.1 `y()` — تهيئة الواجهة (السطور 418-460)

```text
1. إعداد ActionBar (لا عنوان، Home up)
2. قراءة Intent extras: page, title, OP_TYP
3. إنشاء BixlonPrinterManger إذا OP_TYP==1
4. إنشاء WebView + إعدادات خطرة
5. ربط الـ JavaScript Interface "mobile"
6. زر savePdfBtn (مخفي بشكل افتراضي)
7. إذا OP_TYP==3 && URL يحوي "&action=prntInv":
       savePdfBtn ظاهر
       إخفاء ActionBar home up
8. تعيين WebViewClient + WebChromeClient
9. تأخير قصير (10ms) إذا URL ليس file:// ⇒ ثم تحميل
```

### 6.2 `onCreateOptionsMenu()` — قائمة الطباعة

```java
inflate(R.menu.connect_printer_menu, menu);
// يضيف عناصر:
// - action_connect (اتصال طابعة)
// - printer_seting (إعدادات الطابعة)
```

### 6.3 `onResume()` — تتبع PrintJob (السطور 365-392)

```java
public void onResume() {
  if (this.s == null || !this.t) return;
  
  String status;
  if (s.isCompleted())   status = "Completed";
  else if (s.isStarted()) status = "isStarted";
  else if (s.isBlocked()) status = "isBlocked";
  else if (s.isCancelled()) status = "isCancelled";
  else if (s.isFailed())  status = "isFailed";
  else if (s.isQueued())  status = "isQueued";
  
  Toast.makeText(this, status, SHORT).show();
  this.t = false;
}
```

⚠️ **مخاطر UX:**
- Toast لحالة Print غير مفيدة للمستخدم العادي (تعابير إنجليزية تقنية).
- لا فعل ينتج عن الـ status (مثل إعادة المحاولة عند Failed).

### 6.4 `onStart()` / `onStop()` — إعادة اتصال الطابعة

```java
public void onStart() {
  if (q != null) q.h();   // resume printer
}
public void onStop() {
  if (q != null) q.i();   // disconnect printer
}
```

---

## 7. تدفُّق تحميل الصفحة

```text
WebviewActivity.onCreate
       ↓
y() ⇒ إعداد كل شيء
       ↓
new Handler().postDelayed(new d(), delay);
       ↓ (d() غير مرئي في القراءة لكن من السياق)
       ↓
u.loadUrl(v);   // v = page URL
       ↓
WebChromeClient.onJsAlert/Confirm إذا JS طلب
       ↓
WebViewClient.shouldOverrideUrlLoading للـ navigation
       ↓ (في h.java)
       ↓
الـ HTML JavaScript:
   const data = mobile.GetPaymentsRequest();  // ← الجسر
       ↓
i.java.GetPaymentsRequest() يُستدعى في Native
       ↓ يُجهز payload + يستدعي WebviewActivity.v()
       ↓
v() ⇒ POST /api/Payment/GetPaymentsReportData
       ↓
في الإستجابة:
   webview.loadUrl("javascript:showpayList('" + JSON + "');");
       ↓
الـ JS function showpayList() يعرض البيانات
```

---

## 8. الصفحات المُستضافة المُكتشَفة (من `_raw_extracted/`)

| الملف | الإستخدام | مصدر البيانات |
|------|----------|---------------|
| `paymentList.html` | عرض قائمة الدفعات | `mobile.GetPaymentsRequest()` ⇒ JSON من Backend |
| `readinglist.html` | عرض قائمة القراءات | `mobile.GetReadingDataRequest()` ⇒ JSON من Backend |
| `vReport.html` | عرض تقرير دفعة واحدة | localStorage (مكتوب بواسطة Java قبل التحميل) |
| `default_error_page.html` | صفحة خطأ | استاتيك |

### 8.1 ملاحظة على `vReport.html`

في `OprationsActivity` بعد حفظ دفعة، يتم:
```java
String payinfoJson = new Gson().toJson(payinfo);
WebviewActivity.x.loadUrl("javascript:localStorage.setItem('payInfo','" + payinfoJson + "');");
WebviewActivity.x.loadUrl("file:///android_asset/web/vReport.html");
```

⇒ في `vReport.html`:
```js
const payInfo = JSON.parse(localStorage.getItem('payInfo'));
document.getElementById('cust_no').textContent = payInfo.c_no;
// … إلخ
```

⇒ بنية هشّة — localStorage يمكن لأي صفحة على نفس origin قراءته.

---

## 9. منطق `savePdfBtn` (زر حفظ PDF)

```java
y.setOnClickListener(new c());
// c.onClick:
//    PrintManager pm = (PrintManager) getSystemService(PRINT_SERVICE);
//    PrintDocumentAdapter adapter = u.createPrintDocumentAdapter(...);
//    s = pm.print(jobName, adapter, attrs);
//    t = true;
```

ينتج عنه ⇒ نظام Android print framework يفتح dialog حفظ PDF.

---

## 10. التدفُّق ASCII الكامل

```text
┌─────────────────────────────────────────┐
│         WebviewActivity                  │
├─────────────────────────────────────────┤
│ onCreate                                  │
│   ↓ setContentView                        │
│   ↓ y() ⇒ render                          │
│      ↓ extract Intent extras              │
│      ↓ optionally init Bixolon (OP_TYP=1) │
│      ↓ ⚠️ WebView config (dangerous)      │
│      ↓ addJavascriptInterface("mobile")  │
│      ↓ setWebViewClient (h) + Chrome (a) │
│      ↓ Handler.postDelayed → loadUrl(v)  │
│                                           │
│ في الـ WebView:                            │
│   loadUrl(file:///android_asset/web/x.html)│
│      ↓ html script: mobile.X()            │
│         ↓ i.java method ⇒ Java callback   │
│            ↓ v() or w() ⇒ POST endpoint  │
│               ↓ response                  │
│                  ↓ loadUrl("javascript:..")│
│                                           │
│ onResume:                                  │
│   ↓ if PrintJob active ⇒ Toast status     │
│                                           │
│ onStart/onStop:                            │
│   ↓ resume/disconnect Bixolon             │
│                                           │
│ Action Bar:                                │
│   ↓ action_connect → connect printer     │
│   ↓ printer_seting → Setting_Printer_Activity │
└─────────────────────────────────────────┘
```

---

## 11. خلاصة المخاطر

| # | الخطر | الموقع | الشدة |
|---|------|--------|------|
| 1 | `setAllowUniversalAccessFromFileURLs(true)` | السطر 438 | 🔴🔴 |
| 2 | `onReceivedSslError → proceed()` | h.java السطر 134 | 🔴🔴 |
| 3 | Geolocation auto-allow | onGeolocationPermissionsShowPrompt | 🔴 |
| 4 | `setJavaScriptEnabled` + `addJavascriptInterface` | السطر 439-440 | 🔴 |
| 5 | حقن JSON عبر `loadUrl("javascript:" + json)` بدون escape | v(), w() | 🔴 |
| 6 | static WebView reference (`u`, `x`) | عام | 🟡 (memory leak) |
| 7 | `static String v`, `w` تُحمَّل من Intent extras | عام | 🟡 |
| 8 | localStorage يُستخدم لتمرير payment info | vReport.html | 🟡 |
| 9 | لا User-Agent مخصَّص | عام | 🟢 |
| 10 | لا CSP header | عام | 🟡 |
| 11 | `setDomStorageEnabled` يُستدعى مرتين | السطر 432, 437 | 🟢 (zero effect) |
| 12 | `clearCache(true)` يحذف cache كل مرة ⇒ بطء | السطر 435 | 🟡 |

---

## 12. التوصيات للإعادة

| التوصية | التطبيق في React Native |
|---------|-------------------------|
| إستخدام `react-native-webview` مع `originWhitelist` صارم | `<WebView originWhitelist={['https://abbasiy.yedns.org']} />` |
| `setAllowUniversalAccessFromFileURLs=false` | لا تفعِّله أبداً |
| `onReceivedSslError` يجب أن يفحص `host` و `certificate` | `onShouldStartLoadWithRequest` + Certificate Pinning |
| استبدال `addJavascriptInterface` بـ `postMessage` | الـ Type-safe + asynchronous |
| Geolocation: اطلب صلاحية صريحة | `geolocationEnabled={false}` + asking via native |
| Avoid `loadUrl("javascript:")` | استخدام `injectJavaScript` + `onMessage` |
| لا تخزن JSON في localStorage بين سياقات | استخدم `navigation.params` أو state management |

---

> **يربط هذا الملف بـ:**
> - `05_webview_bridge/01_bridge_overview.md` (الجسر التفصيلي).
> - `09_assets_resources/01_html_pages.md` (الصفحات).
> - `09_assets_resources/02_javascript_files.md` (الـ JS).
> - `10_rebuild_blueprint/05_security_improvements.md` (الإصلاحات).
