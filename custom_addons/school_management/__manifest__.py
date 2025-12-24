{
    "name": "School Management",
    "version": "19.0.1.0",
    "category": "Education",
    "summary": "Management of School",
    "author": "Your Name",
    "license": "LGPL-3",
    "depends": ["base"],

    "data": [
        # --------------------
        # SECURITY
        # --------------------
        "security/ir.model.access.csv",

        # --------------------
        # CORE VIEWS (MODELS)
        # --------------------
        "views/student_view.xml",
        "views/teacher_view.xml",
        "views/class_view.xml",

        # --------------------
        # FEES (IMPORTANT ORDER)
        # --------------------
        "views/fees_view.xml",
        "views/fees_payment_view.xml",

        # --------------------
        # EXAMS
        # --------------------
        "views/exam_view.xml",
        "views/exam_result.xml",

        # --------------------
        # REPORTS / DASHBOARDS
        # --------------------
        "views/student_report_view.xml",
        "views/fees_report_view.xml",

        # --------------------
        # MENUS (LAST)
        # --------------------
        "views/school_menu.xml",
    ],

    "application": True,
    "installable": True,
}
