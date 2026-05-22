# 02.2 — Endpoints المصادقة (Authentication)

> 3 endpoints تحت `/api/Users/` للدخول، تغيير كلمة المرور، وجلب مفتاح RSA.

---

## 2.2.1 — `POST /api/Users/getAppPK`

**الوظيفة:** جلب RSA Public Key من السيرفر، يُستخدم لتشفير كلمة المرور و mobile-serial قبل الإرسال.

### Request

```http
POST /payment/api/Users/getAppPK HTTP/1.1
Host: abbasiy.yedns.org:8057
Content-Type: application/json; charset=utf-8
```

**Body:** `null` (لا يوجد)

**Auth:** لا يحتاج Bearer.

### Response — نجاح

```json
{
  "GEN_API_ERR_NO": 0,
  "GEN_API_ERR_MSG": "",
  "apppk": "ANxxxxxxxxxxBASE64MODULUSxxxxxxxxxxx==&AQAB"
}
```

**حقل `apppk`:**
- صيغة: `{modulus_base64}&{publicExponent_base64}`
- الفاصل: علامة `&` (single ampersand).
- Modulus عادةً 256 بايت (RSA-2048) Base64 encoded.
- Exponent عادةً `AQAB` (= `0x010001` = 65537 شائع).

**التحقق من الكود:** `MediaSessionCompat.a()` line 468:
```java
new RSAPublicKeySpec(
    new BigInteger(1, Base64.decode(str.split("&")[0], 0)),  // modulus
    new BigInteger(1, Base64.decode(str.split("&")[1], 0))   // exponent
);
```

### Response — فشل

```json
{
  "GEN_API_ERR_NO": 1,
  "GEN_API_ERR_MSG": "خطأ في الخادم"
}
```

### الاستخدام في التطبيق

```java
// c.b.a.f.b.java - b()
public static void b(Activity activity, q.b callback, boolean withProgress) {
    c cVar = new c(activity);
    C0050b handler = new C0050b(withProgress, activity, callback);
    if (withProgress) {
        cVar.b("/api/Users/getAppPK", null, ApiResponseEnvelope.class, handler, null);
    } else {
        cVar.c("/api/Users/getAppPK", null, ApiResponseEnvelope.class, handler, null);
        //    ^ c() = silent (no progress dialog)
    }
}

// Handler يخزّن الـ PK:
@Override public void a(ApiResponseEnvelope r) {
    if (r.GEN_API_ERR_NO == 0) {
        SharedPrefs["APP_PK_KEY"] = r.apppk;   // يخزّنه للاستخدام لاحقاً
        if (callback != null) callback.a(r);
    }
}
```

### نقاط الاستدعاء

| الموقع | الظرف |
|---|---|
| `LoginActivity.A()` line 167 | عند فتح الشاشة (silent، بدون مؤشر تحميل) |
| `LoginActivity.onClick()` line 75 | إن كانت APP_PK_KEY فارغة عند الضغط على Login (مع مؤشر) |

### ملاحظات أمنية

1. ❌ **لا توقيع** على الـ response — مهاجم MITM يستطيع استبدال الـ apppk بمفتاحه.
2. ❌ **لا certificate pinning** — وبما أن `TrustManager` فارغ، هذا يسحب الأمان كلياً.
3. ❌ **لا nonce** أو timestamp — يمكن استبدال PK قديمة محفوظة.

**الإصلاح للنسخة الجديدة:** يُفضّل التخلي عن RSA-from-server والاعتماد على HTTPS-only مع certificate pinning، أو استخدام TLS client certificates.

---

## 2.2.2 — `POST /api/Users/Login`

**الوظيفة:** تسجيل الدخول. كلمة المرور و mob_srl مُشفّرتان RSA باستخدام `APP_PK_KEY`.

### Request

```http
POST /payment/api/Users/Login HTTP/1.1
Host: abbasiy.yedns.org:8057
Content-Type: application/json; charset=utf-8
```

**Body:**
```json
{
  "Id": null,
  "FirstName": null,
  "LastName": null,
  "Username": "ahmad.cashier",
  "Token": null,
  "Password": "Pj7Wq8sH...== (RSA encrypted password, base64)",
  "mob_srl": "Kj4Lm9...== (RSA encrypted device_id, base64)",
  "restpass": null,
  "Cshr_AddWebPay": null,
  "Cshr_AddWebRead": null,
  "Cshr_AddWebMtrImg": null,
  "Cshr_AddWebCstUpDate": null,
  "webview_url": null,
  "open_url_out_app": 0,
  "Ues_Gps": 0,
  "loc_up_interval": 0,
  "imgWdth": null,
  "Cshr_AddWOtherOpr": null,
  "read_must_take_img": null,
  "read_save_img_online": null,
  "user_branch": "01"
}
```

**حقول مهمة في الـ Body:**

| الحقل | المصدر | التشفير |
|---|---|---|
| `Username` | المستخدم يكتبه | plain |
| `user_branch` | المستخدم يكتبه | plain |
| `Password` | المستخدم يكتبها | **RSA/ECB/PKCS1Padding → Base64** |
| `mob_srl` | `Settings.Secure.android_id` أو IMEI | **RSA/ECB/PKCS1Padding → Base64** |
| (باقي الحقول) | فارغة `null` | — |

**Auth:** لا يحتاج Bearer (هذا هو المنشئ للتوكن).

### كود البناء

```java
// c.b.a.f.b.java - c()
public static void c(Activity activity, String branch, String username, String password, callback) {
    c cVar = new c(activity);
    User user = new User();
    user.p(username);                 // setId() — يُستخدم كـ Username field
    user.t(branch);                   // setUserBranch()
    try {
        String pk = SharedPrefs["APP_PK_KEY"];
        user.r(MediaSessionCompat.a(pk, password));         // setPassword(RSA(password))
        user.q(MediaSessionCompat.a(pk, deviceId()));       // setMob_srl(RSA(android_id))
        cVar.b("/api/Users/Login", user, ApiResponseEnvelope.class, handler, null);
    } catch (Exception e) {
        showAlert(e.getMessage() + "\n in app");
    }
}
```

⚠️ **ملاحظة:** في الـ User model، الـ `Username` يأتي من `Id` لأن الـ `setId()` يضع `Username` بنفسه في الـ JSON (مرتبط بـ `@SerializedName`):
```java
@c.c.b.a0.b("Id")
private String f2438a;
public String f() { return this.f2438a; }    // getId
public void p(String str) { this.f2438a = str; }   // setId
```
لكن في Login، يُملأ `Username` field بقيمة من `setId()`. هذا غير دقيق ويجب التحقق منه ميدانياً.

### Response — نجاح

```json
{
  "GEN_API_ERR_NO": 0,
  "GEN_API_ERR_MSG": "",
  "user": {
    "Id": "123",
    "FirstName": "أحمد",
    "LastName": "علي",
    "Username": "ahmad.cashier",
    "Token": "eyJhbGciOiJIUzI1NiI...full JWT or opaque token",
    "Password": null,
    "mob_srl": "...",
    "restpass": "0",
    "Cshr_AddWebPay": "1",
    "Cshr_AddWebRead": "1",
    "Cshr_AddWebMtrImg": "1",
    "Cshr_AddWebCstUpDate": "0",
    "webview_url": "",
    "open_url_out_app": 0,
    "Ues_Gps": 1,
    "loc_up_interval": 20000,
    "imgWdth": "300",
    "Cshr_AddWOtherOpr": "0",
    "read_must_take_img": "1",
    "read_save_img_online": "1",
    "user_branch": "01"
  },
  "AreaList": [
    {"f1828a": "كل المناطق", "f1829b": "0", ...},
    {"f1828a": "حي السبعين", "f1829b": "01", "f1830c": 1, ...},
    {"f1828a": "حي الستين", "f1829b": "02", "f1830c": 1, ...}
  ]
}
```

### Response — فشل

أكثر الحالات شيوعاً:

```json
// كلمة مرور خاطئة
{"GEN_API_ERR_NO": 100, "GEN_API_ERR_MSG": "اسم المستخدم أو كلمة المرور غير صحيحة"}

// انتهاء صلاحية الحساب
{"GEN_API_ERR_NO": 101, "GEN_API_ERR_MSG": "الحساب موقوف"}

// خطأ ربط الجهاز (mob_srl لا يتطابق)
{"GEN_API_ERR_NO": 102, "GEN_API_ERR_MSG": "الجهاز غير مفعّل"}
```

⚠️ **الأرقام تخمين** — مبنية على المعتاد في .NET WCF Yemeni apps. **يجب تأكيدها بمراقبة الشبكة الفعلية.**

### مُعالجة الـ Response

```java
// c.b.a.f.b.java line 31-58
@Override public void a(ApiResponseEnvelope r) {
    if (r.GEN_API_ERR_NO > 0) {
        showAlert(r.GEN_API_ERR_MSG);
        return;
    }
    
    // يحقن user_branch المُرسلة في كائن الـ user المُستلم (لأن الخادم لا يعيدها)
    r.user.user_branch = original_user.user_branch;
    
    // يخزّن المستخدم
    SharedPrefs["APP_USER_KEY"] = Gson.toJson(r.user);
    
    // يخزّن المناطق (إن وُجدت)
    if (r.AreaList != null && r.AreaList.size() > 0) {
        SharedPrefs["APP_AREADATALIST_KEY"] = Gson.toJson(r.AreaList);
    } else {
        SharedPrefs["APP_AREADATALIST_KEY"] = "";
    }
    
    // ينتقل لـ MainActivity
    callback.a(r);
}
```

### النموذج بعد الدخول

كل الـ permissions (`Cshr_AddWebPay`, `Cshr_AddWebRead`, …) هي **strings** بقيم `"0"` أو `"1"` (وليست boolean) — هذا تصميم سيئ ويجب تحويله في الـ rebuild.

---

## 2.2.3 — `POST /api/Users/changePasswordRequest`

**الوظيفة:** تغيير كلمة المرور (الحالية والجديدة كلاهما RSA-encrypted).

### Request

```http
POST /payment/api/Users/changePasswordRequest HTTP/1.1
Host: abbasiy.yedns.org:8057
Content-Type: application/json; charset=utf-8
Authorization: Bearer {token}
```

**Body:**
```json
{
  "c_no": null,
  "findVal": null,
  "area_no": null,
  "user_no": "123",
  "user_branch": "01",
  "user": {
    "Id": "123",
    "FirstName": "أحمد",
    /* … كل بيانات المستخدم … */
    "mob_srl": "Kj4Lm9...== (RSA encrypted device_id)",
    "Token": "",                       ← يُمسح قبل الإرسال (User.s(""))
    "user_branch": "01"
  },
  "oldpass": "Pj7Wq8sH... (RSA encrypted)",
  "newpass": "Az9Bn7Cm... (RSA encrypted)",
  "op_typ": null
}
```

### كود البناء

```java
// c.b.a.f.b.java - a()
public static void a(Activity activity, String oldPass, String newPass, callback) {
    c cVar = new c(activity);
    ApiRequestEnvelope dvr = new ApiRequestEnvelope();
    dvr.user_branch = MediaSessionCompat.C(activity).getUserBranch();
    
    User u = MediaSessionCompat.C(activity);
    dvr.user = u;
    u.setToken("");                    // يُفرغ الـ Token قبل الإرسال (يبقى في header فقط)
    
    try {
        String pk = SharedPrefs["APP_PK_KEY"];
        dvr.newpass = MediaSessionCompat.a(pk, newPass);
        dvr.oldpass = MediaSessionCompat.a(pk, oldPass);
        dvr.user.setMobSrl(MediaSessionCompat.a(pk, deviceId()));
        cVar.b("/api/Users/changePasswordRequest", dvr, ApiResponseEnvelope.class, handler, null);
    } catch (Exception e) {
        showAlert(e.getMessage() + "\n in app");
    }
}
```

### Response — نجاح

```json
{
  "GEN_API_ERR_NO": 0,
  "GEN_API_ERR_MSG": "تم تغيير كلمة المرور بنجاح",
  "user": { /* بيانات المستخدم المُحدّثة */ }
}
```

التطبيق يخزّن الـ `user` المُعاد إلى SharedPrefs (مما قد يُحدّث الـ Token أو الـ permissions).

### Response — فشل

```json
{"GEN_API_ERR_NO": 200, "GEN_API_ERR_MSG": "كلمة المرور الحالية خاطئة"}
```

---

## ملخّص خوارزمية المصادقة

```
1️⃣ getAppPK()
        ↓
2️⃣ Get RSA public key (modulus, exponent)
        ↓
3️⃣ RSA_encrypt(password, public_key) → base64 → send
        ↓
4️⃣ Server RSA_decrypts using its private key
        ↓
5️⃣ Server verifies (username, decrypted_password) against DB
        ↓
6️⃣ Server returns User object + Token
        ↓
7️⃣ Client stores User+Token in SharedPreferences
        ↓
8️⃣ Subsequent requests: Authorization: Bearer {Token}
```

### نقاط الضعف في هذا التصميم

| الخطر | الوصف | الإصلاح المُقترح |
|---|---|---|
| 🔴 **حرج** | لا certificate pinning + TrustManager فارغ ⇒ MITM كامل ممكن | TLS pinning + شهادة CA حقيقية |
| 🟠 **عالٍ** | RSA padding PKCS1 v1.5 معروف بهجمات Bleichenbacher | تبديل لـ OAEP padding |
| 🟠 **عالٍ** | لا nonce ⇒ replay attack ممكن | إضافة nonce + server-side validation |
| 🟡 **متوسط** | RSA بدلاً من TLS-only ⇒ تعقيد إضافي بلا فائدة فعلية | بما أن HTTPS موجود، يُفضّل إزالة الـ RSA الزائد |
| 🟡 **متوسط** | mob_srl = android_id يتغيّر مع factory reset | استخدام App-installation-id من Play Install Referrer |

---

**التالي:** [`03_payments_endpoints.md`](03_payments_endpoints.md)
