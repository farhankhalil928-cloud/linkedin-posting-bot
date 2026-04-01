import os
import datetime
import requests
from google import genai

# ==========================================
# 1. YOUR CREDENTIALS
# ==========================================
# Pull credentials securely and strip invisible characters
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()
LINKEDIN_PERSON_URN = os.environ.get("LINKEDIN_PERSON_URN", "").strip()

# ==========================================
# 2. DETERMINISTIC CONTENT ENGINE
# ==========================================
# Get the day of the year (1 through 365) to cycle through the lists mathematically
day_of_year = datetime.datetime.today().timetuple().tm_yday

# 14 Expanded Formats: Cycles every 2 weeks
engagement_formats = [
    "The Data vs. Reality Breakdown (Focus on contrasting expected models vs actual physics)",
    "The Engineering Unpopular Opinion (A bold but technically sound diagnostic stance)",
    "The Root Cause Analysis (Third-party observation of a common industry failure mode)",
    "The 'Hidden Cost' Expose (The financial impact of a technical measurement oversight)",
    "The Hardware vs. Software Debate (Why physical sensors fail vs data models)",
    "The Design Flaw Teardown (Critique of standard but flawed estimation practices)",
    "The 'Myth vs. Fact' Technical Reality (Debunking a common solar O&M assumption)",
    "The 'Back to Basics' Mentor Post (Explaining a complex concept simply for junior engineers)",
    "The System Degradation Deep-Dive (Long-term performance realities vs day-one commissioning)",
    "The Commissioning Trap (What gets missed during site handover and testing)",
    "The SCADA Alarm Fatigue Breakdown (How to filter signal from noise in monitoring platforms)",
    "The Predictive Maintenance Pivot (Shifting from reactive truck-rolls to proactive data analysis)",
    "The Underperformance Diagnostic Framework (A step-by-step troubleshooting logic flow)",
    "The Weather Data Disconnect (Satellite tracking vs. ground sensor accuracy)"
]

# 28 Expanded Technical Topics: Cycles every 4 weeks
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
    "The gap between modeled baseline PR and actual commissioning PR",
    "Drone thermography vs. string-level monitoring for bypassed diode failures",
    "Bifacial module albedo assumptions vs. real-world backside gain",
    "Tracker wind stow mode trigger delays causing mechanical stress",
    "DC ground faults that clear themselves before technicians arrive",
    "IV curve tracing misinterpretations in partial shading scenarios",
    "Curtailment algorithms fighting with localized frequency regulation",
    "Capacitor aging in central inverters and early warning thermal signatures",
    "Irradiance sensor soiling masking actual array underperformance",
    "The impact of uncalibrated reference cells on capacity testing",
    "Network packet loss causing phantom inverter communication timeouts",
    "Reactive power (VAR) dispatch limits cutting into real active power generation",
    "Combining historical satellite data with local software to eliminate sensor dependency",
    "Thermal cycling fatigue on MC4 connectors in high-heat environments",
    "Software-based shadow modeling vs. actual near-field shading losses"
]

# Select today's strategy mathematically so they rotate smoothly
engagement_format = engagement_formats[day_of_year % len(engagement_formats)]
technical_focus = technical_focuses[day_of_year % len(technical_focuses)]

# ==========================================
# 3. THE HIGH-INTEGRITY AI PROMPT
# ==========================================
client = genai.Client(api_key=GEMINI_API_KEY)

prompt = f"""
You are an electrical engineer with 10 years of hands-on experience in the solar field, specializing in O&M, SCADA, and performance diagnostics. You are writing a post for your personal LinkedIn profile. 

Your audience includes highly technical peers (solar asset managers, SCADA technicians) AND junior engineers. You need to break down complex field realities so they are easy to understand in one reading, yet technical enough to earn the respect of seasoned veterans.

Today's Strategy:
- Technical Focus: {technical_focus}
- Format: {engagement_format}

Generate 1 highly engaging, conversational, and insightful LinkedIn post based strictly on this strategy.

Strict Constraints on Perspective & Authenticity (CRITICAL):
- NO FAKE EXPERIENCE: Frame case studies as industry observations, common field realities, or third-party data breakdowns (e.g., "A common failure mode in utility-scale sites is...", "We often see data showing..."). Do not claim you personally fixed a specific massive plant.
- REALISM & CLARITY: Discuss real, scientifically accurate physics and metrics. Explain the "why" behind the problem so a new engineer can learn from it, but keep it grounded in reality.
- IMPLICIT ENGAGEMENT: Structure the insight to leave a dangling technical question, a bold stance, or a slight "knowledge gap" that compels engineers to comment with their own experiences or corrections.
- NO ASKING FOR COMMENTS: NEVER explicitly ask for comments (e.g., "What do you think?", "Share below").

Narrative Flow (Make it flow naturally, not like a robotic checklist):
1. The Hook: Start with a strong, relatable, or counter-intuitive observation about the technical focus. Stop the scroll.
2. The Breakdown: Explain the scenario clearly. What actually happens in the field? Use technical terms but provide enough context so it makes logical sense. Tell a realistic story of how this issue unfolds.
3. The Veteran Insight: Point out why standard tools, generic reporting, or junior-level thinking usually miss the root cause.
4. The Dynamic CTA: End the post with a smooth, natural transition that directs the reader to check out the "featured section on your profile." Do NOT use a fixed, repetitive sentence. Tailor the CTA so it directly connects to the topic of the post.

Style Constraints:
- TONE: Conversational, seasoned, insightful, and accessible. Write like a human mentor sharing a hard-learned lesson.
- BANNED WORDS: "In today's fast-paced world," "Delve," "Navigating," "Crucial," "Landscape," "Transform," "Revolutionize," "Synergy," or any generic AI corporate fluff.
- FORMATTING: Use generous whitespace to make it highly scannable on mobile, but group related thoughts logically instead of chopping every single sentence into a new line.
- LENGTH: Keep the post around 150 to 250 words. Give yourself enough room to clearly explain the concept without rambling.
- HASHTAGS: #SolarEnergy #PVOptimization #O&M #SolarEngineering #Renewables
"""

print(f"Generating post about: {technical_focus}...")

# Standardized the model name to gemini-2.5-flash for maximum stability
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
)
post_text = response.text
print(f"\n--- AI Generated Post ---\n{post_text}\n-------------------------\n")


# ==========================================
# 4. PUSH TO LINKEDIN API
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

