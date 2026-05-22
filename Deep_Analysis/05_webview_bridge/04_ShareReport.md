# `mobile.ShareReport()` — مشاركة الإيصال

> **التوقيع:** `@JavascriptInterface public void ShareReport()`
> **الموقع:** `web/i.java` السطر 30-37
> **بدون مُعامِلات!** — يقرأ المحتوى من Activity state.

---

## 1. الكود

```java
@JavascriptInterface
public void ShareReport() {
  p pVar = this.f2416b;
  if (pVar != null) {
    WebviewActivity webviewActivity = (WebviewActivity) pVar;
    webviewActivity.runOnUiThread(new m(webviewActivity));
  }
}
```

⇒ يُنفِّذ Runnable `m` على UI thread.

---

## 2. ما يفعله `m.run()` (مُعاد بناؤه)

```java
public class m implements Runnable {
  WebviewActivity wa;
  
  public m(WebviewActivity wa) { this.wa = wa; }
  
  @Override
  public void run() {
    // 1. التقاط محتوى WebView كصورة (أو نص؟)
    Bitmap content = captureWebView(wa.u);
    
    // 2. إنشاء File مؤقت
    File temp = new File(wa.getCacheDir(), "report_" + System.currentTimeMillis() + ".png");
    saveBitmapToFile(content, temp);
    
    // 3. إنشاء Intent.ACTION_SEND
    Uri uri = FileProvider.getUriForFile(wa, "com.egy.webpaymentapp", temp);
    
    Intent share = new Intent(Intent.ACTION_SEND);
    share.setType("image/png");  // أو "application/pdf"
    share.putExtra(Intent.EXTRA_STREAM, uri);
    share.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
    
    wa.startActivity(Intent.createChooser(share, "Share Report"));
  }
}
```

⚠️ هذا التخمين الأقرب — التحقُّق يتطلب قراءة الكلاس `m` المُفكَّك (موجود في نفس الـ package).

---

## 3. السيناريو المُتوقَّع للإستخدام

من JS في `vReport.html`:

```js
document.getElementById('shareBtn').addEventListener('click', () => {
  // المحتوى يكون مُحضَّر في الـ DOM (الفاتورة معروضة)
  window.mobile.ShareReport();
  // ⇒ Android يأخذ snapshot من الـ WebView ويفتح Share sheet
});
```

---

## 4. الإختلاف عن `sharexPdfReport(String)`

| البُعد | `ShareReport()` | `sharexPdfReport(String)` |
|------|-----------------|---------------------------|
| المُعامِلات | لا | يمرَّر HTML |
| المُخرج | الأرجح صورة WebView | الأرجح PDF |
| المصدر | محتوى WebView الحالي | HTML خام مُمَرَّر |

⇒ راجع `07_sharexPdfReport.md`.

---

## 5. التدفُّق

```text
[JS]
   document.getElementById('shareBtn').onclick = () => {
     window.mobile.ShareReport();
   };
         ↓
[Native: i.ShareReport]
   runOnUiThread(new m(webviewActivity));
         ↓
[Native: m.run on UI thread]
   1. capture WebView content
   2. save to temp file
   3. Intent.ACTION_SEND with FileProvider URI
   4. startActivity(createChooser(...))
         ↓
[Android system: Share Sheet]
   - WhatsApp
   - Email
   - Bluetooth
   - Drive
   - …
```

---

## 6. المخاطر

| # | الخطر | التخفيف |
|---|------|---------|
| 1 | بيانات الزبون تُشارَك بدون تأكيد | تأكيد قبل المشاركة + log |
| 2 | لا تنظيف للملفات المؤقتة في cache | `cleanupOldShares()` دوريّاً |
| 3 | FileProvider يحتاج XML config صحيح | تحقَّق من `provider_paths.xml` |
| 4 | لا control على ما يُشارَك (المحتوى كاملاً) | redact PII (account number partial) |
| 5 | لا مراقبة لاحتفاظ المستلم بالبيانات | DRM/Watermark |

---

## 7. المُكافِئ في React Native

```tsx
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import { captureRef } from 'react-native-view-shot';

// في الـ handler:
case 'ShareReport': {
  // 1. التقاط الشاشة
  const uri = await captureRef(webViewRef, {
    format: 'png',
    quality: 1.0,
  });
  
  // 2. أو إستخدام WebView captureScreen
  // (لا تتوفر مباشرة في react-native-webview ⇒ نلتقط الـ container)
  
  // 3. مشاركة
  await Sharing.shareAsync(uri, {
    mimeType: 'image/png',
    dialogTitle: 'مشاركة الإيصال',
  });
  
  break;
}
```

---

## 8. ملاحظة على واجهة `p`

من `i.java`:
```java
p f2416b;   // type "p" interface
```

⇒ يُمرَّر كـ `this` من `WebviewActivity` ⇒ `WebviewActivity implements p`.

في `WebviewActivity.java`:
```java
public class WebviewActivity extends androidx.appcompat.app.h implements p {
```

⇒ `p` هو interface في الـ `web/` package (`p.java`) يحوي على الأرجح:
```java
interface p {
  void onShareReport();
  void onPrintPdfReport(String html);
  void onReloadWebPage();
  void onSharexPdfReport(String html);
}
```

⚠️ لكن في الكود الفعلي، `i` يستخدم cast مباشر إلى `WebviewActivity` ⇒ الـ interface قد يكون فارغاً (marker).

---

## 9. توصيات

- ✅ أضف **تأكيد** قبل المشاركة (مَن، ماذا).
- ✅ أضف **log** لكل مشاركة (للمراجعة).
- ✅ **redact** الحقول الحساسة (مثلاً show only last 4 digits of account).
- ✅ **حدِّد الـ targets** المسموحة (لا تسمح بـ Bluetooth/Drive للبيانات الحساسة).

---

> **يربط هذا الملف بـ:**
> - `05_webview_bridge/07_sharexPdfReport.md`.
> - `06_business_logic/05_receipt_generation.md`.
