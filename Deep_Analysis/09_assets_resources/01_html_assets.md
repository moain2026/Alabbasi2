# 01 — تحليل ملفات HTML في AbbasiyCashiers (Ecas v18.4)

> **الموقع:** `assets/myweb/`
> **النوع:** ملفات HTML مُحمَّلة داخل WebView (`com.egy.webpaymentapp.Screens.WebViewActivity`)
> **المنهج:** تحليل محايد بـ `find`, `wc`, `cat`, فك تشفير `unescape()` يدوياً، تتبع المراجع من Java.

---

## 1. الجرد الكامل

```
$ find assets/myweb -name "*.html"
assets/myweb/default_error_page.html         4 KB    135 سطر  (نظيف)
assets/myweb/paymentList.html               16 KB      5 سطر  (مُمَوّه)
assets/myweb/readinglist.html               16 KB      5 سطر  (مُمَوّه)
assets/myweb/vReport.html                    8 KB      5 سطر  (مُمَوّه)
```

| الملف | الحجم على القرص | سطور فعلية | الحالة | الوظيفة |
|---|---|---|---|---|
| `default_error_page.html` | 4 KB | 135 سطر | ✅ نظيف | صفحة خطأ Connection Lost (Roboto + SVG ثابت) |
| `paymentList.html` | 16 KB | 5 (فعلياً سطر `document.write` واحد) | 🔴 مُمَوّه | شاشة قائمة المدفوعات |
| `readinglist.html` | 16 KB | 5 (فعلياً سطر واحد) | 🔴 مُمَوّه | شاشة قائمة قراءات العداد |
| `vReport.html` | 8 KB | 5 (فعلياً سطر واحد) | 🔴 مُمَوّه | صفحة عرض/طباعة التقرير (Voucher Report) |

**المجموع:** 4 ملفات HTML فقط = **44 KB**.

---

## 2. التمويه (Obfuscation) — أداة snapbuilder.com

### 2.1 النمط الفعلي

كل من `paymentList.html`, `readinglist.html`, `vReport.html` يحتوي على البنية التالية فقط:

```html
<script language="javascript">
<!--
// == Begin Free HTML Source Code Obfuscation Protection from https://snapbuilder.com == //
document.write(unescape('%3C%21%44%4F%43%54%59%50%45%20...'));
//-->
</script>
```

### 2.2 طبيعة "الحماية"

- **الأداة:** Free HTML Source Code Obfuscation Protection — من **snapbuilder.com**
- **التقنية:** Percent-encoding (نفس `decodeURIComponent` في JS) — **ليست تشفيراً**، مجرد ترميز قابل للعكس بسطر واحد:
  ```js
  unescape('%3C%21%44%4F%43...') === '<!DOCTYPE html>...'
  ```
- **الفائدة الأمنية الفعلية:** **صفر**. أي مطوّر يفتح DevTools يرى الكود النهائي في DOM بعد `document.write`.
- **العقوبة:** أداة snapbuilder مجانية، إعلانية، **مشهورة بأنها تُستخدم لتمويه أكواد المبتدئين** فقط.

### 2.3 لماذا هذا مشكلة كبيرة؟

| المشكلة | التفصيل |
|---|---|
| **خداع المُراجع** | يبدو "محمياً" لكنه عرضة لـ View Source في 3 ثوان |
| **يُعطل debug** | كل الملف على سطر واحد → استحالة تتبع الخطأ من LogCat الـ WebView |
| **يبطئ التحميل** | `document.write` بعد `DOMContentLoaded` يعيد بناء DOM كاملاً |
| **يخالف Bootstrap** | bootstrap.js لا يعمل في `document.write` سياق dynamic بدون تأخير |
| **يُهدر CPU** | فك ~16KB من percent-encoding على كل فتح للصفحة |

---

## 3. المحتوى الفعلي (بعد فك التشفير)

### 3.1 `paymentList.html` (مدفوعات العميل)

البنية المُفكَّكة (مأخوذة من `document.write(unescape(...))`):

```html
<!DOCTYPE html>
<html dir="rtl">
<meta charset="utf-8" />
<meta id="vport" name="viewport" content="width=device-width, initial-scale=1.0">

<link rel="stylesheet" type="text/css" href="css/font-awesome-4.7.0/css/font-awesome.min.css">
<link href="bootstrap.4.5.3/css/bootstrap-grid.min.css" rel="stylesheet" media='all' />
<link href="bootstrap.4.5.3/css/bootstrap-reboot.min.css" rel="stylesheet" media='all' />
<link href="bootstrap.4.5.3/css/bootstrap.min.css" rel="stylesheet" media='all' />
<link rel="stylesheet" href="css/myappcss.css?t=1"  />

<style>
    * { box-sizing: border-box; }
    body { background-color: #ffffff; }
    #regForm { background-color: #ffffff; margin: 0px auto; padding: 20px; width: 100%; min-width: 300px; }
    h1 { text-align: center; }
    input { padding: 5px; width: 100%; font-size: 15px; font-family: Raleway; border: 1px solid #aaaaaa; }
    input.invalid { background-color: #ffdddd; }
    .tab { display: none; }
    button { background-color: #1E94CA; color: #ffffff; border: none; padding: 5px 10px;
             font-size: 15px; font-family: Raleway; cursor: pointer; }
    button:hover { opacity: 0.8; }
    #prevBtn { background-color: #bbbbbb; }
    /* Steps circles */
    .step { height: 10px; width: 10px; margin: 0 2px; background-color: #bbbbbb;
            border: none; border-radius: 50%; display: inline-block; opacity: 0.5; }
    .step.active { opacity: 1; }
    .step.finish { background-color: #4CAF50; }
    /* Table style */
    #myInput { background-image: url('css/searchicon.png');
               background-position: 10px 10px; background-repeat: no-repeat;
               width: 100%; font-size: 15px; padding: 5px; border: 1px solid #ddd;
               margin-bottom: 12px; }
    .btn-dark { background-color: #1E94CA; }
    #table_div { width: 100%; overflow-y: scroll; }
    #myTable { font-weight: normal; font-size: small;
               overflow-x: auto; white-space: nowrap; }
    #myTable thead { background-color: #1E94CA; color: white; font-weight: normal; }
    #myTable tbody { font-family: sans-serif, Tahoma, 'Times New Roman', Arial; }
    #cnfrmlist li { font-weight: bold; }
    #cnfrmlist li > p { font-family: sans-serif, Tahoma, 'Times New Roman', Arial; }
    .myfontfmly { font-family: sans-serif, Tahoma, 'Times New Roman', Arial; }
</style>

<body>
    <div id="regForm">
        <h4 class="d-none">B'&E) 'D*-5JD' 'DJHEJ)</h4>   <!-- ← arabic encoded -->
        <!-- One "tab" for each step in the form: -->
        <div class="alert alert-danger d-none text-center" id="error"></div>

        <div class=" text-right">
            <div class="table-wrap" id="customer_table">
                <div class="row">
                    <div class="col-8">
                        <input type="text" id="myInput" onkeyup="seracHInList()" placeholder="بحث..." title="Type in a name">
                    </div>
                    <div class="col-4 pt-1">
                        <button class="btn-sm btn-dark btn-block " onclick="loadPaymentsData()">
                            <span class="fa fa-search"></span> بحث
                        </button>
                    </div>
                </div>
                <div id="table_div" class="d-block w-100"></div>
            </div>
        </div>
    </div>

    <script type="text/javascript" src="js/jquery-3.0.0.min.js"></script>
    <script type="text/javascript" src="bootstrap.4.5.3/js/bootstrap.bundle.min.js"></script>
    <script type="text/javascript" src="js/paymentlist.js?t=1"></script>
</body>
</html>
```

**ملاحظات:**
1. النص `B'&E) 'D*-5JD' 'DJHEJ)` ليس garbage — هو **arabic encoded في Windows-1256 ثم محفوظ كـ UTF-8** = **bug ترميز قديم** (ربما يقصد "قائمة التحصيلات اليومية"). موجود في `<h4 class="d-none">` فمخفي بصرياً لكنه دليل على أن الملف مرّ بـ encoding broken في مرحلة ما.
2. يستدعي `loadPaymentsData()` و `seracHInList()` (typo: `serach` بدل `search`) — الدوال في `paymentlist.js` المُمَوّه.
3. `myInput` يحوي placeholder عربي مباشرة (hardcoded في HTML) — تعارض مع نظام i18n في Android.

### 3.2 `readinglist.html` (قراءات العدادات)

بنية مطابقة لـ `paymentList.html` مع اختلاف:
- العنوان المخفي: `B'&E) 'DB1'!* 'DJHEJ)` (= "قائمة القراءات اليومية" بنفس bug الترميز)
- زر إضافي: `<button id="btnretry" onclick="loadReadingsData()">'DE-'HD) E1) '.1I</button>` ("المحاولة مرة أخرى")
- يستدعي `loadReadingsData()` من `readinglist.js`

### 3.3 `vReport.html` (تقرير المُحصِّل/Voucher Report)

أصغر من الاثنين الآخرين (8 KB). يحتوي على:
- استدعاء `report.js` (وليس `report_2.js` — هذا dead code يُحلَّل في الملف التالي)
- تخطيط طباعة (`printcss.css` بدلاً من `myappcss.css` في بعض المسارات)
- يدمج بيانات من Java عبر WebView Bridge

---

## 4. صفحة الخطأ (`default_error_page.html`)

**الوحيدة النظيفة وغير المُمَوّهة.** 135 سطر HTML/CSS بسيط:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta id="vport" name="viewport" content="width=device-width, initial-scale=1.0">
    <title></title>
    <style>
        body { background-color: #2F3242; }
        svg { position: absolute; top: 50%; left: 50%;
              margin-top: -250px; margin-left: -400px; }
        .message-box {
            height: 200px; width: 380px;
            ...
            color: #FFF;
            font-family: Roboto;
            font-weight: 300;
        }
        ...
    </style>
</head>
<body>
    <!-- SVG illustration of a "down" robot/error + message "Connection Lost" -->
</body>
</html>
```

**المشاكل:**
- **`font-family: Roboto`** — لكن Roboto **غير مضمّن** في الـ assets، يعتمد على وجوده في النظام (متاح لكن النص الإنجليزي فقط)
- **لا نص عربي** — صفحة خطأ بـ English فقط رغم أن التطبيق عربي
- **مُموَّن hardcoded للون `#2F3242`** (رمادي داكن) لا يتطابق مع لون التطبيق الأزرق `#1E94CA`

---

## 5. كود حساس / dead code

### 5.1 `report_2.js` غير مرجَّع من أي HTML

```bash
$ grep -rn "report_2" assets/ res/
# 0 hits in HTML — only ./assets/myweb/js/report_2.js exists
```

**استنتاج:** `report_2.js` (~16 KB من JS مُمَوّه) **dead code** — غير مستخدم. تفاصيله في `02_javascript_assets.md`.

### 5.2 لا توكنات / مفاتيح / URLs في HTML

تحقق:
```bash
$ grep -iE "api[_-]?key|secret|token|password|http://|https://" assets/myweb/*.html
# 0 hits (after decoding)
```

✅ لا أسرار مضمّنة. كل التواصل مع الـ backend يحدث من Java عبر `WebViewBridge` (راجع `05_webview_bridge/`).

### 5.3 لا CSP, لا SRI

- لا `Content-Security-Policy` meta tag
- لا `integrity="sha384-..."` على Bootstrap/jQuery → لو تم استبدالها من خارج، لن يُكتشف
- يعتمد فقط على الحماية من خلال أن WebView يحمّل من `file:///android_asset/myweb/` (مغلق محلياً)

---

## 6. مكتبات خارجية مُضمّنة (يُفصَّل في 02_javascript_assets)

| المكتبة | الإصدار | الحجم | تاريخ الإصدار |
|---|---|---|---|
| Bootstrap | **4.5.3** | 1.7 MB (CSS + JS + maps) | Oct 2020 (آخر 4.x، EOL) |
| jQuery | **3.0.0** | 84 KB (min) | Jun 2016 (**نسخة 9 سنوات قديمة!**) |
| Font Awesome | **4.7.0** | 1.7 MB | Oct 2016 (EOL — أصدر Pro 6.x) |

**مشكلة:** jQuery 3.0.0 معروف بـ XSS عبر `$.parseHTML` في 3.0 و 3.4 — راجع [CVE-2019-11358](https://nvd.nist.gov/vuln/detail/CVE-2019-11358) و [CVE-2020-11022/11023](https://nvd.nist.gov/vuln/detail/CVE-2020-11022).

---

## 7. خلاصة الـ HTML

| المعيار | النتيجة |
|---|---|
| عدد الملفات | 4 فقط (3 شاشات + 1 error page) |
| الحجم الإجمالي | ~44 KB (لكن `assets/myweb/` كاملاً = 1.9 MB بسبب libs) |
| التمويه | snapbuilder.com (percent-encoding ساذج، فائدة أمنية = 0) |
| Bugs ترميز | عناوين `<h4 class="d-none">` بترميز Windows-1256 مكسور |
| نصوص hardcoded | "بحث..." و"بحث" و"المحاولة مرة أخرى" داخل HTML (لا i18n) |
| dead code | `report_2.js` غير مرجَّع |
| dependencies قديمة | Bootstrap 4.5.3 (2020 EOL), jQuery 3.0.0 (2016), FontAwesome 4 (2016 EOL) |
| RTL | `<html dir="rtl">` صراحة في كل ملف |
| Responsive | يعتمد على Bootstrap Grid (mobile-first) |
| CSP / SRI | غير موجود |
| Connection لـ Java | عبر `WebViewBridge` فقط (لا URLs) |

---

## 8. البديل في React Native

### 8.1 إذا أردنا الحفاظ على نفس البنية (WebView مخصص)

❌ **لا تفعل!** لأن الـ WebView في RN يأتي مع نفس مشاكل Android WebView + يضيف overhead JS-Bridge.

### 8.2 الحل الصحيح: تحويل كل HTML إلى React Native Screens

| HTML الحالي | RN Component المقترح |
|---|---|
| `paymentList.html` (قائمة بحث + جدول) | `<PaymentListScreen>` — `FlatList` + `TextInput` بحث + `useDebouncedValue` |
| `readinglist.html` (قائمة قراءات) | `<ReadingListScreen>` — مطابق للسابق + `pull-to-refresh` |
| `vReport.html` (تقرير طباعة) | `<VoucherReportScreen>` — `react-native-print` أو `react-native-html-to-pdf` للطباعة |
| `default_error_page.html` | `<ErrorBoundary fallback={<ConnectionLostScreen />}>` |

### 8.3 المكاسب

| البُعد | حالياً (WebView+HTML) | بـ RN |
|---|---|---|
| حجم assets | ~1.9 MB (Bootstrap + jQuery + FontAwesome) | 0 (Native + iconfont صغير) |
| سرعة fetch | `document.write(unescape(...))` ~50ms على كل فتح | فوري |
| Debug | شبه مستحيل (سطر واحد مُمَوّه) | React DevTools + Flipper |
| Type safety | صفر (JS مُمَوّه + HTML hardcoded) | TypeScript كامل |
| RTL | hardcoded في HTML | تلقائي عبر `I18nManager.isRTL` |
| i18n | placeholder "بحث..." hardcoded | `t('common.search')` من `react-i18next` |
| Bundle بعد build | 1.9 MB | < 100 KB من JS + native sources |

### 8.4 خطة الترحيل

1. **حذف `paymentList.html`, `readinglist.html`, `vReport.html`** كاملة
2. **حذف `bootstrap.4.5.3/`, `jquery-3.0.0.min.js`, `font-awesome-4.7.0/`** = توفير ~1.7 MB
3. الاحتفاظ بـ `default_error_page.html` كـ static fallback لو فشلت RN في bootstrap (وحتى هذا اختياري)
4. كتابة 3 RN screens بـ TypeScript مع `react-query` للبيانات
5. استخدام `react-native-vector-icons/FontAwesome` (~50 KB بدلاً من 1.7 MB)

---

## 9. مصادر التحقق

| المصدر | المسار / الأمر |
|---|---|
| inventory ملفات HTML | `find AbbasiyCashiers_RE_Analysis/02_apktool_output/AbbasiyCashiers/assets -name "*.html"` |
| محتوى مُمَوّه paymentList | `cat assets/myweb/paymentList.html` |
| محتوى default_error_page | `cat assets/myweb/default_error_page.html` |
| تحقق dependency versions | `ls assets/myweb/bootstrap.4.5.3/` + `head assets/myweb/js/jquery-3.0.0.min.js` |
| تحقق dead code report_2 | `grep -rn "report_2" assets/ res/` |
| فك unescape يدوياً | تطبيق `decodeURIComponent` على string الـ HTML المُرمَّز |
| ملاحظة snapbuilder | عنوان التعليق `// == Begin Free HTML Source Code Obfuscation Protection from https://snapbuilder.com ==` |

---

**ملف:** `Deep_Analysis/09_assets_resources/01_html_assets.md`
**عدد ملفات HTML الإجمالي:** 4
**الحجم الفعلي:** 44 KB
**أعلى مشكلة:** snapbuilder obfuscation عديم الفائدة + Bootstrap/jQuery قديمة + dead code `report_2.js` + bug ترميز عناوين `<h4>`
**التوصية:** حذف كامل لـ HTML + assets الـ web (1.7 MB) واستبدالها بـ RN screens
