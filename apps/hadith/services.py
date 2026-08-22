"""
Service helper for Hadith API (Fawaz Ahmed Hadith Repository on jsDelivr CDN).
Provides fast, permanent access to major Hadith collections and Daily Hadith.
"""
import json
import logging
import random
import urllib.request
from datetime import date

logger = logging.getLogger(__name__)

HADITH_COLLECTIONS = [
    {
        "id": "bukhari",
        "api_name": "bukhari",
        "name": "Sahih al-Bukhari",
        "arabic_name": "صحيح البخاري",
        "author": "Imam Muhammad al-Bukhari",
        "total_hadiths": 7563,
        "description": "The most authentic book of Hadith after the Holy Quran.",
        "badge_color": "primary",
    },
    {
        "id": "muslim",
        "api_name": "muslim",
        "name": "Sahih Muslim",
        "arabic_name": "صحيح مسلم",
        "author": "Imam Muslim ibn al-Hajjaj",
        "total_hadiths": 3033,
        "description": "Highly authentic collection with continuous chains of narration.",
        "badge_color": "success",
    },
    {
        "id": "nawawi40",
        "api_name": "nawawi40",
        "name": "40 Hadith an-Nawawi",
        "arabic_name": "الأربعون النووية",
        "author": "Imam Yahya ibn Sharaf an-Nawawi",
        "total_hadiths": 42,
        "description": "Essential compilation covering the core foundational principles of Islam.",
        "badge_color": "warning",
    },
    {
        "id": "tirmidhi",
        "api_name": "tirmidhi",
        "name": "Jami` at-Tirmidhi",
        "arabic_name": "جامع الترمذي",
        "author": "Imam Abu Isa Muhammad at-Tirmidhi",
        "total_hadiths": 3956,
        "description": "Renowned for its grading of Hadiths and legal discussions.",
        "badge_color": "info",
    },
    {
        "id": "abudawud",
        "api_name": "abudawud",
        "name": "Sunan Abi Dawud",
        "arabic_name": "سنن أبي داود",
        "author": "Imam Abu Dawud Sulayman",
        "total_hadiths": 5274,
        "description": "Focused primarily on legal traditions and Islamic jurisprudence.",
        "badge_color": "secondary",
    },
    {
        "id": "nasai",
        "api_name": "nasai",
        "name": "Sunan an-Nasa'i",
        "arabic_name": "سنن النسائي",
        "author": "Imam Ahmad ibn Shu'ayb an-Nasa'i",
        "total_hadiths": 5758,
        "description": "Strict criteria in chain evaluation and authentic narrations.",
        "badge_color": "dark",
    },
    {
        "id": "ibnmajah",
        "api_name": "ibnmajah",
        "name": "Sunan Ibn Majah",
        "arabic_name": "سنن ابن ماجه",
        "author": "Imam Ibn Majah",
        "total_hadiths": 4341,
        "description": "One of the six major canonical Hadith compilations (Kutub al-Sittah).",
        "badge_color": "light",
    },
    {
        "id": "riyadussalihin",
        "api_name": "riyadussalihin",
        "name": "Riyad as-Salihin",
        "arabic_name": "رياض الصالحين",
        "author": "Imam Yahya ibn Sharaf an-Nawawi",
        "total_hadiths": 1905,
        "description": "The Gardens of the Righteous — virtues, ethics, and good deeds.",
        "badge_color": "success",
    },
]

# Curated Hadiths of the Day for guaranteed immediate rich display
CURATED_DAILY_HADITHS = [
    {
        "collection_id": "bukhari",
        "collection_name": "Sahih al-Bukhari",
        "hadith_number": "1",
        "chapter_name": "Revelation",
        "arabic_text": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى",
        "translation_text": "I heard Allah's Messenger (ﷺ) saying: 'The reward of deeds depends upon the intentions and every person will get the reward according to what he has intended.'",
        "grade": "Sahih",
    },
    {
        "collection_id": "nawawi40",
        "collection_name": "40 Hadith an-Nawawi",
        "hadith_number": "13",
        "chapter_name": "Faith & Brotherhood",
        "arabic_text": "لاَ يُؤْمِنُ أَحَدُكُمْ حَتَّى يُحِبَّ لأَخِيهِ مَا يُحِبُّ لِنَفْسِهِ",
        "translation_text": "None of you truly believes until he loves for his brother what he loves for himself.",
        "grade": "Sahih",
    },
    {
        "collection_id": "bukhari",
        "collection_name": "Sahih al-Bukhari",
        "hadith_number": "13",
        "chapter_name": "Belief",
        "arabic_text": "المُسْلِمُ مَنْ سَلِمَ المُسْلِمُونَ مِنْ لِسَانِهِ وَيَدِهِ",
        "translation_text": "The Muslim is the one from whose tongue and hands the Muslims are safe.",
        "grade": "Sahih",
    },
    {
        "collection_id": "muslim",
        "collection_name": "Sahih Muslim",
        "hadith_number": "223",
        "chapter_name": "Purification",
        "arabic_text": "الطُّهُورُ شَطْرُ الإِيمَانِ، وَالْحَمْدُ لِلَّهِ تَمْلأُ الْمِيزَانَ",
        "translation_text": "Cleanliness and purification is half of faith, and 'Al-hamdulillah' (praise be to Allah) fills the scale.",
        "grade": "Sahih",
    },
    {
        "collection_id": "tirmidhi",
        "collection_name": "Jami` at-Tirmidhi",
        "hadith_number": "1956",
        "chapter_name": "Righteousness & Kindness",
        "arabic_text": "تَبَسُّمُكَ فِي وَجْهِ أَخِيكَ لَكَ صَدَقَةٌ",
        "translation_text": "Your smiling in the face of your brother is charity for you.",
        "grade": "Hasan Sahih",
    },
    {
        "collection_id": "nawawi40",
        "collection_name": "40 Hadith an-Nawawi",
        "hadith_number": "18",
        "chapter_name": "Good Character",
        "arabic_text": "اتَّقِ اللَّهَ حَيْثُمَا كُنْتَ، وَأَتْبِعِ السَّيِّئَةَ الْحَسَنَةَ تَمْحُهَا، وَخَالِقِ النَّاسَ بِخُلُقٍ حَسَنٍ",
        "translation_text": "Fear Allah wherever you may be; follow up an evil deed with a good one to wipe it out; and treat the people with good character.",
        "grade": "Hasan",
    },
    {
        "collection_id": "bukhari",
        "collection_name": "Sahih al-Bukhari",
        "hadith_number": "6018",
        "chapter_name": "Good Manners",
        "arabic_text": "إِنَّ خِيَارَكُمْ أَحَاسِنُكُمْ أَخْلاَقًا",
        "translation_text": "The best among you are those who have the best manners and character.",
        "grade": "Sahih",
    },
]


def get_hadith_collections():
    """Returns list of supported Hadith collections."""
    return HADITH_COLLECTIONS


def get_collection_by_id(collection_id):
    """Finds collection metadata by ID."""
    for c in HADITH_COLLECTIONS:
        if c["id"] == collection_id:
            return c
    return None


def get_daily_hadith():
    """Selects a daily featured hadith based on the day of the year."""
    today = date.today()
    day_index = (today.year * 365 + today.timetuple().tm_yday) % len(CURATED_DAILY_HADITHS)
    return CURATED_DAILY_HADITHS[day_index]


def get_hadith_by_number(collection_id, number):
    """
    Fetches a specific hadith (English & Arabic) from Fawaz Ahmed Hadith API.
    """
    # Map collection ID to API editions
    edition_en = f"eng-{collection_id}"
    edition_ar = f"ara-{collection_id}"

    eng_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{edition_en}/{number}.json"
    ara_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{edition_ar}/{number}.json"

    hadith_en = None
    hadith_ar = None

    try:
        req = urllib.request.Request(eng_url, headers={"User-Agent": "PersonalApp-Hadith/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "hadiths" in data and len(data["hadiths"]) > 0:
                hadith_en = data["hadiths"][0]
    except Exception as e:
        logger.warning(f"Failed to fetch English hadith {collection_id} #{number}: {e}")

    try:
        req_ar = urllib.request.Request(ara_url, headers={"User-Agent": "PersonalApp-Hadith/1.0"})
        with urllib.request.urlopen(req_ar, timeout=6) as resp_ar:
            data_ar = json.loads(resp_ar.read().decode("utf-8"))
            if "hadiths" in data_ar and len(data_ar["hadiths"]) > 0:
                hadith_ar = data_ar["hadiths"][0]
    except Exception as e:
        logger.warning(f"Failed to fetch Arabic hadith {collection_id} #{number}: {e}")

    if hadith_en or hadith_ar:
        grades = hadith_en.get("grades", []) if hadith_en else []
        grade_text = grades[0].get("grade", "Sahih") if grades else "Sahih"

        col_meta = get_collection_by_id(collection_id) or {"name": collection_id.capitalize()}
        return {
            "success": True,
            "collection_id": collection_id,
            "collection_name": col_meta["name"],
            "hadith_number": str(number),
            "arabic_text": hadith_ar.get("text", "") if hadith_ar else "",
            "translation_text": hadith_en.get("text", "") if hadith_en else "",
            "grade": grade_text,
        }

    # Fallback to curated if available
    for h in CURATED_DAILY_HADITHS:
        if h["collection_id"] == collection_id and str(h["hadith_number"]) == str(number):
            return {"success": True, **h}

    col_meta = get_collection_by_id(collection_id) or {"name": collection_id.capitalize()}
    return {
        "success": False,
        "collection_id": collection_id,
        "collection_name": col_meta["name"],
        "hadith_number": str(number),
        "arabic_text": "",
        "translation_text": "Hadith could not be loaded at this moment. Please check your network connection.",
        "grade": "",
    }


def get_hadiths_page(collection_id, page=1, page_size=10):
    """
    Fetches a slice/page of hadiths for a given collection.
    """
    col = get_collection_by_id(collection_id)
    total = col["total_hadiths"] if col else 100

    start_num = (page - 1) * page_size + 1
    end_num = min(start_num + page_size - 1, total)

    hadiths = []
    for num in range(start_num, end_num + 1):
        h = get_hadith_by_number(collection_id, num)
        if h.get("success"):
            hadiths.append(h)

    total_pages = (total + page_size - 1) // page_size

    return {
        "collection": col,
        "hadiths": hadiths,
        "current_page": page,
        "total_pages": total_pages,
        "start_num": start_num,
        "end_num": end_num,
        "total": total,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1,
        "next_page": page + 1,
    }
