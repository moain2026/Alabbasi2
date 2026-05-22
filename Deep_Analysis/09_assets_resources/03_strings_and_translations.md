# 03 — تحليل النصوص والترجمات في AbbasiyCashiers (Ecas v18.4)

> **الموقع:** `res/values*/strings.xml` + `res/values*/plurals.xml`
> **المنهج:** `grep '<string '` لكل ملف، تحديد نصوص التطبيق vs نصوص Material/AndroidX، فحص `Locale` في كود Java، تفتيش `supportsRtl` في Manifest، البحث عن hardcoded strings.

---

## 1. عدد اللغات الظاهر vs الفعلي

### 1.1 الجرد الأولي

```bash
$ ls -d res/values*
```

| فئة | عدد المجلدات |
|---|---|
| `res/values/` (default) | 1 |
| `res/values-XX/` (لغات) | 116 |
| **المجموع** | **117 مجلد لغة** |

### 1.2 الحقيقة المخادعة

```bash
$ for f in res/values*/strings.xml; do
    lang=$(echo "$f" | sed 's|res/values-\?||; s|/strings.xml||')
    count=$(grep -c '<string ' "$f")
    echo "$lang: $count strings"
  done
```

| اللغة | عدد strings | ملاحظة |
|---|---|---|
| `values/` (default) | **192** | الإنجليزية + بعض العربية المُسرَّبة |
| `values-ar/` | **173** | العربية — يحوي ترجمات Material |
| `values-af` (Afrikaans) | 101 | فقط Material + AndroidX |
| `values-am` (Amharic) | 101 | فقط Material + AndroidX |
| `values-as` (Assamese) | 101 | فقط Material + AndroidX |
| `values-az` (Azerbaijani) | 101 | فقط Material + AndroidX |
| `values-bg, be, bn, bs, ca, cs, da, de, ...` | ~101 لكل لغة | فقط Material + AndroidX |
| 115 لغة أخرى | ~100-101 لكل واحدة | فقط Material + AndroidX |

### 1.3 الاستنتاج

**التطبيق يدّعي دعم 117 لغة لكنه فعلياً يدعم لغتين فقط:**

```
الحقيقة:
  values/      → English fallback + بعض الـ hardcoded عربي (192 strings)
  values-ar/   → Arabic (173 strings) ← اللغة الرئيسية
  values-XX/   → كل الباقي = ترجمات Material Components + AndroidX (~101 string لكل لغة)
                 لا يحوي ترجمة سلسلة واحدة من سلاسل التطبيق نفسه!
```

| فئة الـ string | في `values/` | في `values-ar/` |
|---|---|---|
| من Material Library (mtrl_, abc_, material_) | 87 | 87 (نفسها) |
| من AndroidX/Common (androidx_, common_google_play) | 28 | 0 (لم تُترجم) |
| **من التطبيق نفسه (custom)** | **77** | **86** ← بعضها عربي فقط في `values-ar`! |

**خلاصة: التطبيق فعلياً = أحادي اللغة (عربي)** مع `values/` = fallback ضعيف يحوي 77% نص عربي + 23% نص إنجليزي مختلط.

---

## 2. خلط فادح في `values/strings.xml` (المفروض English)

### 2.1 نصوص عربية في `values/` (default الذي يجب أن يكون إنجليزياً!)

```xml
<!-- في res/values/strings.xml — المفروض English fallback! -->
<string name="Exit_From_System">الخروج من البرنامج ؟</string>          <!-- عربي! -->
<string name="add_castomer">اضافة عميل</string>                          <!-- عربي! + typo: castomer -->
<string name="alert_title">تنبيه</string>                                <!-- عربي! -->
<string name="amt_grter_bal">المبلغ المدفوع اكبر من رصيد العميل</string>  <!-- عربي! -->
<string name="back">عودة</string>                                        <!-- عربي! -->
<string name="btn_login">دخول</string>                                   <!-- عربي! -->
<string name="connect_printer">توصيل</string>                            <!-- عربي! -->
<string name="cp_ar">عربي</string>                                       <!-- عربي! -->
<string name="cp_en">English</string>                                    <!-- مختلط! -->
<string name="cust_bal">رصيد العميل</string>                             <!-- عربي! -->
<string name="loadingMsg">يرجى الانتظار</string>                         <!-- عربي! -->
<string name="settings">اعدادات</string>                                 <!-- عربي! -->
<string name="save">حفظ</string>                                         <!-- عربي! -->

<!-- لكن بعض النصوص إنجليزية: -->
<string name="app_name">ECAS WEB</string>                                <!-- English -->
<string name="msg_error_procedure_pymny">Payment Procedure Error.</string>  <!-- English -->
<string name="msg_error_procedure_read">Meter Reading Procedure Error.</string> <!-- English -->
<string name="msg_error_ws_serv_nm">Incorrect Server Name at ws app setting!</string> <!-- English -->

<!-- و بعضها مختلط (engrish): -->
<string name="sewoo">طابعة نوع SEWOO</string>                            <!-- "Sewoo printer" بـ عربي -->
```

### 2.2 المشكلة العملية

عندما يستخدم المستخدم جهازاً بلغة إنجليزية:
- يفتح Login screen → يرى:
  - زر "دخول" (من `btn_login` في values/)
  - "Payment Procedure Error." (من values/)
  - "ECAS WEB" (app_name)
- = تجربة مستخدم مكسورة بالكامل (خليط فوضوي)

**حل المطور:** لا يوجد، يبدو أن التطبيق صُمم للعمل **حصرياً على أجهزة بلغة عربية**.

### 2.3 typos حقيقية في أسماء strings.xml

```xml
<string name="add_castomer">           <!-- ← castomer ≠ customer -->
<string name="cp_enable_reading_netxt">  <!-- ← netxt ≠ next -->
<string name="msg_error_procedure_pymny">  <!-- ← pymny ≠ payment -->
<string name="prntInvs">              <!-- ← prnt = print, Invs = invoices (مختصر بدون داعٍ) -->
```

---

## 3. هل التطبيق RTL صحيح؟

### 3.1 إعداد AndroidManifest.xml

```xml
<application
    android:supportsRtl="true"           ← ✅ مفعّل
    android:theme="@style/AppTheme"
    ... >
```

`supportsRtl="true"` ✅ → Android يقلب الـ layouts تلقائياً للغة العربية (start/end بدلاً من left/right).

### 3.2 لكن في الـ layouts

```bash
$ grep -rn "android:layout_marginStart\|android:layout_marginEnd" res/layout/ | wc -l
$ grep -rn "android:layout_marginLeft\|android:layout_marginRight" res/layout/ | wc -l
```

من فحص `activity_login.xml`:
```xml
<EditText android:layout_marginStart="20.0dip" android:layout_marginEnd="20.0dip" />
```

✅ معظم الـ layouts تستخدم `Start/End` (RTL-aware).

### 3.3 لكن في HTML/CSS الـ WebView

```html
<html dir="rtl">    ← hardcoded في كل HTML
```

و في JS:
```js
document.body.dir = 'rtl';   // في report.js
```

= **RTL مفروض دائماً** على WebView، لا يحترم لغة الجهاز. ⇒ مشكلة لو حاول مستخدم انجليزي استعمال التطبيق.

### 3.4 الـ Locale في كود Java

```bash
$ grep -rn "Locale\|setLocale" com/egy/webpaymentapp/
```

النتيجة:
```java
// OprationsActivity.java:312
String format = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.ENGLISH).format(new Date());
```

**هذا الاستخدام الوحيد!** لا `Locale.setDefault()`, لا `Configuration.setLocale()`, لا language selector.

❌ **التطبيق لا يدير اللغة برمجياً** — يعتمد كلياً على لغة النظام:
- لو الجهاز `ar-YE` → `values-ar/` (عمل صحيح)
- لو الجهاز `en-US` → `values/` (الذي يحوي خليط عربي وإنجليزي = شاشات مكسورة)
- لو الجهاز `fr-FR` → `values/` (نفس المشكلة)

---

## 4. نصوص hardcoded في كود Java (BAD PRACTICE)

```bash
$ grep -rPo '"[\xd8-\xdb][^"]+"' com/egy/webpaymentapp/
```

النتيجة:

| الملف | السطر | النص المُهرَّب |
|---|---|---|
| `com/egy/webpaymentapp/Screens/web/h.java` | (مكرر مرتين) | `"لايوجد إتصال بالشبكة"` (Connection Lost) |
| `com/egy/webpaymentapp/Screens/LoginActivity.java` | (مكرر مرتين) | `"تمت العملية بنجاح"` (Operation Successful) |

**فقط 4 strings عربية hardcoded في Java code** — رقم منخفض نسبياً (نقطة إيجابية صغيرة).

⚠️ **لكن:** نفس النصوص موجودة في strings.xml:
```xml
<string name="no_connection">لايوجد اتصال بالشبكة</string>   ← لاحظ "اتصال" بدون همزة
<!-- vs hardcoded: "لايوجد إتصال بالشبكة" ← مع همزة! -->
```

= **عدم اتساق في الإملاء العربي!** نسخة بهمزة، نسخة بدون. تجربة مستخدم غير متماسكة.

---

## 5. نصوص hardcoded في XML layouts

من `activity_main.xml`:
```xml
<TextView android:id="@id/txt_name"
    android:text="Hello World!"           ← ⚠️ hardcoded English في layout!
    .../>
```

من `activity_login.xml`:
```xml
<TextView android:id="@id/txt_about"
    android:text="About App"               ← ⚠️ hardcoded English في layout!
    .../>
```

**هذه قيم placeholder من Android Studio templates** لم يُحذفها المطور:
- `"Hello World!"` → يجب أن يكون `@string/welcome_message` أو ديناميكي
- `"About App"` → يجب أن يكون `@string/about_app`

---

## 6. نصوص hardcoded في HTML/JS

من تحليل `01_html_assets.md` و `02_javascript_assets.md`:

| الموقع | النص العربي |
|---|---|
| `paymentList.html` placeholder | `"بحث..."` |
| `paymentList.html` button | `"بحث"` |
| `readinglist.html` button | `"المحاولة مرة أخرى"` |
| `readinglist.js` (في array مُمَوّه) | `"القراءة"`, `"الاسم"`, `"الاجمالي"`, `"العدد :"` |

= **8+ نصوص عربية hardcoded في طبقة الـ web**، خارج نظام Android i18n تماماً.

---

## 7. ملف الـ Plurals (الجمع)

```bash
$ cat res/values-ar/plurals.xml
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="mtrl_badge_content_description">
        <item quantity="other">%d إشعار جديد</item>
        <item quantity="zero">%d إشعار جديد</item>
        <item quantity="one">إشعار جديد واحد (%d)</item>
        <item quantity="two">إشعاران جديدان (%d)</item>
        <item quantity="few">%d إشعارات جديدة</item>
        <item quantity="many">%d إشعارًا جديدًا</item>
    </plurals>
</resources>
```

✅ هذا الـ plural يدعم 6 صيغ الجمع العربية (Zero, One, Two, Few, Many, Other) — كلها من Material Library.

❌ **لكن التطبيق نفسه لا يستخدم `plurals` لأي نص!**

تأكيد:
```bash
$ grep -rn "getQuantityString\|@plurals" com/egy/webpaymentapp/
# 0 hits
```

- في الإيصال: "10 سندات", "1 سند", "2 سند" — الكود يبني هذه يدوياً
- في خوارزمية التفقيط (راجع `06_business_logic/06_arabic_number_to_words.md`): bug "اثنين" بدلاً من "اثنان" — لا يستفيد من plurals.

---

## 8. عدد strings التطبيق الفعلية

```bash
$ grep '<string ' res/values/strings.xml \
    | grep -vE "abc_|mtrl_|androidx_|material_|common_google|chip_text|bottom_sheet|tooltip|cardview_|notify|search_menu|side_sheet|m3_|preference_|range_start|range_end|nav_app_bar|date_picker|expand_button|character_counter|path_password|action_bar_|menu_|select_dialog|item_view_role|exposed_drop|fab_|appbar_|password_toggle|switch_|status_bar_notification|hide_bottom" \
    | wc -l
```

⇒ **~77 string فعلية للتطبيق** (من 192 إجمالي في `values/`).

**77 نص فقط** يصف التطبيق كاملاً. عدد قليل جداً لتطبيق دفع — يدل على أن:
- معظم البيانات (الأسماء، المبالغ، التواريخ) تأتي **ديناميكياً من backend**
- أو **hardcoded في HTML/JS/Java**

---

## 9. عيّنة من النصوص (للتعرف على نطاق التطبيق)

| `name` | النص العربي | الوظيفة |
|---|---|---|
| `app_name` | ECAS WEB | اسم التطبيق |
| `btn_login` | دخول | زر تسجيل الدخول |
| `Exit_From_System` | الخروج من البرنامج ؟ | تأكيد خروج |
| `add_castomer` | اضافة عميل | إضافة عميل جديد |
| `amt_grter_bal` | المبلغ المدفوع اكبر من رصيد العميل | خطأ تحصيل |
| `cust_bal` | رصيد العميل | عرض رصيد |
| `cust_call` | اتصال بالمشترك | زر الاتصال |
| `doc_printing_done` | تم طباعة السند بنجاح | نجاح طباعة |
| `doc_printing_fail` | فشل عملية طباعة المستند | فشل طباعة |
| `pay_list` | التحصيلات | قائمة المدفوعات |
| `prev_reading` | "القراءة السابقة " | عداد كهرباء |
| `print` | طباعة التقرير | زر طباعة |
| `prntInvs` | طباعة فاتورة | زر طباعة (مختصر) |
| `r310_bixlion` | Bixlion | اسم طابعة (typo: Bixolon) |
| `rpp300_rongta` | Rongta | اسم طابعة |
| `sewoo` | طابعة نوع SEWOO | نوع طابعة |
| `scrn_titl_bill_pay` | التسديدات | عنوان شاشة |
| `scrn_titl_change_pass` | تغير كلمة مرور الحساب | عنوان شاشة |
| `connect_printer` | توصيل | زر اتصال طابعة |
| `not_connected` | غير متصل بالطابعة | حالة طابعة |
| `no_connection` | لايوجد اتصال بالشبكة | خطأ شبكة |

---

## 10. typos / إملاء غير متسق

| المُكتشف | الصحيح | الموقع |
|---|---|---|
| `castomer` | customer | `add_castomer` (key) |
| `netxt` | next | `cp_enable_reading_netxt` (key) |
| `pymny` | payment | `msg_error_procedure_pymny` (key) |
| `prntInvs` | print_invoices | اختصار غير معياري (key) |
| `Bixlion` | Bixolon | `r310_bixlion` (value) — اسم العلامة التجارية خطأ! |
| `لايوجد اتصال` vs `لايوجد إتصال` | إتصال (مع همزة) | inconsistent |
| `لايوجد` | لا يوجد (بمسافة) | rule العربية القياسية |
| `Hello World!` | حذف | hardcoded في activity_main.xml |
| `About App` | translate | hardcoded في activity_login.xml |

---

## 11. الـ Plurals + Numerals: مشكلة الأرقام

التطبيق يعرض أرقاماً (مبالغ، عدّادات) **لكن**:
- لا يستخدم `NumberFormat.getInstance(Locale.forLanguageTag("ar"))` لتنسيق الأرقام
- لا يفرّق بين الأرقام العربية الشرقية (٠١٢٣٤) والغربية (01234)
- يستخدم `Integer.parseInt` و `Double.parseDouble` مباشرة (راجع `06_business_logic/07_currency_handling.md` للـ bug الكبير)

النتيجة: واجهة عربية لكن الأرقام تظهر دائماً بالأرقام الغربية (Arabic-Indic numerals غير مدعومة).

---

## 12. استراتيجية الترجمة في النسخة الجديدة (React Native)

### 12.1 المكتبة المقترحة: `react-i18next`

```bash
npm i react-i18next i18next
```

### 12.2 بنية الملفات

```
src/
├── i18n/
│   ├── index.ts
│   ├── locales/
│   │   ├── ar.json      ← العربية (default)
│   │   ├── en.json      ← الإنجليزية
│   │   └── tr.json      ← (اختياري) التركية (تواجد يمني-تركي)
│   └── plurals.ts       ← مخصص للجمع العربي
```

### 12.3 مثال `ar.json`

```json
{
  "common": {
    "search": "بحث...",
    "save": "حفظ",
    "ok": "موافق",
    "cancel": "إلغاء",
    "retry": "المحاولة مرة أخرى",
    "loading": "يرجى الانتظار"
  },
  "auth": {
    "loginButton": "دخول",
    "userIdHint": "رقم المستخدم",
    "passwordHint": "كلمة المرور",
    "successLogin": "تمت العملية بنجاح"
  },
  "errors": {
    "noConnection": "لا يوجد اتصال بالشبكة",
    "invalidBranch": "رقم الفرع غير صحيح",
    "amountExceedsBalance": "المبلغ المدفوع أكبر من رصيد العميل"
  },
  "screens": {
    "main": "الشاشة الرئيسية",
    "payments": "التحصيلات",
    "readings": "القراءات",
    "settings": "الإعدادات"
  },
  "printer": {
    "connect": "توصيل",
    "notConnected": "غير متصل بالطابعة",
    "printSuccess": "تم طباعة السند بنجاح",
    "printFail": "فشل عملية طباعة المستند",
    "types": {
      "bixolon": "Bixolon",
      "rongta": "Rongta",
      "sewoo": "Sewoo"
    }
  }
}
```

### 12.4 استخدام في الكود

```tsx
import { useTranslation } from 'react-i18next';

export function LoginScreen() {
  const { t } = useTranslation();
  return (
    <View>
      <TextInput placeholder={t('auth.userIdHint')} />
      <Button title={t('auth.loginButton')} />
    </View>
  );
}
```

### 12.5 RTL تلقائي

```tsx
import { I18nManager } from 'react-native';

// في App.tsx على bootstrap:
I18nManager.allowRTL(true);
I18nManager.forceRTL(i18n.language === 'ar');
```

### 12.6 الجمع العربي (6 صيغ)

```tsx
// ar.json
{
  "notifications": {
    "count_zero": "لا إشعارات",
    "count_one": "إشعار واحد",
    "count_two": "إشعاران",
    "count_few": "{{count}} إشعارات",
    "count_many": "{{count}} إشعارًا",
    "count_other": "{{count}} إشعار"
  }
}

// Usage:
t('notifications.count', { count: 7 })   // → "7 إشعارات"
t('notifications.count', { count: 50 })  // → "50 إشعارًا"
t('notifications.count', { count: 100 }) // → "100 إشعار"
```

### 12.7 الأرقام العربية

```tsx
const formatNumberAR = (n: number) =>
  new Intl.NumberFormat('ar-YE', { useGrouping: true }).format(n);

// formatNumberAR(1234.5)  → "١٬٢٣٤٫٥"
```

---

## 13. خطة الترحيل

| المرحلة | الإجراء |
|---|---|
| 1 | استخراج كل strings من `values/` + `values-ar/` (~165 string فريد بعد الدمج) |
| 2 | إصلاح typos: `add_castomer`→`add_customer`, `Bixlion`→`Bixolon`, إلخ. |
| 3 | إصلاح إملاء عربي: توحيد "اتصال"، "لا يوجد"، إلخ. |
| 4 | تحويل النصوص العربية المُسرَّبة من `values/` إلى `values-ar/` |
| 5 | إنشاء `values/` (English) جديد بترجمة كاملة |
| 6 | حذف 115 لغة Material غير ضرورية (بنية build توليدها تلقائياً) |
| 7 | استخراج كل النصوص hardcoded من HTML/JS (8+ نصوص) |
| 8 | استخراج كل النصوص hardcoded من Java (4 نصوص) |
| 9 | تحويل كل ذلك إلى `ar.json` + `en.json` لـ react-i18next |
| 10 | إضافة `plurals` العربية الفعلية للنصوص المعدودة |
| 11 | اختبار جميع الشاشات على `en-US` و `ar-YE` و `ar-SA` |

**التوفير المتوقع:**
- 115 ملف values-XX مكرر × ~5 KB = **~575 KB من APK**
- وضوح كامل للنصوص (لا hardcoded)
- اتساق إملائي

---

## 14. مصادر التحقق

| المصدر | الأمر |
|---|---|
| عدد اللغات | `ls -d res/values* \| wc -l` |
| strings per lang | `for f in res/values*/strings.xml; do grep -c '<string ' $f; done` |
| Arabic in default | `grep '<string ' res/values/strings.xml \| grep -P "[\u0600-\u06FF]"` |
| supportsRtl | `grep "supportsRtl" AndroidManifest.xml` |
| Locale usage | `grep -rn "Locale\|setLocale" com/egy/webpaymentapp/` |
| hardcoded Arabic in Java | `grep -rPo '"[\xd8-\xdb][^"]+"' com/egy/webpaymentapp/` |
| hardcoded English in layouts | `grep -n 'android:text="[A-Za-z]' res/layout/*.xml` |
| plurals usage | `grep -rn "getQuantityString\|@plurals" com/egy/webpaymentapp/` |

---

**ملف:** `Deep_Analysis/09_assets_resources/03_strings_and_translations.md`
**عدد اللغات المدّعى:** 117
**عدد اللغات الفعلية:** 2 (عربي + إنجليزي fallback مكسور)
**عدد strings فعلية للتطبيق:** ~77
**Hardcoded خارج strings.xml:** 4 في Java + 8 في HTML/JS = **12 على الأقل**
**Typos:** 5+ (castomer, netxt, pymny, Bixlion, hardcoded "Hello World!")
**أكبر مشكلة:** `values/` (default) ليس Englishـً صافياً — مُلوَّث بعربية ⇒ تجربة مكسورة على أي جهاز غير عربي + لا تحكم برمجي بـ Locale + لا plurals مستخدمة + لا تنسيق أرقام عربية
**التوصية:** إعادة بناء كاملة بـ react-i18next مع 2 لغات (ar/en) نظيفة + plurals صحيحة + توحيد إملائي
