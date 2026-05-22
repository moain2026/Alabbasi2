# 05 — Receipt Generation (تحليل محايد لتوليد الإيصال)

> **منهجية:** كل اكتشاف مُوثَّق بـ `file:line` من كود jadx الفعلي + decompiled JavaScript. لا فرضيات. التقييم: 🟢 جيد / 🟡 متوسط / 🔴 سيء.

---

## 🎯 ملخص تنفيذي

التطبيق يستخدم **معمارية هجينة غير تقليدية لتوليد الإيصال:**

```
[Java] استجابة السيرفر (Payinfo JSON)
   ↓
[Java] إنشاء WebView مخفي محشو بـ vReport.html
   ↓
[JavaScript في WebView] قراءة JSON من mobile.getPayReport()
   ↓
[JavaScript] بناء HTML الإيصال + استدعاء tafqeet() للتفقيط
   ↓
[Java بعد timeout 3000ms ثابت!] WebView.createPrintDocumentAdapter("vdoc")
   ↓
[Android Print Framework] إنشاء PDF (voucher_.pdf)
   ↓
   ├─→ مسار 1: Bixolon JPOS — printPDF() عبر Bluetooth (طابعة 3-inch)
   ├─→ مسار 2: Sewoo — PdfRenderer → Bitmap → Bluetooth bytes
   └─→ مسار 3: Intent ACTION_SEND → application/pdf → user picks app
```

**نقاط رئيسية مُكتشَفة:**
- ✅ يستخدم Android Print Framework (PDF رسمي، ليس HTML خام)
- 🔴 **vReport.html مُبهَّم** بـ `unescape(%hex)` من snapbuilder.com (security through obscurity)
- 🔴 **timeout 3000ms ثابت** بين تحميل HTML والطباعة (race condition محتمل)
- 🔴 **اسم الملف ثابت** `voucher_.pdf` (يُكتب فوق السابق)
- 🔴 `setAllowUniversalAccessFromFileURLs(true)` في WebView (ثغرة معروفة)
- 🔴 `setMixedContentMode(0)` يسمح بمحتوى HTTP داخل HTTPS
- 🟡 يدعم طابعتَين (Bixolon SPP-R310 + Sewoo) لكن بمسارَين كود مختلفَين
- 🟡 يعتمد JPOS API القديمة (sun.com/JavaPOS) للـ Bixolon

---

## 1. متى يُولَّد الإيصال؟

### 1.1 فقط بعد دفع ناجح

📍 **`OprationsActivity.java:493-494`**:
```java
if (this.B == 1) {                                              // Payment only
    r().m(R.string.text_payments);
    this.q = new com.egy.webpaymentapp.BixlonPrinterManger.a(this);
}
if (this.B == 2) {                                              // Reading
    r().m(R.string.text_meter_reading);
    // ⚠️ لا يوجد printer manager — لا يمكن طباعة إيصال للقراءة
}
```

🔴 **اكتشاف**: لا يوجد إيصال لعملية قراءة العدّاد — فقط للدفع. تصميمي، لكن قد يكون قيداً غير مرغوب.

### 1.2 بعد استجابة ناجحة من `saveBillRequest`

📍 **`Screens/s.java:22-56`** — Success handler للدفع:
```java
public void a(b bVar2) {
    if (bVar2.e() > 0) {                          // GEN_API_ERR_NO > 0 = error
        c.b.a.d.e(bVar2.d(), this.f2394a);
        return;
    }
    c.b.a.c.d(this.f2394a).a("APP_USER_LOC_KEY", "");   // clear GPS
    linearLayout = this.f2394a.C;
    linearLayout.setVisibility(8);                // إخفاء layout الإدخال
    linearLayout2 = this.f2394a.D;
    linearLayout2.setVisibility(0);               // إظهار layout النجاح
    textView = this.f2394a.E;
    textView.setText(R.string.txt_op_no + ":" + bVar2.g().a());  // op_no = v_no
    button = this.f2394a.G;
    button.setVisibility(0);                      // زر "اطبع"
    button2 = this.f2394a.F;
    button2.setVisibility(0);                     // زر "شارك"
    button3 = this.f2394a.H;
    button3.setVisibility(0);                     // زر "جديد"
    button4 = this.f2394a.G;
    button4.setOnClickListener(new p(this, bVar2));  // ← Print
    button5 = this.f2394a.F;
    button5.setOnClickListener(new q(this, bVar2));  // ← Share
    button6 = this.f2394a.H;
    button6.setOnClickListener(new r(this));
}
```

🟢 **تصميم جيد:** المستخدم يختار طباعة أو مشاركة بعد التأكيد من النجاح.

---

## 2. بيانات الإيصال المطبوعة

### 2.1 المصدر: استجابة السيرفر

📍 **`webapi/models/b.java`** + **`webapi/models/Payinfo.java`**:

السيرفر يُرجع `Payinfo` يحوي:
| الحقل | JSON Name | الاستخدام في الإيصال |
|---|---|---|
| `c_no` | `c_no` | رقم المشترك |
| `c_name` | `c_name` | اسم المشترك |
| `c_bal` | `c_bal` | الرصيد المتبقي بعد الدفع |
| `v_amt` | `v_amt` | مبلغ التسديد |
| `v_no` | `v_no` | رقم السند (مُولَّد من السيرفر) |
| `v_date` | `v_date` | تاريخ السند |
| `user_name` | `user_name` | اسم المُحصِّل (الكاشير) |
| `comp_name` | `comp_name` | اسم الشركة |
| `comp_add` | `comp_add` | عنوان الشركة |
| `comp_tel` | `comp_tel` | هاتف الشركة |

### 2.2 ما **لا** يُطبَع

- ❌ المبلغ بالحروف (التفقيط) — يُحسَب في JS لاحقاً
- ❌ Barcode/QR code (لا يوجد في الكود)
- ❌ توقيع رقمي
- ❌ ختم الشركة (في HTML يقول "لا يحتاج إلى ختم أو توقيع")

📍 **النص المضمَّن في `report.js[57]`**:
```html
<div class="text-center font-weight-bolder h3">
  <strong><u>هذا السند آلي حراري.. يجب تصويره للاحتفاظ به ولا يحتاج الى ختم أو توقيع..</u></strong>
</div>
```

---

## 3. القالب: `vReport.html`

### 3.1 الإبهام (Obfuscation)

📍 **`assets/myweb/vReport.html`** — السطر الأول:
```html
<script language="javascript">
<!--
// == Begin Free HTML Source Code Obfuscation Protection from https://snapbuilder.com == //
document.write(unescape('%3C%21%44%4F%43%54%59%50%45%20%68%74%6D%6C%3E...'));
//-->
</script>
```

🔴 **اكتشاف**: HTML مُبهَّم بـ `unescape(%hex)` — استُخدم obfuscator من **snapbuilder.com**. هذا:
- لا يحمي من أي مهاجم (decode بـ سطر Python واحد)
- يُضيف ~30% حجم
- يجعل التعديل أصعب على المطوّر نفسه

### 3.2 بعد فك التشفير (Python):

```python
import urllib.parse, re
with open('vReport.html', encoding='utf-8-sig') as f:
    s = f.read()
m = re.search(r"unescape\('([^']+)'\)", s)
print(urllib.parse.unquote(m.group(1)))
```

ينتج HTML واضح:
```html
<!DOCTYPE html>
<html>
<head id="head">
  <meta charset="utf-8" />
  <link rel="stylesheet" href="css/font-awesome-4.7.0/css/font-awesome.min.css">
  <link href="bootstrap.4.5.3/css/bootstrap-grid.min.css" rel="stylesheet">
  <link href="bootstrap.4.5.3/css/bootstrap-reboot.min.css" rel="stylesheet">
  <link href="bootstrap.4.5.3/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="css/myappcss.css?t=1">
  <script src="js/jquery-3.0.0.min.js"></script>
  <script src="bootstrap.4.5.3/js/bootstrap.bundle.min.js"></script>
  <script src="js/report.js?t=1"></script>

  <style>
    @media print {
      body { font-family: sans-serif !important; font-size: 2.75rem !important; }
      .h3, h3 { font-size: 2.75rem !important; }
      .h4, h4 { font-size: 2.5rem !important; }
    }
  </style>
</head>
<body onload="ReportData()" id="mbody">
  <button id="btnprint" onclick="sharePdf()">طباعة</button>
  <div id="hrow" class="row m-1"></div>
  <div id="mRow" class="row"></div>
  <div id="fRow" class="row"></div>
  <div id="error"></div>
</body>
</html>
```

### 3.3 التبعيات (Dependencies)

| المكتبة | الإصدار | الحجم | ملاحظة |
|---|---|---|---|
| jQuery | 3.0.0 | ~85KB | 🔴 **قديمة جداً** (current 3.7.x) — ثغرات معروفة |
| Bootstrap | 4.5.3 | ~150KB CSS+JS | 🟡 قديم (current 5.x) |
| Font-Awesome | 4.7.0 | ~75KB | 🟡 قديم (current 6.x) |

🔴 jQuery 3.0.0 (يونيو 2016!) فيها ثغرات XSS موثَّقة (CVE-2019-11358, CVE-2020-11022, CVE-2020-11023).

---

## 4. منطق توليد الإيصال في `report.js`

### 4.1 المدخل: `ReportData()`

📍 **`report.js`** (بعد فك تشفير `_$_174b[]`):
```javascript
function ReportData() {
    try {
        document.body.dir = 'rtl';
        var data = window.mobile.getPayReport();   // ← Bridge مع Java!
        printJsonObject(data);
    } catch (er) { error(er); }
}

function printJsonObject(jsonStr) {
    ReportDataObject(JSON.parse(jsonStr));
    addCss('css/printcss.css');
}
```

📍 **`Screens/web/j.java:80-82`** — `mobile.getPayReport`:
```java
@JavascriptInterface
public String getPayReport() {
    return j.this.f2420d;        // = Gson().toJson(payinfo)
}
```

### 4.2 بناء الإيصال

📍 **`report.js` (decoded)**:
```javascript
function ReportDataObject(data) {
    var printingDateTime = nDate();   // مثال: "12/05/2026 14:30:45"
    var v_copy = data.v_copy != undefined ? data.v_copy : '';

    // Header (Company Info)
    var hrow = '<div id="divcentercol" class="col-12">';
    hrow += '<div id="cntr">';
    hrow += '<div class="text-center font-weight-bolder h3">' + data.comp_name + '</div>';
    hrow += '<div class="text-center font-weight-bold h4">'  + data.comp_add  + '</div>';
    hrow += '<div class="text-center font-weight-bold h4">'  + data.comp_tel  + '</div>';
    hrow += '</div>';
    var titleSection = '<div class="text-center font-weight-bolder h3">' +
                       '<strong><u>سند تحصيل ' + v_copy + '</u></strong></div>';
    var hr = '<div class="col-12"><hr class="col new4"/></div>';
    $('#hrow').append(hrow + titleSection + hr);

    // Body (Receipt Details)
    var template = '<div class="col-12 text-center">' +
                   '<div class="row"><div class="col-auto font-weight-bolder text-right">@flbl</div>' +
                   ' <div class="col-auto px-1 text-right font-weight-bold defaultfont">@fval</div></div></div>';
    var body = '';
    body += template.replace('@flbl', 'سند رقم')      .replace('@fval', data.v_no);
    body += template.replace('@flbl', 'تاريخ السند')   .replace('@fval', '<span dir=ltr>' + data.v_date + '</span>');
    body += template.replace('@flbl', 'رقم المشترك: ').replace('@fval', data.c_no);
    body += template.replace('@flbl', 'اسم المشترك:') .replace('@fval', data.c_name);
    body += template.replace('@flbl', 'مبلغ التسديد:').replace('@fval', data.v_amt + ' ' + tafqeet(data.v_amt));
    body += template.replace('@flbl', 'اسم المتحصل:') .replace('@fval', data.user_name);
    if (data.c_bal != null) {
        body += template.replace('@flbl', 'الرصيد الحالي:').replace('@fval', data.c_bal + ' ' + tafqeet(data.c_bal));
    }
    body += template.replace('@flbl', 'وقت الطباعة')  .replace('@fval', printingDateTime);
    $('#mRow').append(body);

    // Footer
    $('#fRow').append('<div class="text-center font-weight-bolder h3">' +
                     '<strong><u>هذا السند آلي حراري.. يجب تصويره للاحتفاظ به ولا يحتاج الى ختم أو توقيع..</u></strong></div>');
}
```

### 4.3 لا حسابات في الـ JS — كل الإجماليات من السيرفر

🟢 **نقطة إيجابية**: لا يوجد:
- لا جمع/طرح للأرقام في JS (كله من السيرفر)
- لا حسابات ضريبية في العميل
- لا تطبيق رسوم

🔴 **نقطة سلبية**: السيرفر هو **المصدر الوحيد للحقيقة** — التطبيق لا يعرض الرصيد المُتوقَّع بعد العملية إلا بقراءته من السيرفر.

---

## 5. الترميز والـ Encoding للعربية

### 5.1 ترميز الملف

📍 **`vReport.html`** يبدأ بـ:
```
BOM (UTF-8 BOM) + <meta charset="utf-8" />
```

📍 **داخل `report.js`** الكلمات العربية مُخزَّنة كـ `\u0633\u0646\u062F` (Unicode escapes):
```javascript
"\u0633\u0646\u062F\x20\u062A\u062D\u0635\u064A\u0644"  // = "سند تحصيل"
```

🟢 **جيد**: استخدام Unicode escapes آمن من مشاكل ترميز الملف.

### 5.2 اتجاه النص

📍 **`report.js`** — `document.body.dir = 'rtl'` يُضبط برمجياً.

📍 **التواريخ تُلَفّ بـ `<span dir=ltr>`** لتجنب قلب الأرقام:
```javascript
.replace('@fval', '<span dir=ltr>' + data.v_date + '</span>')
```

🟢 **جيد**: تعامل صحيح مع bidi للتواريخ.

### 5.3 الخط المستخدم

📍 **`vReport.html` (decoded)** style block:
```css
@media print {
    body { font-family: sans-serif !important; font-size: 2.75rem !important; }
}
.defaultfont { font-family: sans-serif !important; }
```

🟡 **اعتماد على `sans-serif` العامة فقط** — يعتمد على ما يوفّره النظام (قد يكون Noto Sans Arabic على Android حديث، أو خط رديء على إصدارات قديمة).

---

## 6. تحويل HTML إلى PDF

### 6.1 تهيئة الـ WebView المخفي

📍 **`Screens/web/j.java:123-149`** — `b(boolean z)`:
```java
public void b(boolean z) {
    this.f = z;                              // z=true → share, z=false → print
    LinearLayout linearLayout = new LinearLayout(this.f2421e);
    linearLayout.setBackgroundColor(-16776961);   // أزرق! (مخفي عملياً)
    linearLayout.setOrientation(0);
    WebView webView = new WebView(this.f2421e);
    this.f2418b = webView;
    linearLayout.addView(webView);
    this.f2418b.setLayoutParams(layoutParams);
    this.f2418b.setBackgroundColor(-1);

    this.f2418b.getSettings().setJavaScriptEnabled(true);
    this.f2418b.setWebViewClient(new WebViewClient());
    this.f2418b.getSettings().setDomStorageEnabled(true);
    this.f2418b.getSettings().setAllowFileAccess(true);
    this.f2418b.getSettings().setAllowContentAccess(true);
    this.f2418b.getSettings().setAllowUniversalAccessFromFileURLs(true);  // 🔴 ثغرة!

    if (Build.VERSION.SDK_INT >= 21) {
        this.f2418b.getSettings().setMixedContentMode(2);    // ALLOW (briefly)
        this.f2418b.getSettings().setMixedContentMode(0);    // 🔴 ALLOW (final)
    }
    this.f2418b.addJavascriptInterface(new c(null), "mobile");
    this.f2418b.loadUrl(this.f2419c);                        // = vReport.html
    this.f2418b.setWebChromeClient(new a(this));

    // 🔴 timeout ثابت! 3000ms للـ Bixolon، 6000ms للـ Sewoo
    new Handler().postDelayed(new b(),
        !c.b.a.c.e(this.f2421e).equals(this.f2421e.getString(R.string.sewoo)) ? 3000 : 6000);
}
```

### 6.2 الإعدادات الأمنية الخطرة

| الإعداد | القيمة | الخطر |
|---|---|---|
| `setAllowUniversalAccessFromFileURLs(true)` | true | 🔴 **CVE معروفة** — JS من ملف محلي يمكنه قراءة أي ملف محلي |
| `setMixedContentMode(0)` | ALLOW | 🔴 يسمح بـ HTTP داخل HTTPS |
| `setJavaScriptEnabled(true)` | true | 🟡 ضروري لكن يجب تقييد الـ scope |
| `addJavascriptInterface(c, "mobile")` | exposed | 🟡 يكشف `getPayReport`, `printRImage`, `getReportPrintCss` |

### 6.3 الإنشاء الفعلي للـ PDF

📍 **`a/a/b.java:303-336`** — `h()`:
```java
public String h() {
    PrintDocumentAdapter createPrintDocumentAdapter;
    CancellationSignal cancellationSignal;
    a.a.a aVar;
    try {
        PrintAttributes build = new PrintAttributes.Builder()
            .setMediaSize(PrintAttributes.MediaSize.ISO_C4)                  // 🔴 C4!
            .setResolution(new PrintAttributes.Resolution("pdf", "pdf",
                JposEntryEditorConfig.MIN_SUPPORTED_HEIGHT,                  // 100 dpi
                JposEntryEditorConfig.MIN_SUPPORTED_HEIGHT))                 // 100 dpi
            .setMinMargins(new PrintAttributes.Margins(0, 1, 0, 0))
            .build();

        File filesDir = this.f6b.getFilesDir();
        Long.valueOf(System.currentTimeMillis() / 1000).toString();          // 🔴 unused!
        File file = new File(filesDir.getPath() + "/voucher_.pdf");          // 🔴 fixed name!
        if (file.isFile() && file.exists()) {
            file.delete();
        }
        ProgressDialog progressDialog = new ProgressDialog(this.f6b);
        this.f5a = progressDialog;
        progressDialog.setMessage("Please wait");                            // 🔴 not localized!
        this.f5a.show();

        if (Build.VERSION.SDK_INT >= 21) {
            createPrintDocumentAdapter = this.f8d.createPrintDocumentAdapter("vdoc");
            cancellationSignal = new CancellationSignal();
            aVar = new a.a.a(this, filesDir, "voucher_.pdf", createPrintDocumentAdapter);
        } else {
            createPrintDocumentAdapter = this.f8d.createPrintDocumentAdapter();
            cancellationSignal = new CancellationSignal();
            aVar = new a.a.a(this, filesDir, "voucher_.pdf", createPrintDocumentAdapter);
        }
        createPrintDocumentAdapter.onLayout(build, build, cancellationSignal, aVar, null);
        return filesDir.getPath() + "/voucher_.pdf";
    } catch (Exception e2) {
        ...
        return "";
    }
}
```

### 6.4 اكتشافات الـ PDF

| # | الاكتشاف | الموقع | التقييم |
|---|---|---|---|
| 1 | حجم الورق **ISO C4** (229×324mm) للطباعة على رول 3-inch! | `b.java:308` | 🔴 غير منطقي — يجب أن يكون مخصصاً |
| 2 | الـ Resolution **100 dpi** (MIN_SUPPORTED) | `b.java:308` | 🟡 منخفض، لكن يكفي للطابعة الحرارية |
| 3 | اسم الملف **`voucher_.pdf` ثابت** | `b.java:311` | 🔴 يُكتب فوق السابق — لا تاريخ |
| 4 | `voucher_.pdf` في `context.getFilesDir()` | `b.java:309` | 🟢 جيد — internal storage |
| 5 | الـ timestamp يُحسَب لكن **لا يُستخدم** | `b.java:310` | 🔴 dead code |
| 6 | رسالة Progress **"Please wait"** بالإنجليزية! | `b.java:317` | 🟡 غير معرَّبة |
| 7 | لا حذف الملف بعد الطباعة | — | 🔴 PDFs قديمة تبقى |

---

## 7. الطباعة على Bixolon SPP-R310

### 7.1 المسار

📍 **`a/a/b.java:294-301`** — `g(String pdfPath)`:
```java
public void g(String str) {
    try {
        this.g.obtainMessage(0).sendToTarget();      // show ProgressDialog
    } catch (Exception e2) { e2.printStackTrace(); }
    new Thread(new a(str)).start();                  // run Bixolon thread
}
```

📍 **`a/a/b.java:48-85`** — Thread `a`:
```java
public void run() {
    try {
        if (c.b.a.d.f1852a == null) {
            c.b.a.d.f1852a = new com.egy.webpaymentapp.BixlonPrinterManger.b(b.this.f6b, b.this.f());
        }
        com.egy.webpaymentapp.BixlonPrinterManger.b bVar = c.b.a.d.f1852a;
        if (!(! (bVar.d().equals("JPOS_S_CLOSED") || bVar.c().equals("OFFLINE")))) {
            try {
                c.b.a.d.f1852a.a();                  // open + claim
            } catch (Exception e3) {
                b.this.g.obtainMessage(1, 0, 0, e3.getMessage()).sendToTarget();
                return;
            }
        }
        (c.b.a.d.f1852a.e(this.f10b)                   // printPDF
            ? b.this.g.obtainMessage(1, 0, 0, R.string.doc_printing_done)
            : b.this.g.obtainMessage(1, 0, 0, R.string.doc_printing_fail)
        ).sendToTarget();
    } catch (Exception e4) {
        b.this.g.obtainMessage(1, 0, 0, e4.getMessage()).sendToTarget();
    }
}
```

📍 **`BixlonPrinterManger/b.java:144-155`** — `e(String pdfPath)`:
```java
public boolean e(String str) {
    try {
        if (!this.f2327c.getDeviceEnabled()) {
            return false;
        }
        this.f2327c.printPDF(2, str, BXLConst.LINE_WIDTH_3INCH_203DPI, -2, 0, 2, 50);
        //                       ^ pdfFilePath
        //                                       ^ line width = 3 inch @ 203 DPI
        //                                                                  ^ -2 = scale to fit
        //                                                                       ^ 0 = page 0
        //                                                                          ^ 2 = align center
        //                                                                            ^ 50 = brightness
        return true;
    } catch (Exception e2) {
        e2.printStackTrace();
        return false;
    }
}
```

### 7.2 خصائص الطباعة

| العنصر | القيمة | المصدر |
|---|---|---|
| عرض الورق | 3 inch (76mm) @ 203 DPI | `BXLConst.LINE_WIDTH_3INCH_203DPI` |
| Model | `SPP-R310` (ثابت) | `BixlonPrinterManger/b.java:30` |
| API | JPOS (Java POS) | `import jpos.POSPrinter` |
| اتصال | Bluetooth Classic | `BluetoothAdapter.getDefaultAdapter().getRemoteDevice(MAC)` |
| Sync/Async | Async mode | `this.f2327c.setAsyncMode(true)` |
| MAC Storage | `APP_PRINTERADREES_KEY` في SharedPreferences | `c.b.a.c` |

### 7.3 اكتشافات Bixolon

🔴 **خطأ في معالجة الأحداث**:
📍 **`BixlonPrinterManger/b.java:33-61`**:
```java
class a implements OutputCompleteListener {
    public void outputCompleteOccurred(OutputCompleteEvent outputCompleteEvent) {
        // 🔴 فارغ — لا يبلّغ المستخدم بانتهاء الطباعة فعلياً
    }
}
class C0069b implements StatusUpdateListener {
    public void statusUpdateOccurred(StatusUpdateEvent statusUpdateEvent) {
        // 🔴 فارغ — لا يكتشف "Out of Paper" أو "Cover Open"
    }
}
class c implements ErrorListener {
    public void errorOccurred(ErrorEvent errorEvent) {
        // 🔴 فارغ — يبتلع أخطاء الطابعة!
    }
}
```

🔴 **اعتماد سلسلة Status hardcoded**:
📍 **`BixlonPrinterManger/b.java:129-141`**:
```java
public String c() {
    int powerState = this.f2327c.getPowerState();
    return powerState != 2001 ? powerState != 2004
        ? JposEntryConst.UNKNOWN_DEVICE_BUS
        : "OFFLINE"
        : "ONLINE";
}
public String d() {
    int state = this.f2327c.getState();
    return state != 1 ? state != 2 ? state != 3 ? state != 4 ? "Unknown State"
        : "JPOS_S_ERROR"
        : "JPOS_S_BUSY"
        : "JPOS_S_IDLE"
        : "JPOS_S_CLOSED";
}
```

🟡 **POSPrinter listeners تستلم Status updates** مثل:
- `(a & 8) > 0` = Battery Low
- `(a & 16) > 0` = Cover Open
- `(a & 64) > 0` = MSR Read status
- `(a & 32) > 0` = Paper Empty

لكن — كما يظهر في `a/a/b.java:251-269` — هذه فقط في مسار **Sewoo** (الـ Bitmap) وليس في Bixolon!

---

## 8. الطباعة على Sewoo (مسار بديل)

### 8.1 المسار

📍 **`Screens/web/j.java:55-71`** — Handler delayed:
```java
@Override // java.lang.Runnable
public void run() {
    try {
        if (j.this.f2417a == null) {
            j.this.f2417a = new a.a.b(j.this.f2421e, j.this.f2418b);
        }
        String h = j.this.f2417a.h();                       // create PDF
        if (j.this.f) {
            j.this.f2417a.c(h);                             // share path
        }
        if (c.b.a.c.e(j.this.f2421e).equals(R.string.r310_bixlion)) {
            j.this.f2417a.g(h);                             // Bixolon path
        }
        // 🔴 ملاحظة: لا else! إذا الطابعة Sewoo، يجب على JS استدعاء printRImage
    } catch (Exception e2) { ... }
}
```

### 8.2 آلية Sewoo (عبر JS Bridge)

📍 **`Screens/web/j.java:89-114`** — `printRImage(String base64)`:
```java
@JavascriptInterface
public void printRImage(String str) {
    Log.i("printbase64", "printbase64");
    a.a.b bVar = j.this.f2417a;
    try { ... }
    catch (Exception e2) { e2.printStackTrace(); bitmap = null; }

    if (bVar != null) {
        try {
            // strip "data:image/png;base64," prefix
            str2 = str.substring(str.indexOf(DefaultProperties.STRING_LIST_SEPARATOR) + 1);
        } catch (...) { str2 = ""; }
        if (!TextUtils.isEmpty(str2)) { str = str2; }
        byte[] decode = Base64.decode(str, 0);
        bitmap = BitmapFactory.decodeByteArray(decode, 0, decode.length);
        bVar.b(bitmap);                                     // print bitmap
    }
}
```

📍 **`a/a/b.java:251-274`** — `b(Bitmap bitmap)`:
```java
public void b(Bitmap bitmap) {
    c.b.a.d.a(this.f6b, f());                              // ensure printer connected
    c.b.a.e.a.a aVar = new c.b.a.e.a.a();
    try {
        Log.e("b", "IMG Width:" + bitmap.getWidth() + "  IMG Hight:" + bitmap.getHeight());
        int a2 = aVar.a(bitmap);
        if (a2 != 0) {
            String str = (a2 & 8) > 0  ? "Battery Low\r\n" : "";
            if ((a2 & 16) > 0) str += "Cover Open\r\n";
            if ((a2 & 64) > 0) str += "MSR Read status\r\n";
            if ((a2 & 32) > 0) str += "Paper Empty\r\n";
            Toast.makeText(this.f6b, "Status Error\n" + str, 1).show();
        }
    } catch (Exception e2) {
        Toast.makeText(this.f6b, e2.getMessage(), 1).show();
    }
}
```

🟢 **مسار Sewoo يكتشف Battery Low / Cover Open / Paper Empty** (على عكس Bixolon).

🔴 **رسائل الحالة بالإنجليزية**: "Battery Low", "Cover Open", "Paper Empty" — غير معرَّبة للمستخدم اليمني.

### 8.3 تحويل PDF → Bitmap (لـ Sewoo)

📍 **`a/a/b.java:184-201`** — `d(b bVar)`:
```java
public static void d(b bVar) {
    if (Build.VERSION.SDK_INT >= 21) {
        PdfRenderer pdfRenderer = new PdfRenderer(bVar.f7c);
        if (pdfRenderer.getPageCount() > 0) {
            PdfRenderer.Page openPage = pdfRenderer.openPage(0);   // 🔴 الصفحة 0 فقط!
            Bitmap createBitmap = Bitmap.createBitmap(
                openPage.getWidth(), openPage.getHeight(), Bitmap.Config.ARGB_8888);
            bVar.f9e = createBitmap;
            openPage.render(createBitmap, null, null, 2);          // RENDER_MODE_FOR_PRINT
            int height = (bVar.f9e.getHeight() - 20) - 20;
            bVar.f9e = Bitmap.createBitmap(bVar.f9e, 20, 20,
                r4.getWidth() - 40, height);                       // crop 20px margins
            openPage.close();
        }
        pdfRenderer.close();
    }
}
```

🔴 **اكتشاف**: تُحوَّل **الصفحة الأولى فقط** من PDF — إذا تجاوز الإيصال صفحة (بسبب C4 size!)، فإن البقية تُفقَد.

---

## 9. مشاركة الإيصال (Share)

### 9.1 الـ Intent

📍 **`a/a/b.java:276-292`** — `c(String pdfPath)`:
```java
public void c(String str) {
    File file = new File(str);
    try {
        this.f8d.loadUrl("javascript:removeCss()");                // remove print CSS from WebView
        Uri b2 = Build.VERSION.SDK_INT >= 24
            ? FileProvider.b(this.f6b, "com.egy.webpaymentapp", file)
            : Uri.fromFile(file);
        Intent intent = new Intent("android.intent.action.SEND");
        intent.setType("*/*");                                     // 🟡 should be "application/pdf"
        intent.setDataAndType(b2, "application/pdf");
        intent.putExtra("android.intent.extra.STREAM", b2);
        intent.addFlags(1);                                        // FLAG_GRANT_READ_URI_PERMISSION
        this.f6b.startActivity(Intent.createChooser(intent, "print to"));
        //                                                ^ 🔴 "print to" بالإنجليزية
    } catch (Exception e2) {
        Toast.makeText(context, R.string.save_report_fail, 0).show();
        e2.printStackTrace();
    }
}
```

🟡 **اكتشافات**:
- نوع MIME المحدد مزدوج: `setType("*/*")` ثم `setDataAndType(uri, "application/pdf")` — الثاني يفوز لكن الأول غير ضروري
- نص الـ chooser "print to" بالإنجليزية ولا يوصف الإجراء بدقة (يجب "مشاركة الإيصال")
- استخدام `FileProvider` صحيح لـ Android 7+

---

## 10. مخطط تسلسلي كامل (Sequence Diagram)

```
User                OprationsActivity      Server              j.java (WebView)    a.a.b (PDF)        Bixolon/Sewoo
 │                       │                    │                     │                   │                   │
 ├─ Press [Save]─────────►                    │                     │                   │                   │
 │                       ├──saveBillRequest───►                     │                   │                   │
 │                       ◄─Payinfo (v_no...)──┤                     │                   │                   │
 │                  show success UI            │                     │                   │                   │
 │                                            │                     │                   │                   │
 ├─ Press [Print]────────►                    │                     │                   │                   │
 │                  Gson.toJson(payinfo)──────────►new j()           │                   │                   │
 │                                            │       │             │                   │                   │
 │                                            │   create WebView    │                   │                   │
 │                                            │   load vReport.html │                   │                   │
 │                                            │   (decode unescape) │                   │                   │
 │                                            │       │             │                   │                   │
 │                                            │       JS: ReportData()                  │                   │
 │                                            │       JS: getPayReport() → bridge       │                   │
 │                                            │       JS: tafqeet(v_amt)                │                   │
 │                                            │       JS: build HTML                    │                   │
 │                                            │       JS: addCss('css/printcss.css')    │                   │
 │                                            │       │             │                   │                   │
 │                                            │       ⏱ wait 3000ms (hardcoded!)       │                   │
 │                                            │       │             │                   │                   │
 │                                            │       new a.a.b().h()─────────────────► │                   │
 │                                            │                     │ createPrintDocumentAdapter            │
 │                                            │                     │ ISO_C4 @ 100dpi                       │
 │                                            │                     │ → voucher_.pdf                        │
 │                                            │                     │                   │                   │
 │                                            │                     │ Bixolon path?─────►printPDF(...)     │
 │                                            │                     │ Sewoo path?       │ OR                │
 │                                            │                     │                   ├──PdfRenderer──►   │
 │                                            │                     │                   │  → Bitmap → BT    │
 │                                  Toast: doc_printing_done/fail   │                   │                   │
```

---

## 11. ملخص الاكتشافات والتقييم

### 🟢 نقاط إيجابية

| # | النقطة | الموقع |
|---|---|---|
| 1 | يستخدم Android Print Framework (PDF رسمي) | `a/a/b.java:308-329` |
| 2 | فصل البيانات (JSON) عن العرض (HTML) | `j.java:80-82` + `report.js` |
| 3 | الإيصال يُولَّد بعد تأكيد السيرفر فقط | `Screens/s.java:33-36` |
| 4 | بيانات الشركة + Footer "حراري" مُدمجة في القالب | `report.js[57]` |
| 5 | FileProvider لـ sharing (Android 7+ compliant) | `a/a/b.java:280` |
| 6 | Async Mode للطابعة Bixolon | `BixlonPrinterManger/b.java:104` |
| 7 | اكتشاف حالة الطابعة Sewoo (Battery/Cover/Paper) | `a/a/b.java:258-267` |
| 8 | دعم RTL برمجياً مع تغليف dir=ltr للتواريخ | `report.js` |

### 🟡 نقاط متوسطة

| # | الملاحظة | الموقع |
|---|---|---|
| 1 | اعتماد jQuery 3.0.0 + Bootstrap 4.5.3 (قديمة) | `vReport.html` |
| 2 | الخط `sans-serif` العام (لا خط مخصص) | `vReport.html` |
| 3 | mime type "*/*" مع `setDataAndType` متضارب | `a/a/b.java:282-283` |
| 4 | رسائل الطابعة بالإنجليزية (Battery Low...) | `a/a/b.java:258-267` |
| 5 | "Please wait" / "print to" بالإنجليزية | `a/a/b.java:317, 286` |

### 🔴 مشاكل حقيقية

| # | المشكلة | الموقع | الأثر |
|---|---|---|---|
| 1 | **HTML مُبهَّم بـ snapbuilder** (security through obscurity) | `vReport.html` | لا يحمي + يُصعِّب الصيانة |
| 2 | **timeout 3000ms ثابت** بين load و print | `j.java:148` | race condition: شبكة بطيئة → PDF فارغ |
| 3 | **اسم ملف PDF ثابت** `voucher_.pdf` | `b.java:311` | يُكتب فوق السابق، لا أرشيف |
| 4 | **حجم ورق ISO_C4** للطابعة 3-inch | `b.java:308` | ضياع PDF متعدد الصفحات |
| 5 | **Resolution 100 dpi (MIN)** | `b.java:308` | جودة منخفضة للنصوص الصغيرة |
| 6 | **`setAllowUniversalAccessFromFileURLs(true)`** | `j.java:140` | ثغرة CVE معروفة في WebView |
| 7 | **`setMixedContentMode(0)` = ALLOW** | `j.java:143` | يسمح بـ HTTP داخل HTTPS |
| 8 | **jQuery 3.0.0** (CVE-2019-11358, CVE-2020-11022) | `vReport.html` | XSS محتمل |
| 9 | **listeners الـ Bixolon كلها فارغة** | `BixlonPrinterManger/b.java:33-61` | لا يكتشف Paper Empty/Cover Open |
| 10 | **PdfRenderer يأخذ الصفحة 0 فقط** | `b.java:191` | فقدان صفحات إيصال طويل |
| 11 | **PDFs قديمة لا تُمسَح** | — | تراكم في `filesDir` |
| 12 | **POSPrinter Listeners empty** للأخطاء | `b.java:54-60` | يبتلع كل خطأ من الطابعة |
| 13 | **لا QR Code / Barcode** | — | صعب التحقق من السند لاحقاً |
| 14 | **لا توقيع رقمي** للإيصال | — | يمكن تزويره بسهولة |

---

## 12. توصيات الإصلاح

### الأولوية الحرجة (P0)

1. **إصلاح إعدادات WebView الأمنية**:
   ```java
   webView.getSettings().setAllowUniversalAccessFromFileURLs(false);
   webView.getSettings().setAllowFileAccessFromFileURLs(false);
   webView.getSettings().setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
   webView.getSettings().setAllowFileAccess(false);  // إذا غير ضروري
   ```

2. **استبدال timeout 3000ms بـ Promise/Callback من JS**:
   ```javascript
   function ReportData() {
       // ... build HTML
       window.mobile.onReportReady();   // signal Java
   }
   ```
   ```java
   @JavascriptInterface
   public void onReportReady() {
       // proceed to PDF generation
   }
   ```

### الأولوية العالية (P1)

3. **اسم PDF فريد** (يستخدم timestamp المحسوب لكن غير المُستَخدم!):
   ```java
   String ts = Long.toString(System.currentTimeMillis());
   File file = new File(filesDir.getPath() + "/voucher_" + ts + ".pdf");
   ```

4. **حجم ورق مخصص للطابعة 3-inch**:
   ```java
   .setMediaSize(new PrintAttributes.MediaSize("3inch", "3inch", 3000, 8000))
   .setResolution(new PrintAttributes.Resolution("pdf", "pdf", 203, 203))
   ```

5. **معالجة listeners الـ Bixolon**:
   - `errorListener` → Toast/UI feedback
   - `statusUpdateListener` → كشف Paper Empty
   - `outputCompleteListener` → تأكيد فعلي للطباعة

### الأولوية المتوسطة (P2)

6. **تحديث jQuery + Bootstrap** (أو إزالتهما لصالح Vanilla JS)
7. **إضافة QR Code للسند** (يحوي v_no + hash للتحقق)
8. **توقيع رقمي للإيصال** (HMAC من السيرفر مع v_no)
9. **عربنة كل النصوص** (Battery Low, print to, Please wait, ...)
10. **Cleanup للـ PDFs القديمة** (احتفظ بآخر 30 يوماً فقط)

---

## 13. مصادر التحقق

| الملف | الأسطر المهمة |
|---|---|
| `com/egy/webpaymentapp/Screens/s.java` | full (success handler) |
| `com/egy/webpaymentapp/Screens/p.java` | full (print button) |
| `com/egy/webpaymentapp/Screens/q.java` | full (share button) |
| `com/egy/webpaymentapp/Screens/web/j.java` | 80-82 (mobile bridge), 117-149 (WebView setup) |
| `com/egy/webpaymentapp/Screens/web/i.java` | 31-46 (JS interface ShareReport, printPdfReport) |
| `com/egy/webpaymentapp/Screens/web/l.java` | full (print runnable) |
| `com/egy/webpaymentapp/Screens/web/n.java` | full (share runnable) |
| `com/egy/webpaymentapp/BixlonPrinterManger/b.java` | full (POSPrinter wrapper) |
| `a/a/b.java` | 48-85 (Bixolon thread), 251-274 (Sewoo bitmap), 303-336 (PDF generation) |
| `a/a/a.java` | (FileDescriptor adapter for PrintDocumentAdapter callbacks) |
| `assets/myweb/vReport.html` | full (decoded) |
| `assets/myweb/js/report.js` | tafqeet + ReportDataObject |
| `assets/myweb/css/printcss.css` | print stylesheet |
| `webapi/models/Payinfo.java` | full (DTO with c_no, c_name, v_amt, v_no, comp_*, user_name) |

---

**🔑 الخلاصة**: المعمارية الهجينة (HTML/JS → PDF → Printer) **معقَّدة لكنها تعمل**. أكبر مشاكلها: timeout صلب، إعدادات WebView خطيرة، listeners فارغة، حجم ورق خاطئ، اسم ملف ثابت. الإصلاحات المُقترَحة قابلة للتطبيق دون إعادة كتابة كاملة.
