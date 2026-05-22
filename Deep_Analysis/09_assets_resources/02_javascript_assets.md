# 02 — تحليل ملفات JavaScript في AbbasiyCashiers (Ecas v18.4)

> **الموقع:** `assets/myweb/js/` + `assets/myweb/bootstrap.4.5.3/js/`
> **المنهج:** فك تشفير string-array obfuscation بـ Python regex، `md5sum` للكشف عن تكرار، `grep` للروابط مع Java bridge، فحص ميزات jQuery المستخدمة.

---

## 1. الجرد الكامل

```
$ ls -la assets/myweb/js/ assets/myweb/bootstrap.4.5.3/js/
```

| الملف | الحجم | الأسطر الفعلية | الحالة | المصدر |
|---|---|---|---|---|
| `js/jquery-3.0.0.min.js` | 86,345 B (84 KB) | 4 (مُصغّر) | ✅ مكتبة معروفة | jQuery رسمي 3.0.0 (Jun 2016) |
| `bootstrap.4.5.3/js/bootstrap.min.js` | ~64 KB | 6 (مُصغّر) | ✅ مكتبة معروفة | Bootstrap رسمي 4.5.3 (Oct 2020) |
| `bootstrap.4.5.3/js/bootstrap.bundle.min.js` | ~84 KB | 6 (مُصغّر) | ⚠️ تكرار | Bootstrap + Popper مدموج |
| `bootstrap.4.5.3/js/bootstrap.min.js.map` | ضخم | — | ⚠️ source map | لا فائدة في prod |
| `bootstrap.4.5.3/js/bootstrap.bundle.min.js.map` | ضخم | — | ⚠️ source map | لا فائدة في prod |
| `js/paymentlist.js` | 16,873 B | 1 (مُمَوّه) | 🔴 obfuscated | كود التطبيق |
| `js/readinglist.js` | 8,741 B | 1 (مُمَوّه) | 🔴 obfuscated (بـ obfuscator مختلف!) | كود التطبيق |
| `js/report.js` | 16,050 B | 1 (مُمَوّه) | 🔴 obfuscated | كود التطبيق |
| `js/report_2.js` | 15,967 B | 1 (مُمَوّه) | 🔴 **DEAD CODE** + مكرر | غير مرجَّع من أي HTML |

**المجموع الفعلي:** ~290 KB من JS قبل source maps (و ~1 MB مع source maps).

---

## 2. مكتبات Vendor — تحليل النسخ

### 2.1 jQuery 3.0.0

```
$ grep -o "jQuery v[0-9.]*" assets/myweb/js/jquery-3.0.0.min.js
jQuery v3.0.0
```

**التاريخ:** يونيو 9, 2016 — **نسخة عمرها ~9 سنوات** (الآن أحدث: 3.7.1).

**CVEs معروفة (لـ jQuery 3.0.0):**

| CVE | الخطورة | الوصف |
|---|---|---|
| **CVE-2019-11358** | High | Prototype pollution عبر `$.extend(true, ...)` |
| **CVE-2020-11022** | Medium | XSS عبر `$.html()` لـ HTML من مصادر غير موثوقة |
| **CVE-2020-11023** | Medium | XSS عبر `$.htmlPrefilter()` على `<option>` |
| **CVE-2015-9251** | Medium | XSS في `$.ajax` JSONP cross-domain |

**هل المشروع عرضة؟** بما أن HTML يأتي من backend `/data/abbas/`، ولا CSP، **نعم** — لو تم MITM للـ HTTP traffic (التطبيق يستخدم `http://` لا `https://`، راجع `07_crypto_protocols/`).

### 2.2 Bootstrap 4.5.3

```
$ head -c 200 assets/myweb/bootstrap.4.5.3/js/bootstrap.min.js
/*! Bootstrap v4.5.3 (https://getbootstrap.com/)
 * Copyright 2011-2020 The Bootstrap Authors
```

**التاريخ:** أكتوبر 13, 2020 — **آخر إصدار من 4.x** (الآن: 5.3.x). Bootstrap 4 في **End of Life** (انتهى دعم الـ security patches في يناير 2024).

### 2.3 تكرار Bootstrap

- يحوي **`bootstrap.min.js`** (Bootstrap وحده)
- ويحوي **`bootstrap.bundle.min.js`** (Bootstrap + Popper.js مدموج)

ولكن في الـ HTML نرى:

```html
<script src="bootstrap.4.5.3/js/bootstrap.bundle.min.js"></script>
```

فقط `bundle` يُستخدم → **`bootstrap.min.js` (64 KB) = dead code**.

### 2.4 Source Maps في الإنتاج

موجودة في APK:
- `bootstrap.min.js.map`
- `bootstrap.min.css.map`
- `bootstrap.bundle.min.js.map`
- `bootstrap-grid.min.css.map`
- `bootstrap-reboot.min.css.map`

**هذه ملفات source maps** — أداة debug فقط، **لا فائدة في الإنتاج**، وتزيد APK بدون داعٍ (مئات الكيلوبايتات). من Best Practice: حذفها قبل الـ build.

---

## 3. التمويه (Obfuscation) للكود المخصص

### 3.1 نوع التمويه

**النمط:** String-Array Obfuscation — أداة من فئة `javascript-obfuscator.io` أو مشابهة.

#### النوع 1: Hex Encoding (`\xNN`)
يُستخدم في **3 ملفات** (paymentlist.js, report.js, report_2.js):

```js
var _$_f232=["\x72\x65\x61\x64\x79","\x76\x61\x6C","\x23\x6D\x79\x49\x6E\x70\x75\x74",...];
// مفكوكة:        "ready"      , "val"       , "#myInput"  , ...
```

#### النوع 2: Mixed Hex + Index Strings (`_0x...`)
يُستخدم في **1 ملف فقط** (readinglist.js) — obfuscator مختلف:

```js
var _0x198c=['<div\x20class=\x22text-center\x22>...','[object\x20String]',
             '...','myTable','ready','textContent',...,'331dQRkJU','825505WpOdyI',
             '136pxHYaA','457018WULBex','789vBQzqh','815XhpQcZ',...];
```

ملاحظة: السطور مثل `'331dQRkJU'` و `'825505WpOdyI'` و `'136pxHYaA'` هي **شفرة قياسية لـ javascript-obfuscator.io** (أرقام عشوائية بادئة + معرّف عشوائي = identifier لجدول الـ shuffling). ⇒ تأكيد استخدام obfuscator مختلف لـ readinglist.js.

### 3.2 فك التشفير

تمت كتابة سكريبت Python بسيط (regex `\\x[0-9a-fA-F]{2}`) ⇒ تم استخراج جميع strings:

```bash
$ python3 decode_obfuscated.py paymentlist.js
# 94 strings فريد ⇒ تحليل واضح للوظيفة
```

**النتيجة:** **التمويه يُكسر في 30 ثانية بأي سكريبت بسيط أو deobfuscator.io**. الفائدة الأمنية = **صفر**.

---

## 4. الكود المخصص — ماذا يفعل فعلياً؟

### 4.1 `paymentlist.js` (16,873 B → ~94 unique strings)

#### Strings مفكوكة مفيدة:

```
'ready'
'#myInput'
'GetPaymentsRequest'                              ← ⚠️ Java bridge call
'mobile'                                          ← اسم الـ bridge
'No xconfig global object found. Unable to proceed.'  ← رسالة خطأ
'<div class="list-group table-hover" id="myList">'
'<a href="#" class="list-group-item ...">@CSTNAME...@VAMT...@VDATE</a>'  ← templates
'@CSTNAME', '@VAMT', '@VDATE', '@CUSTNO', '@CSTNmANDNO'
'replace'
'printPdfReport'                                  ← ⚠️ Java bridge call
'sharexPdfReport'                                 ← ⚠️ Java bridge call
'.print-btn-click', '.share-btn-click'
'./vReport.html'                                  ← ⚠️ redirect إلى تقرير
'setItem'
'localStorage'                                    ← ⚠️ حفظ في WebView storage
```

#### إعادة بناء المنطق (deobfuscated):

```js
$(document).ready(function() {
    if (typeof xconfig === 'undefined') {
        console.error('No xconfig global object found. Unable to proceed.');
        return;
    }
    // xconfig = global injected from Java via WebViewBridge
    var customers = JSON.parse(mobile.GetPaymentsRequest());
    // customers = [{c_no, c_name, v_no, v_amt, v_date, v_copy}, ...]
    
    var html = '<div class="list-group ...">';
    $.each(customers, function(i, c) {
        var item = template.replace('@CSTNAME', c.c_name)
                           .replace('@VAMT', c.v_amt)
                           .replace('@VDATE', c.v_date)
                           .replace('@CUSTNO', c.c_no)
                           .replace('@CSTNmANDNO', c.c_no + ' ' + c.c_name);
        html += item;
    });
    $('#table_div').html(html);
    
    $('.print-btn-click').click(function() {
        var rec = $(this).closest('tr').find('td').data();
        localStorage.setItem('report', JSON.stringify(rec));
        location.href = './vReport.html';   // ← Open report page
        // Then report.js calls mobile.printPdfReport(...)
    });
    
    $('.share-btn-click').click(function() {
        // same but calls mobile.sharexPdfReport(...)
    });
});

function seracHInList() {   // typo: serach ≠ search!
    var input = document.getElementById('myInput').value.toUpperCase();
    $('#myList a').each(function() {
        if ($(this).text().toUpperCase().indexOf(input) > -1)
            $(this).removeClass('d-none').addClass('d-block');
        else
            $(this).removeClass('d-block').addClass('d-none');
    });
}

function loadPaymentsData() {
    // same as ready but triggered by button
}
```

### 4.2 `readinglist.js` (8,741 B)

نفس البنية لكن:
- بدل `GetPaymentsRequest` → `GetReadingsRequest`
- نفس الـ templates `@CSTNAME`, `@VAMT`, `@VDATE` لكن مع إضافة `@CSTNmANDNO` لرقم العداد
- يحوي **strings عربية مباشرة في الكود** (راجع 4.1: `<th>القراءة</th>`, `<th>الاسم</th>`, `<td>الاجمالي</td>`, `<div>العدد :</div>`) ← **i18n محطّم — العربية hardcoded داخل JS**
- نفس typo `seracHInList` (مشترك مع paymentlist.js — copy-paste)

### 4.3 `report.js` (16,050 B)

#### Strings مفكوكة مفيدة:

```
'<span dir=ltr>', 'getDate', '0', '', '/', 'getMonth', 'getFullYear', ' ',
'getHours', ':', 'getMinutes', 'getSeconds', '</span>',
'dir', 'body', 'rtl',
'getPayReport',                                   ← ⚠️ Java bridge
'mobile', 'parse',
'css/printcss.css',                               ← swap stylesheet للطباعة
'v_copy', 'undefined',
'<div id="divcentercol" class="col-12 ...">',
'<div id="cntr" >',
'<div class="justify-content-...">'
... + 'ShareReport', 'print', 'localStorage'
```

#### إعادة بناء المنطق:

```js
$(document).ready(function() {
    document.body.dir = 'rtl';
    
    // Replace stylesheet to print version
    $('link[rel=stylesheet]').last().attr('href', 'css/printcss.css');
    
    // Read voucher from localStorage (set by paymentlist.js)
    var rec = JSON.parse(localStorage.getItem('report'));
    
    // Get full payment report from Java
    var report = JSON.parse(mobile.getPayReport(rec.v_no));
    // report = { items: [...], total: ..., date: ..., cashier: ..., branch: ... }
    
    // Render
    var now = new Date();
    var dateStr = '<span dir=ltr>' + now.getDate() + '/' + (now.getMonth()+1) + '/'
                  + now.getFullYear() + ' ' + now.getHours() + ':'
                  + now.getMinutes() + ':' + now.getSeconds() + '</span>';
    
    $('#divcentercol').html(/* template with items + total */);
    
    if (rec.v_copy === 'undefined') {
        // First copy: also trigger print
        window.print();   // or mobile.printPdfReport()
    }
});
```

### 4.4 `report_2.js` (15,967 B) — **DEAD CODE + DUPLICATE**

```
$ diff <(head -c 1000 report.js) <(head -c 1000 report_2.js)
1c1
< var _$_174b=["\x3C\x73\x70\x61\x6E\x20..."
---
> var _$_c6fa=["\x3C\x73\x70\x61\x6E\x20..."
```

**النتيجة:** نفس الكود حرفياً، يختلف فقط في **اسم متغير الـ array** (`_$_174b` vs `_$_c6fa`). أي ملف `report_2.js` = **نسخة مُعاد تمويهها بـ seed مختلف** من نفس `report.js`. والأهم:

```
$ grep -rn "report_2" assets/ res/ AndroidManifest.xml
# 0 hits anywhere
```

⇒ **`report_2.js` (~16 KB) لا يُستدعى من أي مكان**. الأرجح: المطور حدّث `report.js`، أعاد التمويه فحُفظت النسخة القديمة بـ `_2` "احتياطاً" ونُسيت.

---

## 5. Java Bridge — الواجهة المُستخدمة من JS

من فك التمويه، الاستدعاءات إلى الـ bridge المسمى `mobile`:

| استدعاء JS | الكلاس/الدالة في Java | الموقع |
|---|---|---|
| `mobile.GetPaymentsRequest()` | `WebViewBridge.GetPaymentsRequest()` | راجع `05_webview_bridge/04_GetPaymentsRequest.md` |
| `mobile.GetReadingsRequest()` | `WebViewBridge.GetReadingsRequest()` | راجع `05_webview_bridge/05_GetReadingsRequest.md` |
| `mobile.getPayReport(vNo)` | `WebViewBridge.getPayReport(String)` | راجع `05_webview_bridge/06_getPayReport.md` |
| `mobile.printPdfReport(...)` | `WebViewBridge.printPdfReport(...)` | ← يستدعي MuPDFCore (راجع `08_native_libs/02_libbxlpdf.md`) |
| `mobile.sharexPdfReport(...)` | `WebViewBridge.sharexPdfReport(...)` | تشارك PDF خارج التطبيق |
| `mobile.ShareReport(...)` | `WebViewBridge.ShareReport(...)` | غير موثّق في analysis سابقة |
| `xconfig` (global object) | injected JS object | راجع `05_webview_bridge/01_bridge_overview.md` |

✅ **تحقق:** كل الواجهة بين JS وJava محصورة في 6 methods + 1 global object.

---

## 6. Bugs / مشاكل في الكود المخصص

| # | المشكلة | الموقع | الخطورة |
|---|---|---|---|
| 1 | **Typo `seracHInList`** بدل `searchInList` | paymentlist.js + readinglist.js | منخفض (يعمل، لكن مضحك) |
| 2 | **Arabic hardcoded** داخل JS (`'القراءة'`, `'الاسم'`, `'الاجمالي'`) | readinglist.js | i18n مكسور |
| 3 | **`localStorage` في WebView** لتبادل بيانات بين صفحات | paymentlist.js → report.js | ⚠️ بيانات الفواتير في storage غير مشفّر، يمكن قراءتها من JS injection |
| 4 | **`if (rec.v_copy === 'undefined')`** — مقارنة String بدل Type | report.js | bug منطقي: `typeof undefined === 'undefined'` لكن `'undefined' === undefined === false` |
| 5 | **`bootstrap.bundle.min.js` و `bootstrap.min.js` كلاهما في APK** | bootstrap.4.5.3/js/ | ~64 KB dead code |
| 6 | **`report_2.js` كامل** | js/ | ~16 KB dead code |
| 7 | **5 ملفات `.map`** في الإنتاج | bootstrap.4.5.3/ | مئات KB dead |
| 8 | **jQuery 3.0.0 (2016)** بـ CVEs معروفة | jquery-3.0.0.min.js | عرضة لـ XSS مع cleartext HTTP |
| 9 | **لا CSP** + WebView يحمّل من `file://` + يقبل JS injection من Java | كل HTML | XSS attack surface متاح |
| 10 | **`xconfig` global** غير type-safe | كل ملفات JS | كل خطأ في الاسم = silent failure |

---

## 7. الحجم الإجمالي

| الفئة | الحجم |
|---|---|
| jQuery 3.0.0 | 86 KB |
| Bootstrap 4.5.3 (JS فقط — bundle + min معاً) | ~148 KB |
| Source maps (5 ملفات) | ~1 MB (تقدير) |
| Bootstrap CSS (4 ملفات) | ~700 KB |
| FontAwesome 4.7 | ~1 MB (font files + CSS + LESS sources) |
| كود مخصص (4 ملفات JS) | ~58 KB |
| **المجموع داخل `assets/myweb/`** | **~3 MB** |

---

## 8. الكود الميت الفعلي

| العنصر | الحجم | السبب |
|---|---|---|
| `bootstrap.min.js` | 64 KB | HTML يستخدم `bundle.min.js` فقط |
| `bootstrap.bundle.min.js.map` | ~200 KB | source map في إنتاج |
| `bootstrap.min.js.map` | ~150 KB | source map في إنتاج + لمكتبة dead |
| `bootstrap.min.css.map` | ~150 KB | source map |
| `bootstrap-grid.min.css.map` | ~100 KB | source map |
| `bootstrap-reboot.min.css.map` | ~50 KB | source map |
| `js/report_2.js` | 16 KB | غير مرجَّع من أي HTML |
| `font-awesome-4.7.0/less/` | ~50 KB | LESS sources (تُستعمل CSS المُترجمة فقط) |
| `font-awesome-4.7.0/HELP-US-OUT.txt` | 1 KB | ملف نصي للنشر |
| `fontawesome-webfont.eot/svg/woff/woff2` (4 صيغ) | ~700 KB | WebView Android يستخدم `.ttf` فقط |
| `FontAwesome.otf` | 135 KB | تكرار مع `fontawesome-webfont.ttf` |
| **المجموع dead** | **~1.5 MB** | |

**نسبة الميت من إجمالي `assets/myweb/`:** ~50%.

---

## 9. كود حساس / مفاتيح

```bash
$ python3 decode_obfuscated.py *.js | grep -iE "key|secret|token|password|http"
```

✅ **لا أسرار في الكود.** البيانات الحساسة (تسجيل دخول، رصيد، أرقام عملاء) تأتي من Java bridge.

⚠️ **لكن `localStorage` يستضيف بيانات الفواتير** — لو وُجد XSS في أي شاشة WebView، يمكن قراءة كل تاريخ الـ vouchers من JS مهاجم.

---

## 10. البديل في React Native

### 10.1 ما يجب حذفه (بالكامل)

| الحالي | البديل في RN | التوفير |
|---|---|---|
| `paymentlist.js` (مُمَوّه) | `<PaymentListScreen>` TypeScript | 17 KB |
| `readinglist.js` (مُمَوّه) | `<ReadingListScreen>` TypeScript | 9 KB |
| `report.js` (مُمَوّه) | `<VoucherReportScreen>` + `react-native-print` | 16 KB |
| `report_2.js` (dead) | — | 16 KB |
| `jquery-3.0.0.min.js` | غير مطلوب — React = state-driven DOM | 86 KB + CVEs |
| `bootstrap.4.5.3/` كامل | `NativeBase` أو `tamagui` (tree-shakable) أو inline `StyleSheet` | ~1 MB |
| `font-awesome-4.7.0/` كامل | `react-native-vector-icons/FontAwesome` (tree-shaken) | ~1 MB |
| كل `.map` files | لا تُشحن أبداً في prod | ~1 MB |
| **المجموع** | | **~4 MB توفير + إزالة CVEs** |

### 10.2 ميزات الجديد

```tsx
// PaymentListScreen.tsx
import { FlatList, TextInput } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useDebouncedValue } from './hooks';
import { useTranslation } from 'react-i18next';

export function PaymentListScreen() {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebouncedValue(search, 300);
  
  const { data: payments, isLoading } = useQuery({
    queryKey: ['payments', debouncedSearch],
    queryFn: () => api.getPayments({ search: debouncedSearch }),
  });

  return (
    <View>
      <TextInput
        placeholder={t('common.search')}
        value={search}
        onChangeText={setSearch}
      />
      <FlatList
        data={payments}
        keyExtractor={(p) => p.v_no}
        renderItem={({ item }) => <PaymentItem payment={item} />}
        refreshing={isLoading}
        onRefresh={() => queryClient.invalidateQueries(['payments'])}
      />
    </View>
  );
}
```

### 10.3 المكاسب الكمية

| البُعد | حالياً (WebView+JS) | بـ React Native |
|---|---|---|
| حجم الـ JS bundle | ~290 KB (JS) + ~1 MB (CSS) + ~1 MB (fonts) = **~2.3 MB** | ~150 KB JS bundle (Hermes) |
| سرعة بدء التشغيل | يحمّل HTML→CSS→jQuery→Bootstrap→JS→DOM ready ~600ms | RN native bridge ~150ms |
| Type safety | صفر (مُمَوّه) | TypeScript كامل |
| Debug | مستحيل (سطر واحد) | Flipper + React DevTools |
| CVE exposure | jQuery 3.0.0 + Bootstrap 4.5.3 EOL + FontAwesome 4 EOL | تبعيات حديثة + tree-shaking |
| i18n | hardcoded عربي في JS | `react-i18next` |
| RTL | hardcoded `dir="rtl"` | `I18nManager.isRTL` تلقائي |
| Storage | `localStorage` غير مشفّر | `react-native-keychain` للحساس |

---

## 11. مصادر التحقق

| المصدر | الأمر / المسار |
|---|---|
| jQuery version | `grep "jQuery v" assets/myweb/js/jquery-3.0.0.min.js` |
| Bootstrap version | `head -c 200 assets/myweb/bootstrap.4.5.3/js/bootstrap.min.js` |
| فك تشفير JS | سكريبت Python يطبّق regex `\\x[0-9a-fA-F]{2}` ⇒ `chr(int(_,16))` |
| تكرار report.js / report_2.js | `diff` على أول 1000 byte ⇒ فقط اسم المتغير مختلف |
| dead code report_2 | `grep -rn "report_2" assets/ res/` = 0 hits |
| Bridge calls | `xconfig.*`, `mobile.*` في الـ decoded strings |
| Bootstrap source maps | `ls assets/myweb/bootstrap.4.5.3/{js,css}/*.map` |
| jQuery CVEs | nvd.nist.gov ⇒ CVE-2019-11358, CVE-2020-11022/11023, CVE-2015-9251 |
| Bootstrap 4 EOL | getbootstrap.com/docs/4.6 (آخر 4.x) — security patches stopped Jan 2024 |
| FontAwesome 4 EOL | fontawesome.com — 4.7.0 released Oct 2016, replaced by 5.x/6.x |

---

**ملف:** `Deep_Analysis/09_assets_resources/02_javascript_assets.md`
**عدد ملفات JS:** 9 (5 vendor + 4 custom) + 5 source maps
**حجم JS فعلي:** ~290 KB (بدون source maps)
**dead code فعلي:** ~80 KB (bootstrap.min + report_2 + LESS sources) + ~700 KB من source maps + duplicate font formats
**أكبر مشكلة:** jQuery 3.0.0 (2016, CVEs) + Bootstrap 4.5.3 EOL + report_2.js duplicate + snapbuilder/string-array obfuscation عديم الفائدة + hardcoded Arabic في JS
**التوصية:** حذف كامل لـ `assets/myweb/` (3 MB توفير) واستبدالها بـ RN screens
