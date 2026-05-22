# مخطط إعادة البناء — الإصلاحات الأمنية المطلوبة

> **الملف:** `10_rebuild_blueprint/05_security_improvements.md`
> **الغرض:** قائمة شاملة بكل الثغرات الأمنية في التطبيق الحالي مع الحل المُوصى به لكل واحدة.
> **المرجع:** الثغرات موثَّقة بالتفصيل في `AbbasiyCashiers_RE_Analysis/06_findings/` و `Deep_Analysis/06_business_logic/02_deeplink_handler.md`

---

## 📋 جدول المحتويات

1. [مصفوفة الثغرات الشاملة](#1-مصفوفة-الثغرات-الشاملة)
2. [إصلاح Magic Backdoor](#2-إصلاح-magic-backdoor)
3. [إصلاح TLS Bypass](#3-إصلاح-tls-bypass)
4. [إصلاح Hardcoded Crypto Keys](#4-إصلاح-hardcoded-crypto-keys)
5. [إصلاح WebView Dangerous Settings](#5-إصلاح-webview-dangerous-settings)
6. [إصلاح Token Storage](#6-إصلاح-token-storage)
7. [إصلاح Deeplink Hijacking](#7-إصلاح-deeplink-hijacking)
8. [إضافة Root Detection](#8-إضافة-root-detection)
9. [إضافة Code Obfuscation](#9-إضافة-code-obfuscation)
10. [إضافة Audit Logging](#10-إضافة-audit-logging)
11. [Security Testing Checklist](#11-security-testing-checklist)

---

## 1. مصفوفة الثغرات الشاملة

| # | الثغرة | الخطورة | الموقع الأصلي | الإصلاح |
|---|--------|---------|----------------|---------|
| V1 | **Magic Backdoor `1/1/1`** | 🔴 حرج | `LoginActivity.java:65` | حذف الباب الخلفي بالكامل (§2) |
| V2 | **Empty X509TrustManager** | 🔴 حرج | `c.b.a.f.d` | SSL Pinning (§3) |
| V3 | **Permissive HostnameVerifier** | 🔴 حرج | `c.b.a.f.c` | Strict verification (§3) |
| V4 | **Hardcoded DESede Key** | 🔴 حرج | `MediaSessionCompat:621` | JWT signed config (§4) |
| V5 | **Deeplink Server Hijack** | 🔴 حرج | `LoginActivity:145` | Host whitelist + signed URL (§7) |
| V6 | **WebView Universal Access** | 🟠 عالٍ | `WebviewActivity.y()` | Disable + restrict (§5) |
| V7 | **WebView File Access** | 🟠 عالٍ | `WebviewActivity.y()` | Disable (§5) |
| V8 | **Token in SharedPreferences (plain)** | 🟠 عالٍ | `c.b.a.c` wrapper | Keychain/Keystore (§6) |
| V9 | **No Certificate Pinning** | 🟠 عالٍ | (missing) | إضافة pinning (§3) |
| V10 | **No Root Detection** | 🟡 متوسط | (missing) | إضافة detection (§8) |
| V11 | **No Code Obfuscation** | 🟡 متوسط | (missing) | ProGuard + R8 (§9) |
| V12 | **Verbose Error Messages** | 🟡 متوسط | متعدد | Generic messages (§10) |
| V13 | **Token Clear Bug `C.s("")`** | 🟡 متوسط | `OprationsActivity.E():139` | Immutable User (§6) |
| V14 | **No Session Timeout** | 🟡 متوسط | (missing) | إضافة timeout (§6) |
| V15 | **No Audit Logging** | 🟡 متوسط | (missing) | إضافة logging (§10) |
| V16 | **DESede ECB Mode** | 🟡 متوسط | `MediaSessionCompat:628` | AES-GCM (§4) |
| V17 | **2-Key 3DES (112-bit)** | 🟡 متوسط | `MediaSessionCompat:621` | AES-256 (§4) |
| V18 | **HTTP Allow** | 🟢 منخفض | (auto-upgrade only) | إجبار HTTPS (§3) |
| V19 | **No Biometric Lock** | 🟢 منخفض | (missing) | إضافة (اختياري) (§6) |
| V20 | **No Anti-Tamper** | 🟢 منخفض | (missing) | Signature check (§9) |

---

## 2. إصلاح Magic Backdoor

### 2.1 المشكلة
في `LoginActivity.java:65`:
```java
if ("1".equals(branch) && "1".equals(user) && "1".equals(pass)) {
    Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
    intent.setData(Uri.fromParts("package", getPackageName(), null));
    startActivity(intent);
    return;
}
```

**الأثر:** أي شخص يعرف هذه المعلومة (وهي مكتوبة في الكود!) يستطيع الوصول لإعدادات النظام بدون مصادقة.

### 2.2 الحل
**حذف هذا الكود بالكامل من النسخة الجديدة.** لا يوجد له بديل مقبول.

```ts
// ❌ لا تكتب هذا أبداً!
// if (branchCode === '1' && username === '1' && password === '1') {
//   navigation.navigate('Settings');
//   return;
// }

// ✅ التحقق الصحيح
function validateLogin(input: LoginInput): boolean {
  // كل التحقق يحدث على السيرفر، لا توجد credentials محلية
  return LoginInputSchema.safeParse(input).success;
}
```

### 2.3 البديل: شاشة Debug للمطورين
إذا كان الهدف الأصلي هو **شاشة debug للمطورين**، نضيفها بطريقة آمنة:

```ts
// src/screens/debug/DebugScreen.tsx
import { isDevBuild } from '@/config/env';

export function DebugScreen() {
  if (!isDevBuild) {
    // في الإنتاج: لا يمكن الوصول لهذه الشاشة أبداً
    return <Redirect to="/login" />;
  }
  
  return (
    <View>
      <Text>Debug Tools</Text>
      <Button onPress={clearDatabase}>Clear DB</Button>
      <Button onPress={resetSettings}>Reset Settings</Button>
      <Button onPress={() => Linking.openSettings()}>Open System Settings</Button>
    </View>
  );
}
```

```ts
// src/config/env.ts
export const isDevBuild = __DEV__ || env.ENVIRONMENT === 'development';
```

---

## 3. إصلاح TLS Bypass

### 3.1 المشكلة
في `c.b.a.f.d`:
```java
public class d implements X509TrustManager {
    public void checkClientTrusted(X509Certificate[] chain, String authType) {}
    public void checkServerTrusted(X509Certificate[] chain, String authType) {}
    //                                                              ↑ فارغ
    public X509Certificate[] getAcceptedIssuers() {
        return new X509Certificate[0];
    }
}
```

**الأثر:** التطبيق يقبل **أي شهادة TLS**، بما في ذلك شهادات MITM المُزوَّرة.

### 3.2 الحل: SSL Pinning

```ts
// src/api/ssl-pinning.ts
import { fetch as pinnedFetch } from 'react-native-ssl-pinning';

const PINNED_HOSTS = ['abbasiy.yedns.org'];

export function shouldPin(url: string): boolean {
  const host = new URL(url).hostname;
  return PINNED_HOSTS.includes(host);
}

export async function pinnedRequest(url: string, options: any) {
  return pinnedFetch(url, {
    ...options,
    sslPinning: {
      certs: ['abbasiy-cert-primary', 'abbasiy-cert-backup'],
    },
    timeoutInterval: 15000,
  });
}
```

### 3.3 ProGuard rules للحماية الإضافية

```proguard
# android/app/proguard-rules.pro
-keepclassmembers class com.toyberman.RNSslPinning.OkHttpClientFactory {
    *;
}
```

### 3.4 Certificate Rotation Plan
- **Primary certificate:** المستخدم حالياً
- **Backup certificate:** الجيل القادم (يُنشَر قبل انتهاء الأول بـ 90 يوم)
- **Emergency:** إصدار update من Play Store بشهادة جديدة

---

## 4. إصلاح Hardcoded Crypto Keys

### 4.1 المشكلة
- **DESede Key مزروع:** `m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##` في `MediaSessionCompat.java:621`
- **ECB Mode** (textbook insecure)
- **2-Key 3DES** (112-bit, deprecated by NIST SP 800-131A 2017)

### 4.2 الحل: حذف التشفير المحلي بالكامل
في النسخة الجديدة، **لا تشفير محلي للمعلومات الحساسة**. كل التشفير على المستوى الـ TLS فقط.

```ts
// ❌ لا تستخدم crypto محلية لـ:
// - تشفير URLs
// - تشفير IDs
// - تشفير tokens

// ✅ استخدم TLS فقط للنقل الآمن
// ✅ استخدم Keychain/Keystore للتخزين الآمن
```

### 4.3 RSA Password Encryption (محتفظ به)
نُبقي على RSA لتشفير كلمة المرور عند الإرسال (مثل الأصل) لأنه إضافة دفاعية فوق TLS:

```ts
// src/features/auth/crypto.ts
import { RSA } from 'react-native-rsa-native';

/**
 * تشفير كلمة المرور بـ RSA Public Key من السيرفر
 * يستبدل MediaSessionCompat.a() من الأصل
 */
export async function encryptPasswordWithRSA(
  password: string,
  publicKeyPem: string,
): Promise<string> {
  try {
    const encrypted = await RSA.encrypt(password, publicKeyPem);
    return encrypted;
  } catch (error) {
    throw new Error('فشل في تشفير كلمة المرور');
  }
}
```

### 4.4 إذا احتجنا تشفير محلي مستقبلاً
إذا فعلاً احتجنا تشفير حقل معين محلياً، نستخدم **AES-256-GCM** مع مفتاح من Keychain:

```ts
import { encrypt, decrypt } from 'react-native-aes-crypto';
import * as Keychain from 'react-native-keychain';

async function encryptSensitive(plaintext: string): Promise<string> {
  // المفتاح يُولَّد مرة واحدة ويُخزَّن في Keychain
  let key = await getOrCreateEncryptionKey();
  const iv = await generateIV();
  
  const ciphertext = await encrypt(plaintext, key, iv, 'aes-256-gcm');
  
  return JSON.stringify({ ciphertext, iv });
}

async function getOrCreateEncryptionKey(): Promise<string> {
  const stored = await Keychain.getGenericPassword({ service: 'encryption-key' });
  if (stored) return stored.password;
  
  // أول مرة: ولّد مفتاح آمن
  const newKey = await generateRandomKey(256);  // 256-bit
  await Keychain.setGenericPassword('key', newKey, { service: 'encryption-key' });
  return newKey;
}
```

---

## 5. إصلاح WebView Dangerous Settings

### 5.1 المشكلة في الأصل
في `WebviewActivity.y()` (lines 431-440):
```java
webSettings.setAllowUniversalAccessFromFileURLs(true);  // 🔴 خطير جداً
webSettings.setAllowFileAccess(true);                    // 🔴 خطير
webSettings.setJavaScriptEnabled(true);                  // 🟡 مطلوب لكن خطر
webSettings.setAllowFileAccessFromFileURLs(true);       // 🔴 خطير
```

### 5.2 الحل في النسخة الجديدة

#### الخيار 1: لا WebView على الإطلاق
إعادة بناء التقارير كـ React Native components بدلاً من HTML.

```tsx
// بدلاً من WebView، استخدم RN component
function PaymentsReport({ data }) {
  return (
    <ScrollView>
      <ReportHeader />
      <FlatList
        data={data.payments}
        renderItem={({ item }) => <PaymentRow payment={item} />}
      />
      <ReportFooter total={data.total} />
    </ScrollView>
  );
}
```

#### الخيار 2: WebView مع إعدادات آمنة
إذا أبقينا WebView لسبب ما:

```tsx
import { WebView } from 'react-native-webview';

function SafeWebView({ url }: { url: string }) {
  // 1. تحقق من أن URL في allowlist
  if (!isAllowedUrl(url)) {
    throw new Error('URL غير مسموح به');
  }
  
  return (
    <WebView
      source={{ uri: url }}
      // ✅ إعدادات آمنة
      javaScriptEnabled={true}        // مطلوب للوظائف الأساسية
      domStorageEnabled={true}
      
      // ❌ منع كل ما هو خطير
      allowFileAccess={false}
      allowUniversalAccessFromFileURLs={false}
      allowFileAccessFromFileURLs={false}
      allowingReadAccessToURL={undefined}  // لا تسمح بأي ملف
      mixedContentMode="never"             // لا HTTP داخل HTTPS
      
      // ✅ Sandbox JavaScript
      injectedJavaScriptBeforeContentLoaded={`
        // امنع وصول JS لـ device APIs
        Object.defineProperty(window, 'mobile', {
          value: undefined,
          writable: false,
          configurable: false,
        });
        true;
      `}
      
      // ✅ تحقق من كل request
      onShouldStartLoadWithRequest={(request) => {
        return isAllowedUrl(request.url);
      }}
      
      // ✅ منع pop-ups
      setSupportMultipleWindows={false}
      
      // ✅ منع الاتصالات الخارجية غير المتوقعة
      originWhitelist={['https://abbasiy.yedns.org']}
    />
  );
}

function isAllowedUrl(url: string): boolean {
  try {
    const u = new URL(url);
    return ['abbasiy.yedns.org'].includes(u.hostname) && u.protocol === 'https:';
  } catch {
    return false;
  }
}
```

### 5.3 JS Bridge آمن (لو أبقينا عليه)

```tsx
import { WebView } from 'react-native-webview';

function ReportWebView() {
  const webViewRef = useRef<WebView>(null);
  
  /**
   * استبدال @JavascriptInterface من الأصل بـ message passing
   */
  const handleMessage = (event: WebViewMessageEvent) => {
    try {
      const message = JSON.parse(event.nativeEvent.data);
      
      // ✅ Validation صارم
      const result = MessageSchema.safeParse(message);
      if (!result.success) {
        console.warn('Invalid message from WebView:', message);
        return;
      }
      
      // ✅ Whitelist للـ actions المسموحة
      switch (result.data.action) {
        case 'PRINT_RECEIPT':
          return handlePrintReceipt(result.data.payload);
        case 'SHARE_REPORT':
          return handleShareReport(result.data.payload);
        // لا default — أي action آخر مرفوض
      }
    } catch (error) {
      console.error('Failed to handle WebView message:', error);
    }
  };
  
  return (
    <WebView
      ref={webViewRef}
      onMessage={handleMessage}
      // ... باقي الإعدادات الآمنة
    />
  );
}

const MessageSchema = z.discriminatedUnion('action', [
  z.object({ action: z.literal('PRINT_RECEIPT'), payload: PrintPayloadSchema }),
  z.object({ action: z.literal('SHARE_REPORT'), payload: SharePayloadSchema }),
]);
```

---

## 6. إصلاح Token Storage

### 6.1 المشكلة
التطبيق الأصلي يحفظ Token في SharedPreferences بنص واضح، يمكن قراءته بواسطة:
- تطبيقات أخرى (لو الجهاز Rooted)
- ADB backup
- أي malware داخلي

### 6.2 الحل: Keychain (iOS) / Keystore (Android)

```ts
// src/features/auth/storage.ts
import * as Keychain from 'react-native-keychain';

const TOKEN_SERVICE = 'AbbasiyCashiers.token';

export const tokenStorage = {
  async store(token: string): Promise<void> {
    await Keychain.setGenericPassword('token', token, {
      service: TOKEN_SERVICE,
      // ✅ الحماية القصوى
      accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_CURRENT_SET_OR_DEVICE_PASSCODE,
      accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
      // ✅ Hardware-backed (Trusted Execution Environment)
      storage: Keychain.STORAGE_TYPE.AES,
    });
  },
  
  async get(): Promise<string | null> {
    const result = await Keychain.getGenericPassword({ service: TOKEN_SERVICE });
    return result ? result.password : null;
  },
  
  async clear(): Promise<void> {
    await Keychain.resetGenericPassword({ service: TOKEN_SERVICE });
  },
};
```

### 6.3 إصلاح Token Clear Bug
في الأصل: `C.s("")` يمسح Token من الكائن المرجعي.

**الحل:** Immutable types في TypeScript

```ts
// ✅ readonly يمنع التعديل من خارج المُنشئ
export interface User {
  readonly token: string;
  // ... باقي الحقول
}

// لو احتجنا تحديث Token، نُنشئ كائن جديد:
function refreshToken(user: User, newToken: string): User {
  return { ...user, token: newToken };
}
```

### 6.4 Session Timeout

```ts
// src/features/auth/session.ts
import { tokenStorage } from './storage';
import { authStore } from './store';

const SESSION_TIMEOUT_MS = 30 * 60 * 1000;  // 30 min

let lastActivityTime = Date.now();
let timeoutTimer: NodeJS.Timeout | null = null;

export function trackActivity(): void {
  lastActivityTime = Date.now();
  resetTimeout();
}

function resetTimeout() {
  if (timeoutTimer) clearTimeout(timeoutTimer);
  
  timeoutTimer = setTimeout(async () => {
    const idleTime = Date.now() - lastActivityTime;
    if (idleTime >= SESSION_TIMEOUT_MS) {
      await tokenStorage.clear();
      authStore.getState().logout();
      // Navigate to login
    }
  }, SESSION_TIMEOUT_MS);
}

// تكامل مع navigation
// كل ما المستخدم يتفاعل (touch, navigation)، استدعِ trackActivity()
```

### 6.5 Biometric Lock (اختياري)

```ts
import ReactNativeBiometrics from 'react-native-biometrics';

const rnBiometrics = new ReactNativeBiometrics();

export async function authenticateWithBiometric(): Promise<boolean> {
  const { available, biometryType } = await rnBiometrics.isSensorAvailable();
  
  if (!available) {
    // fallback to PIN
    return false;
  }
  
  const { success } = await rnBiometrics.simplePrompt({
    promptMessage: 'تأكيد الهوية للوصول للتطبيق',
    fallbackPromptMessage: 'استخدم رمز PIN',
  });
  
  return success;
}
```

---

## 7. إصلاح Deeplink Hijacking

### 7.1 المشكلة (تفصيل في `06_business_logic/02_deeplink_handler.md`)
- لا allow-list للخوادم
- لا تأكيد من المستخدم
- التشفير وهمي (`r(s(ip)) == ip`)
- لا signature verification

### 7.2 الحل الكامل

```ts
// src/features/deeplink/handler.ts
import { Linking } from 'react-native';
import { verifyJWT } from '@/utils/jwt';
import { showConfirmDialog } from '@/ui/dialogs';
import { ConfigStore } from '@/config/store';
import * as Sentry from '@sentry/react-native';

// ✅ Whitelist صارم
const ALLOWED_HOSTS = [
  'abbasiy.yedns.org',
  'abbasiy-backup.example.com',
  'abbasiy-test.example.com',  // فقط في dev
];

// Public key للتحقق من توقيع الـ JWT (مُضمَّن في التطبيق)
const SERVER_CONFIG_PUBLIC_KEY = `-----BEGIN PUBLIC KEY-----
... (RSA-2048 public key)
-----END PUBLIC KEY-----`;

export function setupDeeplinkHandler() {
  Linking.addEventListener('url', handleDeeplink);
}

async function handleDeeplink({ url }: { url: string }) {
  try {
    const parsedUrl = new URL(url);
    
    // 1. تحقق من الـ host
    if (parsedUrl.host !== 'ecas.web.link') {
      console.warn('Unexpected deeplink host:', parsedUrl.host);
      return;
    }
    
    // 2. اقرأ الـ token (بدلاً من ?ip=)
    const configToken = parsedUrl.searchParams.get('config');
    if (!configToken) {
      return showError('رابط غير صالح');
    }
    
    // 3. تحقق من توقيع الـ JWT
    let payload;
    try {
      payload = await verifyJWT(configToken, SERVER_CONFIG_PUBLIC_KEY);
    } catch (error) {
      Sentry.captureMessage(`Invalid deeplink JWT: ${error}`);
      return showError('رابط غير موثوق');
    }
    
    // 4. تحقق من انتهاء الصلاحية
    if (payload.exp && Date.now() / 1000 > payload.exp) {
      return showError('رابط منتهي الصلاحية');
    }
    
    // 5. تحقق من الـ host في الـ payload
    const targetUrl = new URL(payload.serverUrl);
    if (!ALLOWED_HOSTS.includes(targetUrl.host)) {
      Sentry.captureMessage(`Unauthorized server in deeplink: ${targetUrl.host}`);
      return showError(`الخادم ${targetUrl.host} غير معتمد`);
    }
    
    // 6. تأكيد من المستخدم
    const confirmed = await showConfirmDialog({
      title: 'تغيير الخادم',
      message: `هل تريد تغيير الخادم إلى:\n${targetUrl.host}\n\nسبب التغيير: ${payload.reason || 'غير محدد'}`,
      confirmText: 'موافق',
      cancelText: 'إلغاء',
    });
    
    if (!confirmed) return;
    
    // 7. طلب credentials المسؤول
    const adminPin = await promptAdminPin();
    if (!await verifyAdminPin(adminPin)) {
      return showError('PIN غير صحيح');
    }
    
    // 8. تحديث الإعداد
    await ConfigStore.set('API_BASE_URL', targetUrl.toString());
    await ConfigStore.set('LAST_SERVER_CHANGE_AT', new Date().toISOString());
    
    // 9. Audit log
    logSecurityEvent({
      type: 'SERVER_CHANGED',
      from: ConfigStore.get('API_BASE_URL'),
      to: targetUrl.toString(),
      reason: payload.reason,
    });
    
    showSuccess('تم تغيير الخادم بنجاح');
  } catch (error) {
    Sentry.captureException(error);
    showError('فشل في معالجة الرابط');
  }
}
```

### 7.3 شكل الـ Deeplink الجديد

```
الأصل (غير آمن):
https://ecas.web.link/?ip=<DESede-encrypted-URL>

الجديد (آمن):
https://ecas.web.link/?config=<JWT>
```

JWT payload:
```json
{
  "serverUrl": "https://abbasiy-backup.example.com:8443/payment",
  "reason": "تحديث الخادم الأساسي",
  "exp": 1716345600,
  "iss": "abbasiy-admin",
  "iat": 1716259200
}
```

JWT signed with RSA-2048 private key على الخادم.

---

## 8. إضافة Root Detection

```ts
// src/security/root-detection.ts
import JailMonkey from 'jail-monkey';
import { Alert } from 'react-native';

export async function checkRootStatus(): Promise<boolean> {
  const isJailBroken = JailMonkey.isJailBroken();
  const trustFall = JailMonkey.trustFall();
  const canMockLocation = JailMonkey.canMockLocation();
  const isOnExternalStorage = JailMonkey.isOnExternalStorage();
  const isDevMode = JailMonkey.isDevelopmentSettingsMode();
  
  if (isJailBroken || trustFall) {
    // الجهاز Rooted/Jailbroken
    return true;
  }
  
  return false;
}

export async function enforceRootCheck() {
  const isRooted = await checkRootStatus();
  
  if (isRooted) {
    Alert.alert(
      'تنبيه أمني',
      'تم اكتشاف أن الجهاز Rooted/Jailbroken. لأسباب أمنية لا يمكن استخدام التطبيق على هذا الجهاز.',
      [{ text: 'حسناً', onPress: () => BackHandler.exitApp() }],
      { cancelable: false },
    );
  }
}
```

---

## 9. إضافة Code Obfuscation

### 9.1 ProGuard (Android)

```proguard
# android/app/proguard-rules.pro

# === Aggressive optimization ===
-optimizationpasses 5
-allowaccessmodification
-mergeinterfacesaggressively

# === Hide source file names ===
-renamesourcefileattribute SourceFile
-keepattributes SourceFile,LineNumberTable

# === Obfuscate everything by default ===
-dontskipnonpubliclibraryclasses

# === Keep React Native ===
-keep class com.facebook.react.** { *; }
-keep class com.facebook.hermes.** { *; }

# === Hide sensitive class names ===
-keepnames class com.abbasiycashiers.api.** { *; }
# ... but rename their internals

# === Strip logging in release ===
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}
```

### 9.2 Enable in build.gradle

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            
            // Hermes bytecode is harder to reverse than JS
            // (Already enabled in modern RN)
        }
    }
}
```

### 9.3 String Obfuscation للقيم الحساسة

```ts
// src/security/secret.ts

/**
 * لا تكتب strings حساسة مباشرة في الكود
 * استخدم encoding بسيط (مش حماية حقيقية، لكن يصعّب الاستخراج)
 */
function decode(encoded: string): string {
  return Buffer.from(encoded, 'base64').toString('utf-8');
}

// ❌ سيء: const API_KEY = "abc123";

// ✅ أفضل: 
const API_KEY = decode('YWJjMTIz');

// ✅✅ الأفضل: استخدم env variables + native secure storage
```

### 9.4 Anti-Tamper (Signature Verification)

```ts
// التحقق من توقيع APK لمنع التعديل
import { isVerifiedSignature } from 'react-native-tamper-checker';

async function checkAppIntegrity() {
  const isOriginal = await isVerifiedSignature([
    'EXPECTED_SHA256_FINGERPRINT_HERE',
  ]);
  
  if (!isOriginal) {
    Alert.alert('تم اكتشاف تعديل غير مصرح به على التطبيق');
    BackHandler.exitApp();
  }
}
```

---

## 10. إضافة Audit Logging

### 10.1 الفكرة
كل حدث أمني حساس يُسجَّل محلياً + يُرسَل للسيرفر:

```ts
// src/security/audit.ts
import { paymentRepository } from '@/database/repositories';

export interface SecurityEvent {
  type: SecurityEventType;
  timestamp: Date;
  userId?: string;
  details: Record<string, unknown>;
  severity: 'info' | 'warning' | 'critical';
}

export enum SecurityEventType {
  // Authentication
  LOGIN_SUCCESS = 'LOGIN_SUCCESS',
  LOGIN_FAILURE = 'LOGIN_FAILURE',
  LOGOUT = 'LOGOUT',
  SESSION_EXPIRED = 'SESSION_EXPIRED',
  PASSWORD_CHANGED = 'PASSWORD_CHANGED',
  
  // Authorization
  ACCESS_DENIED = 'ACCESS_DENIED',
  
  // Configuration
  SERVER_CHANGED = 'SERVER_CHANGED',
  
  // Suspicious
  ROOT_DETECTED = 'ROOT_DETECTED',
  TAMPER_DETECTED = 'TAMPER_DETECTED',
  INVALID_DEEPLINK = 'INVALID_DEEPLINK',
  
  // Operations
  PAYMENT_SAVED = 'PAYMENT_SAVED',
  READING_SAVED = 'READING_SAVED',
}

export async function logSecurityEvent(event: Omit<SecurityEvent, 'timestamp'>) {
  const fullEvent: SecurityEvent = {
    ...event,
    timestamp: new Date(),
  };
  
  // 1. سجّل محلياً
  await auditRepository.create(fullEvent);
  
  // 2. أرسل لـ Sentry (للأخطاء)
  if (event.severity === 'critical') {
    Sentry.captureMessage(`Security: ${event.type}`, {
      level: 'error',
      extra: event.details,
    });
  }
  
  // 3. أرسل للسيرفر (async)
  api.post('/api/audit/events', fullEvent).catch((err) => {
    console.warn('Failed to send audit event', err);
  });
}
```

### 10.2 Generic Error Messages
```ts
// ❌ لا تكشف معلومات داخلية:
// throw new Error('User with ID 12345 not found in database X');

// ✅ رسائل عامة للمستخدم
throw new AuthError('فشل تسجيل الدخول، تحقق من البيانات');

// لكن سجّل التفاصيل في الـ logs
logSecurityEvent({
  type: 'LOGIN_FAILURE',
  details: { username, attempt: 3, ip: deviceIp },
  severity: 'warning',
});
```

---

## 11. Security Testing Checklist

### 11.1 Static Analysis
- [ ] `npm audit --production` — لا dependencies بثغرات
- [ ] `eslint --plugin security` — اكتشاف patterns خطيرة
- [ ] `tsc --noEmit --strict` — type safety كامل
- [ ] فحص يدوي للـ `// TODO security` markers

### 11.2 Dynamic Analysis
- [ ] **MobSF (Mobile Security Framework):** فحص شامل للـ APK
- [ ] **Burp Suite:** اختبار MITM (يجب أن يفشل بسبب SSL Pinning)
- [ ] **Frida:** محاولة hooking على functions حساسة
- [ ] **adb backup:** التحقق من أن backup لا يحتوي بيانات حساسة

### 11.3 Penetration Tests
- [ ] محاولة تسجيل دخول بـ `1/1/1` — يجب أن يفشل
- [ ] محاولة MITM على API calls — يجب أن يفشل
- [ ] محاولة قراءة Token من SharedPreferences — يجب أن لا يكون موجوداً
- [ ] محاولة تعديل APK وإعادة التوقيع — يجب أن يكتشف Anti-Tamper
- [ ] محاولة فتح deeplink بـ host غير مصرح به — يجب أن يُرفض
- [ ] محاولة تشغيل التطبيق على جهاز Rooted — يجب أن يُمنع

### 11.4 Compliance
- [ ] **OWASP MASVS (Mobile Application Security Verification Standard)** — مستوى L1 على الأقل
- [ ] **OWASP Mobile Top 10** — كل البنود مغطاة
- [ ] **GDPR** (لو احتاج لاحقاً) — موافقة على البيانات

---

## 12. الملخص: ما تغير بالضبط؟

| المجال | الأصل (الحالي) | النسخة الجديدة |
|--------|------------------|------------------|
| **Backdoor** | `1/1/1` ⚠️ | ❌ محذوف |
| **TLS** | يقبل أي شهادة | SSL Pinning صارم |
| **Crypto** | DESede ECB hardcoded | TLS فقط (لا local crypto) |
| **Token** | SharedPreferences plain | Keychain/Keystore |
| **WebView** | إعدادات خطيرة | إعدادات آمنة + sandboxed |
| **Deeplink** | يقبل أي host | Whitelist + JWT signed + admin PIN |
| **Root** | لا فحص | منع كامل |
| **Code** | لا obfuscation | ProGuard + Hermes |
| **Sessions** | بدون انتهاء | 30 دقيقة timeout |
| **Audit** | لا logs | كل حدث مسجل |
| **Biometric** | لا | اختياري |

---

## 13. الخطوة التالية

اقرأ الملف التالي:
👉 **`06_ui_modernization.md`** — تحديث الواجهة

---

## مراجع
- `06_business_logic/02_deeplink_handler.md` — تفصيل ثغرة الـ deeplink
- `AbbasiyCashiers_RE_Analysis/06_findings/security_findings_summary.md` — جميع الثغرات الأصلية
- OWASP MASVS: https://mas.owasp.org/MASVS/
- React Native Security: https://reactnative.dev/docs/security

---

> *نهاية `10_rebuild_blueprint/05_security_improvements.md`*
