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
    "%(num)s result": ("%(num)s نتيجة", "%(num)s نتائج"),
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

    # Hero / home
    "Faculty of Computer Studies — AOU Kuwait": "كلية الدراسات الحاسوبية — الجامعة العربية المفتوحة، الكويت",
    "Preserve and discover graduation projects.": "احفظ مشاريع التخرج واكتشفها.",
    "A bilingual digital archive that lets students publish, doctors supervise, and the next generation learn from every graduation project the university produces.":
        "أرشيف رقمي ثنائي اللغة يتيح للطلاب النشر، وللدكاترة الإشراف، وللأجيال القادمة التعلم من كل مشروع تخرج تنتجه الجامعة.",
    "A bilingual digital repository preserving the graduation projects of the Faculty of Computer Studies at the Arab Open University — Kuwait Branch.":
        "مستودع رقمي ثنائي اللغة يحفظ مشاريع تخرج كلية الدراسات الحاسوبية بالجامعة العربية المفتوحة — فرع الكويت.",
    "A bilingual digital repository for graduation projects at Arab Open University — Kuwait Branch.":
        "مستودع رقمي ثنائي اللغة لمشاريع التخرج في الجامعة العربية المفتوحة — فرع الكويت.",
    "Search by title, keyword, year…": "ابحث بالعنوان أو الكلمة المفتاحية أو السنة…",
    "Browse projects": "تصفح المشاريع",
    "Create account": "إنشاء حساب",
    "Submit a project": "تقديم مشروع",
    "Illustration of a digital archive": "رسم توضيحي لأرشيف رقمي",
    "Open": "فتح",
    "approved projects": "مشاريع معتمدة",
    "departments": "أقسام",
    "academic years archived": "سنوات أكاديمية مؤرشفة",
    "Open access for the AOU community": "وصول مفتوح لمجتمع الجامعة",
    "Browse by topic": "تصفح حسب الموضوع",
    "Popular categories": "الفئات الرائجة",
    "See all": "عرض الكل",
    "project": "مشروع",
    "projects": "مشاريع",
    "Latest work": "أحدث المشاريع",
    "All projects": "جميع المشاريع",
    "No projects yet — once a doctor approves submissions they appear here.":
        "لا توجد مشاريع بعد — ستظهر هنا حالما يوافق الدكتور على الطلبات.",
    "Years archived": "السنوات المؤرشفة",
    "WCAG 2.1 conformance": "التوافق مع WCAG 2.1",
    "Graduation Project Archive": "أرشيف مشاريع التخرج",

    # Browse polish
    "All work": "كل المشاريع",
    "Discover": "اكتشف",
    "Apply filters": "تطبيق الفلاتر",
    "See all projects": "عرض جميع المشاريع",
    "Video": "فيديو",
    "GitHub": "GitHub",

    # Project view polish
    "Cite this work": "اقتبس هذا العمل",
    "Copy citation": "نسخ الاقتباس",
    "Copied!": "تم النسخ!",
    "Graduation Project Archival System, Arab Open University — Kuwait Branch.":
        "نظام أرشفة مشاريع التخرج، الجامعة العربية المفتوحة — فرع الكويت.",

    # Upload polish
    "New submission": "طلب جديد",
    "Optional, recommended": "اختياري، موصى به",
    "Adding a thumbnail, video, slides, and GitHub link makes the project page richer.":
        "إضافة صورة مصغرة وفيديو وعرض تقديمي ورابط GitHub يجعل صفحة المشروع أكثر ثراءً.",
    "Thumbnail image (optional, JPG / PNG / WebP)": "صورة مصغرة (اختياري، JPG / PNG / WebP)",
    "Images only (JPG, PNG, WebP, SVG)": "الصور فقط (JPG أو PNG أو WebP أو SVG)",
    "Used as the cover on cards and the project page. 16:9 ratio looks best.":
        "تُستخدم كغلاف على البطاقات وصفحة المشروع. النسبة 16:9 هي الأفضل.",
    "Plays directly on the project page. Up to ~150 MB recommended.":
        "يُشغَّل مباشرةً على صفحة المشروع. يُفضَّل ألا يتجاوز 150 ميغابايت تقريباً.",
    "start typing — popular keywords appear as you go":
        "ابدأ الكتابة — تظهر الكلمات الرائجة أثناء الإدخال",
    "Tip: pick from the most-used keywords below to improve discoverability.":
        "نصيحة: اختر من الكلمات الرائجة أدناه لتحسين الاكتشاف.",
    "Most-used keywords": "الكلمات الأكثر استخداماً",
    "No suggestions yet — be the first to add keywords.":
        "لا توجد اقتراحات بعد — كن أول من يضيف كلمات.",

    # Footer
    "Explore": "استكشاف",
    "Account": "الحساب",
    "Standards": "المعايير",
    "WCAG 2.1 Level AA accessibility": "إمكانية وصول WCAG 2.1 المستوى AA",
    "Bilingual EN / AR with full RTL support": "ثنائي اللغة EN / AR مع دعم كامل لاتجاه RTL",
    "Bilingual EN / AR with full RTL support.": "ثنائي اللغة EN / AR مع دعم كامل لاتجاه RTL.",
    "Built for TM471 Graduation Project": "صُمِّم لمشروع التخرج TM471",

    # Auth pages additions
    "Welcome to GPAS": "أهلاً بك في GPAS",
    "Welcome back": "أهلاً بعودتك",
    "Sign in to GPAS.": "سجّل الدخول إلى GPAS.",
    "Join the AOU graduation project archive.": "انضم إلى أرشيف مشاريع تخرج الجامعة.",
    "Submit your own graduation project for archival.": "أرسل مشروع تخرجك ليُحفظ في الأرشيف.",
    "Browse and learn from past student work.": "تصفح وتعلَّم من أعمال الطلاب السابقة.",
    "WCAG 2.1 AA accessible.": "متوافق مع WCAG 2.1 AA لإمكانية الوصول.",
    "Demo accounts:": "حسابات تجريبية:",
    "All new accounts default to Student. A doctor can promote your role from the admin panel.":
        "جميع الحسابات الجديدة تكون افتراضياً «طالب»، ويمكن للدكتور ترقية الدور من لوحة الإدارة.",
    "Access your submissions, track approval status, and download archived graduation projects.":
        "اطّلع على طلباتك، وتابع حالة الموافقة، ونزّل مشاريع التخرج المؤرشفة.",

    # Admin / approvals additions
    "Preview": "معاينة",
    "Review pending": "مراجعة المعلَّق",
    "Manage users": "إدارة المستخدمين",
    "Back to dashboard": "العودة إلى لوحة التحكم",
    "Explain what the student should fix…": "اشرح ما الذي يجب أن يُصلحه الطالب…",

    # My submissions additions
    "Your work": "أعمالك",
    "Submit your first project": "قدّم مشروعك الأول",
    "View": "عرض",

    # Upload additions
    "Pick all that apply.": "اختر كل ما ينطبق.",
    "Categories": "الفئات",

    # Project view additions
    "Share": "مشاركة",
    "Print": "طباعة",
    "Print this page": "طباعة هذه الصفحة",
    "Copy share link": "نسخ رابط المشاركة",
    "Link copied!": "تم نسخ الرابط!",
}

def fill(po_path: str, lang: str) -> int:
    """Read PO with Babel, set translations from our dict, drop fuzzy flags."""
    from babel.messages.pofile import read_po, write_po

    with open(po_path, "rb") as fh:
        catalog = read_po(fh)

    catalog.language_team = lang
    if lang == "ar":
        catalog._plural_expr = "(n != 1)"

    filled = 0
    missing = []
    for msg in catalog:
        if not msg.id:  # header
            continue
        is_plural = isinstance(msg.id, (list, tuple))
        msgid = msg.id[0] if is_plural else msg.id

        if lang == "en":
            # Identity translation. Plurals: use singular for [0], plural for [1+]
            if is_plural:
                msg.string = tuple(msg.id)
            else:
                msg.string = msgid
            msg.flags = {f for f in msg.flags if f != "fuzzy"}
            filled += 1
            continue

        # AR / other
        new_str = TRANSLATIONS.get(msgid)
        if new_str is None:
            if "fuzzy" in msg.flags:
                msg.flags = {f for f in msg.flags if f != "fuzzy"}
                if is_plural:
                    msg.string = ("",) * len(msg.id)
                else:
                    msg.string = ""
            if not msg.string or (is_plural and not any(msg.string)):
                missing.append(msgid)
            continue

        if is_plural:
            # If the translation dict has a tuple/list, use it; else mirror singular for both forms
            if isinstance(new_str, (list, tuple)):
                msg.string = tuple(new_str)
            else:
                msg.string = (new_str,) * len(msg.id)
        else:
            msg.string = new_str
        msg.flags = {f for f in msg.flags if f != "fuzzy"}
        filled += 1

    with open(po_path, "wb") as fh:
        write_po(fh, catalog, sort_output=False, ignore_obsolete=True)

    if missing and lang == "ar":
        # Quietly count — not all paragraphs need AR copies
        print(f"  ({len(missing)} long descriptive strings still EN-only — fine for now)")
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
