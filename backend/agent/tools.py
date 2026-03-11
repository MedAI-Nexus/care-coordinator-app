TOOL_DEFINITIONS = [
    {
        "name": "search_knowledge_base",
        "description": "Search the clinical knowledge base (drug monographs, treatment cycle sheets, patient/caregiver handbooks) for relevant information. Use this when the user asks about medications, side effects, treatment protocols, or general brain tumour care guidance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query describing what information is needed"
                },
                "drug_filter": {
                    "type": "string",
                    "description": "Optional: filter results to a specific drug (e.g. 'tmz', 'bevacizumab', 'lomustine', 'etoposide', 'vorasidenib')",
                },
                "doc_type_filter": {
                    "type": "string",
                    "description": "Optional: filter by document type ('drug_monograph', 'cycle_sheet', 'handbook')",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "save_symptom",
        "description": "Log a symptom reported by the user. Use this whenever the user mentions experiencing a symptom, side effect, or health concern.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symptom": {
                    "type": "string",
                    "description": "The symptom being reported (e.g. 'nausea', 'headache', 'fatigue')"
                },
                "severity": {
                    "type": "string",
                    "enum": ["mild", "moderate", "severe"],
                    "description": "Severity of the symptom"
                },
            },
            "required": ["symptom", "severity"],
        },
    },
    {
        "name": "save_wellbeing_score",
        "description": "Log a wellbeing score (mood, stress level, or caregiver burnout). Use when the user shares how they're feeling emotionally or their stress level.",
        "input_schema": {
            "type": "object",
            "properties": {
                "score_type": {
                    "type": "string",
                    "enum": ["mood", "stress", "zarit_burnout"],
                    "description": "Type of wellbeing score"
                },
                "score": {
                    "type": "number",
                    "description": "Score from 1-10 (1=lowest/worst, 10=highest/best for mood; 1=lowest, 10=highest for stress)"
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes about the score"
                },
            },
            "required": ["score_type", "score"],
        },
    },
    {
        "name": "get_symptom_history",
        "description": "Retrieve the user's recent symptom reports. Use this to identify patterns or prepare for appointments.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back (default 30)",
                    "default": 30,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_wellbeing_history",
        "description": "Retrieve the user's wellbeing score history. Use this to identify mood/stress trends.",
        "input_schema": {
            "type": "object",
            "properties": {
                "score_type": {
                    "type": "string",
                    "enum": ["mood", "stress", "zarit_burnout"],
                    "description": "Type of score to retrieve"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back (default 30)",
                    "default": 30,
                },
            },
            "required": [],
        },
    },
    {
        "name": "save_medication",
        "description": "Save or update a medication for the user. Use during onboarding or when the user mentions a new or changed medication.",
        "input_schema": {
            "type": "object",
            "properties": {
                "drug_name": {
                    "type": "string",
                    "description": "Name of the medication"
                },
                "drug_key": {
                    "type": "string",
                    "description": "Normalized key: 'tmz', 'bevacizumab', 'lomustine', 'etoposide', 'vorasidenib'",
                },
                "dosage": {
                    "type": "string",
                    "description": "Dosage information (e.g. '150mg daily')"
                },
                "cycle_type": {
                    "type": "string",
                    "description": "Treatment cycle type if applicable: 'tmz28' or 'etoposide28'",
                },
                "cycle_start_date": {
                    "type": "string",
                    "description": "Start date of current cycle (YYYY-MM-DD)"
                },
                "cycle_number": {
                    "type": "integer",
                    "description": "Current cycle number"
                },
            },
            "required": ["drug_name"],
        },
    },
    {
        "name": "save_appointment",
        "description": "Save an upcoming appointment. Use during onboarding or when the user mentions an upcoming appointment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "appointment_date": {
                    "type": "string",
                    "description": "Date of appointment (YYYY-MM-DD)"
                },
                "appointment_type": {
                    "type": "string",
                    "description": "Type of appointment (e.g. 'oncologist', 'MRI', 'bloodwork', 'follow-up')"
                },
                "doctor_name": {
                    "type": "string",
                    "description": "Doctor's name"
                },
            },
            "required": ["appointment_date"],
        },
    },
    {
        "name": "generate_appointment_prep",
        "description": "Generate a pre-appointment summary compiling recent symptoms, medication changes, wellbeing trends, and suggested questions for the doctor. Use when the user wants to prepare for an upcoming appointment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "integer",
                    "description": "ID of the appointment to prepare for (optional, uses next upcoming if not specified)"
                },
            },
            "required": [],
        },
    },
]
