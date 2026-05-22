# ChangePassActivity — شاشة تغيير كلمة المرور

> **المصدر:** `com.egy.webpaymentapp.Screens.ChangePassActivity`
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/Screens/ChangePassActivity.java`
> **عدد الأسطر:** 41 سطر (الأبسط في التطبيق)
> **الـ Layout:** `R.layout.activity_change_pass`
> **العنوان:** `R.string.scrn_titl_change_pass`

---

## 1. مكوّنات الواجهة

| المتغير | View ID | النوع | الوظيفة |
|---------|---------|------|---------|
| `q` | `R.id.te_old_pass` | `EditText` | كلمة المرور القديمة |
| `r` | `R.id.te_new_pass` | `EditText` | كلمة المرور الجديدة |
| `s` | `R.id.btn_save` | `Button` | زر الحفظ |

⚠️ **لا حقل تأكيد كلمة المرور الجديدة** — يدخل المستخدم القيمة مرة واحدة فقط.

---

## 2. دورة الحياة

### 2.1 `onCreate(Bundle)` (السطور 21-34)

```text
setContentView(activity_change_pass)
       ↓
ربط الـ EditTexts
       ↓
ربط زر الحفظ بـ b.onClick(this)
       ↓
إعداد الـ ActionBar:
   - k(false): no title text
   - j(true): home enabled
   - h(true): home as up
   - i(true): home as up indicator
   - m(R.string.scrn_titl_change_pass): العنوان
```

### 2.2 `u()` (الزر `Home`) — السطر 37-40
```java
public boolean u() {
  finish();       // إغلاق الشاشة عند الضغط على رمز الرجوع في الـ ActionBar
  return true;
}
```

⚠️ **مخاطرة UX:** المستخدم قد يخرج بدون حفظ كلمة المرور الجديدة بدون تأكيد ⇒ خاصة في حالة `restpass=="1"` (إجباري).

---

## 3. منطق الحفظ — `x()` (السطر 15-17)

```java
public static void x(ChangePassActivity changePassActivity) {
  c.b.a.f.b.a(
    changePassActivity,
    changePassActivity.q.getText().toString(),   // old password
    changePassActivity.r.getText().toString(),   // new password
    new c(changePassActivity)                     // callback
  );
}
```

### الذي يحدث داخل `c.b.a.f.b.a()`:

1. **قراءة المفتاح العام (PK):** من `SharedPreferences[APP_PK_KEY]`.
2. **تشفير كلمتي المرور:**
   - `MediaSessionCompat.a(pk, oldPass)` ⇒ RSA-encrypt القديمة.
   - `MediaSessionCompat.a(pk, newPass)` ⇒ RSA-encrypt الجديدة.
3. **بناء `RequestEnvelope` (`models/d`):**
   ```java
   d req = new d();
   req.h = encryptedOldPass;   // oldpass
   req.i = encryptedNewPass;   // newpass
   req.g = currentUser;        // user
   req.f2462e = user.l();      // acc_token
   req.f2461d = user.f();      // user_no
   req.a(user.n());            // user_branch
   ```
4. **POST إلى `/api/Users/changePasswordRequest`** بعد `b()` (الترميز Bearer).
5. **في الـ callback:**
   - `GEN_API_ERR_NO == 0` ⇒ نجاح ⇒ تحديث `User.restpass = "0"` محلياً + Toast + `finish()`.
   - غير ذلك ⇒ عرض `GEN_API_ERR_MSG` كـ Snackbar.

---

## 4. النقاط الحرجة

| # | النقطة | المخاطرة | التوصية |
|---|--------|---------|---------|
| 1 | لا حقل تأكيد كلمة المرور الجديدة | 🟡 UX | إضافة `txt_confirm_new_pass` + مقارنة |
| 2 | لا فحص حد أدنى للكلمة (طول/تعقيد) | 🟡 أمن | فرض 8+ حرف، رقم، رمز |
| 3 | لا فحص أن الجديدة ≠ القديمة | 🟢 UX | إضافة فحص |
| 4 | لا تأكيد للخروج بدون حفظ | 🟡 UX | Dialog عند `finish()` إذا كان النص غير فارغ |
| 5 | `u()` لا يحترم حالة `restpass=="1"` | 🔴 أمن | منع الخروج إذا كان إلزامي |
| 6 | لا feedback أثناء الإرسال | 🟢 UX | إظهار ProgressDialog |
| 7 | `setError` غير مستخدم للفحص | 🟢 UX | استخدام TextInputLayout error |

---

## 5. السيناريوهات

### 5.1 السيناريو العادي
```text
المستخدم في MainActivity ⇒ يضغط btnchangepass
        ↓
ChangePassActivity تفتح
        ↓
يدخل القديمة + الجديدة ⇒ زر حفظ
        ↓
RSA encrypt كلاهما
        ↓
POST /api/Users/changePasswordRequest
        ↓
الخادم يتحقق من القديمة ⇒ يحدِّث الجديدة
        ↓
في الإستجابة الناجحة ⇒ User.restpass = "0" + Toast + finish()
```

### 5.2 السيناريو الإجباري (restpass == "1")
```text
بعد Login ناجح، g.callback يفحص user.k() == "1"
        ↓
startActivity(ChangePassActivity)
        ↓
المستخدم يجب أن يُغيِّر
        ↓
لكن ⚠️ ChangePassActivity لا تعرف أن الحالة "إجبارية"
        ↓
المستخدم يمكنه الضغط على Home ⇒ finish() ⇒ يعود لـ Login
        ↓
ولأن restpass==1 ما يزال ⇒ حلقة لا نهاية محتملة!
        ↓
أو ⇒ المستخدم يفتح إعدادات النظام عبر deeplink Magic ⇒ يمسح بيانات التطبيق ⇒ يتجاوز
```

**نتيجة:** المنطق الإجباري غير محكم.

### 5.3 السيناريو السيئ
- المستخدم يدخل كلمة مرور خاطئة في القديمة ⇒ الخادم يرفض ⇒ Snackbar ⇒ يحاول مرة أخرى.
- لا يوجد محدد عدد محاولات ⇒ Brute force محتمل (على الخادم).

---

## 6. السلوك المُقترَح في الإعادة

```tsx
// src/screens/ChangePasswordScreen.tsx
const ChangePasswordScreen = () => {
  const { user } = useAuth();
  const isMandatory = user.mustResetPassword;
  
  const schema = z.object({
    oldPassword: z.string().min(6),
    newPassword: z.string()
      .min(8, 'الحد الأدنى 8 حروف')
      .regex(/[A-Z]/, 'يجب أن تحوي حرفاً كبيراً')
      .regex(/[0-9]/, 'يجب أن تحوي رقماً'),
    confirmPassword: z.string(),
  }).refine(d => d.newPassword === d.confirmPassword, {
    message: 'كلمتا المرور غير متطابقتين',
    path: ['confirmPassword'],
  }).refine(d => d.newPassword !== d.oldPassword, {
    message: 'كلمة المرور الجديدة يجب أن تختلف عن القديمة',
    path: ['newPassword'],
  });

  // منع الخروج إذا إجباري
  useEffect(() => {
    if (!isMandatory) return;
    const handler = BackHandler.addEventListener('hardwareBackPress', () => true);
    return () => handler.remove();
  }, [isMandatory]);

  // form…
};
```

---

## 7. ASCII لتدفُّق Change Password

```text
┌──────────────────────────────────────────┐
│         ChangePassActivity                │
├──────────────────────────────────────────┤
│                                          │
│ onCreate                                  │
│   ↓ setContentView                        │
│   ↓ bind 2 EditText + 1 Button           │
│   ↓ ActionBar setup                       │
│                                          │
│ btn.save.click → x()                      │
│   ↓ c.b.a.f.b.a(activity, old, new, cb)  │
│       ↓ read PK                          │
│       ↓ RSA encrypt old & new            │
│       ↓ build RequestEnvelope            │
│       ↓ POST /api/Users/changePasswordRequest │
│       ↓ on success:                       │
│           ↓ User.restpass="0"            │
│           ↓ Toast                         │
│           ↓ finish()                      │
│       ↓ on error:                         │
│           ↓ Snackbar                      │
│                                          │
└──────────────────────────────────────────┘
```

---

> **يربط هذا الملف بـ:**
> - `02_api_contract/02_authentication.md` (Endpoint).
> - `07_crypto_protocols/01_rsa_password_encryption.md` (التشفير).
> - `10_rebuild_blueprint/05_security_improvements.md` (Validation).
