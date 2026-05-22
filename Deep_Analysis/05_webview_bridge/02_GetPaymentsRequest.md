# `mobile.GetPaymentsRequest(String)` — جلب قائمة الدفعات

> **التوقيع:** `@JavascriptInterface public void GetPaymentsRequest(String str)`
> **الموقع:** `web/i.java` السطر 20-23
> **المُستدعَى من:** `paymentList.html` / `paymentlist.js`

---

## 1. الكود الكامل

```java
@JavascriptInterface
public void GetPaymentsRequest(String str) {
  WebviewActivity.v(str, this.f2415a);
}
```

⇒ يفوِّض كل العمل إلى `WebviewActivity.v(String, Activity)` (static method).

---

## 2. المُعامِل `String str`

النوع: `String` (JSON).

### 2.1 المُحتوى المُتوقَّع (من JS)
```json
{
  "c_no": "12345",
  "findVal": "",
  "area_no": "A001",
  "fromDate": "2024-01-01",
  "toDate": "2024-12-31"
}
```

⚠️ **التطبيق الفعلي قد يختلف** — يحتاج التحقق من `paymentlist.js`. التخمين بناءً على بنية `models/d`.

---

## 3. ما يفعله `WebviewActivity.v(String, Activity)` (مُعاد بناؤه)

```java
public static void v(String json, Activity activity) {
  User user = MediaSessionCompat.C(activity);
  
  d req = new Gson().fromJson(json, d.class);
  // إكمال الحقول الإجبارية
  req.f2461d = user.f();              // user_no
  req.f2462e = user.l();              // acc_token
  req.a(user.n());                     // user_branch
  req.k = "1";                         // op_typ = Payment
  
  c.b.a.f.c client = new c.b.a.f.c(activity);
  client.b(
    "/api/Payment/GetPaymentsReportData",
    req,
    com.egy.webpaymentapp.webapi.models.b.class,
    response -> {
      // response.f() ⇒ List<c> payList
      String payListJson = new Gson().toJson(response.f());
      
      // ⚠️ خطر injection
      WebviewActivity.u.loadUrl(
        "javascript:showpayList('" + payListJson + "');"
      );
    },
    error -> {
      Toast.makeText(activity, "Error: " + error.getMessage(), 1).show();
    }
  );
}
```

⚠️ **التعليق:** الكود الفعلي لـ `v()` غير ظاهر مباشرة في `WebviewActivity.java` المُفكَّك (يحتمل أنه في طبقة inner class). لكن النمط مُتوقَّع من السياق.

---

## 4. الإستجابة (Response)

تُحقن في `paymentList.html` عبر:

```js
function showpayList(jsonStr) {
  const records = JSON.parse(jsonStr);
  // كل عنصر:
  // {c_no, c_name, c_bal, v_amt, v_date, v_no, user_name, user_no, comp_name, comp_add, comp_tel, brD_ImgName}
  
  records.forEach(rec => {
    // أضف صف للجدول
  });
}
```

⇒ النموذج: `List<models/c>` (12 حقل، راجع `03_data_models/04_payment_record.md`).

---

## 5. التدفُّق الكامل (Sequence)

```text
┌────────────┐                ┌──────────┐              ┌──────────────┐
│ paymentList.html / JS  │    │ i.java   │              │ WebviewActivity │   │ Backend │
└─────┬─────────────────┘    └────┬─────┘              └────────┬─────┘   └────┬────┘
      │                            │                              │              │
      │ window.mobile               │                              │              │
      │   .GetPaymentsRequest(json) │                              │              │
      │───────────────────────────>│                              │              │
      │                            │ WebviewActivity.v(json, act) │              │
      │                            │─────────────────────────────>│              │
      │                            │                              │ POST /api/Payment │
      │                            │                              │ /GetPaymentsReportData│
      │                            │                              │─────────────>│
      │                            │                              │              │
      │                            │                              │ response (List<c>)│
      │                            │                              │<─────────────│
      │                            │                              │              │
      │                            │                              │ webview.loadUrl( │
      │                            │                              │  "javascript:    │
      │                            │                              │   showpayList(...)")│
      │ showpayList(json)          │                              │              │
      │<─────────────────────────────────────────────────────────│              │
      │ ↓                          │                              │              │
      │ JSON.parse + render        │                              │              │
      │                            │                              │              │
```

---

## 6. المخاطر الأمنية

| # | الخطر | التخفيف |
|---|------|---------|
| 1 | حقن JS عبر `loadUrl("javascript:" + json)` بدون escape | استخدام `evaluateJavascript()` + escape |
| 2 | استلام JSON من JS غير-trusted بدون validation | Zod-like validation في Java |
| 3 | الـ Token يُرسَل من Java ⇒ لكن JS قد يعدِّل `str` لإستخدام token مستخدم آخر | جمع الـ Token من SharedPrefs فقط |
| 4 | لا rate-limiting ⇒ JS spamming endpoint | local rate-limit في Java |

---

## 7. المُكافِئ في React Native

```tsx
// في الـ WebView injected JS:
window.mobile.GetPaymentsRequest = (filtersJson) => {
  window.ReactNativeWebView.postMessage(JSON.stringify({
    type: 'GetPayments',
    payload: JSON.parse(filtersJson),
  }));
};

// في الـ Native handler:
case 'GetPayments': {
  // فحص حدود
  const filters = paymentFiltersSchema.parse(payload);
  
  // استدعاء API typed
  const records = await api.payments.list(filters);
  
  // حقن آمن
  const json = JSON.stringify(records).replace(/[\\'"\u2028\u2029]/g, '\\$&');
  webViewRef.current?.injectJavaScript(`
    if (typeof showpayList === 'function') {
      showpayList(${json});
    }
    true;
  `);
  break;
}
```

---

## 8. توصيات

- ✅ **افحص JSON المُدخَل** قبل deserialize.
- ✅ **استخدم `evaluateJavascript`** (Android 4.4+) بدل `loadUrl`.
- ✅ **اضبط Token من الـ Native** فقط (لا تثق بـ JS).
- ✅ **أضف debounce** على الإستدعاء من JS لمنع spam.
- ✅ **اطّلع على `paymentlist.js`** لمعرفة محتوى `str` الفعلي.

---

> **يربط هذا الملف بـ:**
> - `02_api_contract/03_payments_endpoints.md` (GetPaymentsReportData).
> - `03_data_models/04_payment_record.md` (response model).
> - `09_assets_resources/02_javascript_files.md` (paymentlist.js).
