# `mobile.printPdfReport(String)` — طباعة الإيصال كـ PDF

> **التوقيع:** `@JavascriptInterface public void printPdfReport(String str)`
> **الموقع:** `web/i.java` السطر 39-46
> **المُعامِل:** `String str` — HTML محتوى أو اسم الإيصال

---

## 1. الكود

```java
@JavascriptInterface
public void printPdfReport(String str) {
  p pVar = this.f2416b;
  if (pVar != null) {
    WebviewActivity webviewActivity = (WebviewActivity) pVar;
    webviewActivity.runOnUiThread(new l(webviewActivity, str));
  }
}
```

---

## 2. ما يفعله `l.run()` (مُعاد بناؤه)

```java
public class l implements Runnable {
  WebviewActivity wa;
  String htmlOrName;
  
  public l(WebviewActivity wa, String s) {
    this.wa = wa;
    this.htmlOrName = s;
  }
  
  @Override
  public void run() {
    // إستخدام Android Print Framework
    PrintManager pm = (PrintManager) wa.getSystemService(Context.PRINT_SERVICE);
    
    // طريقة 1: طباعة المحتوى الحالي للـ WebView
    PrintDocumentAdapter adapter = wa.u.createPrintDocumentAdapter(
      htmlOrName != null ? htmlOrName : "AbbasiyReport"
    );
    
    PrintAttributes attrs = new PrintAttributes.Builder()
      .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
      .setResolution(new PrintAttributes.Resolution("res", "Default", 600, 600))
      .setMinMargins(PrintAttributes.Margins.NO_MARGINS)
      .build();
    
    PrintJob job = pm.print("AbbasiyReport_" + System.currentTimeMillis(), adapter, attrs);
    
    wa.s = job;       // حفظ المرجع
    wa.t = true;       // علم: تتبع في onResume
  }
}
```

---

## 3. التدفُّق

```text
[JS in vReport.html]
   document.getElementById('printBtn').onclick = () => {
     // المُعامِل: قد يكون اسم الـ job أو HTML
     window.mobile.printPdfReport('Receipt_' + voucherNo);
   };
         ↓
[Native: i.printPdfReport]
   runOnUiThread(new l(wa, str));
         ↓
[Native: l.run on UI thread]
   PrintManager pm = getSystemService(PRINT_SERVICE);
   PrintDocumentAdapter adapter = webView.createPrintDocumentAdapter(name);
   PrintJob job = pm.print(jobName, adapter, attrs);
   wa.s = job;
   wa.t = true;
         ↓
[Android Print Framework]
   1. يفتح UI نظام الطباعة
   2. المستخدم يختار: طابعة / Save as PDF
   3. يضغط طباعة
         ↓
[Native: WebviewActivity.onResume عند العودة]
   if (s != null && t):
       status = "Completed" / "Failed" / "Cancelled" / "..."
       Toast.makeText(this, status, SHORT).show();
       t = false;
```

---

## 4. الفرق بين `printPdfReport` و الطباعة الحرارية

| البُعد | `printPdfReport()` (الجسر الرئيسي i.java) | `printRImage()` (الجسر الثانوي j.java) |
|------|----------------------------------------|----------------------------------------|
| الجهاز | أي طابعة عبر Print Framework | طابعة Bixolon الحرارية فقط |
| التنسيق | PDF عبر Print Adapter | صورة Bitmap من Base64 |
| الإستخدام | حفظ PDF أو طباعة مكتبية | إيصال حراري سريع |
| التأخير | يفتح Dialog | فوري بدون Dialog |

---

## 5. المخاطر

| # | الخطر | التخفيف |
|---|------|---------|
| 1 | معلومات حساسة في عنوان مهمة الطباعة | لا تضع account number في jobName |
| 2 | لا تنظيف للـ Print job في حالة الإلغاء | reset s/t في onActivityResult |
| 3 | المستخدم قد يرسل الـ PDF لجهة أخرى عبر "Save to Drive" | لا حماية ⇒ training المستخدم |
| 4 | محتوى الـ WebView كامل يُطبَع (بما فيه عناصر UI) | استخدم print-friendly CSS @media print |
| 5 | لا preview قبل الإرسال | استخدم Custom adapter لـ preview |

---

## 6. المُكافِئ في React Native

```tsx
import * as Print from 'expo-print';

case 'PrintPdf': {
  const html = payload.html;
  
  // إنتاج PDF ثم طباعته أو حفظه
  const { uri } = await Print.printToFileAsync({
    html,
    width: 595,   // A4 width
    height: 842,
  });
  
  // عرض الـ system print dialog
  await Print.printAsync({ uri });
  
  break;
}

// أو إستخدام print directly:
case 'PrintPdfDirect': {
  await Print.printAsync({
    html: payload.html,
    printerUrl: settings.printerUrl,  // optional
  });
  break;
}
```

---

## 7. توصيات

- ✅ **CSS @media print** للتحكم في ما يُطبَع.
- ✅ **Watermark** على الـ PDF (employee name + timestamp).
- ✅ **Log** كل عملية طباعة.
- ✅ **Validate the HTML** المُمَرَّر من JS قبل الطباعة (لا تطبع HTML خبيث).
- ✅ **استخدم `evaluateJavascript`** للحصول على HTML بدلاً من تمريره من JS مباشرة.

---

> **يربط هذا الملف بـ:**
> - `06_business_logic/05_receipt_generation.md`.
> - `08_native_libs/02_bxlpdf.md` (Bixolon PDF lib).
