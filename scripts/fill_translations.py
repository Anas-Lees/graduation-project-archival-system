"""One-shot helper: fills msgstr entries in en + ar .po files, then compiles."""
import os
import re
import subprocess
import sys

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# English: identity strings (msgstr = msgid). Keeps lazy_gettext working.
# Arabic: translated strings.
TRANSLATIONS = {
    # Forms / generic
    "Full name": "الاسم الكامل",
    "Email": "البريد الإلكتروني",
    "Password": "كلمة المرور",
    "Confirm password": "تأكيد كلمة المرور",
    "Create account": "إنشاء حساب",
    "Remember me": "تذكرني",
    "Sign in": "تسجيل الدخول",
    "Sign out": "تسجيل الخروج",
    "Title": "العنوان",
    "Abstract": "الملخص",
    "Keywords": "الكلمات المفتاحية",
    "Keywords (comma-separated)": "الكلمات المفتاحية (مفصولة بفواصل)",
    "Year": "السنة",
    "Department": "القسم",
    "Categories": "الفئات",
    "Category": "فئة",
    "Project file (PDF or DOCX)": "ملف المشروع (PDF أو DOCX)",
    "Submit for approval": "إرسال للموافقة",
    "Reason": "السبب",
    "Reject": "رفض",
    "Reject…": "رفض…",
    "Approve": "موافقة",
    "Save": "حفظ",
    "Cancel": "إلغاء",
    "Edit": "تعديل",
    "Delete": "حذف",
    "Apply": "تطبيق",
    "Reset": "إعادة تعيين",
    "Role": "الدور",
    "Password (leave blank to keep)": "كلمة المرور (اتركها فارغة للإبقاء عليها)",
    "PDF or DOCX only": "PDF أو DOCX فقط",
    "At least 8 characters.": "8 أحرف على الأقل.",
    "Hold Ctrl/Cmd to select multiple.": "اضغط Ctrl/Cmd لاختيار عدة عناصر.",
    "e.g. accessibility": "مثال: إمكانية الوصول",

    # Nav / chrome
    "Graduation Project Archival System": "نظام أرشفة مشاريع التخرج",
    "Browse": "تصفح",
    "Search": "بحث",
    "Upload": "رفع",
    "My submissions": "مشاريعي",
    "Admin": "الإدارة",
    "Dashboard": "لوحة التحكم",
    "Approvals": "الموافقات",
    "Users": "المستخدمون",
    "Reports": "التقارير",
    "Register": "تسجيل",
    "Skip to main content": "الانتقال إلى المحتوى الرئيسي",
    "Toggle navigation": "تبديل التنقل",
    "Primary navigation": "التنقل الرئيسي",
    "Language switcher": "تبديل اللغة",
    "Arab Open University — Kuwait Branch": "الجامعة العربية المفتوحة — فرع الكويت",
    "About": "حول",
    "Privacy": "الخصوصية",
    "About GPAS": "حول النظام",
    "Privacy notice": "إشعار الخصوصية",
    "Home": "الرئيسية",
    "Go home": "العودة إلى الرئيسية",

    # Home / index
    "Recently added": "أُضيف مؤخراً",
    "Repository statistics": "إحصاءات المستودع",
    "Approved projects": "المشاريع المعتمدة",
    "Departments represented": "الأقسام الممثَّلة",
    "Goals": "الأهداف",
    "Preserve student work that would otherwise be lost.":
        "الحفاظ على أعمال الطلاب التي قد تُفقد لولا ذلك.",
    "Help current students learn from past projects.":
        "مساعدة الطلاب الحاليين على التعلم من مشاريع سابقة.",
    "Support faculty in advising and ensuring originality.":
        "دعم أعضاء هيئة التدريس في الإشراف والتحقق من الأصالة.",
    "Provide administrators with reporting and oversight.":
        "تزويد الإدارة بتقارير وأدوات إشراف.",

    # Browse / search
    "Browse projects": "تصفح المشاريع",
    "Search by title, abstract, keyword…": "ابحث عن طريق العنوان أو الملخص أو الكلمات المفتاحية…",
    "Search query": "نص البحث",
    "Search results": "نتائج البحث",
    "%(num)s result": "%(num)s نتيجة",
    "Any": "الكل",
    "No matching projects.": "لا توجد مشاريع مطابقة.",
    "No projects yet — admins, please approve some submissions.":
        "لا توجد مشاريع بعد — على المسؤولين الموافقة على بعض الطلبات.",
    "Uploaded by": "رُفع بواسطة",
    "by": "بواسطة",

    # Project view
    "Files": "الملفات",
    "Download": "تنزيل",
    "Sign in to download": "سجّل الدخول للتنزيل",
    "No files attached.": "لا توجد ملفات مرفقة.",
    "This project is currently": "هذا المشروع حالياً",
    "and is not publicly visible.": "وغير ظاهر للعموم.",

    # Upload
    "Submit a graduation project": "إرسال مشروع تخرج",
    "Upload project": "رفع مشروع",

    # Auth flows
    "Already have an account?": "هل لديك حساب بالفعل؟",
    "No account?": "ليس لديك حساب؟",
    "Register here": "سجّل هنا",
    "Sign in to GPAS": "تسجيل الدخول إلى GPAS",
    "Create your GPAS account": "أنشئ حسابك في GPAS",
    "Please sign in to continue.": "يرجى تسجيل الدخول للمتابعة.",
    "An account with that email already exists.": "يوجد حساب مسجَّل بهذا البريد بالفعل.",
    "Account created. Check email.log to verify your account.":
        "تم إنشاء الحساب. راجع ملف email.log لتفعيل حسابك.",
    "Welcome back, %(name)s!": "أهلاً بعودتك يا %(name)s!",
    "You have been signed out.": "تم تسجيل خروجك.",
    "Invalid email or password.": "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
    "Verification link expired.": "انتهت صلاحية رابط التحقق.",
    "Invalid verification link.": "رابط تحقق غير صالح.",
    "Email verified! You can now sign in.": "تم تفعيل البريد! يمكنك الآن تسجيل الدخول.",
    "Verify your GPAS account": "فعّل حسابك في GPAS",
    "Welcome to GPAS! Please verify your email by visiting: %(url)s":
        "مرحباً بك في GPAS! يرجى تفعيل بريدك بزيارة: %(url)s",

    # Project workflow messages
    "Project submitted and is pending admin approval.":
        "تم إرسال المشروع وهو بانتظار موافقة الإدارة.",
    "Project approved.": "تمت الموافقة على المشروع.",
    "Project rejected.": "تم رفض المشروع.",
    "A rejection reason is required.": "سبب الرفض مطلوب.",
    "Confirm rejection": "تأكيد الرفض",
    "New project pending approval: %(title)s": "مشروع جديد بانتظار الموافقة: %(title)s",
    "Faculty member %(name)s submitted '%(title)s'. Review at /admin/approvals.":
        "أرسل عضو هيئة التدريس %(name)s مشروع «%(title)s». راجعه على /admin/approvals.",
    "Your project '%(t)s' was approved": "تمت الموافقة على مشروعك «%(t)s»",
    "Your submission is now publicly available in GPAS.":
        "أصبح مشروعك متاحاً للعموم في GPAS.",
    "Your project '%(t)s' was rejected": "تم رفض مشروعك «%(t)s»",
    "Reason: %(r)s": "السبب: %(r)s",

    # Status
    "Pending": "قيد الانتظار",
    "Approved": "معتمَد",
    "Rejected": "مرفوض",
    "Status": "الحالة",
    "Submitted": "مُرسَل",
    "Created": "أُنشئ",
    "Verified": "موثَّق",

    # Admin dashboard / users / reports
    "Admin dashboard": "لوحة الإدارة",
    "Pending approvals": "الموافقات المعلَّقة",
    "Registered users": "المستخدمون المسجَّلون",
    "View reports": "عرض التقارير",
    "Nothing pending. Good job!": "لا توجد طلبات معلَّقة. أحسنت!",
    "Edit user": "تعديل مستخدم",
    "New user": "مستخدم جديد",
    "Delete this user?": "حذف هذا المستخدم؟",
    "User created.": "تم إنشاء المستخدم.",
    "User updated.": "تم تحديث المستخدم.",
    "User deleted.": "تم حذف المستخدم.",
    "Email already in use.": "البريد مستخدم بالفعل.",
    "Password is required for new users.": "كلمة المرور مطلوبة للمستخدمين الجدد.",
    "You cannot delete your own account.": "لا يمكنك حذف حسابك الخاص.",
    "Name": "الاسم",
    "Usage reports": "تقارير الاستخدام",
    "Most viewed projects": "أكثر المشاريع مشاهدةً",
    "Most downloaded projects": "أكثر المشاريع تنزيلاً",
    "Approved projects by department": "المشاريع المعتمدة حسب القسم",
    "Approved projects by year": "المشاريع المعتمدة حسب السنة",
    "Downloads (30d)": "التنزيلات (30 يوماً)",
    "Views (30d)": "المشاهدات (30 يوماً)",
    "Count": "العدد",
    "No data yet.": "لا توجد بيانات بعد.",
    "You have not submitted any projects yet.": "لم تُرسل أي مشاريع بعد.",

    # Errors
    "Page not found.": "الصفحة غير موجودة.",
    "Something went wrong on our side. Please try again.":
        "حدث خطأ من جانبنا. يرجى المحاولة مرة أخرى.",
    "You do not have permission to access this resource.":
        "ليست لديك صلاحية الوصول إلى هذا المورد.",

    # Accessibility / misc
    "Accessibility": "إمكانية الوصول",

    # Roles + role panel
    "Student": "طالب",
    "Doctor": "دكتور",
    "Doctor panel": "لوحة الدكتور",
    "Close": "إغلاق",

    # Project view: video / GitHub / slides
    "Demo video": "فيديو توضيحي",
    "Demo video for": "فيديو توضيحي للمشروع",
    "Your browser does not support embedded video.": "متصفحك لا يدعم تشغيل الفيديو مدمجاً.",
    "Open video": "فتح الفيديو",
    "Source code": "الشيفرة المصدرية",
    "View on GitHub": "عرض على GitHub",
    "Slides": "العرض التقديمي",

    # Upload form: optional fields
    "Project document (PDF or DOCX)": "مستند المشروع (PDF أو DOCX)",
    "Demo video (optional, MP4 / WebM / MOV)": "فيديو توضيحي (اختياري، MP4 / WebM / MOV)",
    "Slides (optional, PPTX / PPT / PDF)": "العرض التقديمي (اختياري، PPTX / PPT / PDF)",
    "GitHub repository (optional)": "مستودع GitHub (اختياري)",
    "MP4, WebM, MOV, or M4V only": "MP4 أو WebM أو MOV أو M4V فقط",
    "PPTX, PPT, or PDF only": "PPTX أو PPT أو PDF فقط",
    "Must be a github.com URL, e.g. https://github.com/user/repo":
        "يجب أن يكون رابط github.com، مثل https://github.com/user/repo",
    "The fields below are optional but recommended for richer demos.":
        "الحقول التالية اختيارية لكنها موصى بها لعرض أكثر ثراءً.",
    "Will play directly on the project page. Up to ~150 MB recommended.":
        "سيُشغَّل مباشرةً على صفحة المشروع. يُفضَّل ألا يتجاوز 150 ميغابايت تقريباً.",

    # Updated workflow notification
    "%(name)s submitted '%(title)s'. Review at /admin/approvals.":
        "أرسل %(name)s مشروع «%(title)s». راجعه على /admin/approvals.",
    "Submissions enter a pending queue and are published once a doctor approves them.":
        "تدخل الطلبات قائمة الانتظار وتُنشَر بعد موافقة الدكتور.",
}

PO_HEADER_RX = re.compile(r'(?s)("Content-Transfer-Encoding: 8bit\\n"\n)')
ENTRY_RX = re.compile(r'(msgid "((?:[^"\\]|\\.)*)"\nmsgstr )""', re.MULTILINE)


def fill(po_path: str, lang: str) -> int:
    with open(po_path, "r", encoding="utf-8") as fh:
        text = fh.read()

    # Set Plural-Forms for ar (6 plural forms is overkill; use simple 2-form)
    text = text.replace('"Language: \\n"', f'"Language: {lang}\\n"')
    text = text.replace(
        '"Plural-Forms: nplurals=INTEGER; plural=EXPRESSION;\\n"',
        '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"',
    )
    if 'Plural-Forms' not in text:
        text = text.replace(
            '"Content-Transfer-Encoding: 8bit\\n"',
            '"Content-Transfer-Encoding: 8bit\\n"\n"Plural-Forms: nplurals=2; plural=(n != 1);\\n"',
            1,
        )

    filled = 0
    missing = []

    def _po_unescape(s: str) -> str:
        return s.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')

    def _po_escape(s: str) -> str:
        return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')

    def _replace(m: re.Match) -> str:
        nonlocal filled
        msgid_escaped = m.group(2)
        msgid = _po_unescape(msgid_escaped)
        if lang == "en":
            translation = msgid
        else:
            translation = TRANSLATIONS.get(msgid)
            if translation is None:
                missing.append(msgid)
                translation = msgid  # fallback so UI still works
        escaped = _po_escape(translation)
        filled += 1
        return f'msgid "{msgid_escaped}"\nmsgstr "{escaped}"'

    new_text = ENTRY_RX.sub(_replace, text)

    with open(po_path, "w", encoding="utf-8") as fh:
        fh.write(new_text)

    if missing and lang == "ar":
        print(f"  WARN: {len(missing)} Arabic translations missing (fell back to English):")
        for m in missing[:10]:
            print(f"    - {m!r}")
    return filled


def main():
    en_po = os.path.join(BASE, "translations", "en", "LC_MESSAGES", "messages.po")
    ar_po = os.path.join(BASE, "translations", "ar", "LC_MESSAGES", "messages.po")
    print(f"Filling EN: {fill(en_po, 'en')} entries")
    print(f"Filling AR: {fill(ar_po, 'ar')} entries")

    pybabel = os.path.join(BASE, "venv", "Scripts", "pybabel.exe")
    for lang in ("en", "ar"):
        r = subprocess.run([pybabel, "compile", "-d", "translations", "-l", lang],
                           cwd=BASE, capture_output=True, text=True)
        print(f"  compile {lang}: {(r.stdout + r.stderr).strip()}")
        if r.returncode:
            sys.exit(r.returncode)
    print("Done.")


if __name__ == "__main__":
    main()
