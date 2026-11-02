from typing import Dict, Any, Optional, List

class PromptBuilder:
    def build(
        self,
        query: str,
        context: str,
        language_code: str,
        holiday_intel: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> dict:
        if language_code == "hinglish":
            lang_instruction = (
                "CRITICAL LANGUAGE RULE: RESPOND IN HINGLISH ONLY (Roman Hindi / Hindi written in English alphabets).\n"
                "Example format: 'Aapke exams aamtaur par... Aap administrative office me confirm kar sakte hain.'\n"
                "STRICT RESTRICTION: Do NOT use Afrikaans, Dutch, German or any other language! Do NOT use Hindi Devanagari script. Use only friendly, conversational Hinglish."
            )
        elif language_code == "hindi":
            lang_instruction = (
                "CRITICAL LANGUAGE RULE: RESPOND IN HINDI ONLY (Devanagari script).\n"
                "Example format: 'नमस्ते! आपके प्रश्न का उत्तर नीचे दिया गया है...'\n"
                "STRICT RESTRICTION: Do NOT use foreign languages or English. Write in clear, respectful Hindi."
            )
        else: # english
            lang_instruction = (
                "CRITICAL LANGUAGE RULE: RESPOND IN ENGLISH ONLY.\n"
                "Write in clear, professional, friendly and accessible English."
            )

        # Student Profile Context
        student_info = ""
        if user_profile:
            name = user_profile.get("name") or "Student"
            course = user_profile.get("course") or "General"
            sem = user_profile.get("semester")
            dept = user_profile.get("department")
            student_info = f"STUDENT PROFILE:\n- Name: {name}\n- Course: {course}\n"
            if sem: student_info += f"- Semester: {sem}\n"
            if dept: student_info += f"- Department: {dept}\n"

        # Conversation History Context (Multi-turn dialogue memory)
        history_block = ""
        if conversation_history:
            history_block = "\n======================================================================\nCONVERSATION HISTORY (Recent turns in this conversation):\n======================================================================\n"
            for turn in conversation_history[-6:]:
                role = turn.get("role", "user").upper()
                content = turn.get("content", "").strip()
                history_block += f"{role}: {content}\n"
            history_block += "======================================================================\nUse this history to maintain seamless context for follow-up questions (e.g. 'Give me an example', 'Explain in detail', 'What about 3NF?').\n"

        # Build Holiday & Admin Announcements section
        holiday_block = ""
        if holiday_intel and holiday_intel.get("is_holiday_query"):
            scenario = holiday_intel.get("scenario")
            target_date = holiday_intel.get("target_date") or holiday_intel.get("date_descriptor") or "the requested date"
            admin_ann = holiday_intel.get("admin_announcement")
            gov_hol = holiday_intel.get("gov_holiday")
            
            holiday_block = f"""
======================================================================
OFFICIAL COLLEGE HOLIDAY & ADMIN ANNOUNCEMENT INTELLIGENCE:
======================================================================
Scenario Detected: {scenario}
Target Date: {target_date}
Admin Confirmed Holiday: {"YES" if holiday_intel.get("admin_confirmed_holiday") else "NO"}
"""
            if admin_ann:
                holiday_block += f"""
[OFFICIAL ADMIN ANNOUNCEMENT FOUND]
- Title: {admin_ann.get('title')}
- Category: {admin_ann.get('category')}
- Published On: {admin_ann.get('published_at')}
- Details: {admin_ann.get('content')}
"""
            if gov_hol:
                holiday_block += f"""
[GOVERNMENT / FESTIVAL CALENDAR]
- Name: {gov_hol.get('name')}
- Type: {gov_hol.get('type')}
- Description: {gov_hol.get('desc')}
"""

            holiday_block += """
MANDATORY RULES FOR HOLIDAY & CLOSURE QUERIES:
1. CASE A (Admin Confirmed Holiday):
   If Scenario is CASE_A, confirm clearly that the college administration has officially announced a holiday for this date. Cite the announcement title and details.
   Example: "Yes! The college administration has officially announced a holiday for 3 November. [Quote notice details]."

2. CASE B (Government/Festival Holiday, but NO college announcement):
   If Scenario is CASE_B, clearly distinguish that while this is a recognized festival/public holiday, NO official college closure announcement has been found in the portal. Remind students NOT to assume a holiday without official college confirmation.
   Example: "Diwali is an officially recognized festival holiday. However, I could not find a confirmed college closure announcement for this date. Please check the college's official notification."

3. CASE C (No announcement available):
   If Scenario is CASE_C, state explicitly that no official college holiday announcement has been found. Instruct students NOT to treat it as a holiday and to follow regular classes.
   Example: "Currently, no official college holiday announcement has been found for tomorrow. Please do not consider it a confirmed holiday."

4. ZERO ASSUMPTIONS:
   NEVER invent a holiday. NEVER assume the college is closed just because of a festival or rumor. Official confirmation must ALWAYS take priority over predictions!
======================================================================
"""
        elif holiday_intel and holiday_intel.get("all_active_announcements"):
            # Provide latest notices for general context
            holiday_block = "\n--- RECENT ACTIVE ADMIN NOTICES ---\n"
            for a in holiday_intel["all_active_announcements"][:3]:
                holiday_block += f"* [{a.get('published_at')}] {a.get('title')}: {a.get('content')}\n"

        has_context = bool(context and context.strip())
        context_block = context if has_context else (
            "[NOTE: No specific college PDF chunk directly matched. Use comprehensive academic knowledge and official announcements above to give a complete, helpful answer.]"
        )

        system_instructions = f"""You are the official Institute AI Assistant — a trustworthy, highly intelligent academic AI assistant with ChatGPT-like conversational capabilities.

{lang_instruction}

PRIMARY SOURCE OF TRUTH & TWO KNOWLEDGE MODES:
1. OFFICIAL COLLEGE INFORMATION:
   - For fees, exam schedules, attendance rules, official holiday announcements, admission deadlines, and institute circulars:
     STRICTLY rely on the Uploaded Official Institute Documents and Admin Announcements provided below.
     NEVER invent or hallucinate college-specific facts, dates, fees, or holiday confirmations.
2. GENERAL ACADEMIC & EDUCATIONAL KNOWLEDGE:
   - For computer science, BCA topics, programming (Python, C, Java, Web Dev), database concepts (DBMS, normalization, SQL), mathematics, study notes, formula derivations, MCQs with explanations, and code debugging:
     Act like an expert professor! Provide simple, easy-to-understand explanations with clear markdown, bullet points, and code blocks even if the exact textbook chapter is not uploaded.

{student_info}
{history_block}
{holiday_block}

GOOGLE-LIKE TYPO TOLERANCE:
Students frequently type with typos or abbreviations (e.g. 'exm', 'syllbus', 'admison', 'kbb', 'semstr'). Intelligently interpret their intent just like Google Search.

TONE & ACCURACY:
Warm, encouraging, structured, accurate, and completely grounded in verified sources. Never fabricate college dates or policies.

RETRIEVED CONTEXT FROM INSTITUTE DOCUMENTS:
{context_block}
"""
        user_prompt = f"STUDENT QUERY:\n{query}"
        
        return {
            "system_instruction": system_instructions,
            "prompt": user_prompt
        }

prompt_builder = PromptBuilder()
