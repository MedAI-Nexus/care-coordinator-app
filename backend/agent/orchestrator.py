import json
from datetime import datetime, timedelta, date
from anthropic import Anthropic
from sqlalchemy.orm import Session

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from models import User, Medication, Appointment, Conversation, SymptomReport, WellbeingScore
from agent.prompts import build_system_prompt
from agent.tools import TOOL_DEFINITIONS

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def get_user_context(db: Session, user_id: int) -> dict:
    """Build user context dict for the system prompt."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}

    medications = db.query(Medication).filter(
        Medication.user_id == user_id, Medication.is_active == True
    ).all()

    appointments = db.query(Appointment).filter(
        Appointment.user_id == user_id,
        Appointment.appointment_date >= date.today().isoformat(),
    ).order_by(Appointment.appointment_date).all()

    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent_symptoms = db.query(SymptomReport).filter(
        SymptomReport.user_id == user_id,
        SymptomReport.reported_at >= seven_days_ago,
    ).order_by(SymptomReport.reported_at.desc()).all()

    return {
        "user": {
            "role": user.role,
            "patient_name": user.patient_name,
            "caregiver_name": user.caregiver_name,
            "diagnosis": user.diagnosis,
            "doctor_name": user.doctor_name,
            "clinic_name": user.clinic_name,
            "onboarding_complete": user.onboarding_complete,
        },
        "medications": [
            {
                "drug_name": m.drug_name,
                "dosage": m.dosage,
                "cycle_type": m.cycle_type,
                "cycle_start_date": m.cycle_start_date,
                "cycle_number": m.cycle_number,
            }
            for m in medications
        ],
        "appointments": [
            {
                "appointment_date": a.appointment_date,
                "appointment_type": a.appointment_type,
                "doctor_name": a.doctor_name,
            }
            for a in appointments
        ],
        "recent_symptoms": [
            {
                "symptom": s.symptom,
                "severity": s.severity,
                "reported_at": s.reported_at.isoformat() if s.reported_at else None,
            }
            for s in recent_symptoms
        ],
    }


def get_conversation_history(db: Session, user_id: int, limit: int = 20) -> list:
    """Get recent conversation messages for context."""
    messages = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    return [{"role": m.role, "content": m.content} for m in messages]


def execute_tool(db: Session, user_id: int, tool_name: str, tool_input: dict) -> str:
    """Execute a tool call and return the result as a string."""

    if tool_name == "search_knowledge_base":
        try:
            from rag.retriever import search
            results = search(
                query=tool_input["query"],
                drug_filter=tool_input.get("drug_filter"),
                doc_type_filter=tool_input.get("doc_type_filter"),
                n_results=5,
            )
            if not results:
                return "No relevant information found in the knowledge base."
            return "\n\n---\n\n".join(
                [f"[Source: {r['source']}]\n{r['content']}" for r in results]
            )
        except Exception as e:
            return f"Knowledge base search error: {str(e)}"

    elif tool_name == "save_symptom":
        # Calculate cycle day if possible
        cycle_day = None
        med = db.query(Medication).filter(
            Medication.user_id == user_id,
            Medication.is_active == True,
            Medication.cycle_start_date.isnot(None),
        ).first()
        if med and med.cycle_start_date:
            try:
                start = datetime.strptime(med.cycle_start_date, "%Y-%m-%d").date()
                cycle_day = (date.today() - start).days % 28 + 1
            except (ValueError, TypeError):
                pass

        report = SymptomReport(
            user_id=user_id,
            symptom=tool_input["symptom"],
            severity=tool_input["severity"],
            cycle_day=cycle_day,
        )
        db.add(report)
        db.commit()
        result = f"Symptom logged: {tool_input['symptom']} (severity: {tool_input['severity']})"
        if cycle_day:
            result += f" on cycle day {cycle_day}"
        return result

    elif tool_name == "save_wellbeing_score":
        score = WellbeingScore(
            user_id=user_id,
            score_type=tool_input["score_type"],
            score=tool_input["score"],
            notes=tool_input.get("notes"),
        )
        db.add(score)
        db.commit()
        return f"Wellbeing score logged: {tool_input['score_type']} = {tool_input['score']}/10"

    elif tool_name == "get_symptom_history":
        days = tool_input.get("days", 30)
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        symptoms = db.query(SymptomReport).filter(
            SymptomReport.user_id == user_id,
            SymptomReport.reported_at >= cutoff,
        ).order_by(SymptomReport.reported_at.desc()).all()

        if not symptoms:
            return f"No symptoms reported in the last {days} days."

        lines = []
        for s in symptoms:
            line = f"- {s.symptom} (severity: {s.severity}"
            if s.cycle_day:
                line += f", cycle day {s.cycle_day}"
            line += f", {s.reported_at.strftime('%Y-%m-%d') if s.reported_at else 'unknown date'})"
            lines.append(line)
        return f"Symptom history (last {days} days):\n" + "\n".join(lines)

    elif tool_name == "get_wellbeing_history":
        days = tool_input.get("days", 30)
        score_type = tool_input.get("score_type")
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        query = db.query(WellbeingScore).filter(
            WellbeingScore.user_id == user_id,
            WellbeingScore.recorded_at >= cutoff,
        )
        if score_type:
            query = query.filter(WellbeingScore.score_type == score_type)
        scores = query.order_by(WellbeingScore.recorded_at.desc()).all()

        if not scores:
            return f"No wellbeing scores recorded in the last {days} days."

        lines = []
        for s in scores:
            line = f"- {s.score_type}: {s.score}/10"
            if s.notes:
                line += f" ({s.notes})"
            line += f" — {s.recorded_at.strftime('%Y-%m-%d') if s.recorded_at else 'unknown'}"
            lines.append(line)
        return f"Wellbeing history (last {days} days):\n" + "\n".join(lines)

    elif tool_name == "save_medication":
        # Check if medication already exists
        existing = db.query(Medication).filter(
            Medication.user_id == user_id,
            Medication.drug_name == tool_input["drug_name"],
            Medication.is_active == True,
        ).first()

        if existing:
            for key in ["drug_key", "dosage", "cycle_type", "cycle_start_date", "cycle_number"]:
                if key in tool_input and tool_input[key] is not None:
                    setattr(existing, key, tool_input[key])
            db.commit()
            return f"Medication updated: {tool_input['drug_name']}"
        else:
            med = Medication(
                user_id=user_id,
                drug_name=tool_input["drug_name"],
                drug_key=tool_input.get("drug_key"),
                dosage=tool_input.get("dosage"),
                cycle_type=tool_input.get("cycle_type"),
                cycle_start_date=tool_input.get("cycle_start_date"),
                cycle_number=tool_input.get("cycle_number"),
            )
            db.add(med)
            db.commit()
            return f"Medication saved: {tool_input['drug_name']}"

    elif tool_name == "save_appointment":
        apt = Appointment(
            user_id=user_id,
            appointment_date=tool_input["appointment_date"],
            appointment_type=tool_input.get("appointment_type"),
            doctor_name=tool_input.get("doctor_name"),
        )
        db.add(apt)
        db.commit()
        return f"Appointment saved: {tool_input['appointment_date']}"

    elif tool_name == "generate_appointment_prep":
        # Find the appointment
        apt_id = tool_input.get("appointment_id")
        if apt_id:
            apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
        else:
            apt = db.query(Appointment).filter(
                Appointment.user_id == user_id,
                Appointment.appointment_date >= date.today().isoformat(),
            ).order_by(Appointment.appointment_date).first()

        if not apt:
            return "No upcoming appointments found."

        # Gather data
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        symptoms = db.query(SymptomReport).filter(
            SymptomReport.user_id == user_id,
            SymptomReport.reported_at >= thirty_days_ago,
        ).order_by(SymptomReport.reported_at.desc()).all()

        meds = db.query(Medication).filter(
            Medication.user_id == user_id, Medication.is_active == True
        ).all()

        scores = db.query(WellbeingScore).filter(
            WellbeingScore.user_id == user_id,
            WellbeingScore.recorded_at >= thirty_days_ago,
        ).order_by(WellbeingScore.recorded_at.desc()).all()

        user = db.query(User).filter(User.id == user_id).first()

        summary_parts = [
            f"## Appointment Preparation Summary",
            f"**Date:** {apt.appointment_date}",
            f"**Type:** {apt.appointment_type or 'General'}",
            f"**Doctor:** {apt.doctor_name or user.doctor_name or 'Not specified'}",
            "",
        ]

        if meds:
            summary_parts.append("### Current Medications")
            for m in meds:
                line = f"- {m.drug_name}"
                if m.dosage:
                    line += f" ({m.dosage})"
                summary_parts.append(line)
            summary_parts.append("")

        if symptoms:
            summary_parts.append("### Symptoms Reported (Last 30 Days)")
            for s in symptoms:
                line = f"- {s.symptom} — severity: {s.severity}"
                if s.cycle_day:
                    line += f" (cycle day {s.cycle_day})"
                line += f" [{s.reported_at.strftime('%Y-%m-%d') if s.reported_at else ''}]"
                summary_parts.append(line)
            summary_parts.append("")

        if scores:
            summary_parts.append("### Wellbeing Scores (Last 30 Days)")
            for sc in scores:
                summary_parts.append(
                    f"- {sc.score_type}: {sc.score}/10 [{sc.recorded_at.strftime('%Y-%m-%d') if sc.recorded_at else ''}]"
                )
            summary_parts.append("")

        summary_parts.append("### Suggested Discussion Points")
        summary_parts.append("- Review any recurring symptoms and their impact on daily life")
        summary_parts.append("- Discuss current medication effectiveness and side effects")
        if any(s.severity == "severe" for s in symptoms):
            summary_parts.append("- Address severe symptoms that were reported")
        summary_parts.append("- Ask about upcoming scans or tests")
        summary_parts.append("- Discuss any concerns about treatment plan")

        summary = "\n".join(summary_parts)

        # Save the prep summary to the appointment
        apt.prep_summary = summary
        db.commit()

        return summary

    return f"Unknown tool: {tool_name}"


async def run_agent(db: Session, user_id: int, user_message: str):
    """Run the agent loop: call Claude, execute tools, return final response.
    Yields text chunks for streaming."""

    # Save user message
    db.add(Conversation(user_id=user_id, role="user", content=user_message))
    db.commit()

    # Build context
    user_context = get_user_context(db, user_id)
    system_prompt = build_system_prompt(user_context)
    history = get_conversation_history(db, user_id)

    messages = history

    # Agent loop
    while True:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Process response
        assistant_text = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                assistant_text += block.text
            elif block.type == "tool_use":
                tool_calls.append(block)

        if tool_calls:
            # Add assistant message with tool use to history
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool and add results
            tool_results = []
            for tool_call in tool_calls:
                result = execute_tool(db, user_id, tool_call.name, tool_call.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})

            # If stop_reason is tool_use, continue the loop
            if response.stop_reason == "tool_use":
                continue

        # Final response — yield text and save
        if assistant_text:
            db.add(Conversation(
                user_id=user_id, role="assistant", content=assistant_text
            ))
            db.commit()

        yield assistant_text
        break
