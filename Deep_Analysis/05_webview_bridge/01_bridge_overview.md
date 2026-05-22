# JavaScript ↔ Android Bridge — نظرة شاملة

> **النوع:** `@JavascriptInterface` (الأسلوب القديم في Android، خطر إذا أُسيء استخدامه).
> **الإسم في JavaScript:** `mobile` (يظهر في الـ `window.mobile.*`).
> **الجسر الرئيسي:** `com.egy.webpaymentapp.Screens.web.i` (65 سطر).
> **الجسر الثانوي (للطباعة):** `com.egy.webpaymentapp.Screens.web.j.c` (داخل الكلاس `j`).

---

## 1. خريطة الجسرين

### 1.1 الجسر الرئيسي (`web/i.java`) — لـ WebView العام

يُربط في `WebviewActivity.y()` السطر 440:
```java
u.addJavascriptInterface(new i(this, this), "mobile");
```

**6 طرق `@JavascriptInterface`:**

| الطريقة | المُستخدِم | الوظيفة |
|---------|-----------|---------|
| `GetPaymentsRequest(String)` | paymentList.html | جلب قائمة الدفعات |
| `GetReadingDataRequest(String)` | readinglist.html | جلب قائمة القراءات |
| `ShareReport()` | vReport.html | مشاركة الإيصال (Intent.ACTION_SEND) |
| `printPdfReport(String)` | vReport.html | طباعة كـ PDF عبر طابعة Android |
| `reloadWebPage()` | أي صفحة | إعادة تحميل الـ WebView |
| `sharexPdfReport(String)` | vReport.html | مشاركة الإيصال كـ PDF |

### 1.2 الجسر الثانوي (`web/j.java`) — لـ WebView طباعة Bixolon

يُنشَأ في `j.b()` السطر 145:
```java
webView.addJavascriptInterface(new c(null), "mobile");
```

**3 طرق `@JavascriptInterface`:**

| الطريقة | الوظيفة |
|---------|---------|
| `getPayReport(): String` | يُرجع JSON من Java إلى JS (payInfo) |
| `getReportPrintCss(): String` | يُرجع مسار CSS الطباعة حسب نوع الطابعة |
| `printRImage(String)` | يستقبل Base64 من JS ⇒ يطبعه على الطابعة الحرارية |

⚠️ **مفاجأة:** الإسم `mobile` يُستخدَم في **كلا** الجسرين — لكن في WebView منفصل ⇒ لا تصادم.

---

## 2. الكود الكامل للجسر الرئيسي

```java
public class i {
  Activity f2415a;
  p f2416b;   // = WebviewActivity (يطبق interface p)
  
  public i(Activity activity, p pVar) {
    this.f2415a = activity;
    this.f2416b = pVar;
  }
  
  @JavascriptInterface
  public void GetPaymentsRequest(String str) {
    WebviewActivity.v(str, this.f2415a);    // static method
  }
  
  @JavascriptInterface
  public void GetReadingDataRequest(String str) {
    WebviewActivity.w(str, this.f2415a);
  }
  
  @JavascriptInterface
  public void ShareReport() {
    WebviewActivity wa = (WebviewActivity) this.f2416b;
    wa.runOnUiThread(new m(wa));
  }
  
  @JavascriptInterface
  public void printPdfReport(String str) {
    WebviewActivity wa = (WebviewActivity) this.f2416b;
    wa.runOnUiThread(new l(wa, str));
  }
  
  @JavascriptInterface
  public void reloadWebPage() {
    WebviewActivity wa = (WebviewActivity) this.f2416b;
    wa.runOnUiThread(new o(wa));
  }
  
  @JavascriptInterface
  public void sharexPdfReport(String str) {
    WebviewActivity wa = (WebviewActivity) this.f2416b;
    wa.runOnUiThread(new n(wa, str));
  }
}
```

### الـ Lambdas المُمَرَّرة:
- `m`, `n`, `l`, `o` ⇒ كلاسات داخلية في `web/` تنفذ `Runnable`.

---

## 3. الجسر الثانوي (`web/j.c`)

```java
private class c {
  c(a aVar) {}
  
  @JavascriptInterface
  public String getPayReport() {
    return j.this.f2420d;   // JSON string for the report
  }
  
  @JavascriptInterface
  public String getReportPrintCss() {
    if (printerType.equals("sewoo")) {
      return "css/printcss_swoo.css";
    }
    return "css/printcss.css";
  }
  
  @JavascriptInterface
  public void printRImage(String base64) {
    // Strip Data URI prefix
    String pureBase64 = base64.substring(base64.indexOf(',') + 1);
    byte[] decoded = Base64.decode(pureBase64, 0);
    Bitmap bmp = BitmapFactory.decodeByteArray(decoded, 0, decoded.length);
    j.this.f2417a.b(bmp);   // print on thermal printer (a.a.b = Bixolon SDK)
  }
}
```

---

## 4. كيف يُستخدَم الجسر في JavaScript

### 4.1 من `paymentList.html` / `paymentlist.js`
```js
// عند تحميل الصفحة
function initPage() {
  const filters = {
    fromDate: document.getElementById('fromDate').value,
    toDate: document.getElementById('toDate').value,
  };
  // استدعاء Android للحصول على البيانات
  window.mobile.GetPaymentsRequest(JSON.stringify(filters));
}

// Java يستجيب لاحقاً عبر:
// webview.loadUrl("javascript:showpayList('" + JSON + "');");

function showpayList(jsonStr) {
  const records = JSON.parse(jsonStr);
  renderTable(records);
}
```

### 4.2 من `vReport.html` / `report.js`
```js
// زر مشاركة
document.getElementById('shareBtn').addEventListener('click', () => {
  window.mobile.sharexPdfReport(JSON.stringify(currentInvoice));
});

// زر طباعة
document.getElementById('printBtn').addEventListener('click', () => {
  window.mobile.printPdfReport(documentHtml);
});

// إعادة تحميل
document.getElementById('refreshBtn').addEventListener('click', () => {
  window.mobile.reloadWebPage();
});
```

### 4.3 من `vReport.html` للجسر الثانوي (Bixolon)
```js
// عند فتح WebView الطباعة (`j.b()`)
function generateReceiptImage() {
  // 1. اقرأ بيانات الفاتورة
  const data = JSON.parse(window.mobile.getPayReport());
  
  // 2. اقرأ CSS المناسب
  const cssPath = window.mobile.getReportPrintCss();
  
  // 3. ابني HTML للإيصال
  buildReceiptHtml(data, cssPath);
  
  // 4. حوِّل الـ DOM إلى صورة (html2canvas)
  html2canvas(document.getElementById('receipt')).then(canvas => {
    const base64 = canvas.toDataURL('image/png');
    // 5. أرسلها للطابعة
    window.mobile.printRImage(base64);
  });
}
```

---

## 5. تدفُّق المكالمات

### 5.1 تدفُّق `GetPaymentsRequest`

```text
[JS in paymentList.html]
   const filters = JSON.stringify({fromDate, toDate});
   window.mobile.GetPaymentsRequest(filters);
         ↓
[Native: i.java]
   GetPaymentsRequest(String str) {
     WebviewActivity.v(str, activity);
   }
         ↓
[Native: WebviewActivity.v static method]
   d req = parse(str);
   POST /api/Payment/GetPaymentsReportData
         ↓
[Response from server]
   List<c> payList
         ↓
[Native: callback]
   String json = new Gson().toJson(payList);
   webview.loadUrl("javascript:showpayList('" + json + "');");
         ↓
[JS]
   function showpayList(jsonStr) {
     const list = JSON.parse(jsonStr);
     // render in table
   }
```

### 5.2 تدفُّق `printPdfReport`

```text
[JS in vReport.html]
   const html = document.documentElement.outerHTML;
   window.mobile.printPdfReport(html);
         ↓
[Native: i.java]
   printPdfReport(String str) {
     runOnUiThread(new l(wa, str));
   }
         ↓
[Native: l.run()]
   PrintManager pm = (PrintManager) getSystemService(PRINT_SERVICE);
   PrintDocumentAdapter adapter = WebView.createPrintDocumentAdapter(jobName);
   PrintJob job = pm.print(jobName, adapter, attrs);
   webviewActivity.s = job;
   webviewActivity.t = true;   ⇒ سيُتابع في onResume
```

### 5.3 تدفُّق `printRImage` (الطباعة الحرارية)

```text
[JS in vReport.html]
   html2canvas(receiptDiv).then(canvas => {
     window.mobile.printRImage(canvas.toDataURL('image/png'));
   });
         ↓
[Native: j.c.printRImage]
   strip "data:image/png;base64," prefix
   decode Base64 → byte[]
   BitmapFactory.decodeByteArray → Bitmap
   bixolonSdk.b(bitmap);   ⇒ يطبع على الطابعة الحرارية
```

---

## 6. مخاطر الـ Bridge (تفصيلية)

### 6.1 خطر #1: `@JavascriptInterface` على Android < 4.2 = RCE
- المخاطرة: في Android < 4.2 (SDK < 17)، `@JavascriptInterface` كان يفتح ثغرة Remote Code Execution عبر Reflection.
- **التخفيف:** التطبيق على الأرجح minSdk >= 19 (Android 4.4) ⇒ ليس مُتأثراً مباشرة.
- **لكن:** لا يضمن — يحتاج فحص `AndroidManifest.xml`.

### 6.2 خطر #2: حقن JavaScript عبر `loadUrl("javascript:")`
- في `WebviewActivity.v()` و `w()`:
  ```java
  webview.loadUrl("javascript:showpayList('" + json + "');");
  ```
- إذا `json` يحوي `'`, ` \n`, أو `</script>` ⇒ كسر السياق ⇒ تنفيذ JS اختياري.
- **مثال هجومي:** زبون باسم `أحمد'); alert('hacked'); //` ⇒ كسر.
- **الإصلاح:** استخدام `evaluateJavascript(escape(json))` بدل `loadUrl`.

### 6.3 خطر #3: `getPayReport` يُرجع نص خام
- `j.f2420d` هو JSON يحوي بيانات الفاتورة كاملة.
- لو الـ WebView يحمِّل صفحة خارجية بسبب CSP المفقود ⇒ يمكن للصفحة سحب البيانات.
- **الإصلاح:** Origin whitelist + Hash-verified content.

### 6.4 خطر #4: `printRImage` بلا فحص حجم
- Base64 بأي حجم يُفك ⇒ Bitmap ⇒ OOM محتمل.
- **الإصلاح:** حد أقصى للحجم (مثلاً 10 MB) + try/catch.

### 6.5 خطر #5: لا فحص للـ caller
- أي صفحة محمَّلة (حتى من file://) يمكنها استدعاء `mobile.*`.
- **الإصلاح:** فحص الـ URL المحمَّل قبل تنفيذ الأوامر:
  ```java
  if (!webview.getUrl().startsWith("https://abbasiy.yedns.org")) {
    throw new SecurityException("Unauthorized origin");
  }
  ```

---

## 7. مقارنة بالإعادة في React Native

### 7.1 المُكافِئ في `react-native-webview`

```tsx
import { WebView, WebViewMessageEvent } from 'react-native-webview';

const PaymentListScreen = () => {
  const webViewRef = useRef<WebView>(null);
  
  // استقبال رسائل من JS
  const onMessage = async (event: WebViewMessageEvent) => {
    const { type, payload } = JSON.parse(event.nativeEvent.data);
    
    switch (type) {
      case 'GetPaymentsRequest': {
        const filters = payload;
        const records = await api.payments.list(filters);
        const escaped = JSON.stringify(records).replace(/[\\'"\u2028\u2029]/g, '\\$&');
        webViewRef.current?.injectJavaScript(
          `showpayList(${escaped}); true;`
        );
        break;
      }
      case 'ShareReport': {
        await Share.share({ title: 'Receipt', message: payload.text });
        break;
      }
      case 'PrintPdf': {
        await Print.printAsync({ html: payload.html });
        break;
      }
    }
  };
  
  // JS injected to expose the bridge
  const injectedJS = `
    window.mobile = {
      GetPaymentsRequest: (filters) => window.ReactNativeWebView.postMessage(JSON.stringify({type:'GetPaymentsRequest',payload:filters})),
      GetReadingDataRequest: (filters) => window.ReactNativeWebView.postMessage(JSON.stringify({type:'GetReadingDataRequest',payload:filters})),
      ShareReport: () => window.ReactNativeWebView.postMessage(JSON.stringify({type:'ShareReport',payload:{}})),
      printPdfReport: (html) => window.ReactNativeWebView.postMessage(JSON.stringify({type:'PrintPdf',payload:{html}})),
      reloadWebPage: () => window.location.reload(),
      sharexPdfReport: (html) => window.ReactNativeWebView.postMessage(JSON.stringify({type:'SharePdf',payload:{html}})),
    };
    true;
  `;
  
  return (
    <WebView
      ref={webViewRef}
      source={{ uri: 'https://reports.example.com/payments' }}
      originWhitelist={['https://reports.example.com']}
      onMessage={onMessage}
      injectedJavaScript={injectedJS}
      javaScriptEnabled
      domStorageEnabled
      // لا تفعّل أبداً:
      // allowUniversalAccessFromFileURLs={false}
      // allowFileAccess={false}
    />
  );
};
```

### 7.2 المزايا
- ✅ Type-safe (TypeScript).
- ✅ Asynchronous بطبيعتها.
- ✅ لا Reflection-based RCE.
- ✅ Origin whitelist مدمج.
- ✅ Easy escape via `JSON.stringify` + regex.

---

## 8. خلاصة الـ Bridge

| البُعد | AbbasiyCashiers | الإعادة المُقترَحة |
|------|----------------|---------------------|
| الإسم في JS | `window.mobile` | `window.mobile` (للتوافق) لكن internally → postMessage |
| عدد الطرق الأساسية | 6 | 6 (نفسها) |
| Type safety | لا | TypeScript |
| Origin check | لا | Whitelist إجباري |
| Escape JSON | لا | regex escape |
| Async/Promise | sync | Promise-based |
| Memory leak | محتمل (static refs) | مدار عبر hooks |

---

## 9. الملفات المرتبطة (كل طريقة في ملف منفصل)

- `02_GetPaymentsRequest.md` — جلب قائمة الدفعات.
- `03_GetReadingDataRequest.md` — جلب قائمة القراءات.
- `04_ShareReport.md` — مشاركة الإيصال.
- `05_printPdfReport.md` — طباعة الإيصال كـ PDF.
- `06_reloadWebPage.md` — إعادة التحميل.
- `07_sharexPdfReport.md` — مشاركة الإيصال كـ PDF.

---

> **يربط هذا الملف بـ:**
> - `04_screens_flow/05_webview_screen.md` (الـ WebView).
> - `09_assets_resources/02_javascript_files.md` (الـ JS).
> - `10_rebuild_blueprint/05_security_improvements.md`.
