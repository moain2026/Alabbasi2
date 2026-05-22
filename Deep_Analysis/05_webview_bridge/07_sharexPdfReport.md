# `mobile.sharexPdfReport(String)` — مشاركة الإيصال كـ PDF

> **التوقيع:** `@JavascriptInterface public void sharexPdfReport(String str)`
> **الموقع:** `web/i.java` السطر 57-64
> **المُعامِل:** `String str` — HTML أو محتوى يُمرَّر للتحويل إلى PDF.

---

## 1. الكود

```java
@JavascriptInterface
public void sharexPdfReport(String str) {
  p pVar = this.f2416b;
  if (pVar != null) {
    WebviewActivity webviewActivity = (WebviewActivity) pVar;
    webviewActivity.runOnUiThread(new n(webviewActivity, str));
  }
}
```

---

## 2. ما يفعله `n.run()` (مُعاد بناؤه)

```java
public class n implements Runnable {
  WebviewActivity wa;
  String htmlContent;
  
  public n(WebviewActivity wa, String s) {
    this.wa = wa;
    this.htmlContent = s;
  }
  
  @Override
  public void run() {
    try {
      // 1. توليد PDF من HTML
      // قد تستخدم itext / bxlpdf أو Android Print Adapter يكتب لـ File
      File pdfFile = new File(wa.getCacheDir(), "report_" + System.currentTimeMillis() + ".pdf");
      
      // طريقة 1: استخدام WebView print adapter
      // (Android 5+)
      PrintDocumentAdapter adapter = wa.u.createPrintDocumentAdapter("AbbasiyReport");
      writeAdapterToPdf(adapter, pdfFile);
      
      // طريقة 2: استخدام itext أو libbxlpdf
      // PdfDocument doc = new PdfDocument(pdfFile);
      // ...
      
      // 2. مشاركة الـ PDF
      Uri uri = FileProvider.getUriForFile(wa, "com.egy.webpaymentapp", pdfFile);
      
      Intent share = new Intent(Intent.ACTION_SEND);
      share.setType("application/pdf");
      share.putExtra(Intent.EXTRA_STREAM, uri);
      share.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
      
      wa.startActivity(Intent.createChooser(share, "مشاركة الإيصال PDF"));
      
    } catch (Exception e) {
      Toast.makeText(wa, "Error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
    }
  }
}
```

⚠️ هذا التخمين الأقرب من السياق. الكود الحقيقي قد يستخدم `bxlpdf` (Bixolon PDF library) من `libbxlpdf.so`.

---

## 3. الإختلاف عن `ShareReport()`

| البُعد | `ShareReport()` | `sharexPdfReport(String)` |
|------|-----------------|---------------------------|
| المُعامِلات | لا يوجد | HTML خام كنص |
| المُخرج | الأرجح صورة PNG | PDF |
| المصدر | محتوى الـ WebView | HTML مُمَرَّر من JS |
| المرونة | محدود (snapshot) | مرن (يمكن تحويل أي HTML) |

---

## 4. الإختلاف عن `printPdfReport(String)`

| البُعد | `printPdfReport()` | `sharexPdfReport()` |
|------|--------------------|---------------------|
| السلوك | يفتح Android Print UI | يفتح Share Sheet |
| المُتلقّي | طابعة / Save to PDF | تطبيق مشاركة |
| التحكم | الـ user يختار وجهة | الـ user يختار وجهة |

⇒ **التشابه كبير** — كلاهما يُنتج PDF. الفرق هو **الـ Intent النهائي** (print vs share).

---

## 5. الإستخدام في JS

```js
document.getElementById('shareAsPdfBtn').onclick = () => {
  const html = document.documentElement.outerHTML;
  window.mobile.sharexPdfReport(html);
};
```

---

## 6. التدفُّق

```text
[JS in vReport.html]
   const html = document.documentElement.outerHTML;
   window.mobile.sharexPdfReport(html);
         ↓
[Native: i.sharexPdfReport]
   runOnUiThread(new n(wa, str));
         ↓
[Native: n.run on UI thread]
   1. تحويل HTML → PDF (via WebView Print adapter or itext)
   2. حفظ في cache
   3. FileProvider.getUriForFile
   4. Intent.ACTION_SEND with MIME=application/pdf
   5. startActivity(createChooser)
         ↓
[Android Share Sheet]
   WhatsApp / Email / Drive / Bluetooth / ...
```

---

## 7. لماذا الإسم "sharex"؟

التخمين: المطوّر استخدم `share` (لـ ShareReport بدون PDF) ⇒ ثم اضطر لإضافة method للـ PDF ⇒ سمَّاه `sharexPdfReport` (`x` كحرف فاصل).

⇒ **ربما** يدل على أن `ShareReport` ينتج صورة و `sharexPdfReport` ينتج PDF.

---

## 8. المخاطر

نفس مخاطر `ShareReport` + `printPdfReport`:

| # | الخطر | التخفيف |
|---|------|---------|
| 1 | HTML من JS قد يكون خبيثاً (XSS في الـ PDF) | تحقّق وعالج HTML |
| 2 | حجم HTML غير محدود | حدّ 5 MB كحد أقصى |
| 3 | PDF يحتوي بيانات حساسة كاملة | redact PII |
| 4 | لا تنظيف الـ cache | cron-like cleanup |
| 5 | المستخدم يشارك الـ PDF عبر قنوات غير آمنة | training + warning |

---

## 9. المُكافِئ في React Native

```tsx
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';

case 'SharePdfReport': {
  const html = payload.html;
  
  // 1. تحويل HTML → PDF
  const { uri } = await Print.printToFileAsync({
    html,
    width: 595,
    height: 842,
  });
  
  // 2. مشاركة
  if (await Sharing.isAvailableAsync()) {
    await Sharing.shareAsync(uri, {
      mimeType: 'application/pdf',
      dialogTitle: 'مشاركة الإيصال',
    });
  }
  
  break;
}
```

---

## 10. توصيات

- ✅ **CSP** في الـ HTML المُمَرَّر (no inline scripts).
- ✅ **Sanitize** الـ HTML قبل تحويل لـ PDF.
- ✅ **Watermark** على PDF (employee + timestamp).
- ✅ **Log** كل مشاركة (audit trail).
- ✅ **Encrypt** الـ PDF إذا حسّاس (مع كلمة مرور أو DRM).
- ✅ **حدّد القنوات** المسموحة (block clipboard for sensitive data).

---

> **يربط هذا الملف بـ:**
> - `05_webview_bridge/04_ShareReport.md`.
> - `05_webview_bridge/05_printPdfReport.md`.
> - `08_native_libs/02_bxlpdf.md`.
