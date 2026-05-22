# MainActivity — الشاشة الرئيسية (لوحة الأزرار)

> **المصدر:** `com.egy.webpaymentapp.Screens.MainActivity`
> **الملف:** `AbbasiyCashiers_RE_Analysis/03_jadx_output/sources/com/egy/webpaymentapp/Screens/MainActivity.java`
> **عدد الأسطر:** 132 سطر
> **الـ Layout:** `R.layout.activity_main`
> **الدور:** Hub رئيسي يعرض 7 أزرار تتحكم رؤيتها صلاحيات المستخدم.

---

## 1. مكوّنات الواجهة

### 1.1 الأزرار السبعة

| المتغير | View ID | الإسم العربي (مُتوقَّع) | المُستهدَف |
|---------|---------|------------------------|------------|
| `q` | `R.id.btnpayment` | إضافة دفعة | `OprationsActivity` (OP_TYP=1) |
| `s` | `R.id.btnpaymentList` | قائمة الدفعات | `WebviewActivity` (paymentList.html) |
| `t` | `R.id.btnReadingList` | قائمة القراءات | `WebviewActivity` (readinglist.html) |
| `u` | `R.id.btn_add_reading` | إضافة قراءة | `OprationsActivity` (OP_TYP=2) |
| `v` | `R.id.btn_cust_loc` | تحديث موقع الزبون | `OprationsActivity` (OP_TYP=3) |
| `w` | `R.id.btnUserReports` | تقارير المستخدم | `WebviewActivity` |
| `r` | `R.id.btnchangepass` | تغيير كلمة المرور | `ChangePassActivity` |

### 1.2 الـ TextView
| المتغير | View ID | المحتوى |
|---------|---------|---------|
| `y` | `R.id.txt_name` | إسم المستخدم (`User.Username` من `o()`) |

---

## 2. مصفوفة الصلاحيات (Permissions Matrix)

| الصلاحية في `User` | الإسم في `User.java` | Getter | الأزرار المتأثرة |
|---------------------|----------------------|--------|------------------|
| `Cshr_AddWebPay == "1"` | `i` | `d()` | `q` (btnpayment) + `s` (btnpaymentList) |
| `Cshr_AddWebRead == "1"` | `j` | `e()` | `u` (btn_add_reading) + `t` (btnReadingList) |
| `Cshr_AddWebCstUpDate == "1"` | `l` | `b()` | `v` (btn_cust_loc) |
| `Cshr_AddWOtherOpr == "1"` | `r` | `a()` | `w` (btnUserReports) |
| (دائماً مرئي) | — | — | `r` (btnchangepass) |

### 2.1 الشيفرة الفعلية (السطور 80-107)

```java
// الدفعات + قائمة الدفعات
if (user == null || TextUtils.isEmpty(user.d()) || !user.d().equals("1")) {
  q.setVisibility(8);   // GONE
  s.setVisibility(8);
} else {
  q.setVisibility(0);   // VISIBLE
  s.setVisibility(0);
}

// القراءات + قائمة القراءات
if (user == null || TextUtils.isEmpty(user.e()) || !user.e().equals("1")) {
  u.setVisibility(8);
  t.setVisibility(8);
} else {
  u.setVisibility(0);
  t.setVisibility(0);
}

// موقع الزبون
if (user == null || TextUtils.isEmpty(user.b()) || !user.b().equals("1")) {
  v.setVisibility(8);
} else {
  v.setVisibility(0);
}

// التقارير
if (user == null || TextUtils.isEmpty(user.a()) || !user.a().equals("1")) {
  w.setVisibility(8);
} else {
  w.setVisibility(0);
}
```

### 2.2 الملاحظات على المنطق
- **`TextUtils.isEmpty()`** يفحص null + empty.
- **`.equals("1")`** صارم — أي قيمة أخرى ("yes"، "true"، " 1") تُعتبر `false`.
- **`setVisibility(8) = GONE`**, **`setVisibility(0) = VISIBLE`** — لا يستخدم `INVISIBLE`.
- ⚠️ **الزر `btnchangepass`** ليس له فحص ⇒ دائماً مرئي حتى لو كان المستخدم بلا أي صلاحيات.

---

## 3. ربط النقرات (Click Listeners)

```java
this.s.setOnClickListener(new h(this));   // paymentList → WebviewActivity
this.t.setOnClickListener(new i(this));   // readingList → WebviewActivity
this.r.setOnClickListener(new j(this));   // changePass → ChangePassActivity
this.q.setOnClickListener(new k(this));   // payment → OprationsActivity (OP_TYP=1)
this.u.setOnClickListener(new l(this));   // addReading → OprationsActivity (OP_TYP=2)
this.v.setOnClickListener(new m(this));   // custLoc → OprationsActivity (OP_TYP=3)
this.w.setOnClickListener(new n(this));   // userReports → WebviewActivity
```

⚠️ سبع كلاسات منفصلة `h, i, j, k, l, m, n` (lambdas مُفكَّكة عبر JADX). كان يمكن دمجها في `OnClickListener` واحد مع `switch(view.getId())`.

---

## 4. الـ ActionBar Setup

```java
r().k(false);  // setDisplayShowTitleEnabled(false)
r().j(true);   // setDisplayHomeAsUpEnabled(true)
r().h(true);   // setDisplayHomeButtonEnabled(true)
r().i(true);   // setDisplayShowHomeEnabled(true)
```

نتيجة: **لا توجد عنوان النص**، فقط زر `Home` مع رمز السهم.

---

## 5. زر الرجوع (Back Button)

### 5.1 `onBackPressed()` (السطور 57-60)
```java
@Override
public void onBackPressed() {
  w();   // ⇒ alertDialog الخروج
}
```

### 5.2 `u()` (الأيقونة Home في ActionBar)
```java
@Override
public boolean u() {
  w();
  return true;
}
```

### 5.3 `w()` — الحوار (السطور 49-55)
```java
private void w() {
  AlertDialog.Builder builder = new AlertDialog.Builder(this);
  builder.setMessage(R.string.Exit_From_System);
  builder.setPositiveButton(R.string.lbl_yes, new a());    // → finishAffinity()
  builder.setNegativeButton(R.string.lbl_no, new b(this));  // → cancel
  builder.show();
}
```

⇒ المستخدم لا يستطيع الخروج من التطبيق بدون تأكيد ⇒ **سلوك جيد للأمن**.

### 5.4 `a.onClick()` (السطور 27-35)
```java
public void onClick(DialogInterface dialogInterface, int i) {
  MainActivity.this.finishAffinity();   // إغلاق كل الأنشطة في الـ Task
}
```

⚠️ **ملاحظة:** `finishAffinity()` يُغلق التطبيق لكن **لا يُسجِّل الخروج**:
- `User` يبقى محفوظاً في SharedPrefs.
- عند فتح التطبيق مرة أخرى ⇒ LoginActivity تقرأ `User.f()` وتعبئ الحقول تلقائياً.
- **لا توجد آلية Logout صريحة** في التطبيق!

---

## 6. لا يوجد Logout — أكبر عيب أمني

| الإستفسار | الإجابة من الكود |
|----------|------------------|
| هل يوجد زر Logout؟ | ❌ لا |
| كيف يخرج المستخدم من الجلسة؟ | لا يستطيع — إلا بمسح بيانات التطبيق يدوياً |
| هل ينتهي الـ Token؟ | لا — لا يوجد expiration |
| ماذا لو سرق شخص الهاتف؟ | يصل لكل بيانات الزبائن + الإيصالات |

**التوصية الحرجة في الإعادة:**
- إضافة زر Logout صريح.
- JWT مع expiration قصير (15 دقيقة) + Refresh Token (يومين).
- Inactivity timeout (5 دقائق ⇒ قفل تلقائي).
- Biometric/PIN قفل عند فتح التطبيق.

---

## 7. السيناريوهات (Edge Cases)

| السيناريو | السلوك الحالي | المُتوقَّع |
|-----------|--------------|----------|
| `User == null` | كل الأزرار GONE ⇒ فقط changePass + اسم فارغ | إعادة توجيه إلى LoginActivity |
| الكل صلاحيات = `"0"` | فقط changePass مرئي | عرض رسالة "لا صلاحيات" |
| الكل = `"1"` | كل الأزرار مرئية | ✅ صحيح |
| `Username` فارغ | TextView فارغ | عرض fallback |
| Token منتهي على الخادم | الأزرار تظهر لكن أي إستدعاء يفشل | فحص دوري للـ Token |

---

## 8. تدفُّق المستخدم النموذجي

```text
After Login Success:
       ↓
MainActivity opens
       ↓
خوارزمية الـ visibility ⇒ تقرر أي أزرار تظهر
       ↓
المستخدم يضغط زراً
       ↓
┌─────────────────────────────────────────┐
│ Click on btnpayment (q):                 │
│   Intent(MainActivity, OprationsActivity)│
│     .putExtra("OP_TYP", 1)               │
│                                          │
│ Click on btn_add_reading (u):            │
│   Intent(MainActivity, OprationsActivity)│
│     .putExtra("OP_TYP", 2)               │
│                                          │
│ Click on btn_cust_loc (v):               │
│   Intent(MainActivity, OprationsActivity)│
│     .putExtra("OP_TYP", 3)               │
│                                          │
│ Click on btnpaymentList (s):             │
│   Intent(MainActivity, WebviewActivity) │
│     .putExtra("URL", "paymentList.html")│
│                                          │
│ Click on btnReadingList (t):             │
│   Intent(MainActivity, WebviewActivity) │
│     .putExtra("URL", "readinglist.html")│
│                                          │
│ Click on btnUserReports (w):             │
│   Intent(MainActivity, WebviewActivity) │
│     .putExtra("URL", user.webview_url)  │
│                                          │
│ Click on btnchangepass (r):              │
│   Intent(MainActivity, ChangePassActivity)│
└─────────────────────────────────────────┘
```

---

## 9. مقارنة بالإعادة (React Native)

```tsx
// src/screens/MainScreen.tsx
const MainScreen = () => {
  const { user } = useAuth();
  const navigation = useNavigation();
  
  const tiles = [
    { id: 'payment',     icon: '💰', label: 'إضافة دفعة',    show: user.permissions.addWebPayment,   onPress: () => navigation.navigate('Operations', { type: 'PAYMENT' }) },
    { id: 'paymentList', icon: '📋', label: 'قائمة الدفعات', show: user.permissions.addWebPayment,   onPress: () => navigation.navigate('PaymentList') },
    { id: 'reading',     icon: '📊', label: 'إضافة قراءة',   show: user.permissions.addWebReading,   onPress: () => navigation.navigate('Operations', { type: 'READING' }) },
    { id: 'readingList', icon: '📈', label: 'قائمة القراءات', show: user.permissions.addWebReading,   onPress: () => navigation.navigate('ReadingList') },
    { id: 'location',    icon: '📍', label: 'موقع الزبون',   show: user.permissions.updateCustomerLocation, onPress: () => navigation.navigate('Operations', { type: 'LOCATION' }) },
    { id: 'reports',     icon: '📈', label: 'التقارير',      show: user.permissions.doOtherOperations, onPress: () => navigation.navigate('Reports') },
    { id: 'changePass',  icon: '🔑', label: 'كلمة المرور',   show: true, onPress: () => navigation.navigate('ChangePassword') },
    { id: 'logout',      icon: '🚪', label: 'تسجيل الخروج', show: true, onPress: handleLogout }, // ← جديد!
  ];

  return (
    <View>
      <Header username={user.username} />
      <FlatList
        data={tiles.filter(t => t.show)}
        numColumns={2}
        renderItem={({ item }) => <TileButton {...item} />}
      />
    </View>
  );
};
```

---

## 10. خلاصة المخاطر

| الخطر | الشدة | الحلّ |
|------|------|-------|
| لا Logout | 🔴 حرج | إضافة زر مع clear-storage |
| Token دائم | 🔴 حرج | JWT expiring |
| `finishAffinity()` لا يمسح | 🟡 متوسط | استبدالها بـ logout صحيح |
| كل الأزرار تستخدم نفس الـ View pattern | 🟢 minor | الإعادة بـ FlatList |
| رسائل خطأ صلاحيات ضعيفة | 🟢 minor | UI feedback أفضل |

---

> **يربط هذا الملف بـ:**
> - `03_data_models/01_user_model.md` (الصلاحيات).
> - `04_screens_flow/04_operations_screen.md` (الـ OP_TYP).
> - `04_screens_flow/05_webview_screen.md` (WebView).
> - `10_rebuild_blueprint/06_ui_modernization.md` (التحديث).
