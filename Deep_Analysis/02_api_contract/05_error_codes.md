# 02.5 — رموز الأخطاء (Error Codes)

> الـ Envelope الموحد لكل الـ Responses يحتوي `GEN_API_ERR_NO` (رقم) و `GEN_API_ERR_MSG` (نص).
> القيمة `0` = نجاح، أي شيء آخر = فشل (وتُعرض الرسالة في AlertDialog).

---

## مصدر الكود

```java
// com.egy.webpaymentapp.webapi.models.b.java
public class b {
    @SerializedName("GEN_API_ERR_NO")
    private int f2448a;        // .e() = getErrCode()
    
    @SerializedName("GEN_API_ERR_MSG")
    private String f2449b;     // .d() = getErrMsg()
}

// نمط المعالجة في كل callback:
@Override public void a(ApiResponseEnvelope r) {
    if (r.getErrCode() > 0) {
        c.b.a.d.e(r.getErrMsg(), activity);   // showAlert
        return;
    }
    // ... handle success ...
}
```

---

## رموز معروفة فقط من الكود

التطبيق نفسه يتعامل مع **حالتين فقط بشكل خاص**:

| الحالة | المعالجة |
|---|---|
| `GEN_API_ERR_NO == 0` | ✅ نجاح، أكمل المعالجة |
| `GEN_API_ERR_NO > 0` | ❌ فشل، اعرض الرسالة كما هي من السيرفر |
| HTTP `401 Unauthorized` | ❌ Logout (يُعالج خارج الـ envelope، على مستوى HTTP) |
| HTTP `5xx` أو timeout | ❌ "فشل الاتصال بالخادم" (بالعربية) |

---

## الرموز المُحتملة في السيرفر (مبنية على معتاد .NET Web API في اليمن)

> ⚠️ **هذه القائمة استرشادية**، تستند إلى:
> 1. نمط الترقيم الشائع في تطبيقات Yemeni ASP.NET WCF/Web API
> 2. الرسائل العربية الموجودة في `strings.xml` 
> 3. تتبّع الكود في `c.b.a.f.b.java` (Login/ChangePass) و `e0.java` (Save) 
>
> يجب تأكيدها بمراقبة الشبكة الفعلية في عمليات Field-test.

### مجموعة 0: نجاح
| الرمز | المعنى |
|---|---|
| `0` | نجاح |

### مجموعة 1-99: أخطاء عامة
| الرمز | المعنى المُحتمل |
|---|---|
| `1` | خطأ غير محدد في الخادم |
| `2` | بيانات الطلب غير مكتملة |
| `3` | تنسيق JSON خاطئ |
| `10` | خطأ قاعدة البيانات |
| `99` | خطأ داخلي في الخادم |

### مجموعة 100-199: أخطاء المصادقة
| الرمز | المعنى | الـ Endpoint |
|---|---|---|
| `100` | اسم المستخدم أو كلمة المرور خاطئة | `/Login` |
| `101` | الحساب موقوف | `/Login` |
| `102` | الجهاز غير مفعّل (`mob_srl` لا يتطابق) | `/Login` |
| `103` | الحساب منتهٍ الصلاحية | `/Login` |
| `104` | يجب إعادة تعيين كلمة المرور | `/Login` (مع `restpass="1"`) |
| `110` | RSA decryption failed (مفتاح قديم) | الكل |
| `111` | Token غير صالح | الكل (مع Bearer) |
| `112` | Token منتهٍ الصلاحية | الكل |
| `200` | كلمة المرور الحالية خاطئة | `/changePasswordRequest` |
| `201` | كلمة المرور الجديدة لا تستوفي الشروط | `/changePasswordRequest` |

### مجموعة 300-399: أخطاء العمليات (Payment/Reading)
| الرمز | المعنى | الـ Endpoint |
|---|---|---|
| `300` | المشترك غير موجود | `/GetCustomersData` |
| `301` | المشترك في فرع آخر | `/GetCustomersData` |
| `302` | المشترك في منطقة غير مسموحة للمستخدم | `/GetCustomersData` |
| `310` | المبلغ المُدخل أكبر من الرصيد | `/saveBillRequest` |
| `311` | المبلغ يجب أن يكون أكبر من صفر | `/saveBillRequest` |
| `320` | القراءة أقل من القراءة السابقة | `/saveReadingRequest` |
| `321` | الصورة مطلوبة لهذه القراءة | `/saveReadingRequest` |
| `322` | حجم الصورة كبير جداً | `/saveReadingRequest` |
| `330` | إحداثيات GPS غير صالحة | `/saveCustLocation` |
| `390` | تم حفظ هذه العملية مسبقاً (duplicate) | `/saveBill`, `/saveReading` |

### مجموعة 400-499: أخطاء الصلاحيات
| الرمز | المعنى |
|---|---|
| `400` | المستخدم لا يملك صلاحية لهذه العملية |
| `401` | الفرع لا يدعم هذه العملية |
| `402` | تجاوز عدد العمليات اليومية المسموح |

---

## كيف يجب التعامل مع الأخطاء في الـ Rebuild

### النمط الحالي (سيء)
```java
if (r.getErrCode() > 0) {
    showAlert(r.getErrMsg());   // يعرض رسالة عربية واحدة من السيرفر
}
```
**المشاكل:**
- لا يمكن للـ UI تخصيص السلوك حسب نوع الخطأ.
- لا navigation تلقائي (مثلاً 102 → افتح صفحة "اتصل بالدعم").
- لا تلسجيل (telemetry) للأخطاء.

### النمط المُوصى به (في الـ Rebuild)
```typescript
type ApiResponse<T> = 
  | { ok: true; data: T }
  | { ok: false; code: number; message: string };

class ApiError extends Error {
  constructor(public code: number, public arabicMessage: string) {
    super(`API Error ${code}: ${arabicMessage}`);
  }
}

// Handler واحد مركزي:
async function handleApiError(error: ApiError, navigation: Navigation) {
  switch (error.code) {
    case 102: case 104:
      navigation.replace('ContactSupport', { code: error.code });
      break;
    case 111: case 112: case 401:    // Auth errors
      await logout();
      navigation.replace('Login');
      break;
    case 390:    // Duplicate
      showSnackbar('هذه العملية محفوظة مسبقاً');
      break;
    default:
      showAlert(error.arabicMessage);
  }
  
  // Telemetry
  Sentry.captureException(error, { tags: { code: error.code }});
}
```

---

## رسائل عربية شائعة موجودة في `strings.xml`

من الـ APK، الـ strings ذات الصلة بالأخطاء:

```xml
<string name="no_connection">لايوجد إتصال بالشبكة</string>
<string name="connection_failed">فشل الاتصال بالخادم</string>
<string name="enter_filed_data">الحقل مطلوب</string>
<string name="txt_cust_no">يجب إدخال رقم المشترك</string>
<string name="txt_mter_img_must">يجب تصوير العداد</string>
<string name="txt_op_confirmation">هل أنت متأكد من تأكيد العملية؟</string>
<string name="lbl_yes">نعم</string>
<string name="lbl_no">لا</string>
<string name="lbl_ok">موافق</string>
<string name="alert_title">تنبيه</string>
<string name="confirm_title">تأكيد</string>
<string name="Exit_From_System">هل تريد الخروج من البرنامج؟</string>
```

---

## أخطاء على مستوى HTTP

غير الـ envelope errors، هذه الأخطاء تأتي على مستوى Volley:

| HTTP Code | المعالجة في التطبيق |
|---|---|
| **200** | ✅ يفحص الـ envelope |
| **204** | يعتبره نجاحاً بدون body |
| **401** | يسجّل خروج المستخدم وينقله لـ Login (`new f0(activity).h()`) |
| **403** | غير معالج خصيصاً، يظهر كرسالة عامة |
| **404** | غير معالج، يظهر كرسالة عامة |
| **5xx** | يظهر كرسالة عامة "فشل الاتصال" |
| **Timeout** | بعد 10 ثوانٍ + retry واحد، يفشل |
| **SSL Error** | **يتجاوزه** (TrustManager فارغ — VULNERABLE) |
| **DNS error** | يظهر كرسالة عامة |

---

## ملاحظات إضافية

1. **لا يوجد standard JSON error format** مثل RFC 7807 (Problem Details). الـ Envelope مخصص.
2. **رسائل الخطأ من السيرفر باللغة العربية** ـ مما يعني أن أي تدويل (i18n) في الـ Rebuild سيحتاج إما:
   - مطالبة السيرفر بإضافة `Accept-Language` support.
   - أو خريطة `error_code → translation` على الـ client.
3. **بعض السيرفر يستخدم `placeholder XXHOST`** الذي يُستبدل في الـ client بالـ host الحالي. هذا غريب ويستحق التحقيق.

---

**التالي:** [`06_request_examples.md`](06_request_examples.md) — أمثلة JSON كاملة قابلة للاستخدام في Postman.
