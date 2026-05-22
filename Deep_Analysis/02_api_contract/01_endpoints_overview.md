# 02.1 — قائمة الـ Endpoints الشاملة (API Endpoints Overview)

> **المصدر:** الـ Endpoints المُستخلصة من ملفات Java فعلياً (not guessed).
> الكود المرجعي:
> - `c/b/a/f/c.java`        ← `f1899b` (Base URL)
> - `c/b/a/f/b.java`        ← Authentication endpoints
> - `com/egy/webpaymentapp/Screens/OprationsActivity.java`
> - `com/egy/webpaymentapp/Screens/e0.java`
> - `com/egy/webpaymentapp/Screens/d.java`
> - `com/egy/webpaymentapp/Screens/web/WebviewActivity.java`

---

## 1. الـ Base URL

```java
// c/b/a/f/c.java line 33
public static String f1899b = "https://abbasiy.yedns.org:8057/payment";
```

**خصائص:**
- ثابت بالكود (hardcoded) كقيمة افتراضية.
- يمكن تجاوزه عبر:
  1. مفتاح SharedPreferences `APP_SERVER_IP_KEY` (يُكتب من شاشة Login عند deeplink).
  2. deeplink `https://ecas.web.link/?ip=<DESede-encrypted-host>`
- TLS: HTTPS + شهادة self-signed + **التحقق معطّل بالكامل** (`X509TrustManager` فارغ + `HostnameVerifier` يُرجع `true`).
- Port: **8057** (غير قياسي).
- Path prefix: **`/payment`** (مسار ASP.NET-style).
- Server header (محتمل): IIS / Kestrel.

---

## 2. الـ Endpoints الكاملة (9 endpoints)

> جميعها **POST** بدون استثناء. Content-Type: `application/json`. Encoding: `utf-8`.

### Controller A: Users

| # | Method | Path | الوظيفة | يتطلب Auth؟ |
|---|---|---|---|---|
| 1 | POST | `/api/Users/getAppPK` | جلب RSA Public Key | ❌ لا |
| 2 | POST | `/api/Users/Login` | تسجيل الدخول | ❌ لا (يُولّد التوكن) |
| 3 | POST | `/api/Users/changePasswordRequest` | تغيير كلمة المرور | ✅ Bearer Token |

### Controller B: Payment

| # | Method | Path | الوظيفة | يتطلب Auth؟ |
|---|---|---|---|---|
| 4 | POST | `/api/Payment/GetCustomersData` | البحث عن مشترك / جلب بياناته | ✅ Bearer |
| 5 | POST | `/api/Payment/saveBillRequest` | حفظ دفعة | ✅ Bearer |
| 6 | POST | `/api/Payment/saveReadingRequest` | حفظ قراءة عداد | ✅ Bearer |
| 7 | POST | `/api/Payment/saveCustLocation` | حفظ GPS للمشترك | ✅ Bearer |
| 8 | POST | `/api/Payment/GetPaymentsReportData` | قائمة المدفوعات للتقرير | ✅ Bearer |
| 9 | POST | `/api/Payment/GetReadingListData` | قائمة القراءات للتقرير | ✅ Bearer |

---

## 3. الـ Headers المشتركة

كل request يخرج من `c.b.a.f.c.b(...)` يحمل الـ Headers التالية تلقائياً:

```
POST {fullURL} HTTP/1.1
Host: abbasiy.yedns.org:8057
Content-Type: application/json; charset=utf-8
Accept: application/json
Connection: keep-alive
Authorization: Bearer {user.Token}      ← فقط إن كان المستخدم مسجّل دخوله

(Volley يضيف: User-Agent, Accept-Encoding: gzip, …)
```

**التحقق من الـ token:**
```java
// c.b.a.f.c.java line 209-219
private Map<String, String> a() {
    HashMap hashMap = new HashMap();
    User C = MediaSessionCompat.C(this.f1900a);   // قراءة من APP_USER_KEY
    if (C == null) return null;                    // ⚠️ لو null = بدون auth
    StringBuilder sb = new StringBuilder("Bearer ");
    sb.append(C.l());                              // user.Token
    hashMap.put("Authorization", sb.toString());
    return hashMap;
}
```

⚠️ **ملاحظة أمنية:** إن كان `User` غير موجود في SharedPrefs (مثلاً قبل الدخول)، الـ headers تكون `null`. لكن الـ endpoints تتوقع `Authorization` بعد Login. هذا يعمل لأن `getAppPK` و`Login` هما الوحيدان اللذان لا يتطلبان توكن.

---

## 4. الـ Retry Policy و Timeouts

```java
// c.b.a.f.c.java line 240, 259
aVar2.z(new c.a.b.f(10000, 1, 1.0f));
```

| المعيار | القيمة |
|---|---|
| Timeout | **10 ثوانٍ** |
| Max retries | **1 إعادة** |
| Backoff multiplier | 1.0 (لا backoff) |

⚠️ هذا قد يكون مشكلة في الشبكات الضعيفة في اليمن. التطبيق الجديد يجب أن يستخدم: **30s timeout + 3 retries + exponential backoff**.

---

## 5. مُعالجة الأخطاء

```java
// c.b.a.f.c.java C0051c.a()
@Override public void a(u uVar) {
    // 1) لو 401 Unauthorized → logout user (يعيد إلى Login)
    if (uVar.f1779b != null && uVar.f1779b.f1754a == 401) {
        new f0(c.this.f1900a, null).h();   // logout
        return;
    }
    
    // 2) لو "failed to connect to" في الرسالة:
    if (message.contains("failed to connect to"))
        message = "فشل الاتصال بالخادم";
    
    // 3) يستبدل XXHOST بالـ host الحقيقي للسيرفر (نمط placeholder)
    message = message.replace("XXHOST", "abbasiy.yedns.org:8057");
    
    // 4) يعرض AlertDialog
    c.b.a.d.e(message, c.this.f1900a);
}
```

---

## 6. مغلّف الـ Response (Response Envelope)

كل response من السيرفر يأتي **بنفس الشكل** (deserialized to `com.egy.webpaymentapp.webapi.models.b`):

```typescript
interface ApiResponseEnvelope {
  GEN_API_ERR_NO: number;          // 0 = نجاح، > 0 = فشل
  GEN_API_ERR_MSG: string;         // رسالة الخطأ بالعربية (إن فشل)
  
  // الحقول التالية اختيارية، تظهر بحسب الـ endpoint:
  apppk?: string;                  // فقط في getAppPK: "modulus_b64&exponent_b64"
  user?: User;                     // فقط في Login: بيانات المستخدم الكاملة + Token
  payinfo?: Payinfo;               // غير مستخدم حالياً، لكن مُعرّف
  userRoles?: UserRoles;           // (الكلاس فارغ في التطبيق)
  customersList?: Customer[];      // قائمة المشتركين (للبحث)
  payList?: PaymentReportEntry[];  // قائمة المدفوعات (للتقرير)
  AreaList?: Area[];               // قائمة المناطق (مع Login)
}
```

تفاصيل الحقول في [`../03_data_models/`](../03_data_models/).

---

## 7. الـ Request Envelope الموحَّد

أغلب الـ endpoints (ما عدا Login و getAppPK) ترسل الـ body بنفس البنية (`com.egy.webpaymentapp.webapi.models.d`):

```typescript
interface ApiRequestEnvelope {
  c_no?: string;          // رقم المشترك (للبحث)
  findVal?: string;       // قيمة البحث (للقوائم)
  area_no?: string;       // رقم المنطقة المختارة
  user_no: string;        // معرف المستخدم (User.Id)
  user_branch: string;    // فرع المستخدم
  op_typ?: string;        // "1" payment | "2" reading | "3" location
  acc_token?: string;     // غير مستخدم في الكود
  payinfo?: Payinfo;      // عنصر العملية (دفع/قراءة/موقع)
  user?: User;            // بيانات المستخدم (لـ Login)
  oldpass?: string;       // فقط في changePassword
  newpass?: string;       // فقط في changePassword
}
```

تفاصيل في [`../03_data_models/01_user_model.md`](../03_data_models/) ⋯

---

## 8. ملخّص بالأمثلة (Cheatsheet)

```
POST https://abbasiy.yedns.org:8057/payment/api/Users/getAppPK
Body: (empty or null)
Auth: none
Response: {"GEN_API_ERR_NO":0,"apppk":"<modulus_b64>&<exponent_b64>"}
─────────────────────────────────────────────────────────────────────────
POST https://abbasiy.yedns.org:8057/payment/api/Users/Login
Body: {"Username":"u1","user_branch":"01","Password":"<RSA_b64>","mob_srl":"<RSA_b64>"}
Auth: none
Response: {"GEN_API_ERR_NO":0,"user":{...},"AreaList":[...]}
─────────────────────────────────────────────────────────────────────────
POST https://abbasiy.yedns.org:8057/payment/api/Users/changePasswordRequest
Body: {"user_no":"...","user_branch":"...","user":{...},"oldpass":"<RSA>","newpass":"<RSA>"}
Auth: Bearer {token}
Response: {"GEN_API_ERR_NO":0,"user":{...}}
─────────────────────────────────────────────────────────────────────────
POST https://abbasiy.yedns.org:8057/payment/api/Payment/GetCustomersData
Body: {"c_no":"12345","op_typ":"1","user_branch":"01","user_no":"...","area_no":""}
Auth: Bearer
Response: {"GEN_API_ERR_NO":0,"customersList":[{c_no, c_name, c_bal, ...}]}
─────────────────────────────────────────────────────────────────────────
POST https://abbasiy.yedns.org:8057/payment/api/Payment/saveBillRequest
Body: {user:{}, user_no, user_branch, payinfo:{c_no, c_name, c_bal, v_amt, c_note, user_gps_loc}}
Auth: Bearer
Response: {"GEN_API_ERR_NO":0,"payinfo":{v_no, v_date, ...}}
─────────────────────────────────────────────────────────────────────────
POST https://abbasiy.yedns.org:8057/payment/api/Payment/saveReadingRequest
Body: {user:{}, user_no, op_typ:"2", payinfo:{c_no, c_name, v_amt, c_note, BRD_ImgName, BRD_ImgData, user_gps_loc}}
Auth: Bearer
Response: {"GEN_API_ERR_NO":0, payinfo:{v_no, v_date}}
─────────────────────────────────────────────────────────────────────────
POST https://abbasiy.yedns.org:8057/payment/api/Payment/saveCustLocation
Body: {user:{}, user_no, payinfo:{c_no, c_name, user_gps_loc}}
Auth: Bearer
Response: {"GEN_API_ERR_NO":0}
─────────────────────────────────────────────────────────────────────────
POST https://abbasiy.yedns.org:8057/payment/api/Payment/GetPaymentsReportData
Body: {user:{}, user_no, user_branch, findVal:"<search>"}
Auth: Bearer
Response: {"GEN_API_ERR_NO":0, payList:[{c_no, c_name, c_bal, v_amt, v_date, v_no, user_name, comp_name, comp_add, comp_tel, brD_ImgName}]}
─────────────────────────────────────────────────────────────────────────
POST https://abbasiy.yedns.org:8057/payment/api/Payment/GetReadingListData
Body: {user:{}, user_no, user_branch, findVal:"<search>"}
Auth: Bearer
Response: {"GEN_API_ERR_NO":0, payList:[{...similar to payment...}]}
```

---

## 9. ملاحظات هندسية للـ Backend

> هذا القسم يساعد فريق إعادة البناء إن احتاج صنع mock أو خادم اختبار.

1. **النمط `api/Controller/Action`** هو نموذج ASP.NET Web API 2 (قبل .NET Core)، يدعم routing default.
2. **اختلاف case** بين أفعال (`Login` يبدأ بكبير، `saveBillRequest` يبدأ بصغير) يدل على أن المطور الأصلي لم يتبع convention صارمة. Web API بالـ case-insensitive routing افتراضياً.
3. **الـ apppk بصيغة `modulus_b64&exponent_b64`** يكشف أن الخادم يولّد RSA pair في الذاكرة أو يقرأها من keystore بصيغة فاصلها `&`.
4. **`mob_srl`** = mobile serial = `android_id` أو `IMEI` مشفّر بـ RSA — هذا "device binding" بسيط.
5. **حقل `payinfo` يُعاد استخدامه في كل العمليات** بأسلوب overloaded. هذا يدل على أن الـ ASP.NET model binding لديهم `Payinfo` واحدة بكل الحقول الممكنة وتُستخدم الحقول ذات الصلة فقط حسب العملية.
6. **لا يوجد versioning** للـ API (لا `/v1/` أو `Accept: ...; v=1`).
7. **لا CORS** يبدو ضرورياً لأن الزبون Mobile دائماً.

---

**التالي:** [`02_authentication.md`](02_authentication.md) — تفصيل الـ 3 endpoints الخاصة بـ Authentication.
