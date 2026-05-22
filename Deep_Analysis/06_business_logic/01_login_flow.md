# Login Flow — منطق تسجيل الدخول الكامل

> **الـ Activity:** `LoginActivity` (راجع `04_screens_flow/01_login_screen.md` للـ UI).
> **الـ Service Layer:** `c.b.a.f.b` (auth helper) و `c.b.a.f.c` (Volley wrapper).
> **التشفير:** `MediaSessionCompat.a()` (RSA — راجع `07_crypto_protocols/01_rsa_password_encryption.md`).

---

## 1. الـ State Machine الكامل

```text
┌──────────────────────────────────────────────────────────────┐
│  Login State Machine                                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [INITIAL] ─────────────────────────────────────────────┐    │
│      │                                                  │    │
│      │ Activity created                                 │    │
│      ▼                                                  │    │
│  [PERMISSIONS_CHECK]                                    │    │
│      │                                                  │    │
│      │ if missing → ask & finish()                     │    │
│      │ if ok → continue                                │    │
│      ▼                                                  │    │
│  [UI_RENDER]                                            │    │
│      │                                                  │    │
│      │ Restore last user (Id, branch) if exists       │    │
│      │ Handle deeplink (?ip=…)                         │    │
│      │ Update Base URL from APP_SERVER_IP_KEY          │    │
│      │ Async: get APP_PK_KEY (getAppPK)                │    │
│      ▼                                                  │    │
│  [WAITING_INPUT] ◄──────────────────┐                  │    │
│      │                              │                  │    │
│      │ user clicks btOk             │                  │    │
│      ▼                              │                  │    │
│  [VALIDATE_FIELDS]                  │                  │    │
│      │                              │                  │    │
│      │ any empty → setError + return back ─────────────┘    │
│      ▼                                                  │    │
│  [MAGIC_BACKDOOR_CHECK]                                  │    │
│      │                                                  │    │
│      │ if all "1" → open Android Settings + EXIT       │    │
│      ▼                                                  │    │
│  [PK_AVAILABLE_CHECK]                                    │    │
│      │                              │                  │    │
│      │ no PK → getAppPK ─────┐      │                  │    │
│      │                       ▼      │                  │    │
│      │                  [GET_PK]    │                  │    │
│      │                       │      │                  │    │
│      │                       │ ok   │                  │    │
│      ▼                       │      │                  │    │
│  [CALL_LOGIN] ◄──────────────┘      │                  │    │
│      │                              │                  │    │
│      │ RSA encrypt password         │                  │    │
│      │ POST /api/Users/Login        │                  │    │
│      ▼                                                  │    │
│  [LOGIN_RESPONSE]                                        │    │
│      │                                                  │    │
│      │ GEN_API_ERR_NO != 0 → Snackbar + back ──────────┘    │
│      │ GEN_API_ERR_NO == 0 → continue                  │    │
│      ▼                                                  │    │
│  [SAVE_USER]                                             │    │
│      │                                                  │    │
│      │ Save User to SharedPrefs[APP_USER_KEY]          │    │
│      ▼                                                  │    │
│  [CHECK_RESTPASS]                                        │    │
│      │                                                  │    │
│      │ User.restpass == "1" → ChangePassActivity       │    │
│      │ User.restpass == "0" → MainActivity             │    │
│      ▼                                                  │    │
│  [DONE]                                                   │    │
│                                                          │    │
└──────────────────────────────────────────────────────────┘    │
                                                                │
                                                                ┘
```

---

## 2. الـ Sequence Diagram التفصيلي

```text
User              LoginActivity         c.b.a.f.b           c.b.a.f.c (Volley)      Server
  │                     │                    │                      │                 │
  │ open app             │                    │                      │                 │
  │─────────────────────>│                    │                      │                 │
  │                     │ onCreate            │                      │                 │
  │                     │ permission check    │                      │                 │
  │                     │                    │                      │                 │
  │                     │ A() ⇒ render UI     │                      │                 │
  │                     │                    │                      │                 │
  │                     │ async: b()         │                      │                 │
  │                     │───────────────────>│                      │                 │
  │                     │                    │ GET /api/Users/getAppPK                 │
  │                     │                    │─────────────────────>│                 │
  │                     │                    │                      │                 │
  │                     │                    │                      │ {apppk:"…"}    │
  │                     │                    │                      │ <───────────────│
  │                     │                    │ save APP_PK_KEY      │                 │
  │                     │ <──── (silent) ────│                      │                 │
  │                     │                    │                      │                 │
  │ enters data         │                    │                      │                 │
  │ clicks btOk         │                    │                      │                 │
  │─────────────────────>│                    │                      │                 │
  │                     │ validate fields     │                      │                 │
  │                     │ magic backdoor?     │                      │                 │
  │                     │                    │                      │                 │
  │                     │ y() ⇒ c()           │                      │                 │
  │                     │───────────────────>│                      │                 │
  │                     │                    │ read PK              │                 │
  │                     │                    │ RSA encrypt pass     │                 │
  │                     │                    │ build d request       │                 │
  │                     │                    │ POST /api/Users/Login │                 │
  │                     │                    │─────────────────────>│                 │
  │                     │                    │                      │                 │
  │                     │                    │                      │ {user, payinfo, │
  │                     │                    │                      │  userRoles}     │
  │                     │                    │                      │ <───────────────│
  │                     │                    │ parse + save User    │                 │
  │                     │ <─── callback ─────│                      │                 │
  │                     │                    │                      │                 │
  │                     │ check restpass      │                      │                 │
  │                     │ navigate            │                      │                 │
  │ <─── MainActivity ──│                    │                      │                 │
  │                     │                    │                      │                 │
```

---

## 3. الكود الجوهري في `c.b.a.f.b.c()` (الـ Login service)

من قراءة `c.b.a.f.b.java` (173 سطر):

```java
public static void c(Activity activity, String branch, String userId, String password, Response.Listener<b> callback) {
  // 1. قراءة المفتاح العام
  String pk = c.b.a.c.d(activity).b();   // APP_PK_KEY
  
  // 2. تشفير كلمة المرور بـ RSA
  String encryptedPass = MediaSessionCompat.a(pk, password);
  
  // 3. بناء طلب
  d req = new d();
  req.f2461d = userId;              // user_no
  req.a(branch);                     // user_branch
  
  User u = new User();
  u.r(encryptedPass);               // Password (encrypted)
  u.q(MediaSessionCompat.D(activity));  // mob_srl (device_id)
  req.g = u;
  
  // 4. إرسال
  c.b.a.f.c client = new c.b.a.f.c(activity);
  client.b("/api/Users/Login", req, b.class, callback, null);
}
```

---

## 4. الكود الجوهري في `c.b.a.f.b.b()` (الـ getAppPK service)

```java
public static void b(Activity activity, Response.Listener<b> callback, boolean showProgress) {
  // ProgressDialog if showProgress
  ProgressDialog dialog = null;
  if (showProgress) {
    dialog = ProgressDialog.show(activity, "", "Loading...");
  }
  
  // GET /api/Users/getAppPK
  c.b.a.f.c client = new c.b.a.f.c(activity);
  client.a(   // GET method
    "/api/Users/getAppPK",
    b.class,
    response -> {
      if (response.e() == 0) {
        // حفظ PK
        c.b.a.c.d(activity).a("APP_PK_KEY", response.a());
      }
      if (dialog != null) dialog.dismiss();
      if (callback != null) callback.onResponse(response);
    },
    error -> {
      if (dialog != null) dialog.dismiss();
      // Toast / Snackbar
    }
  );
}
```

---

## 5. ⚠️ الحالات الحدّية في تدفُّق Login

### 5.1 الخادم غير متاح في `getAppPK`
- `runOnUiThread(new Thread(new b()))` يفشل بصمت إذا الـ Volley fails.
- لا rety automatically.
- **النتيجة:** زر btOk لاحقاً يُفشِل بسبب `pk` فارغ ⇒ لا يصل لـ Login.
- **المُتوقَّع:** UI feedback صريح ("لا اتصال بالخادم").

### 5.2 الـ Token منتهي في الإستجابة
- لا يوجد فحص — `User.Token` يُحفظ كما هو.
- المُتوقَّع تخصيص handler لـ 401 Unauthorized في الـ Volley.

### 5.3 Magic Backdoor `1/1/1`
```java
if (branch.equals("1") && userId.equals("1") && password.equals("1")) {
  Intent intent = new Intent();
  intent.setAction("android.settings.APPLICATION_DETAILS_SETTINGS");
  intent.setData(Uri.fromParts("package", packageName, null));
  startActivity(intent);
  return;
}
```

⚠️ **هذا يتجاوز كل الـ login تماماً** ⇒ خطر حرج.

### 5.4 الـ Deeplink يغيِّر الخادم
- المهاجم يرسل `https://ecas.web.link/?ip=evil-server.com`.
- التطبيق يقبل + يحدِّث `APP_SERVER_IP_KEY` ⇒ كل العمليات اللاحقة تذهب للخادم الخبيث.
- **النتيجة:** سرقة كلمات المرور (المشفرة بـ PK من الخادم الخبيث ⇒ يستطيع فكها).

---

## 6. لماذا التشفير RSA مع وجود TLS؟

السؤال الواضح: التطبيق يتصل بـ `https://abbasiy.yedns.org:8057` (TLS). لماذا تشفير إضافي للـ password؟

### الفرضيات:
1. **TLS bypass متعمَّد:** الـ empty TrustManager يقبل أي شهادة ⇒ MITM ممكن ⇒ RSA يحمي الـ password.
2. **ميراث تصميم:** Old habit من تطبيقات HTTP خالصة.
3. **تجاوز التحقُّق من الشهادة (`c.b.a.f.d`):** المُطوِّر يعرف أن TLS غير موثوق ⇒ يضيف طبقة.

⚠️ **التحليل الحقيقي:** RSA هنا **مفيد فقط** للحماية من MITM في حالة TLS bypass. لكن لو المهاجم يتحكم بالـ Deeplink ⇒ يستطيع تغيير الخادم ⇒ يُعطي PK من عنده ⇒ يفك RSA.

⇒ **في الإعادة:** TLS مع Certificate Pinning + لا تشفير إضافي.

---

## 7. الـ Migration Plan للإعادة

### 7.1 المراحل
1. **مرحلة 1:** التطبيق الجديد يتعامل مع نفس Backend (Backward compatible).
2. **مرحلة 2:** Backend جديد + token expiration + refresh tokens.
3. **مرحلة 3:** Biometric/PIN + Session timeout.
4. **مرحلة 4:** SSO إن لزم.

### 7.2 الـ Endpoints الجديدة
```ts
// مرحلة 1: نفس الـ endpoints الحالية
POST /api/Users/Login → { user, token, mustResetPassword }

// مرحلة 2: تحديث
POST /api/auth/login → { accessToken, refreshToken, user, expiresIn }
POST /api/auth/refresh → { accessToken, refreshToken }
POST /api/auth/logout → 204
```

### 7.3 المُكافِئ في React Native

```tsx
// src/screens/LoginScreen.tsx
const LoginScreen = () => {
  const { login, isLoading, error } = useAuth();
  const { control, handleSubmit } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });
  
  const onSubmit = async (data: LoginForm) => {
    try {
      const result = await login({
        branch: data.branch,
        username: data.username,
        password: data.password,
      });
      
      if (result.user.mustResetPassword) {
        router.replace('/change-password?mandatory=true');
      } else {
        router.replace('/main');
      }
    } catch (e) {
      // toast handled in error
    }
  };
  
  // …
};

// src/hooks/useAuth.ts
export const useAuth = () => {
  const { mutateAsync: login, isLoading, error } = useMutation({
    mutationFn: async (data: LoginInput): Promise<LoginResult> => {
      // ❌ لا RSA — فقط TLS مع Certificate Pinning
      const response = await api.auth.login(data);
      
      // حفظ الـ tokens في SecureStore (KeyStore على Android, Keychain on iOS)
      await SecureStore.setItemAsync('accessToken', response.accessToken);
      await SecureStore.setItemAsync('refreshToken', response.refreshToken);
      
      return response;
    },
  });
  
  return { login, isLoading, error };
};
```

---

## 8. خلاصة المخاطر في تدفُّق Login

| # | المخاطرة | الشدة | الإصلاح |
|---|---------|------|---------|
| 1 | Magic Backdoor `1/1/1` | 🔴🔴🔴 | إزالة كلياً |
| 2 | Deeplink يغيِّر الخادم بدون فحص | 🔴🔴 | URL signing + JWT |
| 3 | TLS bypass (empty TrustManager) | 🔴🔴 | TrustManager صحيح + Pinning |
| 4 | RSA encryption مع MITM-able TLS | 🔴 | TLS-only |
| 5 | لا انتهاء صلاحية للـ Token | 🔴 | JWT + Refresh |
| 6 | لا Logout صريح | 🔴 | إضافة Logout |
| 7 | كلمة المرور المُشفَّرة تُخزَّن في SharedPrefs | 🟡 | لا تُخزَّن |
| 8 | لا rety / offline handling | 🟡 | TanStack Query |
| 9 | لا Brute force protection | 🟡 | Rate limit + lockout |
| 10 | لا biometric/PIN | 🟡 | إضافة |

---

> **يربط هذا الملف بـ:**
> - `04_screens_flow/01_login_screen.md`.
> - `07_crypto_protocols/01_rsa_password_encryption.md`.
> - `06_business_logic/02_deeplink_handler.md`.
> - `10_rebuild_blueprint/05_security_improvements.md`.
