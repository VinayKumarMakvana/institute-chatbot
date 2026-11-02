from datetime import datetime, date, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import LiveUpdateDB
import logging

logger = logging.getLogger(__name__)

# Official National, Rajasthan State & Major Festival Public Holidays for 2026 - 2027
OFFICIAL_PUBLIC_HOLIDAYS: Dict[str, Dict[str, str]] = {
    # 2026
    "2026-01-26": {"name": "Republic Day", "type": "National Gazetted Holiday", "desc": "Official national celebration"},
    "2026-03-04": {"name": "Maha Shivratri", "type": "Gazetted Festival Holiday", "desc": "Religious public holiday"},
    "2026-03-24": {"name": "Holi / Dhulandi", "type": "Gazetted Festival Holiday", "desc": "Major state & national festival"},
    "2026-03-30": {"name": "Rajasthan Day", "type": "Rajasthan State Observance", "desc": "Statehood day"},
    "2026-04-14": {"name": "Dr. B.R. Ambedkar Jayanti", "type": "National Gazetted Holiday", "desc": "Public observance"},
    "2026-04-17": {"name": "Mahavir Jayanti", "type": "Gazetted Public Holiday", "desc": "Religious public holiday"},
    "2026-04-21": {"name": "Ram Navami", "type": "Gazetted Festival Holiday", "desc": "Festival observance"},
    "2026-05-01": {"name": "International Workers' Day / May Day", "type": "Public Holiday", "desc": "Public holiday"},
    "2026-06-17": {"name": "Eid-ul-Adha (Bakrid)", "type": "Gazetted Public Holiday", "desc": "Religious public holiday"},
    "2026-07-29": {"name": "Muharram", "type": "Gazetted Public Holiday", "desc": "Religious public holiday"},
    "2026-08-15": {"name": "Independence Day", "type": "National Gazetted Holiday", "desc": "Official national holiday"},
    "2026-08-28": {"name": "Raksha Bandhan", "type": "State Festival Holiday", "desc": "Festival observance"},
    "2026-09-04": {"name": "Janmashtami", "type": "Gazetted Festival Holiday", "desc": "Religious festival"},
    "2026-10-02": {"name": "Mahatma Gandhi Jayanti", "type": "National Gazetted Holiday", "desc": "Official national holiday"},
    "2026-10-20": {"name": "Dussehra / Vijayadashami", "type": "National Gazetted Holiday", "desc": "Major festival holiday"},
    "2026-11-08": {"name": "Diwali / Deepawali", "type": "National Festival Holiday", "desc": "Major festival holiday"},
    "2026-11-09": {"name": "Govardhan Puja", "type": "State Festival Holiday", "desc": "Festival holiday"},
    "2026-11-10": {"name": "Bhai Dooj", "type": "Festival Observance", "desc": "Festival holiday"},
    "2026-11-24": {"name": "Guru Nanak Jayanti", "type": "Gazetted Public Holiday", "desc": "Religious public holiday"},
    "2026-12-25": {"name": "Christmas Day", "type": "National Gazetted Holiday", "desc": "Official public holiday"},
    # 2027
    "2027-01-26": {"name": "Republic Day", "type": "National Gazetted Holiday", "desc": "Official national celebration"},
    "2027-03-22": {"name": "Holi / Dhulandi", "type": "Gazetted Festival Holiday", "desc": "Major festival holiday"},
    "2027-04-14": {"name": "Dr. B.R. Ambedkar Jayanti", "type": "National Gazetted Holiday", "desc": "Public observance"},
    "2027-08-15": {"name": "Independence Day", "type": "National Gazetted Holiday", "desc": "Official national holiday"},
    "2027-10-02": {"name": "Mahatma Gandhi Jayanti", "type": "National Gazetted Holiday", "desc": "Official national holiday"},
    "2027-10-29": {"name": "Diwali / Deepawali", "type": "National Festival Holiday", "desc": "Major festival holiday"},
    "2027-12-25": {"name": "Christmas Day", "type": "National Gazetted Holiday", "desc": "Official public holiday"},
}

# Map common festival names to specific dates
FESTIVAL_NAME_TO_DATE: Dict[str, str] = {
    "diwali": "2026-11-08",
    "deepawali": "2026-11-08",
    "govardhan puja": "2026-11-09",
    "bhai dooj": "2026-11-10",
    "guru nanak jayanti": "2026-11-24",
    "christmas": "2026-12-25",
    "republic day": "2026-01-26",
    "holi": "2026-03-24",
    "dhulandi": "2026-03-24",
    "shivratri": "2026-03-04",
    "maha shivratri": "2026-03-04",
    "rajasthan day": "2026-03-30",
    "ambedkar jayanti": "2026-04-14",
    "ram navami": "2026-04-21",
    "eid": "2026-06-17",
    "bakrid": "2026-06-17",
    "independence day": "2026-08-15",
    "raksha bandhan": "2026-08-28",
    "rakhi": "2026-08-28",
    "janmashtami": "2026-09-04",
    "gandhi jayanti": "2026-10-02",
    "dussehra": "2026-10-20",
    "vijayadashami": "2026-10-20",
}

HOLIDAY_QUERY_KEYWORDS = {
    "holiday", "holidays", "chutti", "chhutti", "chuti", "closed", "closure",
    "band", "off", "leave", "open", "khula", "chalega", "working day",
    "festival", "tyohar", "notice", "alert", "announcement", "circular"
}

CLOSURE_AFFIRMATIVE_KEYWORDS = {
    "holiday", "chutti", "chhutti", "chuti", "closed", "closure", "band",
    "off", "leave", "suspended", "suspension", "no classes", "avsar par",
    "remain closed", "will be closed"
}

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

class HolidayService:
    def parse_target_date(self, query: str, ref_dt: Optional[datetime] = None) -> Tuple[Optional[date], Optional[str]]:
        """Parses exact or relative dates from natural language query."""
        if not ref_dt:
            # Anchor reference date to system current date
            ref_dt = datetime.now()
            
        q = query.lower()
        
        # 1. Relative dates
        if re.search(r'\b(tomorrow|kal|kl)\b', q) and not re.search(r'\byesterday\b', q):
            target = ref_dt.date() + timedelta(days=1)
            return target, "tomorrow"
        if re.search(r'\b(today|aaj)\b', q):
            return ref_dt.date(), "today"
        if re.search(r'\b(day after tomorrow|parso|parson)\b', q):
            target = ref_dt.date() + timedelta(days=2)
            return target, "day after tomorrow"

        # 2. Explicit date pattern (e.g. '3 november', '3rd nov', '15 august 2026')
        m = re.search(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+([a-zA-Z]+)(?:\s+(\d{4}))?\b', q)
        if m:
            day = int(m.group(1))
            m_str = m.group(2).lower()
            year = int(m.group(3)) if m.group(3) else ref_dt.year
            for k, val in MONTH_MAP.items():
                if m_str.startswith(k):
                    try:
                        parsed = date(year, val, day)
                        return parsed, f"{day} {k.capitalize()} {year}"
                    except ValueError:
                        pass

        # 3. Reverse pattern ('november 3', 'nov 3rd')
        m2 = re.search(r'\b([a-zA-Z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s+(\d{4}))?\b', q)
        if m2:
            m_str = m2.group(1).lower()
            day = int(m2.group(2))
            year = int(m2.group(3)) if m2.group(3) else ref_dt.year
            for k, val in MONTH_MAP.items():
                if m_str.startswith(k):
                    try:
                        parsed = date(year, val, day)
                        return parsed, f"{day} {k.capitalize()} {year}"
                    except ValueError:
                        pass

        # 4. Festival name lookup
        for fest, d_str in FESTIVAL_NAME_TO_DATE.items():
            if fest in q:
                try:
                    parsed = datetime.strptime(d_str, "%Y-%m-%d").date()
                    return parsed, fest.title()
                except ValueError:
                    pass

        return None, None

    def is_holiday_query(self, query: str) -> bool:
        """Determines if the query is inquiring about holidays, closures, or notices."""
        tokens = set(re.findall(r'[a-zA-Z0-9]+', query.lower()))
        if tokens.intersection(HOLIDAY_QUERY_KEYWORDS):
            return True
        for fest in FESTIVAL_NAME_TO_DATE.keys():
            if fest in query.lower():
                return True
        return False

    async def get_active_admin_announcements(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Fetches active, published, non-expired announcements from the database."""
        now = datetime.utcnow()
        result = await db.execute(
            select(LiveUpdateDB).where(
                LiveUpdateDB.status == "PUBLISHED",
                LiveUpdateDB.is_deleted == False
            ).order_by(LiveUpdateDB.published_at.desc())
        )
        updates = result.scalars().all()
        active = []
        for u in updates:
            if u.expiry_date and u.expiry_date < now:
                continue # Expired announcements must not be treated as active
            active.append({
                "id": u.id,
                "title": u.title,
                "content": u.content,
                "category": u.category or "General",
                "priority": u.priority,
                "published_at": u.published_at.strftime("%d-%b-%Y %H:%M") if u.published_at else "Recently",
                "published_dt": u.published_at
            })
        return active

    async def check_holidays(self, query: str, db: AsyncSession, ref_dt: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Executes complete verification pipeline:
        1. Identifies target date / festival
        2. Scans active admin announcements
        3. Scans official government & festival calendar
        4. Categorizes into CASE_A, CASE_B, or CASE_C with strict accuracy rules
        """
        is_query_related = self.is_holiday_query(query)
        target_date, date_desc = self.parse_target_date(query, ref_dt)
        
        active_announcements = await self.get_active_admin_announcements(db)
        
        target_date_str = target_date.strftime("%d %B %Y") if target_date else None
        target_iso = target_date.strftime("%Y-%m-%d") if target_date else None
        
        # Check Government & Festival calendar
        gov_holiday = None
        if target_iso and target_iso in OFFICIAL_PUBLIC_HOLIDAYS:
            gov_holiday = OFFICIAL_PUBLIC_HOLIDAYS[target_iso]
        
        # Check Admin Announcements for confirmation
        admin_matching_announcement = None
        admin_confirmed_holiday = False
        
        for ann in active_announcements:
            text_corpus = f"{ann['title']} {ann['content']}".lower()
            
            # Check date match
            date_matches = False
            if target_date:
                # Match day number and month
                day_num = str(target_date.day)
                month_name = target_date.strftime("%B").lower()
                month_short = target_date.strftime("%b").lower()
                if (day_num in text_corpus and (month_name in text_corpus or month_short in text_corpus)) or (target_iso in text_corpus):
                    date_matches = True
            
            # Check if announcement title/content matches query keywords or general holiday category
            is_holiday_ann = ann["category"].lower() in ["holiday", "closure", "urgent"] or any(
                w in text_corpus for w in CLOSURE_AFFIRMATIVE_KEYWORDS
            )
            
            if date_matches and is_holiday_ann:
                admin_matching_announcement = ann
                admin_confirmed_holiday = True
                break
            elif not target_date and is_holiday_ann and any(w in query.lower() for w in ["chutti", "holiday", "closed"]):
                # If student asks generally "chutti ka notice aaya hai kya?", link the latest holiday announcement
                admin_matching_announcement = ann
                admin_confirmed_holiday = True
                break

        # Determine Scenario
        if admin_confirmed_holiday:
            scenario = "CASE_A" # Admin has officially announced a holiday
        elif gov_holiday:
            scenario = "CASE_B" # Recognized festival/public holiday, but no official college closure circular
        else:
            scenario = "CASE_C" # No announcement / normal working day

        return {
            "is_holiday_query": is_query_related,
            "target_date": target_date_str,
            "target_date_iso": target_iso,
            "date_descriptor": date_desc,
            "scenario": scenario,
            "admin_confirmed_holiday": admin_confirmed_holiday,
            "admin_announcement": admin_matching_announcement,
            "all_active_announcements": active_announcements[:5],
            "gov_holiday": gov_holiday
        }

holiday_service = HolidayService()

