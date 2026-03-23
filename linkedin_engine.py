import random
import requests
from google import genai

# ==========================================
# 1. YOUR CREDENTIALS
# ==========================================
GEMINI_API_KEY = "AIzaSyAQsqI4Vd7lQYnY2UOg6KrKwq960SNFL-s"
LINKEDIN_ACCESS_TOKEN = "AQUaOPEKXdqavEreGXkKQTbqIEZ9d-pKk03VGpNmQcPiTUwcoCSHO4v7Q8Z1AQHvjyRQHPiyGBFFKdvnWYldQM5a3-YfK_6KAnMbEy_2ZR-c5tYlQoerLGkpb3YBU5PtSl8bqRaVYoqN7XPE_KSmdIS7ARmFHh89pAiZDX1MERbwtEH-Tvk_OXpSg-_vdYt86tCyxGVFtbsXAMDbDc8c6S6jz_teXILlYMWUS5dUE792Gcfp7tFKFzeS2yH4KHnw9G3lEIfInGHUfS5whPl5a_VhYRXYzOQBbc0fZ3fsEMVaFTQj3HD90Hxl7GHc9M4C9EFSsRkr6Ajfgqalkw3pkg-Yn5kvUg"
LINKEDIN_PERSON_URN = "urn:li:member:906275703" # e.g., urn:li:person:123456789

# ==========================================
# 2. DYNAMIC CONTENT ENGINE
# ==========================================
technical_focus = random.choice([
    "SCADA communication failures and false alarms", 
    "PLC automation logic errors in solar trackers",
    "historical weather data vs. local sensor calibration drift",
    "unexpected PR (Performance Ratio) drops due to micro-climates"
])

engagement_format = random.choice([
    "The Field Case Study", 
    "The Data vs. Reality Breakdown",
    "The Engineering Unpopular Opinion"
])

client = genai.Client(api_key=GEMINI_API_KEY)

prompt = f"""
You are a seasoned electrical engineer with years of hands-on experience in solar plant O&M, PLC programming, and performance diagnostics. You are writing a post for your personal LinkedIn profile. 
Your audience consists of highly technical peers: solar asset managers, SCADA technicians, and installers.

Today's Strategy:
- Technical Focus: {technical_focus}
- Format: {engagement_format}

Generate 1 highly engaging LinkedIn post based strictly on this strategy.

Follow this exact structure:
1. The Hook (1-2 lines): Start with a raw, counter-intuitive observation or a specific field failure. Stop the scroll immediately.
2. The Field Scenario (2-3 lines): Describe a realistic, gritty troubleshooting scenario. Use technical abbreviations naturally (e.g., PR drops, SCADA faults, clipping, string mismatch).
3. The Pivot (1-2 lines): Point out why relying on fragile local instruments or generic reporting always fails to catch or predict this issue (e.g., ignoring micro-climates, sensor calibration drift, IT network downtime).
4. The CTA (1 line): End the post with this exact sentence: "P.S. I build tools and write breakdowns for advanced solar O&M. Check out the featured section on my profile."

Strict Constraints:
- BANNED WORDS: "In today's fast-paced world," "Delve," "Navigating," "Crucial," "Landscape," or any generic corporate fluff.
- FORMATTING: Use heavy whitespace. Maximum of 1 to 2 sentences per paragraph. 
- LENGTH: Keep the entire post under 150 words.
- HASHTAGS: Zero hashtags. 
"""

print(f"Generating post about: {technical_focus}...")
response = client.models.generate_content(
    model='gemini-2.5-flash',
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
