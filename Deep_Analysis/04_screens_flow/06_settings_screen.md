# Setting_Printer_Activity — شاشة إعدادات الطابعة

> **المصدر:** `com.egy.webpaymentapp.Screens.Setting_Printer_Activity`
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/Screens/Setting_Printer_Activity.java`
> **عدد الأسطر:** 26 سطر فقط — Activity-Container لـ PreferenceFragment.
> **الـ Layout:** `R.layout.activity_settings_printer` (مُتوقَّع)
> **الـ Fragment الجذر:** `R.id.pref_content`

---

## 1. الكود الكامل

```java
package com.egy.webpaymentapp.Screens;

import android.os.Bundle;
import androidx.appcompat.app.h;
import com.egy.webpaymentapp.R;

public class Setting_Printer_Activity extends h {

  @Override
  protected void onCreate(Bundle bundle) {
    super.onCreate(bundle);
    setContentView(R.layout.activity_settings_printer);
    
    h0();
    
    r().k(false);
    r().j(true);
    r().h(true);
    r().i(true);
    r().m(R.string.setting_printer_title);  // العنوان
  }

  @Override
  public boolean u() {
    finish();
    return true;
  }

  private void h0() {
    getSupportFragmentManager()
      .beginTransaction()
      .replace(R.id.pref_content, new SettingsFragment())   // ⚠️ غير ظاهر مباشرة
      .commit();
  }
}
```

⚠️ **الشيفرة الفعلية في JADX** قد تختلف قليلاً — الـ `h0()` هو الإسم المبهم لإجراء الـ replace.

---

## 2. الإعدادات المحفوظة (من `c.b.a.c.e(context)`)

من تحليل `c.b.a.c.java` (السطر `e(context)`):

```java
public static void e(Context context) {
  PreferenceManager pm = PreferenceManager.getDefaultSharedPreferences(context);
  
  // قراءة كل الإعدادات
  String prevPrinterAddress = pm.getString("printer_address", "");
  String prevPaperSize = pm.getString("paper_size", "");
  String prevDensity = pm.getString("printer_density", "");
  // … إلخ
  
  // قد يستخدمها لإنشاء Bixolon manager بإعدادات الطابعة
}
```

### المفاتيح المُتوقَّعة (من نمط الإسم):

| المفتاح | النوع | القيمة الإفتراضية | الوصف |
|---------|-------|------------------|------|
| `printer_address` | String | "" | عنوان MAC الطابعة المختارة |
| `printer_name` | String | "" | إسم الطابعة |
| `paper_size` | String | "80mm" | حجم الورق (50, 58, 80 mm) |
| `printer_density` | int | 50 | كثافة الحبر (0-100) |
| `auto_print` | boolean | true | طباعة تلقائية بعد كل عملية |
| `print_copies` | int | 1 | عدد النسخ |
| `print_company_logo` | boolean | true | طباعة الشعار |
| `print_gps_loc` | boolean | false | طباعة الإحداثيات |

⚠️ **هذه تخمينات** — يحتاج التحقق عبر فتح `res/xml/pref_printer.xml` أو ما يماثله.

---

## 3. كيف يتم فتحها

من `OprationsActivity.onOptionsItemSelected`:

```java
if (menuItem.getItemId() == R.id.printer_seting) {
  startActivityForResult(new Intent(this, Setting_Printer_Activity.class), 299);
}
```

ومن `WebviewActivity.onOptionsItemSelected`:

```java
if (menuItem.getItemId() == R.id.printer_seting) {
  startActivityForResult(new Intent(this, Setting_Printer_Activity.class), 299);
}
```

⇒ تُفتح من القائمة (Action Bar overflow) في `OprationsActivity` و `WebviewActivity` فقط.

⚠️ **لا يوجد طريق للوصول إليها من `MainActivity` مباشرة** — يجب على المستخدم فتح شاشة Payments أولاً.

---

## 4. تدفُّق النتيجة (`onActivityResult`)

عندما يعود المستخدم من الإعدادات:

```java
// في OprationsActivity.onActivityResult (السطر 373-376):
if (i == 299) {
  c.b.a.c.e(this);   // إعادة قراءة الإعدادات
  return;
}
```

⇒ بعد العودة، Bixolon manager يُعيد قراءة إعدادات الطابعة.

---

## 5. الشاشات الإضافية المرتبطة

### 5.1 `ScanActivity.java` (BixlonPrinterManger)
- 233 سطر
- يفتح من زر "اتصال طابعة" (في `OprationsActivity` Action Bar).
- يستخدم Bluetooth scan + RecyclerView لعرض الطابعات المتاحة.
- بعد إختيار طابعة ⇒ يحفظ MAC + إسم في SharedPreferences.

### 5.2 `BixlonPrinterManger/a.java`
- 295 سطر
- Dialog helper مع RecyclerView لعرض الطابعات المتصلة.
- يستخدم في `OprationsActivity.q`.

---

## 6. تخمينات بنية `SettingsFragment`

استناداً إلى pattern Android Preferences:

```java
public static class SettingsFragment extends PreferenceFragmentCompat {
  @Override
  public void onCreatePreferences(Bundle bundle, String rootKey) {
    setPreferencesFromResource(R.xml.pref_printer, rootKey);
    
    // ربط Preference change listeners
    Preference printerSelect = findPreference("printer_address");
    printerSelect.setOnPreferenceClickListener(p -> {
      startActivityForResult(new Intent(getActivity(), ScanActivity.class), REQ_SCAN);
      return true;
    });
  }
}
```

---

## 7. النقاط القابلة للتحسين في الإعادة

| # | المشكلة الحالية | الحلّ المقترح |
|---|-----------------|---------------|
| 1 | الوصول للإعدادات صعب (فقط من overflow menu) | إضافة tile مرئي في Main screen |
| 2 | لا تجربة اختبار الطابعة (test print) | زر "Print Test Receipt" |
| 3 | لا حفظ تلقائي للطابعات الـ "favorite" | قائمة Recent + Favorite |
| 4 | لا اعتبار لـ USB/Network printers | دعم وأنماط Connection |
| 5 | لا preview للقالب قبل الطباعة | WYSIWYG editor للقالب |
| 6 | لا dark mode دعم | دعم النظام |
| 7 | لا متابعة لمستوى الورق/الحبر | إذا الطابعة تدعم |

---

## 8. مقابل React Native للإعادة

```tsx
// src/screens/PrinterSettingsScreen.tsx
const PrinterSettingsScreen = () => {
  const { settings, updateSettings } = usePrinterSettings();
  
  return (
    <ScrollView>
      <SectionTitle>الإتصال</SectionTitle>
      <ListItem
        title="اختيار طابعة"
        subtitle={settings.printerName || 'لا توجد'}
        onPress={() => navigation.navigate('PrinterScan')}
      />
      
      <SectionTitle>التنسيق</SectionTitle>
      <SegmentedControl
        label="حجم الورق"
        options={['50mm', '58mm', '80mm']}
        value={settings.paperSize}
        onChange={(v) => updateSettings({ paperSize: v })}
      />
      
      <Slider
        label="كثافة الحبر"
        min={0} max={100}
        value={settings.density}
        onChange={(v) => updateSettings({ density: v })}
      />
      
      <Switch
        label="طباعة تلقائية"
        value={settings.autoPrint}
        onChange={(v) => updateSettings({ autoPrint: v })}
      />
      
      <SectionTitle>المحتوى</SectionTitle>
      <Switch
        label="طباعة الشعار"
        value={settings.printLogo}
        onChange={(v) => updateSettings({ printLogo: v })}
      />
      <Switch
        label="طباعة الموقع الجغرافي"
        value={settings.printGps}
        onChange={(v) => updateSettings({ printGps: v })}
      />
      
      <SectionTitle>الإختبار</SectionTitle>
      <Button title="🖨️ طباعة إيصال تجريبي" onPress={handleTestPrint} />
    </ScrollView>
  );
};
```

---

## 9. التدفُّق الكامل ASCII

```text
┌──────────────────────────────────────────┐
│      Setting_Printer_Activity             │
├──────────────────────────────────────────┤
│                                          │
│ onCreate                                  │
│   ↓ setContentView                        │
│   ↓ h0() ⇒ replace pref_content with     │
│            SettingsFragment               │
│   ↓ ActionBar setup                       │
│                                          │
│ SettingsFragment.onCreatePreferences      │
│   ↓ inflate R.xml.pref_printer            │
│   ↓ bind listeners:                       │
│       - printer_address → ScanActivity   │
│       - paper_size      → SharedPrefs    │
│       - print_density   → SharedPrefs    │
│       - …                                │
│                                          │
│ المستخدم يضغط رجوع                         │
│   ↓ finish() (RESULT_OK)                  │
│                                          │
│ في الـ Activity الأم (OprationsActivity):  │
│   onActivityResult(299):                  │
│     ↓ c.b.a.c.e(this) ⇒ re-read prefs    │
└──────────────────────────────────────────┘
```

---

## 10. خلاصة

| نقطة | التفصيل |
|------|---------|
| نوع | Container Activity لـ PreferenceFragment |
| تعقيد الكود | منخفض (26 سطر فقط) |
| التعقيد الفعلي | في الـ Fragment + ScanActivity (مجموعها ~500 سطر) |
| المخاطر | منخفضة — مجرد إعدادات محفوظة في SharedPrefs |
| التحسينات المُقترَحة | كثيرة — الوصول، التجربة، الـ UI |

---

> **يربط هذا الملف بـ:**
> - `08_native_libs/01_bxlpdf.md` (مكتبة Bixolon).
> - `06_business_logic/05_receipt_generation.md` (توليد الإيصال).
> - `10_rebuild_blueprint/06_ui_modernization.md` (التحديث).
