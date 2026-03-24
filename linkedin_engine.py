import random
import requests
from google import genai

# ==========================================
# 1. YOUR CREDENTIALS
# ==========================================
import os
import random
import requests
from google import genai

# Pull credentials securely from GitHub Actions environment
# Pull credentials securely and strip invisible characters
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()
LINKEDIN_PERSON_URN = os.environ.get("LINKEDIN_PERSON_URN", "").strip()
# ... [The rest of the script stays exactly the same] ...

# ==========================================
# 1. DETERMINISTIC CONTENT ENGINE
# ==========================================
# Get the current day of the week (0 = Monday, 6 = Sunday)
day_of_week = datetime.datetime.today().weekday()
# Get the day of the year (1 through 365)
day_of_year = datetime.datetime.today().timetuple().tm_yday

# Exactly 7 formats. It will cycle through these sequentially every week.
engagement_formats = [
    "The Data vs. Reality Breakdown (Focus on contrasting expected models vs actual physics)", # Monday
    "The Engineering Unpopular Opinion (A bold but technically sound diagnostic stance)", # Tuesday
    "The Root Cause Analysis (Third-party observation of a common industry failure mode)", # Wednesday
    "The 'Hidden Cost' Expose (The financial impact of a technical measurement oversight)", # Thursday
    "The Hardware vs. Software Debate (Why physical sensors fail vs data models)", # Friday
    "The Design Flaw Teardown (Critique of standard but flawed estimation practices)", # Saturday
    "The 'Myth vs. Fact' Technical Reality (Debunking a common solar O&M assumption)" # Sunday
]

# 14 highly specific topics. It will cycle through these sequentially over two weeks.
technical_focuses = [
    "SCADA communication failures and RS-485 daisy chain noise",
    "PLC automation logic errors and tracker feedback loops",
    "Historical weather data vs. local pyranometer calibration drift",
    "Unexpected PR (Performance Ratio) drops due to localized micro-climates",
    "Inverter clipping masking true string-level underperformance",
    "PID (Potential Induced Degradation) early warning signs vs generic SCADA alarms",
    "The hidden O&M cost of weather station network downtime",
    "Soiling loss estimations vs. actual module degradation",
    "String mismatch losses caused by uneven thermal pockets",
    "False inverter derating triggered by localized ground loops",
    "The vulnerability of local IT networks in remote solar assets",
    "Why standard PV yield models fail to predict high-wind cooling effects",
    "Sensor calibration drift throwing off entire plant performance metrics",
    "The gap between modeled baseline PR and actual commissioning PR"
]

# Select today's strategy mathematically
engagement_format = engagement_formats[day_of_week]
technical_focus = technical_focuses[day_of_year % len(technical_focuses)]

# ==========================================
# 2. THE HIGH-INTEGRITY AI PROMPT
# ==========================================
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "").strip())

prompt = f"""
You are an electrical engineer with 3 years of hands-on experience in the solar field, specializing in O&M, SCADA, and performance diagnostics. You are writing a post for your personal LinkedIn profile. 
Your audience consists of highly technical peers: solar asset managers, SCADA technicians, and installers.

Today's Strategy:
- Technical Focus: {technical_focus}
- Format: {engagement_format}

Generate 1 highly engaging LinkedIn post based strictly on this strategy.

Strict Constraints on Perspective & Authenticity (CRITICAL):
- NO FAKE EXPERIENCE: You must NOT claim to have personally worked on massive utility-scale sites or resolved the specific issue yourself (e.g., do not say "I recently fixed a 50MW plant"). 
- THE PERSPECTIVE: Frame all case studies as industry observations, common field realities, or third-party data breakdowns (e.g., "When a utility-scale site experiences...", "A common failure mode is...", "Look at the data from...").
- REALISM ONLY: Discuss only real, scientifically accurate problems, physics, and realistic metrics. No exaggerated figures or fake case studies. 
- IMPLICIT ENGAGEMENT: Structure the argument to leave a dangling technical question, a bold diagnostic stance, or a slight "knowledge gap" that compels other engineers to jump into the comments to agree, disagree, correct you, or share their own data. 
- NO ASKING FOR COMMENTS: NEVER explicitly ask for comments. Banned phrases: "What do you think?", "Share your thoughts," "Let me know below."

Follow this exact structure:
1. The Hook (1-2 lines): Start with a raw, counter-intuitive technical observation. Stop the scroll immediately.
2. The Scenario (2-3 lines): Describe a gritty, realistic troubleshooting scenario or system failure. Use abbreviations naturally (e.g., PR drops, SCADA faults, RS-485, clipping).
3. The Pivot (1-2 lines): Point out why relying on fragile local instruments or generic reporting fails to catch this issue (e.g., ignoring micro-climates, hardware drift, local IT downtime).
4. The CTA (1 line): End the post exactly with: "P.S. I build tools and write breakdowns for advanced solar O&M. Check out the featured section on my profile."

Style Constraints:
- BANNED WORDS: "In today's fast-paced world," "Delve," "Navigating," "Crucial," "Landscape," "Transform," "Revolutionize," or any generic corporate fluff.
- FORMATTING: Use heavy whitespace. Maximum of 1 to 2 sentences per paragraph. 
- LENGTH: Keep the entire post under 150 words.
- HASHTAGS: Zero hashtags. 
"""
print(f"Generating post about: {technical_focus}...")
response = client.models.generate_content(
    model='gemini-3.1-flash-lite-preview',
    contents=prompt,
)
post_text = response.text
print(f"\n--- AI Generated Post ---\n{post_text}\n-------------------------\n")


# ==========================================
# 3. PUSH TO LINKEDIN API
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
