# User Model — تحليل عميق لكل حقل

> **المصدر:** `com.egy.webpaymentapp.webapi.models.User`
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/webapi/models/User.java`
> **عدد الحقول:** 21 حقل (Gson `@SerializedName` → كان يُسمَّى `c.c.b.a0.b` بعد ProGuard).
> **مكان حفظ الكائن:** `SharedPreferences("USER_DETAILS_PREF")` تحت المفتاح `APP_USER_KEY` (JSON كامل عبر Gson).

---

## 1. خريطة الحقول الكاملة (21 حقل)

| # | اسم الحقل في JSON | اسم متغير Java (مبهم) | النوع | Getter مبهم | Getter دلالي | الإستخدام في الكود |
|---|------|-----------|------|-----------|------|---------|
| 1 | `Id` | `f2438a` | `String` | `f()` | `getId()` | يُرسل كـ `user_no` في كل طلب POST. |
| 2 | `FirstName` | `f2439b` | `String` | — | `getFirstName()` | عرض اسم الموظف في الشاشة الرئيسية وفي الفواتير. |
| 3 | `LastName` | `f2440c` | `String` | — | `getLastName()` | غير مستخدم بشكل ظاهر — قد يُدمج مع `FirstName` لاحقاً. |
| 4 | `Username` | `f2441d` | `String` | `o()` | `getUsername()` | المستخدم بشكل أساسي في عرض الفاتورة (`user_name`). |
| 5 | `Token` | `f2442e` | `String` | `l()` | `getToken()` | **رمز المصادقة** — يُرسل في كل طلب كـ `acc_token` + في رأس `Authorization: Bearer`. |
| 6 | `Password` | `f` | `String` | — | `getPassword()` | كلمة المرور **المُشفّرة بـ RSA** بعد تشفيرها (لا تُحفظ بصيغة نصية). |
| 7 | `mob_srl` | `g` | `String` | — | `getMobSrl()` | الرقم التسلسلي للجهاز (`device_id` المُولّد من `MediaSessionCompat.D()`). |
| 8 | `restpass` | `h` | `String` | `k()` | `getResetPassFlag()` | إذا كانت `"1"` ⇒ يجب على المستخدم تغيير كلمة المرور عند الدخول. |
| 9 | `Cshr_AddWebPay` | `i` | `String` | `d()` | `canAddWebPayment()` | صلاحية: إضافة دفعة عبر WebView. القيم `"1"` أو `"0"`. |
| 10 | `Cshr_AddWebRead` | `j` | `String` | `e()` | `canAddWebReading()` | صلاحية: إضافة قراءة عداد. |
| 11 | `Cshr_AddWebMtrImg` | `k` | `String` | `c()` | `canAddMeterImage()` | صلاحية: إرفاق صورة العداد. |
| 12 | `Cshr_AddWebCstUpDate` | `l` | `String` | `b()` | `canUpdateCustomerLocation()` | صلاحية: تحديث إحداثيات الزبون. |
| 13 | `webview_url` | `m` | `String` *(public)* | — | — | عنوان صفحة الـ WebView (تقارير) — يُمرَّر إلى `WebviewActivity` كـ Intent extra. |
| 14 | `open_url_out_app` | `n` | `int` *(public)* | — | — | إذا كانت `1` ⇒ تُفتح روابط الـ WebView في متصفّح خارجي بدلاً من داخل التطبيق. |
| 15 | `Ues_Gps` | `o` | `int` | `m()` | `useGps()` | إذا كانت `1` ⇒ تفعيل خدمة GPS الدورية + إرفاق إحداثيات في كل دفعة. |
| 16 | `loc_up_interval` | `p` | `int` | `h()` | `getLocationUpdateInterval()` | فترة تحديث الموقع بالمللي ثانية. **القيمة الإفتراضية إذا كانت `0` = `20000ms` (20 ثانية).** |
| 17 | `imgWdth` | `q` | `String` | `g()` | `getImageWidth()` | عرض ضغط صورة العداد (Pixels). يُحوَّل لـ `int`. الإفتراضي = 0 → ⚠️ في الكود الفعلي يقع `OprationsActivity` على 300px. |
| 18 | `Cshr_AddWOtherOpr` | `r` | `String` | `a()` | `canDoOtherOperations()` | صلاحية: عمليات إضافية متنوّعة (تقارير، تغيير كلمة مرور …). |
| 19 | `read_must_take_img` | `s` | `String` | `i()` | `mustTakeMeterImage()` | إذا `"1"` ⇒ التقاط صورة العداد إجباري قبل حفظ القراءة. |
| 20 | `read_save_img_online` | `t` | `String` | `j()` | `saveImageOnline()` | إذا `"1"` ⇒ ترفع الصورة Base64 ضمن الطلب؛ غير ذلك تُخزَّن محلياً. |
| 21 | `user_branch` | `u` | `String` | `n()` | `getUserBranch()` | الفرع المرتبط بالمستخدم (يُرسل في كل طلب). |

---

## 2. ملاحظات هندسية مهمة على الموديل

### 2.1 خلط `String`/`int` غير منطقي
- الصلاحيات (#9–#12 و #18–#20) كلها `String` بقيم `"1"`/`"0"` بدلاً من `Boolean` أو `int`.
- بينما `Ues_Gps` (#15) و `open_url_out_app` (#14) و `loc_up_interval` (#16) هي `int`.
- **السبب الأرجح:** الخلفية ASP.NET ترسل الصلاحيات كأرقام في صورة نصوص (`varchar(1)` على SQL).
- **التأثير عند إعادة البناء:** يجب توحيدها كـ `boolean` في الـ TypeScript مع طبقة `transform` على Axios.

### 2.2 الحقل `Password` يُخزَّن
- يُرسل في تشفير RSA إلى الخادم لكنه يحتفظ به في كائن `User` المُسترَجَع → يُحفَظ في SharedPreferences كنص JSON.
- **مخاطرة:** أي خرق للجهاز ⇒ كشف كلمة المرور بصيغتها المشفرة (التي قد تكون عرضة لـ Padding Oracle حسب تهيئة الخادم).
- **التوصية للإعادة:** عدم تخزين كلمة المرور إطلاقاً بعد تشفيرها، الإكتفاء بـ `Token`.

### 2.3 الإستخدام في `MainActivity.java`
صلاحيات المستخدم تتحكم في رؤية الأزرار السبعة:

```java
// MainActivity (تقريبي بعد فك التعمية)
if ("1".equals(user.d())) btnpayment.setVisible(true);         // Cshr_AddWebPay
if ("1".equals(user.e())) btnReadingList.setVisible(true);     // Cshr_AddWebRead
if ("1".equals(user.b())) btn_cust_loc.setVisible(true);       // Cshr_AddWebCstUpDate
if ("1".equals(user.a())) btnUserReports.setVisible(true);     // Cshr_AddWOtherOpr
// btnchangepass دائماً مرئي ما لم يكن restpass == "1"
```

### 2.4 الحقل `webview_url` ليس له `getter`
- مُعرّف `public` مباشرة (#13) ⇒ يُستدعى كـ `user.m` من الكلاس `WebviewActivity`.
- **مخاطرة:** أي URL يُحقَن من الخادم يُفتح داخل `WebView` بإعدادات خطرة (`setJavaScriptEnabled(true)` + `setAllowUniversalAccessFromFileURLs(true)`).
- **التوصية:** Whitelist لـ Origins مسموحة فقط (`abbasiy.yedns.org`).

### 2.5 `Ues_Gps` — خطأ إملائي مُتعمَّد
- الإسم الصحيح كان يجب أن يكون `Use_Gps` لكنه يُكتب `Ues_Gps` في الخادم والتطبيق.
- **توصية:** الإحتفاظ بنفس الإسم في الـ Backend الجديد للحفاظ على التوافق مع قاعدة بيانات ASP.NET الحالية، أو الترحيل بـ ALTER COLUMN.

---

## 3. مقابل TypeScript للإعادة (مبدأي)

```ts
// src/types/api/user.ts
export interface UserApiResponse {
  Id: string;
  FirstName: string;
  LastName: string;
  Username: string;
  Token: string;
  Password?: string;          // لن نستخدمه — يجب حذفه من الـ DTO
  mob_srl: string;
  restpass: '0' | '1';
  Cshr_AddWebPay: '0' | '1';
  Cshr_AddWebRead: '0' | '1';
  Cshr_AddWebMtrImg: '0' | '1';
  Cshr_AddWebCstUpDate: '0' | '1';
  webview_url: string;
  open_url_out_app: 0 | 1;
  Ues_Gps: 0 | 1;
  loc_up_interval: number;    // ms
  imgWdth: string;            // أرقام كنصوص — انتبه!
  Cshr_AddWOtherOpr: '0' | '1';
  read_must_take_img: '0' | '1';
  read_save_img_online: '0' | '1';
  user_branch: string;
}

// النموذج الداخلي (نظيف)
export interface User {
  id: string;
  firstName: string;
  lastName: string;
  username: string;
  token: string;
  deviceSerial: string;
  mustResetPassword: boolean;
  permissions: {
    addWebPayment: boolean;
    addWebReading: boolean;
    addMeterImage: boolean;
    updateCustomerLocation: boolean;
    doOtherOperations: boolean;
  };
  reading: {
    mustTakeImage: boolean;
    saveImageOnline: boolean;
    imageWidthPx: number;     // default 300
  };
  webView: {
    url: string;
    openOutsideApp: boolean;
  };
  gps: {
    enabled: boolean;
    updateIntervalMs: number; // default 20000
  };
  branch: string;
}

// Mapper من DTO ⇒ النموذج الداخلي
export const mapUser = (dto: UserApiResponse): User => ({
  id: dto.Id,
  firstName: dto.FirstName,
  lastName: dto.LastName,
  username: dto.Username,
  token: dto.Token,
  deviceSerial: dto.mob_srl,
  mustResetPassword: dto.restpass === '1',
  permissions: {
    addWebPayment: dto.Cshr_AddWebPay === '1',
    addWebReading: dto.Cshr_AddWebRead === '1',
    addMeterImage: dto.Cshr_AddWebMtrImg === '1',
    updateCustomerLocation: dto.Cshr_AddWebCstUpDate === '1',
    doOtherOperations: dto.Cshr_AddWOtherOpr === '1',
  },
  reading: {
    mustTakeImage: dto.read_must_take_img === '1',
    saveImageOnline: dto.read_save_img_online === '1',
    imageWidthPx: parseInt(dto.imgWdth, 10) || 300,
  },
  webView: {
    url: dto.webview_url,
    openOutsideApp: dto.open_url_out_app === 1,
  },
  gps: {
    enabled: dto.Ues_Gps === 1,
    updateIntervalMs: dto.loc_up_interval || 20000,
  },
  branch: dto.user_branch,
});
```

---

## 4. مصفوفة ربط الحقول بـ Endpoints

| الحقل | يُكتَب في الـ DB من | يُقرَأ في الـ App في |
|------|---------------------|----------------------|
| `Id` | عند تسجيل المستخدم | كل طلب POST (`user_no`) |
| `Token` | استجابة `/api/Users/Login` | كل طلب POST (`acc_token` + Bearer Header) |
| `mob_srl` | مرسل من التطبيق عند Login | تأكيد ربط الجهاز |
| `restpass` | Backend ⇒ يُغيَّر إلى `"0"` بعد نجاح `/api/Users/changePasswordRequest` | شاشة Login (إذا `"1"` ⇒ يجبر فتح ChangePassActivity) |
| `Cshr_*` | لوحة الإدارة | `MainActivity` (إخفاء/إظهار الأزرار) |
| `webview_url` | لوحة الإدارة | `WebviewActivity` |
| `imgWdth` | لوحة الإدارة | `OprationsActivity.X()` (قبل رفع الصورة) |
| `loc_up_interval` | لوحة الإدارة | `c.b.a.b.d` (خدمة GPS) |

---

## 5. أنماط مشبوهة — يجب التحقق منها في الإعادة

1. **عدم وجود `email`:** لا يوجد حقل بريد إلكتروني — التواصل عبر `mob_srl` فقط.
2. **عدم وجود `expiresAt` للـ Token:** الـ Token دائم حتى يُعاد إصداره من الخادم.
3. **`LastName` غير مستخدم:** هل هو حشو غير لازم؟ أم محجوز لإستخدام مستقبلي؟
4. **عدم وجود `roleId`:** الصلاحيات منثورة في 5 حقول منفصلة بدلاً من `role` موحَّد.
   - **في الإعادة:** استبدلها بـ `role: 'cashier' | 'reader' | 'supervisor'` وحدد الصلاحيات على الخادم.

---

## 6. مخاطر أمنية مرتبطة بالموديل

| المخاطرة | الحقل | الوصف | التخفيف المقترح |
|---------|------|------|----------------|
| **كشف الباسوورد المشفر** | `Password` | يُحفظ في SharedPrefs (JSON) | عدم تخزينه نهائياً — الإكتفاء بـ `Token` |
| **Token دائم** | `Token` | لا انتهاء صلاحية | JWT + Refresh Token (15 دقيقة / 7 أيام) |
| **صلاحيات نصية** | `Cshr_*` | عرضة للتلاعب لو فُكَّ التشفير | Server-side enforcement فقط |
| **`webview_url` غير مُتحقَّق** | `webview_url` | يفتح أي URL داخل WebView بإعدادات خطرة | URL Whitelist + إغلاق `setAllowUniversalAccessFromFileURLs` |
| **`mob_srl` غير ثابت** | `mob_srl` | يُولَّد محلياً ⇒ يمكن إعادة تعيينه | إستخدام `Android ID` + `FCM Token` معاً |

---

> **يربط هذا الملف بـ:** `04_screens_flow/03_main_screen.md` (الصلاحيات), `02_api_contract/02_authentication.md` (الإستجابة), `10_rebuild_blueprint/03_data_models_typescript.md` (المقابل في TS).
