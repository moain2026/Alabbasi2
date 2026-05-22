# UserRoles Model — كلاس فارغ مُتعمَّد

> **المصدر:** `com.egy.webpaymentapp.webapi.models.UserRoles`
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/webapi/models/UserRoles.java`
> **الحالة:** ⚠️ **كلاس فارغ تماماً — 5 أسطر فقط بلا حقول أو دوال.**

---

## 1. الكود الكامل (بحرفيّته)

```java
package com.egy.webpaymentapp.webapi.models;

/* loaded from: classes.dex */
public class UserRoles {
}
```

نعم — هذا هو الملف بكامله. لا حقول. لا constructor. لا methods. فقط إعلان الكلاس.

---

## 2. لماذا موجود؟

### 2.1 الإستخدام الوحيد
في `models/b.java` (Response Envelope):

```java
@c.c.b.a0.b("userRoles")
private UserRoles f;
```

⇒ يتم Deserialize الحقل `userRoles` من JSON الإستجابة، لكن لأن الكلاس فارغ ⇒ **Gson يُهمل كل البيانات بصمت** (لا exception، لا warning).

### 2.2 السيناريوهات المحتملة

| الفرضية | الإحتمال | الأدلة |
|--------|---------|--------|
| **placeholder لإستخدام مستقبلي** | 🟢 مرتفع | الـ Backend ASP.NET قد يُرجع كائناً يحوي روابط/أدوار، والتطبيق فقط لم يفكّ ربطه بعد. |
| **حقل قديم تم إفراغه** | 🟡 متوسط | لو كانت هناك حقول سابقاً ⇒ أُزيلت لكن الكلاس بقي للتوافق الثنائي. |
| **خطأ تطوير** | 🟢 محتمل | المطوّر بدأ إضافة الميزة ولم يُكمل. |
| **حشو لخداع Reverse Engineers** | 🔴 منخفض | لا يبدو ذلك — لا توجد رموز إضافية حول الكلاس. |

---

## 3. ما الذي قد يأتي في `userRoles` من الخادم؟

استناداً للنمط الموجود في صلاحيات `User` (5 حقول `Cshr_*`)، يُحتمل أن `userRoles` كان يحوي مصفوفة من **العمليات المسموح بها على مستوى أكثر دقّة**، مثل:

```json
"userRoles": {
  "roles": [
    {
      "code": "PAY_COLLECT",
      "name": "تحصيل دفعات",
      "branches": ["B001", "B002"]
    },
    {
      "code": "READ_METER",
      "name": "قراءة عدادات",
      "areas": ["A12", "A13"]
    }
  ]
}
```

أو ربما RBAC أوسع:

```json
"userRoles": {
  "primary": "cashier",
  "secondary": ["printer_admin"],
  "expiresAt": "2030-12-31T23:59:59Z"
}
```

⚠️ **هذا تخمين** — يتطلب التحقق إما عبر:
- Sniffing الإستجابة الفعلية من `https://abbasiy.yedns.org:8057/payment/api/Users/Login`.
- مراجعة سورس الـ Backend (إن توفّر).

---

## 4. التأثير على الإعادة

### 4.1 ماذا نفعل في الإعادة؟

| الخيار | الوصف | التوصية |
|--------|------|---------|
| **A. حذف الحقل** | إزالة `userRoles` من DTO والإستجابة | ❌ يخالف التوافق الخلفي |
| **B. الإحتفاظ كـ `unknown[]`** | TypeScript: `userRoles?: unknown` | 🟡 سريع لكن غير آمن نوعياً |
| **C. تصميم RBAC جديد** | استبدال الصلاحيات `Cshr_*` بنظام أدوار حقيقي | ✅ **مُوصى به** |

### 4.2 تصميم RBAC الموصى به

```ts
// src/types/auth/roles.ts
export type PermissionCode =
  | 'payment:create'
  | 'payment:view'
  | 'reading:create'
  | 'reading:view'
  | 'reading:image:upload'
  | 'customer:location:update'
  | 'report:view'
  | 'report:print'
  | 'password:change';

export interface Role {
  id: string;
  code: 'cashier' | 'reader' | 'supervisor' | 'admin';
  name: string;
  permissions: PermissionCode[];
}

export interface UserRoles {
  primaryRole: Role;
  additionalRoles?: Role[];
  effectivePermissions: PermissionCode[]; // مجموع كل الأدوار
}
```

### 4.3 ترحيل الصلاحيات الحالية إلى RBAC

| الصلاحية القديمة | تصبح في RBAC الجديد |
|-------------------|---------------------|
| `Cshr_AddWebPay == "1"` | `permissions.includes('payment:create')` |
| `Cshr_AddWebRead == "1"` | `permissions.includes('reading:create')` |
| `Cshr_AddWebMtrImg == "1"` | `permissions.includes('reading:image:upload')` |
| `Cshr_AddWebCstUpDate == "1"` | `permissions.includes('customer:location:update')` |
| `Cshr_AddWOtherOpr == "1"` | `permissions.includes('report:view') && includes('report:print')` |

---

## 5. خطر أمني محتمل: Deserialization Side Effect

كون الكلاس فارغاً ⇒ لو حدث **Gson polymorphic exploit** (كما في CVE-2018-19360 لـ FastJSON أو ما يشابه لـ Gson في ظروف خاصة):
- المهاجم يضع `userRoles: {"@class": "java.io.File", ...}` ⇒ في إصدارات قديمة من Gson قد يحدث instantiation غير متوقع.
- **لكن Gson 2.x الحالي لا يدعم polymorphic deserialization إفتراضياً** ⇒ المخاطرة منخفضة عملياً.

التحقق: يجب فحص `build.gradle` للنسخة المستخدمة من Gson.

---

## 6. خلاصة

| النقطة | الحالة |
|--------|--------|
| الحقول | لا يوجد (0) |
| الدوال | لا يوجد (0) |
| الإستخدام الفعلي | فقط في `models/b.java` كحقل deserialization |
| التأثير على المنطق | **صفر** (يُتجاهل تماماً) |
| الإحتفاظ به؟ | ❌ يُحذف في الإعادة، يُستبدل بـ RBAC حقيقي |

---

## 7. مهمة قبل الإعادة (Action Items)

- [ ] **التقاط حركة الشبكة** من تطبيق Production ومراقبة الـ JSON الفعلي للحقل `userRoles`.
- [ ] إذا كان فعلاً فارغاً دائماً ⇒ تأكيد حذفه في الـ DTO الجديد.
- [ ] إذا كان يحوي بيانات ⇒ تصميم النوع المناسب وتحديث هذا الملف.
- [ ] إعادة بناء طبقة الصلاحيات بإستخدام RBAC + Permissions string-based.

---

> **يربط هذا الملف بـ:**
> - `03_data_models/01_user_model.md` (الصلاحيات الحالية المنثورة).
> - `10_rebuild_blueprint/05_security_improvements.md` (تصميم RBAC الجديد).
> - `02_api_contract/02_authentication.md` (الإستجابة التي قد تحوي الحقل).
