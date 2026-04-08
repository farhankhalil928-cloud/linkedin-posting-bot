import os
import time
import random
import datetime
import requests
from google import genai

# ==========================================
# 1. YOUR CREDENTIALS
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()
LINKEDIN_PERSON_URN = os.environ.get("LINKEDIN_PERSON_URN", "").strip()

# ==========================================
# 2. DETERMINISTIC TOPIC ENGINE
# ==========================================
day_of_year = datetime.datetime.today().timetuple().tm_yday

engagement_formats = [
    "The Solar Diagnostic Puzzle (Present a realistic plant anomaly and let engineers deduce the cause)",
    "The Data vs. Reality Breakdown (Contrast expected models vs actual physics)",
    "The Engineering Unpopular Opinion (A bold but technically sound diagnostic stance)",
    "The Root Cause Analysis (Third-party observation of a common industry failure mode)",
    "The 'Hidden Cost' Expose (The financial impact of a technical measurement oversight)",
    "The Hardware vs. Software Debate (Why physical sensors fail vs data models)",
    "The 'Back to Basics' Mentor Post (Explaining a complex concept simply for junior engineers)"
]

technical_focuses = [
    "SCADA communication failures and RS-485 daisy chain noise",
    "PLC automation logic errors and tracker feedback loops",
    "Historical weather data vs. local pyranometer calibration drift",
    "Unexpected PR drops due to localized micro-climates",
    "Inverter clipping masking true string-level underperformance",
    "PID early warning signs vs generic SCADA alarms",
    "The hidden O&M cost of weather station network downtime",
    "Soiling loss estimations vs. actual module degradation",
    "False inverter derating triggered by localized ground loops",
    "Why standard PV yield models fail to predict high-wind cooling effects",
    "Sensor calibration drift throwing off entire plant performance metrics",
    "The gap between modeled baseline PR and actual commissioning PR",
    "Drone thermography vs. string-level monitoring for bypassed diode failures",
    "Network packet loss causing phantom inverter communication timeouts"
]

# Mathematically cycle through core strategies
engagement_format = engagement_formats[day_of_year % len(engagement_formats)]
technical_focus = technical_focuses[day_of_year % len(technical_focuses)]


# ==========================================
# 3. SOCIAL PSYCHOLOGY INJECTORS
# ==========================================
# Force the AI to start with a proven, curiosity-inducing structure
hook_templates = [
    "A solar plant can show perfect {metric} while secretly losing massive {hidden_metric}.",
    "Most engineers blame {common_cause}. The real issue in the field is usually {hidden_cause}.",
    "Here is a physical hardware problem your SCADA dashboard will almost never catch.",
    "The plant looks healthy on the monitors. The string data says otherwise.",
    "Stop trusting your local weather station when a site suddenly drops in PR."
]

# Rotate the CTA so LinkedIn's algorithm doesn't throttle repetitive external links
cta_modes = [
    "The Curiosity Gap: Hint that tracking historical weather data solves this, without explicitly linking.",
    "The Technical Challenge: End with a statement that hardware-free PR tools (like Solar Metrix) catch these anomalies instantly.",
    "The Mentor Sign-off: Mention that you build tools to bypass these specific hardware failures—link in your featured section."
]

# Mid-size hashtags that won't bury your post
hashtag_pool = ["#SolarOandM", "#SolarDiagnostics", "#PVPerformance", "#SolarSCADA", "#UtilityScaleSolar", "#SolarEngineering"]

selected_hook = random.choice(hook_templates)
selected_cta = random.choice(cta_modes)
selected_hashtags = " ".join(random.sample(hashtag_pool, 3))


# ==========================================
# 4. THE VIRAL AI PROMPT
# ==========================================
client = genai.Client(api_key=GEMINI_API_KEY)

prompt = f"""
You are an electrical engineer with 10 years of hands-on experience in the solar field, specializing in O&M, SCADA, and performance diagnostics. You are writing a highly engaging LinkedIn post.

Your audience consists of highly technical peers (solar asset managers, SCADA technicians) AND junior engineers. 

Today's Strategy:
- Topic: {technical_focus}
- Format: {engagement_format}
- Required Hook Tone: Use a variation of this structure: "{selected_hook}"
- CTA Style: {selected_cta}

Generate 1 LinkedIn post based strictly on this strategy.

Strict Constraints on Authenticity & Structure:
1. THE PERSPECTIVE: Frame all case studies as industry observations or common field realities. Do not claim you personally fixed a massive plant yesterday.
2. NO ASKING FOR COMMENTS: Never explicitly ask for comments (e.g., "What do you think?", "Share below"). Instead, leave a dangling technical thought or a bold stance that naturally compels engineers to debate it in the comments.
3. DIAGNOSTIC PUZZLES: If the format is a "Diagnostic Puzzle," lay out the symptoms clearly using bullet points, and end the post by leaving the true root cause ambiguous for the audience to guess. 

Formatting Rules (CRITICAL FOR LINKEDIN):
- Maximum of 1 to 2 sentences per paragraph. Use heavy whitespace.
- Use a short bulleted list (3-4 items) to describe the symptoms, scenario, or data points. 
- Write in a punchy, conversational "broetry" rhythm. 
- BANNED WORDS: "Delve," "Navigating," "Crucial," "Landscape," "Transform," "Revolutionize," "Synergy," or any generic AI fluff.

Keep the post between 150 and 220 words. Do not include hashtags (they will be added later).
"""

print(f"Generating post about: {technical_focus}...")

# ---------------------------------------------------------
# AUTO-RETRY LOGIC FOR RESILIENCE
# ---------------------------------------------------------
max_retries = 3
post_text = ""

for attempt in range(max_retries):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # Append the dynamically selected hashtags to the bottom
        post_text = f"{response.text.strip()}\n\n{selected_hashtags}"
        
        print(f"\n--- AI Generated Post ---\n{post_text}\n-------------------------\n")
        break 
        
    except Exception as e:
        error_msg = str(e)
        if "503" in error_msg or "UNAVAILABLE" in error_msg or "429" in error_msg:
            print(f"⚠️ Google Server Busy/Rate Limited (Attempt {attempt + 1}/{max_retries}).")
            if attempt < max_retries - 1:
                print("Waiting 60 seconds before retrying...")
                time.sleep(60)
            else:
                print("❌ Max retries reached. Exiting.")
                exit(1)
        else:
            raise e

# ==========================================
# 5. PUSH TO LINKEDIN API
# ==========================================
print("Pushing to LinkedIn...")
url = "https://api.linkedin.com/v2/ugcPosts"

headers = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

payload = {
    "author": LINKEDIN_PERSON_URN,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": post_text
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC" 
    }
}

api_response = requests.post(url, headers=headers, json=payload)

if api_response.status_code == 201:
    print("✅ Successfully posted to LinkedIn! Go check your profile.")
else:
    print(f"❌ Failed to post. Status: {api_response.status_code}, Error: {api_response.text}")
