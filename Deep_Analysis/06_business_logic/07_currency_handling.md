# 07 — معالجة العملة (الريال اليمني والفلس)

> **التطبيق:** AbbasiyCashiers — Ecas v18.4 — `com.egy.webpaymentapp`
> **النطاق:** كيفية تخزين / حساب / عرض / إرسال المبالغ النقدية في التطبيق
> **منهج التحليل:** محقق محايد — اكتشاف من الكود الفعلي
> **مصادر التحليل:**
> - `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/**`
> - `AbbasiyCashiers_RE_Analysis/02_apktool_output/AbbasiyCashiers/assets/myweb/js/report.js`

---

## 1. الملخص التنفيذي

تطبيق AbbasiyCashiers يتعامل مع **الريال اليمني (YER)** فقط. لا يوجد دعم لعملات متعددة، ولا تحويل عملات.

**الاكتشافات الجوهرية (محايدة):**

| البند | الحال في التطبيق | التقييم |
|---|---|---|
| نوع البيانات للمبلغ في الذاكرة | `String` (في جميع نماذج DTO) | 🔴 سيء (يفقد الميزات الحسابية) |
| طريقة العمليات الحسابية | `Integer.parseInt` ثم طرح int ثم `String.valueOf` | 🔴 كارثي (يفقد الفلس) |
| طريقة المقارنة | `Double.parseDouble` لمقارنة الرصيد بالمبلغ | 🔴 سيء (double في المال) |
| `BigDecimal` / `DecimalFormat` | **غير موجود** في أي مكان | 🔴 |
| ضبط `Locale` للأرقام | غير مُستخدم — لا `NumberFormat` | 🔴 |
| فاصلة عشرية | الكود الجاوي يقبل العشرية لقراءة العداد فقط — لا للدفع! | 🔴 (تناقض داخلي) |
| فاصل الآلاف | غير موجود — يُعرض الرقم خام | 🟡 |
| تحويل أرقام عربية-هندية | غير موجود — أرقام لاتينية في الإيصال والـ UI | 🟡 |
| طريقة الإرسال للـ Backend | `String` كما هي في الـ JSON | 🟡 (يقبل أي شيء) |
| تقريب (rounding) | **لا يوجد منطق تقريب** — ما يكتبه المستخدم يُرسل كما هو | 🟡 |

> **الخلاصة المحايدة:** تطبيق ETL مالي يستخدم `Integer.parseInt` للطرح المالي و`Double.parseDouble` للمقارنة، **بدون** `BigDecimal` ولا `DecimalFormat` ولا حماية من تجاوز الـ overflow ولا تطبيع رقمي. **هذا تصميم مرفوض في أي معيار محاسبي**. النجاة الوحيدة هي أن قيود `DigitsKeyListener` على واجهة الدفع تمنع الفاصلة، فيكون التحويل integer سليماً بالصدفة — لكن أي تغيير في الواجهة سيكشف عن المشكلة فوراً.

---

## 2. مكان تخزين المبالغ في الذاكرة

### 2.1 نموذج `Payinfo` — DTO الإيصال

**`com/egy/webpaymentapp/webapi/models/Payinfo.java:4-54`:**

```java
public class Payinfo {
    private String f2433a;   // v_no       — رقم السند
    private String f2434b;   // v_date     — تاريخ السند
    private String f2435c;   // c_no       — رقم المشترك
    private String f2436d;   // c_name     — اسم المشترك
    private String f2437e;   // v_amt      — مبلغ التسديد ← هنا الفلوس!
    private String f;        // user_name  — اسم المتحصل
    private String g;        // c_bal      — الرصيد الحالي ← هنا أيضاً!
    private String h;        // ...
    private String i;
    private String j;        // BRD_ImgData (Base64 صورة)
    private String k;        // user_gps_loc
    // ... 15 حقل، كلها String
}
```

> **اكتشاف 🔴 (P0):** **كل** المبالغ المالية مُخزَّنة كـ `String`. لا توجد دلالة على أنها أعداد، ولا قيود على الصيغة، ولا تحقق من الفواصل. الـ `String` يحمل أي شيء (`"100"`, `"100.5"`, `"١٠٠"`, `"abc"`, `""`).

### 2.2 نموذج `User` — مبالغ المستخدم

**`com/egy/webpaymentapp/webapi/models/User.java:104`:**
```java
public int q() {
    return Integer.parseInt(this.q);   // q = String balance
}
```

> **اكتشاف 🔴 (P0):** الرصيد يُحوَّل إلى `int` — هذا يعني أن **الرصيد لا يقبل أي كسر** (لا فلس). أقصى قيمة لـ int في Java = 2,147,483,647 (≈ 2.1 مليار ريال). للسياق اليمني هذا قد يكون كافياً، لكن:
> - رمي خطأ `NumberFormatException` لو فيه فاصلة عشرية.
> - لا يدعم تحصيلات الفلس.

---

## 3. العمليات الحسابية الفعلية — الكشف الكبير

### 3.1 طرح الرصيد بعد الدفع

**`com/egy/webpaymentapp/Screens/e0.java:55-58`** (داخل onClick زر تأكيد الدفع):

```java
int parseInt = Integer.parseInt(str3) - Integer.parseInt(obj2);
//                       ^^^^^^^^^^^^^^^             ^^^^^^^^
//                       الرصيد الحالي               مبلغ التسديد
Payinfo payinfo = new Payinfo();
dVar.f = payinfo;
payinfo.c(String.valueOf(parseInt));   // الرصيد الجديد = String من int
```

**ماذا يحدث فعلياً؟**
1. الرصيد `str3` و المبلغ `obj2` هما `String` من EditText.
2. كلاهما يُحوَّل إلى `int` (Integer.parseInt).
3. الطرح يحدث على `int`.
4. النتيجة تُحوَّل إلى `String` وتُحفظ في `Payinfo.v_amt`.

**كارثة الفلس:**
- لو الرصيد `"1000.50"` ← `Integer.parseInt("1000.50")` يرمي `NumberFormatException`!
- لو الرصيد `"1000"` والمبلغ `"500"` ← النتيجة `"500"` ✅ (يعمل).
- لو الرصيد `"1000.5"` (مع فاصلة عشرية) ← التطبيق سيتعطل (crash) بدون أي تعامل مع الاستثناء.

> **اكتشاف 🔴 (P0):** هذا الكود يفترض ضمنياً أن المدخلات أعداد صحيحة فقط. وهذا الافتراض **محمي فقط بواسطة `DigitsKeyListener(false, false)` في واجهة الدفع** — أي حماية على مستوى الـ UI وليس على مستوى المنطق.

> **اكتشاف 🔴 (P0):** **لا يوجد `try/catch`** حول `Integer.parseInt`. لو نجح المستخدم بطريقة ما (لصق من حافظة، أو لو غيّر مطور لاحقاً الـ KeyListener) في إدخال كسر، التطبيق سينهار.

### 3.2 مقارنة الرصيد بالمبلغ

**`com/egy/webpaymentapp/Screens/x.java:28`** (TextWatcher على حقل المبلغ):

```java
if (Double.parseDouble(this.f2430b.s.f1831d) < Double.parseDouble(this.f2430b.x.getText().toString())) {
    textView = this.f2430b.V;
    str = this.f2430b.getString(R.string.amt_grter_bal);
}
```

**ماذا يحدث؟**
- نفس الرصيد `f1831d` (String) ونفس المبلغ، لكن هنا يُحوَّلان إلى **`double`**!
- المقارنة `<` تعمل على `double`.

> **اكتشاف 🔴 (P0) — التناقض الجوهري:**
> 
> | السياق | نوع التحويل | الملف |
> |---|---|---|
> | المقارنة (هل المبلغ > الرصيد؟) | `Double.parseDouble` | x.java:28 |
> | الطرح الفعلي (تحديث الرصيد) | `Integer.parseInt` | e0.java:55 |
> 
> **النتيجة المتوقعة:** لو الرصيد `"1000.50"`:
> - المقارنة تنجح (double يقبل الفاصلة).
> - الدفع يفشل بـ crash (int لا يقبل الفاصلة).
> 
> هذا تصميم **غير متسق** يكشف عن غياب مراجعة الكود.

### 3.3 أين كلام float? double?

```bash
$ grep -rn "parseInt\|parseDouble\|parseFloat\|parseLong" com/egy/webpaymentapp/
```

نتائج البحث الكاملة:
```
Screens/x.java:28:  Double.parseDouble(...) < Double.parseDouble(...)
Screens/e0.java:55: int parseInt = Integer.parseInt(str3) - Integer.parseInt(obj2);
Screens/e0.java:58: payinfo.c(String.valueOf(parseInt));
webapi/models/User.java:104: return Integer.parseInt(this.q);
```

**هذا كل ما يحدث للأرقام في الكود الجاوي.** لا يوجد `BigDecimal`، لا `Long`، لا `DecimalFormat`، لا `NumberFormat`.

> **اكتشاف 🔴 (P0):** الـ `double` في المال خطر معروف:
> - `0.1 + 0.2 == 0.3` ينتج **`false`** في كل لغات IEEE-754.
> - الحل المعياري: `BigDecimal` للحسابات + `DecimalFormat` للعرض.
> - AbbasiyCashiers يستخدم `double` للمقارنة و`int` للطرح — كلاهما خاطئ.

---

## 4. حماية الواجهة — `DigitsKeyListener`

### 4.1 شاشة الدفع (B==1) — لا فاصلة عشرية!

**`OprationsActivity.java:469`** (للحالة `i == 1` = Payment):

```java
if (i == 1) {
    this.I.T(getString(R.string.txt_payed_amt));
    this.L.setVisibility(8);
    editText = this.x;
    digitsKeyListener = new DigitsKeyListener(false, false);
    //                                         ^^^^^  ^^^^^
    //                                      signed  decimal
    //                                         No      No
}
```

`DigitsKeyListener(false, false)` ← **لا إشارة سالبة، لا فاصلة عشرية**.

> **اكتشاف 🔴 (P0):** هذا يعني المستخدم **لا يستطيع إدخال فلس في الدفع**! 
> - 500 ريال؟ نعم
> - 500.5 ريال؟ مستحيل — لوحة المفاتيح تمنع زر النقطة.
> 
> هذا "حلّ" للمشكلة الجوهرية: بما أن الحساب يحدث على int، الواجهة تمنع الكسر ليتجنّب الـ crash. لكنه **عيب وظيفي**: الفلس موجود في النظام المالي اليمني (1 ريال = 100 فلس)، والتطبيق يتجاهله في الدفع.

### 4.2 شاشة قراءة العداد (B==2) — فاصلة عشرية مسموحة

**`OprationsActivity.java:512`** (للحالة `i == 2` = Reading):

```java
} else {
    editText = this.x;
    digitsKeyListener = new DigitsKeyListener(false, true);
    //                                         ^^^^^  ^^^^
    //                                      signed  decimal
    //                                         No     Yes
}
```

> **اكتشاف 🟡:** قراءة العداد تقبل الفاصلة (الكيلوواط ساعة يحوي كسوراً)، لكن المبلغ النقدي لا يقبلها. هذا **منطقي لقراءة العداد** لكنه يكشف عن **عجز التطبيق في التعامل مع الكسور النقدية**.

### 4.3 شاشة الموقع (B==3)

**`OprationsActivity.java:476`** (للحالة `i == 3`):

```java
if (i == 3) {
    this.x.setInputType(1);     // InputType.TYPE_CLASS_TEXT
    digitsKeyListener = null;   // لا تقييد رقمي — نص حر
}
```

---

## 5. ضبط Locale وتنسيق الأرقام

### 5.1 ما هو الـ Locale المُستخدم؟

`grep -rn "Locale\." com/egy/webpaymentapp/` يعطي:

```
Screens/OprationsActivity.java:308: new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.ENGLISH)
```

**هذا الـ Locale الوحيد المُحدَّد في كل الكود!** وهو للتاريخ فقط (اسم ملف الصورة).

> **اكتشاف 🟡:** التطبيق **لا يحدد Locale للأرقام النقدية**. النتيجة:
> - في الأجهزة الإنجليزية: `"1500"` يُعرض `"1500"` ✅
> - في الأجهزة العربية بأرقام هندية: `"1500"` يُعرض كما هو (`"1500"`) — لأن التطبيق يستخدم `String` خام.
> - عند المقارنة `Double.parseDouble("١٥٠٠")` ← يرمي خطأ! (لكن المستخدم لا يستطيع إدخال أرقام هندية لأن `DigitsKeyListener` يقبل ASCII فقط).

### 5.2 لا يوجد `NumberFormat` ولا `DecimalFormat`

```bash
$ grep -rn "NumberFormat\|DecimalFormat" com/egy/webpaymentapp/
# 0 hits
```

> **اكتشاف 🔴 (P1):** الأرقام تُعرض **كما تأتي من الـ Backend** (String خام). لا يوجد:
> - فاصل آلاف (`1,500,000` يُعرض `1500000`).
> - تنسيق ثابت لخانتين عشريتين (`1.5` يُعرض `1.5` بدلاً من `1.50`).
> - رمز عملة (`ر.ي.` أو `YER`).

### 5.3 العرض في الإيصال

في `report.js` (الجاسكريبت)، المبلغ يُلصَق هكذا:

```javascript
_0x9867.replace("@fvbl", _0x95CD["v_amt"] + " " + tafqeet(_0x95CD["v_amt"]));
//                       ^^^^^^^^^^^^^^^         ^^^^^^^^^^^^^^^^^^^^^^^
//                       الرقم كما جاء          التفقيط
// مثال: "5000 خمسة آلاف ريال يمني"
```

> **اكتشاف 🟡:** الإيصال يعرض `"5000"` بدلاً من `"5,000"`. لو دفع شخص مليون ريال سيظهر `"1000000"` — رقم صعب القراءة. على الأقل التفقيط يخفف هذا (يكتب "مليون").

---

## 6. الإرسال للـ Backend

### 6.1 صيغة JSON

كل المبالغ تُرسَل ضمن `Payinfo` بصيغة JSON:

```json
{
  "f": {
    "v_no": "...",
    "v_amt": "500",
    "c_bal": "500",
    ...
  }
}
```

> **اكتشاف 🟡:** المبالغ تُرسَل كـ **strings داخل JSON** وليس أرقاماً (لأن الحقل من نوع `String` في Java و Gson يحافظ على النوع). هذا يضع العبء على الـ Backend للتحقق.

> **اكتشاف 🔴 (P1):** لا يوجد توحيد للصيغة. مثلاً:
> - لو المستخدم كتب `"500 "` (بمسافة) ← يُرسل كذلك.
> - لو المستخدم كتب `"500.0"` في قراءة العداد ← يُرسل بصيغة عشرية.
> - لا "trim" ولا تطبيع قبل الإرسال.

### 6.2 الاستلام من الـ Backend

عند جلب بيانات المشترك (`getCustomerData`)، يأتي الرصيد كـ `String` في `User.q`. ثم:

```java
return Integer.parseInt(this.q);
```

> **اكتشاف 🔴 (P0):** لو الـ Backend أرسل رصيداً كـ `"1500.75"` (للسماح بفلس)، التطبيق سينهار. عقد API هشّ يفترض دائماً integer.

---

## 7. التقريب (Rounding)

### 7.1 منطق التقريب

```bash
$ grep -rn "Math.round\|RoundingMode\|Math.floor\|Math.ceil\|HALF_UP\|HALF_DOWN" com/egy/webpaymentapp/
# 0 hits
```

> **اكتشاف 🔴 (P0):** **لا يوجد أي منطق تقريب في الكود**. السبب: التطبيق لا يجري حسابات معقدة (لا ضرائب، لا عمولات، لا نسب). كل ما يحدث هو طرح بسيط: الرصيد - المبلغ. والطرح int/int بدون تقريب.

### 7.2 هل يخسر التطبيق الفلس؟

**سيناريو حقيقي:**
- الرصيد في الـ Backend = 1234 ريال + 50 فلس.
- يُرسَل للتطبيق كـ String. إن أرسله الـ Backend كـ `"1234.50"`:
  - `Integer.parseInt("1234.50")` → **`NumberFormatException`** → التطبيق ينهار.
- إن أرسله الـ Backend كـ `"1234"` (تجاهل الفلس):
  - **يضيع 50 فلس بصمت!**
- إن أرسله الـ Backend كـ `"1235"` (تقريب لأعلى):
  - **يكسب المستخدم 50 فلس مجاناً!**

> **اكتشاف 🔴 (P0):** الفلس مفقود بالكامل من المعادلة. أي محاولة لإضافة دعم الفلس ستحطم التطبيق إلى أن يُعاد تصميم نموذج البيانات. هذا **دين تقني فادح**.

---

## 8. الضرائب والرسوم

```bash
$ grep -rn "tax\|VAT\|fee\|commission\|nazlat\|الضريبة\|ضريبة\|رسوم" com/egy/webpaymentapp/
# 0 hits
```

> **اكتشاف 🟡:** **لا يوجد حساب ضرائب أو رسوم في التطبيق**. هذا منطقي لتطبيق تحصيل (الـ Backend يحسب). لكنه **يعني أن أي تغيير ضريبي يتطلب تحديث Backend فقط، وهذا جيد**.

---

## 9. تحويل العملات

```bash
$ grep -rn "exchange\|convert\|USD\|SAR\|currency" com/egy/webpaymentapp/
# 0 hits
```

في الـ JS:

```bash
$ grep "currency\|YER\|USD" assets/myweb/js/report.js
# match: tafqeetISOList = {YER:...}
```

> **اكتشاف ✅:** التطبيق **يدعم YER فقط**. لا تحويل عملات. منطقي لتطبيق تحصيل محلي.

---

## 10. الأرقام العربية-الهندية (٠١٢٣...)

```bash
$ grep -rn "[\u0660-\u0669]" com/egy/webpaymentapp/
# 0 hits
```

> **اكتشاف 🟡:** التطبيق **لا يدعم الأرقام العربية-الهندية**:
> - الإدخال: `DigitsKeyListener` لا يقبلها (ASCII فقط).
> - العرض في الإيصال: يستخدم الأرقام اللاتينية (`0-9`).
> - في WebView/HTML: يعتمد على إعدادات اللغة في الجهاز.
> 
> **حكم:** هذا اختيار مقبول لتطبيق تجاري (الأرقام اللاتينية مفهومة عالمياً). لكنه قد يكون مزعجاً لمستخدم يفضّل العربية الكاملة.

---

## 11. اختبارات نظرية — حالات حافة

(لم تُنفَّذ — تحليل من قراءة الكود)

| السيناريو | السلوك المتوقع | الحكم |
|---|---|---|
| دفع 500 ريال من رصيد 1000 ريال | يعمل: 1000 - 500 = 500 | ✅ |
| دفع 500.5 ريال | مستحيل الإدخال (KeyListener يمنع) | 🟡 (قيد تقني) |
| رصيد من Backend = "1500.75" | Crash عند `Integer.parseInt` | 🔴 |
| رصيد فارغ "" | Crash عند `Integer.parseInt` (NumberFormatException) | 🔴 |
| رصيد سالب "-500" | `Integer.parseInt` يقبل السالب، تظهر "-500" في الواجهة | 🔴 (لا يجب أن يكون الرصيد سالباً) |
| رصيد > Integer.MAX_VALUE (2.1 مليار) | Crash | 🟡 (سيناريو نظري) |
| نسخ ولصق "١٥٠" (عربي-هندي) | KeyListener يمنع | 🟡 |
| نسخ ولصق "1,500" مع فاصلة | `parseInt("1,500")` → Crash | 🔴 |
| رصيد بمسافات " 500 " | `parseInt(" 500 ")` → Crash (لا يوجد trim) | 🔴 |

---

## 12. مقارنة مع معايير الصناعة

| المعيار | التوصية | في AbbasiyCashiers |
|---|---|---|
| نوع المبلغ في الذاكرة | `BigDecimal` (Java) أو `Long` (بالفلس) | `String` + `Integer.parseInt` 🔴 |
| التقريب | `RoundingMode.HALF_UP` (محاسبياً) | لا يوجد تقريب 🔴 |
| التنسيق | `NumberFormat.getCurrencyInstance(Locale)` | إلصاق string خام 🔴 |
| Locale النقدي | `new Locale("ar", "YE")` للريال اليمني | غير محدد 🟡 |
| فاصلة الآلاف | `1,234.56` (إنجليزي) أو `1.234,56` (عربي) | بدون فاصلة 🟡 |
| الفلس في DB | تخزين كـ Long * 100 (cents pattern) | غير موجود 🔴 |
| التحقق من المدخل | regex + range check | KeyListener فقط 🟡 |
| تعامل مع الأخطاء | try/catch + رسائل واضحة | غير موجود 🔴 |

---

## 13. اكتشافات صادمة (Unexpected Findings)

### 13.1 لا يوجد عقد بيانات

الـ DTOs لا تفرّق بين الحقول النقدية والنصية. كلاهما `String`. لا توجد annotations مثل `@Money` أو `@Digits` أو حتى comments تشير لذلك.

### 13.2 الواجهة تخفي عيب المنطق

`DigitsKeyListener(false, false)` للدفع يبدو خياراً عشوائياً، لكنه فعلياً **يحمي الخط الحسابي من crash**. هذا "حل عرضي" يكشف أن المطور وعى المشكلة لكنه لم يحلها جذرياً.

### 13.3 التناقض الصامت

استخدام `Double` للمقارنة و `Integer` للطرح يعني أن قواعد التحقق (validation) لا تتوافق مع قواعد المنطق. **مثال نظري:**
- المستخدم لاصق "500.7" في حقل المبلغ.
- `KeyListener` يرفض النقطة، فيُحفظ "5007" في الـ EditText.
- المقارنة: `Double.parseDouble("5007") < Double.parseDouble(balance)` تعمل.
- الطرح: `Integer.parseInt("5007")` يعمل (لا فاصلة).
- النتيجة: **سُرق المستخدم 4506.3 ريال بصمت** (لأن نيته كانت 500.7).

هذا سيناريو نظري لكن **ممكن**.

### 13.4 لا يوجد حسابات على الجهاز

التطبيق **عملياً لا يحسب شيئاً مهماً**:
- الطرح الوحيد هو `الرصيد - المبلغ` لعرضه في الإيصال.
- المبلغ المراد دفعه يأتي من الـ Backend (`s.f1831d`).
- لا ضرائب، لا عمولات، لا نسب.

> **حكم محايد:** هذا يقلل من خطورة الأخطاء الموثقة أعلاه. **لكنه لا يعفي** من ضرورة الإصلاح، لأن الخطورة كامنة في أي تطور مستقبلي للتطبيق.

---

## 14. التقييم المُحايد

### نقاط جيدة ✅
1. عدم وجود حسابات معقدة على الجهاز يقلل من السطح المعرض للأخطاء.
2. الحسابات الرئيسية في الـ Backend (افتراض معقول من السياق).
3. التطبيق محدود بـ YER واحدة — لا تعقيد تحويل عملات.

### نقاط متوسطة 🟡
1. عدم تنسيق العرض (لا فاصل آلاف، لا تنسيق عشري).
2. عدم دعم الأرقام العربية-الهندية للمستخدم العربي.
3. واجهة الدفع تمنع إدخال الفلس (يحد من الوظيفة).
4. الإرسال للـ Backend بدون تطبيع.

### نقاط حرجة 🔴
1. **`Integer.parseInt` للطرح المالي** — يفقد الفلس + يسقط مع كسر.
2. **`Double.parseDouble` للمقارنة** — IEEE-754 خطر في المال.
3. **لا `BigDecimal` ولا `DecimalFormat`** — انعدام معايير صناعية.
4. **التناقض بين validation (double) ومنطق (int)** — ثغرة منطقية.
5. **`String` لجميع المبالغ في DTO** — لا أمان نوعي.
6. **لا `try/catch` حول `parseInt`** — أي رسالة من الـ Backend مشبوهة تسقط التطبيق.
7. **`User.q()` يستخدم `Integer.parseInt` على الرصيد** — لا يدعم فلس.
8. **لا منطق تقريب** — في حال احتاجوه لاحقاً، التغيير سيكون مكلفاً.

---

## 15. أولويات الإصلاح

| الأولوية | المشكلة | الحل المقترح |
|---|---|---|
| **P0** | استبدال `Integer.parseInt` بـ `BigDecimal` للطرح | `new BigDecimal(str3).subtract(new BigDecimal(obj2))` |
| **P0** | استبدال `Double.parseDouble` بـ `BigDecimal.compareTo` | `new BigDecimal(s.f1831d).compareTo(new BigDecimal(x.getText())) < 0` |
| **P0** | إضافة `try/catch` حول كل تحويل رقمي | منع crash + رسالة واضحة للمستخدم |
| **P0** | تحديد عقد API: هل الـ Backend يرسل decimal أم integer؟ | توحيد على decimal مع `BigDecimal` |
| **P1** | تغيير حقول DTO من `String` إلى `BigDecimal` | يتطلب custom JsonDeserializer لـ Gson |
| **P1** | إضافة `DecimalFormat` للعرض | `new DecimalFormat("#,##0.00 ر.ي.", new DecimalFormatSymbols(arLocale))` |
| **P1** | دعم الفلس في واجهة الدفع | تغيير `DigitsKeyListener(false, false)` إلى `(false, true)` + معالجة الفلس |
| **P1** | تطبيع المدخل قبل الإرسال | `amount.trim().replaceAll("[\\s,]", "")` |
| **P2** | دعم الأرقام العربية-الهندية | `DigitsKeyListener.getInstance("0123456789٠١٢٣٤٥٦٧٨٩.")` |
| **P2** | تنسيق فاصلة الآلاف في العرض | `NumberFormat.getInstance(new Locale("ar","YE"))` |

---

## 16. مصادر التحقق

| الادعاء | المصدر | السطر |
|---|---|---|
| Payinfo كلها String | `webapi/models/Payinfo.java` | 8, 12, 16, 20, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54 |
| طرح بـ int | `Screens/e0.java` | 55-58 |
| مقارنة بـ double | `Screens/x.java` | 28 |
| User.q بـ int | `webapi/models/User.java` | 104 |
| DigitsKeyListener الدفع بدون كسر | `Screens/OprationsActivity.java` | 469 |
| DigitsKeyListener القراءة مع كسر | `Screens/OprationsActivity.java` | 512 |
| لا BigDecimal | `grep -rn "BigDecimal" com/egy/webpaymentapp/` = 0 |
| لا DecimalFormat | `grep -rn "DecimalFormat" com/egy/webpaymentapp/` = 0 |
| لا NumberFormat | `grep -rn "NumberFormat" com/egy/webpaymentapp/` = 0 |
| لا تقريب | `grep -rn "RoundingMode\|Math.round" com/egy/webpaymentapp/` = 0 |
| Locale.ENGLISH للتاريخ فقط | `Screens/OprationsActivity.java` | 308 |
| YER العملة الوحيدة | `assets/myweb/js/report.js` | `tafqeetISOList={YER:...}` |

---

**انتهى تحليل معالجة العملة — `07_currency_handling.md`**
