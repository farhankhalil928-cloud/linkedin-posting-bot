import os
import random
import requests
import base64
import time
from google import genai
from google.genai import types

# ==========================================
# 1. YOUR CREDENTIALS & CONFIG
# ==========================================
# API Keys and Tokens
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()
LINKEDIN_PERSON_URN = os.environ.get("LINKEDIN_PERSON_URN", "").strip()

# GitHub Configuration for your secondary account
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()  # Required if repo is private
GITHUB_OWNER = "your_other_github_username" 
GITHUB_REPO = "your_article_repo_name"
GITHUB_PATH = "articles"  # Leave empty "" if articles are in the root directory

# ==========================================
# 2. GITHUB REPOSITORY PARSER
# ==========================================
def fetch_daily_article_from_github(owner, repo, path, token=None):
    """
    Fetches the file list from a remote GitHub repository path,
    picks a random markdown/text file, and returns its raw text content.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}".strip("/")
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repo contents. Status: {response.status_code}, Error: {response.text}")
        
    repo_items = response.json()
    
    valid_articles = [
        item for item in repo_items 
        if item["type"] == "file" and (item["name"].endswith(".md") or item["name"].endswith(".txt"))
    ]
    
    if not valid_articles:
        raise FileNotFoundError(f"No valid .md or .txt files found in GitHub path: {path}")
    
    selected_item = random.choice(valid_articles)
    print(f"📖 Selected remote article: {selected_item['name']}")
    
    file_response = requests.get(selected_item["url"], headers=headers)
    if file_response.status_code != 200:
        raise Exception(f"Failed to fetch file details. Status: {file_response.status_code}")
        
    file_data = file_response.json()
    
    if file_data.get("encoding") == "base64":
        raw_content = base64.b64decode(file_data["content"]).decode("utf-8")
    else:
        raw_content = requests.get(file_data["download_url"], headers=headers).text
        
    return raw_content

# ==========================================
# 3. TRANSLATION & ENGAGEMENT ENGINE
# ==========================================
def generate_linkedin_post(raw_article_content):
    """
    Translates raw engineering text into an engaging LinkedIn post using Gemini.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    system_instruction = """
    You are a veteran solar engineer and master technical storyteller. Your job is to take complex, dense engineering data, field diagnostics, or solar modeling math, and translate it into a captivating LinkedIn post. 
    Your goal is to make a junior engineer or asset manager understand the absolute weight of the problem without needing a PhD.
    """

    prompt = f"""
    Take the core thesis of the following technical article and turn it into an engaging LinkedIn post.

    Do NOT just summarize the text. Instead, extract the main technical tension (e.g., hardware failing, bad data, hidden financial losses) and tell it like an industry insight or a field realization.

    Strict Constraints:
    1. THE HOOK: Start with a punchy, counter-intuitive line. Disrupt their scrolling. (e.g., "The data says 99% uptime. The cash flow says otherwise.")
    2. STYLE: Write in a punchy, conversational "broetry" style with heavy whitespace (1-2 sentences max per paragraph).
    3. BULLETS: Present the core technical problem or symptoms in a short 3-item bulleted list.
    4. THE SIGN-OFF: End with a lingering technical thought that forces engineers to think, without begging for comments. Do not include any URLs or call-to-actions in the text generation.
    5. BANNED WORDS: "Delve," "Navigating," "Crucial," "Landscape," "Transform," "Revolutionize," "Synergy," "In conclusion."

    Here is the raw article text:
    ---
    {raw_article_content}
    ---
    """

    print("Translating high-tech article into engaging LinkedIn format...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7 
                )
            )
            return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "UNAVAILABLE" in error_msg or "429" in error_msg:
                print(f"⚠️ Google Server Busy/Rate Limited (Attempt {attempt + 1}/{max_retries}).")
                if attempt < max_retries - 1:
                    time.sleep(60)
                else:
                    raise Exception("❌ Max retries reached for Gemini API.")
            else:
                raise e

# ==========================================
# 4. LINKEDIN POST API PUBLISHER
# ==========================================
def publish_to_linkedin(post_text, access_token, person_urn):
    """
    Pushes the finalized post directly to the user's LinkedIn profile feed.
    """
    print("Publishing to LinkedIn API...")
    url = "https://api.linkedin.com/v2/ugcPosts"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    payload = {
        "author": person_urn,
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
        print("✅ Successfully posted to LinkedIn!")
    else:
        print(f"❌ Failed to post. Status: {api_response.status_code}, Error: {api_response.text}")


# ==========================================
# 5. MAIN EXECUTION PIPELINE
# ==========================================
if __name__ == "__main__":
    try:
        # Step 1: Pull raw markdown from your secondary GitHub repo
        article_content = fetch_daily_article_from_github(
            owner=GITHUB_OWNER,
            repo=GITHUB_REPO,
            path=GITHUB_PATH,
            token=GITHUB_TOKEN if GITHUB_TOKEN else None
        )
        
        # Step 2: Use Gemini to translate it into a native LinkedIn post
        linkedin_post_draft = generate_linkedin_post(article_content)
        print(f"\n--- AI Draft ---\n{linkedin_post_draft}\n----------------\n")
        
        # Step 3: Publish to LinkedIn using your API credentials
        if LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN:
            publish_to_linkedin(linkedin_post_draft, LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN)
        else:
            print("⚠️ LinkedIn credentials missing. Skipping API push.")
            
    except Exception as e:
        print(f"Pipeline failed: {e}")
        exit(1)
