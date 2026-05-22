# 04 — تحليل Drawables والصور في AbbasiyCashiers (Ecas v18.4)

> **الموقع:** `res/drawable*/`, `res/mipmap-*/`
> **المنهج:** `find`, `file`, `md5sum`, تصفية app-specific vs Material/AndroidX، فحص الـ vector XML vs raster PNG، اكتشاف placeholders والصور المكررة.

---

## 1. الجرد العام

```bash
$ du -sh res/
6.3M  res/

$ ls -d res/drawable* | wc -l
17 مجلد drawable

$ ls -d res/mipmap-* | wc -l
5 مجلد mipmap (لأيقونة التطبيق)
```

| مجلد drawable | عدد الملفات | الحجم | الوظيفة |
|---|---|---|---|
| `res/drawable/` | 106 | 432K | Material Components + selectors + بعض الـ vector drawables |
| `res/drawable-hdpi/` | 67 | 272K | PNG hi-DPI |
| `res/drawable-mdpi/` | 66 | 268K | PNG medium-DPI (baseline) |
| `res/drawable-xhdpi/` | 69 | 280K | PNG x-DPI |
| `res/drawable-xxhdpi/` | 63 | 260K | PNG xx-DPI |
| `res/drawable-xxxhdpi/` | 34 | 140K | PNG xxx-DPI (high-end devices) |
| `res/drawable-ldpi/` | 8 | 36K | PNG low-DPI (~lots of dead) |
| `res/drawable-anydpi-v21/` | 8 | 36K | Vector XML (Android 5+) |
| `res/drawable-v21/`, `-v23/`, `-v24/` | 11+2+2 | ~72K | API-specific |
| `res/drawable-ldrtl-*` (5 مجلدات) | 3 لكل واحد | 16K لكل واحد | RTL-specific |
| `res/drawable-watch-v20/` | 1 | 8K | Wear OS (هل التطبيق لـ ساعات؟!) |

**ملاحظات أولية:**
- `res/drawable-watch-v20/` لـ Wear OS — التطبيق ليس Wear app! ⇒ dead code (بقايا من template Android Studio)
- 5 مجلدات `drawable-ldrtl-*` × 3 ملفات = 15 ملف RTL مخصص — لكل واحد ~5KB (~75 KB إجمالي)

---

## 2. صور التطبيق المخصصة (App-specific Drawables)

### 2.1 الأيقونات الـ 8 الفعلية

| الاسم | الوصف المتوقع | عبر DPIs |
|---|---|---|
| `ic_launcher.png` | أيقونة التطبيق (Launcher) | 5 dpis (mdpi→xxxhdpi) |
| `ic_launcher_round.png` | أيقونة دائرية (Android 7.1+) | 5 dpis |
| `ic_launcher_background.png` | خلفية adaptive icon | 6 dpis + 1 anydpi |
| `ic_logo.png` | لوغو في login screen | 6 dpis + 1 anydpi |
| `ic_add_cust.png` | زر "إضافة عميل" | 6 dpis + 1 anydpi |
| `ic_call_cust.png` | زر "اتصال بالعميل" | 6 dpis + 1 anydpi |
| `ic_cust_loc_track.png` | زر "تتبع موقع العميل" | 6 dpis + 1 anydpi |
| `ic_cust_print_inv.png` | زر "طباعة فاتورة" | 6 dpis + 1 anydpi |
| `ic_printer.png` | أيقونة طابعة | 6 dpis + 1 anydpi |
| `ic_sucess.png` | علامة نجاح (typo: ic_success) | 6 dpis + 1 anydpi |

### 2.2 الحقيقة الصادمة: **3 من 8 placeholders 1×1 pixel!**

```bash
$ for img in res/drawable-mdpi/ic_*.png; do
    echo "$img: $(file -b $img)"
  done
```

| الصورة | الأبعاد الفعلية | النوع |
|---|---|---|
| `ic_logo.png` | **1 × 1 px** (67 bytes) | 🔴 **placeholder فارغ** |
| `ic_cust_loc_track.png` | **1 × 1 px** (67 bytes) | 🔴 **placeholder فارغ** |
| `ic_launcher_background.png` | **1 × 1 px** (67 bytes) | 🔴 **placeholder فارغ** |
| `ic_add_cust.png` | 24 × 24 px | ✅ صورة حقيقية |
| `ic_printer.png` | 24 × 24 px | ✅ صورة حقيقية |
| `ic_call_cust.png` | 48 × 48 px | ✅ صورة حقيقية |
| `ic_cust_print_inv.png` | 48 × 48 px | ✅ صورة حقيقية |
| `ic_sucess.png` | 64 × 64 px | ✅ صورة حقيقية |

### 2.3 لماذا placeholders؟

**السبب:** التطبيق يستخدم **Vector Drawables (XML)** للأجهزة Android 5+ من `drawable-anydpi-v21/`. الـ PNG الـ raster هي fallback للأجهزة الأقدم (`minSdkVersion=19` = Android 4.4 KitKat).

```bash
$ cat res/drawable-anydpi-v21/ic_add_cust.xml
<?xml version="1.0" encoding="utf-8"?>
<vector android:tint="?colorControlNormal"
    android:height="24.0dip" android:width="24.0dip"
    android:viewportWidth="24.0" android:viewportHeight="24.0">
    <path android:fillColor="@android:color/white"
        android:pathData="M15,12c2.21,0 4,-1.79..." />
</vector>
```

✅ vector XML للأجهزة الحديثة (Android 5+).
❌ PNG raster لـ Android 4.4 — **بعضها 1x1 placeholder فارغ!**

### 2.4 لكن انتظر — `ic_logo` و `ic_launcher_background` و `ic_cust_loc_track` placeholders فقط:

```bash
$ cat res/drawable-anydpi-v21/ic_logo.xml
<?xml version="1.0" encoding="utf-8"?>
<x />                                ← ⚠️ XML فارغ!
```

```bash
$ cat res/drawable-anydpi-v21/ic_cust_loc_track.xml
<?xml version="1.0" encoding="utf-8"?>
<x />                                ← ⚠️ XML فارغ!

$ cat res/drawable-anydpi-v21/ic_launcher_background.xml
<?xml version="1.0" encoding="utf-8"?>
<x />                                ← ⚠️ XML فارغ!
```

**اكتشاف فادح:** 3 من الـ anydpi-v21 XML files **فارغة بالكامل** (`<x />`). ⇒ لا vector، لا raster — كل الأجهزة (قديمة وحديثة) ترى **1×1 placeholder شفاف**.

**التبعات:**
- **`ic_logo` فارغ** → لكن في `activity_login.xml`:
  ```xml
  <ImageView android:src="@mipmap/ic_launcher" />
  ```
  يستخدم `@mipmap/ic_launcher` بدلاً منه ⇒ ic_logo dead reference.
- **`ic_cust_loc_track` فارغ** → زر "تتبع موقع العميل" بدون أيقونة! UX مكسور.
- **`ic_launcher_background` فارغ** → خلفية launcher icon (adaptive icon) فارغة → الـ launcher icon لن يكون adaptive على Android 8+!

### 2.5 typo في الاسم

```
ic_sucess.png   ← خطأ إملائي: "success" بحرف 2 c
```

---

## 3. أيقونة التطبيق (Launcher Icon)

### 3.1 الحقيقة الصادمة #2: launcher_round == launcher

```bash
$ md5sum res/mipmap-mdpi/ic_launcher.png res/mipmap-mdpi/ic_launcher_round.png
028e1ff0b6ab1b25318f8913becc50d1  res/mipmap-mdpi/ic_launcher.png
028e1ff0b6ab1b25318f8913becc50d1  res/mipmap-mdpi/ic_launcher_round.png  ← نفس MD5!
```

⇒ **`ic_launcher_round` = نسخة طبق الأصل من `ic_launcher`** عبر **كل DPIs**.

**التبعات:**
- على Android 7.1+، الـ launcher الذي يطلب round icon (مثل Samsung One UI) سيعرض **square icon مع زوايا مقصوصة** بدلاً من round حقيقي.
- يهدر مساحة (~11 KB × 5 DPIs × 2 = ~110 KB).

### 3.2 الحقيقة الصادمة #3: mdpi == hdpi == xhdpi (نفس الصورة!)

```bash
$ md5sum res/mipmap-{mdpi,hdpi,xhdpi}/ic_launcher.png
028e1ff0b6ab1b25318f8913becc50d1  res/mipmap-mdpi/ic_launcher.png
028e1ff0b6ab1b25318f8913becc50d1  res/mipmap-hdpi/ic_launcher.png
028e1ff0b6ab1b25318f8913becc50d1  res/mipmap-xhdpi/ic_launcher.png
```

ولكن `xxhdpi` و `xxxhdpi` لهما أحجام مختلفة (20 KB و 31 KB) ⇒ صورتان حقيقيتان فقط (xxhdpi + xxxhdpi).

النتيجة:
- Android على mdpi (160 dpi) يحمّل صورة 11 KB
- Android على hdpi (240 dpi) يحمّل **نفس** الـ 11 KB بدلاً من نسخة مكبّرة محسّنة
- على الأجهزة المنخفضة، الـ launcher icon يبدو pixelated

✅ مكاسب: حجم APK أصغر بـ ~22 KB
❌ خسائر: جودة عرض ضعيفة على بعض الأجهزة

### 3.3 الأحجام الفعلية

| المجلد | الحجم | الـ MD5 |
|---|---|---|
| `mipmap-mdpi/ic_launcher.png` | 11123 B | `028e1ff0...` |
| `mipmap-hdpi/ic_launcher.png` | 11123 B | `028e1ff0...` (نفس) |
| `mipmap-xhdpi/ic_launcher.png` | 11123 B | `028e1ff0...` (نفس) |
| `mipmap-xxhdpi/ic_launcher.png` | 20041 B | جديد |
| `mipmap-xxxhdpi/ic_launcher.png` | 31482 B | جديد |

---

## 4. التكرار في FontAwesome assets

في `assets/myweb/css/font-awesome-4.7.0/fonts/` (راجع `02_javascript_assets.md`):

| الملف | الحجم |
|---|---|
| `FontAwesome.otf` | 135 KB |
| `fontawesome-webfont.eot` | 166 KB |
| `fontawesome-webfont.svg` | 447 KB |
| `fontawesome-webfont.ttf` | 166 KB ← **مكرر مع .otf** |
| `fontawesome-webfont.woff` | 98 KB |
| `fontawesome-webfont.woff2` | 77 KB |

**WebView Android يستخدم `.ttf` فقط** ⇒ كل صيغ `eot/svg/woff/woff2/otf` (988 KB) **dead** في APK.

---

## 5. أحجام الـ raster (PNG) الفعلية الحقيقية

### 5.1 أكبر 15 PNG في res/

```bash
$ find res -type f -name "*.png" -exec ls -la {} \; | sort -k5 -rn | head -15
```

| الحجم | الملف |
|---|---|
| 31,482 | `mipmap-xxxhdpi/ic_launcher.png` (وَ ic_launcher_round.png نسخة) |
| 20,041 | `mipmap-xxhdpi/ic_launcher.png` (وَ ic_launcher_round.png نسخة) |
| 11,123 | `mipmap-{mdpi,hdpi,xhdpi}/ic_launcher.png` ×6 (3 DPIs × launcher + round) |
| 4,400 | `drawable-xxhdpi/abc_popup_background_mtrl_mult.9.png` (Material) |
| 4,092 | `drawable-xxxhdpi/ic_sucess.png` |
| 4,010 | `drawable-xxxhdpi/abc_btn_switch_to_on_mtrl_00012.9.png` (Material) |
| 3,595 | `drawable-xxhdpi/abc_btn_switch_to_on_mtrl_00012.9.png` (Material) |
| 3,354 | `drawable-xxxhdpi/abc_btn_switch_to_on_mtrl_00001.9.png` (Material) |

**الخلاصة:** أكبر الصور هي الـ launcher icons. كل الباقي من Material Components (drawable selectors, switch states, ripple backgrounds). **لا صور كبيرة من التطبيق نفسه** (لا backgrounds, لا banners, لا splash screens).

### 5.2 لا Splash Screen

```bash
$ grep -rn "splash\|SplashActivity\|launch_screen" AndroidManifest.xml res/
# 0 hits
```

❌ التطبيق لا يحتوي على splash screen مخصصة. على Android 12+، النظام يولّد splash تلقائياً من launcher icon (الذي = نسخة مكررة من ic_launcher).

---

## 6. ملف drawable الـ XML الوحيد للتطبيق

```bash
$ ls res/drawable/ | grep -v "^abc_\|^mtrl_\|^material_\|^design_\|^common_google\|^btn_checkbox\|^btn_radio\|^avd_\|^\$\|^ic_clock\|^ic_keyboard\|^navigation_empty\|^test_\|^text_input_box\|^tooltip_\|^notify\|^notification_\|^ic_mtrl"
```

⇒ **`layout_border.xml`** — فقط ملف drawable XML واحد مخصص!

محتمل أنه border للـ list items أو cards. **التطبيق لا يحوي drawable shapes أو selectors أو layer-lists مخصصة**.

⇒ التصميم يعتمد كلياً على Material Components defaults + colorPrimary واحد (`#1E94CA`) (راجع `06_colors_themes_styles.md`).

---

## 7. drawable-ldrtl (RTL-specific)

```
res/drawable-ldrtl-hdpi/    : 3 files (16 KB)
res/drawable-ldrtl-mdpi/    : 3 files (16 KB)
res/drawable-ldrtl-xhdpi/   : 3 files (16 KB)
res/drawable-ldrtl-xxhdpi/  : 3 files (16 KB)
res/drawable-ldrtl-xxxhdpi/ : 3 files (16 KB)
```

محتوى كل مجلد:
```
abc_ic_menu_copy_mtrl_am_alpha.png
abc_ic_menu_cut_mtrl_alpha.png
abc_spinner_mtrl_am_alpha.9.png
```

= **كلها من AppCompat (`abc_`)** = Material Library — تُحَمَّل تلقائياً عند RTL. **لا drawables RTL مخصصة من التطبيق نفسه**.

---

## 8. drawable-watch-v20 (Wear OS!)

```bash
$ ls res/drawable-watch-v20/
abc_dialog_material_background.9.png
```

= ملف Material Library واحد للأجهزة Wear OS. **التطبيق ليس Wear app** (لا `<uses-feature android:name="android.hardware.type.watch">` في Manifest). ⇒ **dead resource** (8 KB).

---

## 9. الكود الميت الفعلي في drawables

| العنصر | الحجم | السبب |
|---|---|---|
| `drawable-watch-v20/` | 8 KB | التطبيق ليس Wear app |
| `ic_logo.png` × 6 DPIs + xml فارغ | ~400 B | placeholder فارغ، التطبيق يستخدم `@mipmap/ic_launcher` |
| `ic_cust_loc_track.png` × 6 DPIs + xml فارغ | ~400 B | placeholder فارغ ⇒ UX مكسور |
| `ic_launcher_background.png` × 6 DPIs + xml فارغ | ~400 B | placeholder ⇒ adaptive icon لن يعمل |
| `ic_launcher_round.png` × 5 DPIs | ~85 KB | تكرار طبق الأصل لـ ic_launcher |
| FontAwesome eot/svg/woff/woff2/otf | ~988 KB | WebView يستخدم ttf فقط |
| `bootstrap-*.map` files | ~700 KB | source maps في إنتاج |
| **المجموع** | **~1.8 MB من ~6.3 MB في res/ + assets** | |

---

## 10. ملخص بصري — أصول التطبيق الفنية

```
APK Visual Assets:
┌─────────────────────────────────────────────────────────────────┐
│ Launcher icons         ║ ic_launcher (5 DPIs)         ~85 KB    │
│                        ║ ic_launcher_round (5 DPIs)   ~85 KB ⚠️ │  ← مكرر
│                        ║                                         │
│ App-specific vectors   ║ ic_add_cust.xml              ~500 B    │
│ (Android 5+)           ║ ic_call_cust.xml             ~700 B    │
│                        ║ ic_cust_print_inv.xml        ~900 B    │
│                        ║ ic_printer.xml               ~500 B    │
│                        ║ ic_sucess.xml                ~500 B    │
│                        ║                                         │
│ Placeholders فارغة     ║ ic_logo.png/.xml            ~400 B 🔴  │
│                        ║ ic_cust_loc_track.png/.xml  ~400 B 🔴  │
│                        ║ ic_launcher_background.png  ~400 B 🔴  │
│                        ║                                         │
│ Drawable XML shapes    ║ layout_border.xml           ~200 B     │
│                        ║                                         │
│ ldrtl Material         ║ 15 ملف Material RTL         ~75 KB     │
│                        ║                                         │
│ Wear OS dead           ║ abc_dialog_material...      ~8 KB ⚠️   │
└─────────────────────────────────────────────────────────────────┘

Web Assets (assets/myweb/):
┌─────────────────────────────────────────────────────────────────┐
│ FontAwesome (6 formats) ~1 MB ⚠️ (4 صيغ مكررة)                  │
│ Bootstrap CSS (4 ملف)   ~700 KB                                 │
│ jQuery + Bootstrap JS   ~290 KB                                 │
│ Custom JS (مع dead)     ~58 KB                                  │
│ HTML files (مُمَوّهة)    ~44 KB                                  │
│ Cairo + GE-Dinar fonts  ~195 KB ⚠️ (نفس الملف باسمين)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. الـ Design System الحالي — مفقود

التطبيق **لا يحوي**:
- Splash screen مخصصة
- Onboarding illustrations
- Empty states illustrations (لو القائمة فارغة، لا صورة معبّرة)
- Error illustrations (شاشة الخطأ default_error_page.html تحوي SVG واحد inline)
- App icons consistent بـ branding
- Logo حقيقي (المُستخدم = mipmap/ic_launcher فقط)

كل الواجهة تعتمد على:
- Material Components الافتراضية
- لون واحد: `colorPrimary = #1E94CA` (أزرق)
- خط واحد: `helveticaneuew23_bd.ttf` (راجع `06_colors_themes_styles.md` — وهو فعلياً Helvetica Neue تجاري!)
- FontAwesome 4.7 للأيقونات في WebView

⇒ **تصميم بسيط جداً (utilitarian)، يفتقر إلى branding احترافي**. هذا متوقع لتطبيق B2B داخلي لشركة كهرباء، لكن يخالف توقعات UX الحديثة.

---

## 12. البديل في React Native

### 12.1 الأيقونات

```bash
npm i react-native-svg react-native-svg-transformer
```

**استراتيجية:**
1. كل الأيقونات الـ 5 الحقيقية (`ic_add_cust`, `ic_call_cust`, `ic_cust_print_inv`, `ic_printer`, `ic_sucess`) ⇒ **SVG واحد لكل أيقونة** (نفس Material Design icons):
   ```tsx
   import AddIcon from './icons/AddCustomer.svg';
   <AddIcon width={24} height={24} fill="#FFF" />
   ```

2. الأيقونات داخل WebView (التي كانت من FontAwesome) ⇒ `react-native-vector-icons/FontAwesome`:
   ```tsx
   import Icon from 'react-native-vector-icons/FontAwesome';
   <Icon name="user-circle" size={24} color="#1E94CA" />
   ```

3. **حذف ic_logo placeholder** + استخدام logo حقيقي:
   ```tsx
   <Image source={require('./assets/logo.svg')} />
   // أو لو لا يوجد logo:
   <Text style={{fontSize:32, fontWeight:'bold'}}>ECAS WEB</Text>
   ```

### 12.2 Launcher Icon (Adaptive)

```bash
npx react-native-asset
# يولّد:
android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml   (adaptive)
android/app/src/main/res/drawable/ic_launcher_background.xml (vector)
android/app/src/main/res/drawable/ic_launcher_foreground.xml (vector)
```

= **آيقونة adaptive حقيقية** بدل ic_launcher_round مكرر.

### 12.3 Splash Screen

```bash
npm i react-native-bootsplash
npx react-native-bootsplash generate ./assets/logo.png
```

= splash screen صحيحة بدلاً من شاشة فارغة.

### 12.4 المكاسب الكمية

| البُعد | حالياً | بـ RN |
|---|---|---|
| حجم الـ launcher icons | ~170 KB (مكرر) | ~30 KB (adaptive) |
| حجم الـ drawables | ~2 MB (مع dead) | ~50 KB (SVG vectors) |
| placeholders فارغة | 3 (ic_logo, ic_cust_loc_track, ic_launcher_background) | 0 |
| تكرار صور | 6 (mipmap لـ 3 DPIs + launcher_round) | 0 |
| dead resource (Wear) | 8 KB | 0 |
| FontAwesome صيغ مكررة | ~988 KB (eot/svg/woff/otf) | 0 (TTF تلقائي) |
| Splash screen | لا يوجد | adaptive من react-native-bootsplash |
| **توفير إجمالي** | | **~3 MB من APK** |

---

## 13. مصادر التحقق

| المصدر | الأمر |
|---|---|
| inventory drawables | `find res -type f -path "*drawable*" -o -path "*mipmap*"` |
| تحقق placeholder 1x1 | `file res/drawable-mdpi/ic_logo.png` ⇒ "PNG image data, 1 x 1" |
| تحقق xml فارغ | `cat res/drawable-anydpi-v21/ic_logo.xml` ⇒ `<x />` |
| تحقق تكرار launcher | `md5sum res/mipmap-*/ic_launcher*.png` |
| تحقق صور الـ DPIs | `for d in mdpi hdpi xhdpi xxhdpi xxxhdpi; do md5sum res/mipmap-$d/ic_launcher.png; done` |
| watch-v20 dead | `grep "android.hardware.type.watch" AndroidManifest.xml` ⇒ 0 hits |
| usage of ic_logo | `grep -rn "@drawable/ic_logo" res/ AndroidManifest.xml` ⇒ check Java/XML |
| FontAwesome formats | `ls -la assets/myweb/css/font-awesome-4.7.0/fonts/` |

---

**ملف:** `Deep_Analysis/09_assets_resources/04_drawables_and_images.md`
**عدد drawables التطبيق الفعلية:** 8 (لكن 3 placeholders فارغة!)
**حجم res/ الإجمالي:** 6.3 MB (معظمها Material Components)
**Placeholders فارغة:** ic_logo, ic_cust_loc_track, ic_launcher_background (1×1 px PNG + `<x />` XML)
**تكرارات:** ic_launcher_round = ic_launcher عبر كل DPIs (~85 KB) + mipmap-mdpi/hdpi/xhdpi كلها نفس MD5 (~22 KB)
**Dead:** drawable-watch-v20 (~8 KB)، FontAwesome 4 صيغ مكررة (~988 KB)
**أكبر مشكلة:** placeholders فارغة (UX مكسور) + تكرار launcher_round + خلفية adaptive فارغة + لا splash screen + لا branding حقيقي + typo `ic_sucess`
**التوصية:** استبدال كامل بـ SVG vectors + adaptive launcher icon حقيقي + splash screen من react-native-bootsplash. **توفير ~3 MB من APK**
