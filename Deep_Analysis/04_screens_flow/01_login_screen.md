# LoginActivity — شاشة تسجيل الدخول

> **المصدر:** `com.egy.webpaymentapp.Screens.LoginActivity`
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/Screens/LoginActivity.java`
> **عدد الأسطر:** 192 سطر
> **الـ Layout:** `R.layout.activity_login`
> **يُعتَبر:** نقطة الدخول الأساسية (`MAIN` + `LAUNCHER`) — كما يستقبل deeplink `https://ecas.web.link/?ip=…`.

---

## 1. مكوّنات الواجهة (View IDs)

| المتغير | View ID | النوع | الوظيفة |
|---------|---------|------|---------|
| `q` | `R.id.edt_user_barnch` | `EditText` | إدخال الفرع (مثلاً `001`) |
| `r` | `R.id.edUserId` | `EditText` | إدخال إسم المستخدم |
| `s` | `R.id.edUserPass` | `EditText` | إدخال كلمة المرور |
| `t` | `R.id.btOk` | `Button` | زر تسجيل الدخول |
| `u` | `R.id.txt_about` | `TextView` | عرض `"Ver Ecas v18.4"` مع UnderlineSpan |

> ⚠️ ملاحظة الإسم: `edt_user_barnch` — خطأ إملائي مُتعمَّد (يجب أن يكون `branch`).

---

## 2. دورة الحياة (Lifecycle)

### 2.1 `onCreate(Bundle)` — السطور 173-190

```text
super.onCreate(bundle)
        ↓
setContentView(R.layout.activity_login)
        ↓
if SDK >= 23:
    permissions = MediaSessionCompat.z(this)   // قائمة الصلاحيات الناقصة
    if permissions غير فارغة:
        request permissions (code 2345)
        finish()  ⇒ ينتظر المستخدم
        return   ⇒ لا يكمل setup
        ↓
A()  ⇒ تهيئة الواجهة + معالجة deeplink + تحميل PK
```

### 2.2 `A()` — تهيئة الواجهة (السطور 121-169)

#### الخطوات بالترتيب:

1. **فحص MANAGE_EXTERNAL_STORAGE (Android 11+):**
   ```java
   if (SDK >= 30 && !Environment.isExternalStorageManager()) {
     Snackbar y = Snackbar.y(view, "Permission needed!", LENGTH_INDEFINITE);
     y.z("Settings", new f(this));  // فتح إعدادات الجهاز
     y.A();
   }
   ```

2. **عرض الإصدار:** `"Ver Ecas v18.4"` بـ UnderlineSpan على `R.id.txt_about`.

3. **تعبئة الحقول من المستخدم المحفوظ سابقاً:**
   ```java
   User C = MediaSessionCompat.C(this);  // قراءة من SharedPrefs[APP_USER_KEY]
   if (C != null) {
     edUserId.setText(C.f());     // Id  (مش Username!)
     edt_user_barnch.setText(C.n()); // user_branch
   }
   ```
   ⚠️ **خطأ:** يضع `Id` في حقل إسم المستخدم بدلاً من `Username` — قد يكون متعمَّد لإختصار.

4. **معالجة Deeplink (السطور 143-163):**
   ```java
   if (getIntent().getData() != null) {
     try {
       String ipEncoded = getIntent().getData().getQueryParameters("ip").get(0);
       String r = MediaSessionCompat.r(MediaSessionCompat.s(ipEncoded));
       // ⚠️ r() = DESede decrypt
       // ⚠️ s() = DESede encrypt
       // الإستدعاء r(s(input)) = … decrypt(encrypt(input)) = input بحد ذاته
       // ⇒ هذا قد يكون خطأ في الكود! المُتوقَّع r(input) فقط (decrypt الـ ip المُشفَّر)
       
       if (!r.isEmpty()) {
         if (!r.startsWith("http") && !r.startsWith("https")) {
           r = "https://" + r;
         }
         c.b.a.c.d(this).a("APP_SERVER_CER_KEY", "");
         c.b.a.c.d(this).a("APP_SERVER_IP_KEY", r);
         Toast.makeText(this, "تمت العملية بنجاح", 1).show();
       }
     } catch (Exception e) {
       Toast.makeText(this, e.getLocalizedMessage(), 1).show();
     }
   }
   ```

   ⚠️ **تحليل r(s(ip)):** عند الإمعان:
   - `s(input)` يأخذ نصاً عادياً ⇒ يُشفِّره بـ DESede.
   - `r(input)` يأخذ نصاً مُشفَّراً ⇒ يفكُّه.
   - **إذن `r(s(ip)) = ip`** نظرياً! ⇒ تكلفة CPU بلا فائدة عملية.
   - **التفسير المُحتمَل:** أرادوا تشويش Reverse Engineering ⇒ المخترق سيظن أنه deeplink مشفر بينما هو نص واضح.
   - **أو:** المطوّر أساء فهم الترتيب، وكان المُتوقَّع `r(ip)` فقط (الرابط الفعلي مرسل مُشفَّر من الإدارة).
   - **يحتاج التحقق:** التقاط deeplink فعلي من Production.

5. **تحديث Base URL إن وُجد إعداد محفوظ:**
   ```java
   if (!isEmpty(getPref("APP_SERVER_IP_KEY"))) {
     c.b.a.f.c.f1899b = getPref("APP_SERVER_IP_KEY");
   }
   ```

6. **تحميل المفتاح العام (PK):**
   ```java
   runOnUiThread(new Thread(new b()));
   // b.run() ⇒ c.b.a.f.b.b(this, null, false)
   //         ⇒ GET /api/Users/getAppPK
   //         ⇒ يحفظ apppk في SharedPrefs[APP_PK_KEY]
   ```

7. **IME Action listener:** الضغط على Enter في حقل كلمة المرور ⇒ ينقر زر تسجيل الدخول.

---

## 3. معالجة النقر على زر "OK" — `a.onClick()` (السطور 51-86)

```text
البداية: قراءة قيم الحقول الثلاثة
        ↓
هل الفرع فارغ؟ ⇒ setError + return
هل المستخدم فارغ؟ ⇒ setError + return
هل كلمة المرور فارغة؟ ⇒ setError + return
        ↓
⚠️ فحص الـ Magic Backdoor:
   if branch=="1" && user=="1" && pass=="1":
       Intent ⇒ ACTION_APPLICATION_DETAILS_SETTINGS
       startActivity(intent)  ⇒ فتح إعدادات النظام للتطبيق
       return  ⇒ بدون تسجيل دخول!
        ↓
هل APP_PK_KEY فارغ؟
   ✅ نعم ⇒ getAppPK ⇒ ثم Login (في callback)
   ❌ لا ⇒ Login مباشرة عبر y()
```

### 3.1 الـ Magic Backdoor (السطور 65-72)

**هذا أخطر شيء في التطبيق.** أي شخص يدخل `1` / `1` / `1` يفتح إعدادات النظام للتطبيق، حيث يمكنه:
- مسح بيانات التطبيق (SharedPrefs) ⇒ تجاوز قفل الجلسة.
- إعطاء صلاحيات إضافية للتطبيق.
- منع إغلاق التطبيق.

**التوصية الحرجة:** إزالته كلياً في الإعادة، أو حصره بـ Debug Build فقط.

### 3.2 دالة `y()` (السطر 117) — الإستدعاء الفعلي للـ Login

```java
static void y(LoginActivity loginActivity) {
  c.b.a.f.b.c(
    loginActivity,
    loginActivity.q.getText().toString(),   // branch
    loginActivity.r.getText().toString(),   // username
    loginActivity.s.getText().toString(),   // password (plain)
    new g(loginActivity)                     // callback
  );
}
```

⇒ يُستدعى `c.b.a.f.b.c()` التي بدورها:
1. تشفّر كلمة المرور بـ RSA باستخدام PK.
2. ترسل POST إلى `/api/Users/Login`.
3. في الإستجابة الناجحة ⇒ يُستدعى `g.onSuccess()` ⇒ يحفظ المستخدم ⇒ يفتح `MainActivity`.

---

## 4. تدفُّق Deeplink الكامل

```text
المسؤول يبني رابط:
   ip = "newserver.example.com"
   encrypted = MediaSessionCompat.s(ip)  // DESede encrypt
   url = "https://ecas.web.link/?ip=" + URLEncode(encrypted)
        ↓
المسؤول يرسل الرابط للموظف (واتساب مثلاً)
        ↓
الموظف ينقر الرابط
        ↓
Android: matches intent-filter في AndroidManifest:
   <data android:host="ecas.web.link" android:scheme="https"/>
        ↓
يفتح LoginActivity مع getIntent().getData() != null
        ↓
A() يستخرج "ip" parameter
        ↓
r(s(ip)) = ip   ⇒ ⚠️ الفعلي
        ↓
إضافة "https://" إن لزم
        ↓
حفظ في APP_SERVER_IP_KEY
        ↓
تحديث c.b.a.f.c.f1899b
        ↓
Toast: "تمت العملية بنجاح"
        ↓
الموظف يدخل بياناته كالعادة، لكن الآن يتصل بالخادم الجديد
```

---

## 5. النقاط الحرجة في `LoginActivity`

| # | النقطة | المخاطرة | التوصية للإعادة |
|---|--------|---------|-----------------|
| 1 | Magic backdoor `1/1/1` | 🔴 حرجة | إزالة كلياً |
| 2 | `r(s(ip))` بلا فائدة | 🟡 شك تصميم | استخدام JWT signed token بدل DESede |
| 3 | تخزين كلمة المرور المشفرة في `User.Password` | 🔴 حرجة | عدم تخزين أبداً |
| 4 | `f` (Id) يُعرَض بدلاً من `o` (Username) | 🟢 UX bug | استخدام Username |
| 5 | `Snackbar` للأذونات لا يفرض الموافقة | 🟡 UX/أمن | تطبيق Permission Flow كامل |
| 6 | `Toast` لرسالة "تمت بنجاح" حتى لو deeplink مكسور | 🟡 UX | تحقق من النجاح فعلياً |
| 7 | `getIntent().getData().getQueryParameters("ip").get(0)` بدون null check | 🟡 Crash | استخدام Safe-call |
| 8 | لا فحص شهادة TLS للـ deeplink URL | 🔴 حرجة | فحص الـ host whitelist |

---

## 6. الحالات الحدّية (Edge Cases)

| الحالة | السلوك الحالي | السلوك المُتوقَّع |
|--------|--------------|------------------|
| لا اتصال إنترنت عند الـ getAppPK | فشل صامت ⇒ زر Login يفشل لاحقاً | إظهار رسالة "لا إتصال" |
| الخادم down | الـ Volley يحاول مرة واحدة (timeout=10s) | UI feedback صريح |
| `restpass == "1"` بعد Login | يجب فتح ChangePassActivity (في `g.callback`) | ✅ موجود (يحتاج تأكيد) |
| Magic backdoor + جلسة محفوظة | يفتح إعدادات النظام بدون تغيير الجلسة | إزالة |
| Deeplink بـ `ip` فارغ | Catch ⇒ Toast | تجاهل صامت أفضل |

---

## 7. الإستبدال المُقترح في الإعادة (React Native)

```tsx
// src/screens/LoginScreen.tsx (مخطط مبسَّط)
import { useForm } from 'react-hook-form';
import { useLoginMutation } from '@/api/auth';

export const LoginScreen = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>();
  const login = useLoginMutation();

  const onSubmit = async (data: LoginForm) => {
    // 1. لا Magic backdoor
    // 2. لا Local key fetch — JWT يكتفي
    // 3. كلمة المرور تُرسَل عبر TLS فقط (no extra crypto)
    try {
      const result = await login.mutateAsync(data);
      if (result.user.mustResetPassword) {
        router.replace('/change-password');
      } else {
        router.replace('/main');
      }
    } catch (e) {
      Toast.show({ type: 'error', text: e.message });
    }
  };

  // عرض UI…
};
```

---

## 8. تدفق ASCII كامل لـ LoginActivity

```text
┌────────────────────────────────────────────┐
│              LoginActivity                  │
├────────────────────────────────────────────┤
│                                            │
│  onCreate                                   │
│    ↓                                        │
│  permissions check (SDK >= 23)              │
│    ↓ if missing → request & finish          │
│    ↓ if ok → A()                            │
│                                            │
│  A()                                        │
│    ↓ MANAGE_EXTERNAL_STORAGE (SDK 30+)     │
│    ↓ render UI (3 EditText + Button)       │
│    ↓ Restore last user (Id, branch)        │
│    ↓ handle deeplink ?ip=…                  │
│    ↓ load APP_SERVER_IP_KEY                │
│    ↓ async: getAppPK                        │
│    ↓ bind Enter → btn click                │
│                                            │
│  btn.click() → a.onClick                    │
│    ↓ validate 3 fields                      │
│    ↓ ⚠️ magic backdoor (1/1/1)             │
│    ↓ if PK empty → getAppPK then y()        │
│    ↓ else → y()                             │
│                                            │
│  y() → c.b.a.f.b.c()                        │
│    ↓ RSA encrypt password                   │
│    ↓ POST /api/Users/Login                 │
│    ↓ on success: g.callback                 │
│       ↓ save User to APP_USER_KEY          │
│       ↓ if restpass==1 → ChangePassActivity│
│       ↓ else → MainActivity                 │
│                                            │
└────────────────────────────────────────────┘
```

---

> **يربط هذا الملف بـ:**
> - `06_business_logic/01_login_flow.md` (التفاصيل الخلفية).
> - `06_business_logic/02_deeplink_handler.md` (الـ deeplink).
> - `07_crypto_protocols/01_rsa_password_encryption.md` (تشفير كلمة المرور).
> - `07_crypto_protocols/02_desede_deeplink.md` (تشفير الـ deeplink).
> - `10_rebuild_blueprint/05_security_improvements.md` (الإصلاحات).
