import requests
import json
import time
import pandas as pd
import os
import re
from bs4 import BeautifulSoup

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

# File paths
input_file = 'links.txt'
output_file = 'output/leetcode_topics.csv'

# Read links from file
with open(input_file, 'r') as file:
    links = [line.strip() for line in file if line.strip()]

# Total links
total_links = len(links)
print(f"Starting to process {total_links} links...")

# Prepare results list
results = []

# Function to extract problem slug from URL
def extract_problem_slug(url):
    return url.split('/')[-1]

# Headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://leetcode.com/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# Process each link
for i, link in enumerate(links):
    try:
        problem_slug = extract_problem_slug(link)
        print(f"\nProcessing {i+1}/{total_links}: {problem_slug}")
        
        # First approach: Use GraphQL API to get problem metadata including tags
        try:
            # GraphQL endpoint
            graphql_url = "https://leetcode.com/graphql"
            
            # GraphQL query to get problem data including topic tags
            query = {
                "operationName": "questionData",
                "variables": {"titleSlug": problem_slug},
                "query": """
                query questionData($titleSlug: String!) {
                    question(titleSlug: $titleSlug) {
                        questionId
                        title
                        titleSlug
                        topicTags {
                            name
                            slug
                        }
                    }
                }
                """
            }
            
            # Make the request
            response = requests.post(graphql_url, json=query, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'question' in data['data'] and data['data']['question']:
                    topic_tags = data['data']['question'].get('topicTags', [])
                    if topic_tags:
                        topics = [tag['name'] for tag in topic_tags]
                        print(f"Found topics from GraphQL API: {topics}")
                        results.append({
                            'problem_link': link,
                            'problem_id': problem_slug,
                            'topics': ', '.join(topics)
                        })
                        # If successful, continue to next link
                        continue
                    else:
                        print("No topics found in GraphQL response")
                else:
                    print("Invalid GraphQL response structure or no data returned")
            else:
                print(f"GraphQL request failed with status {response.status_code}")
        
        except Exception as e:
            print(f"Error with GraphQL approach: {str(e)}")
        
        # Second approach: If GraphQL fails, try scraping the HTML directly
        try:
            # Make a GET request to the problem page
            response = requests.get(link, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to find topics section - look for text "Topics" and nearby elements
                topics_found = []
                
                # Method 1: Look for div containing "Topics"
                topics_divs = soup.find_all('div', string=lambda text: text and "Topics" in text)
                
                for div in topics_divs:
                    # Check siblings and nearby elements for topic tags
                    parent = div.parent
                    if parent:
                        # Look for elements that might be topic tags
                        potential_tags = parent.find_all(['div', 'span'], 
                            class_=lambda c: c and ('rounded' in c or 'tag' in c or 'chip' in c or 'badge' in c))
                        
                        for tag in potential_tags:
                            tag_text = tag.get_text().strip()
                            if (tag_text and len(tag_text) < 25 and 
                                not tag_text.endswith('%') and 
                                tag_text not in ['Topics', 'Companies', 'Run', 'Submit', 'Auto']):
                                topics_found.append(tag_text)
                
                # Method 2: Look for "Array", "String", "Sorting" pattern in any element
                if not topics_found:
                    all_elements = soup.find_all(['div', 'span'])
                    for elem in all_elements:
                        elem_text = elem.get_text().strip()
                        if (elem_text in ['Array', 'String', 'Sorting', 'Hash Table', 'Math',
                                         'Dynamic Programming', 'Tree', 'Depth-First Search',
                                         'Binary Search', 'Graph', 'Binary Tree']):
                            topics_found.append(elem_text)
                
                # Method 3: Look for topics in page source
                if not topics_found:
                    # Try to find a JSON object in script tags that might contain topics
                    scripts = soup.find_all('script')
                    for script in scripts:
                        script_text = script.string if script.string else ""
                        if script_text and '"topicTags"' in script_text:
                            # Try to extract JSON containing topicTags
                            try:
                                # Use regex to find the JSON object
                                json_match = re.search(r'({[^{]*"topicTags"[^}]*})', script_text)
                                if json_match:
                                    json_str = json_match.group(1)
                                    # Make it proper JSON if needed
                                    json_str = json_str.replace("'", '"')
                                    data = json.loads(json_str)
                                    if 'topicTags' in data:
                                        for tag in data['topicTags']:
                                            if 'name' in tag:
                                                topics_found.append(tag['name'])
                            except Exception as e:
                                print(f"Error extracting topics from script: {str(e)}")
                
                if topics_found:
                    # Filter out duplicates
                    topics_found = list(set(topics_found))
                    print(f"Found topics from HTML: {topics_found}")
                    results.append({
                        'problem_link': link,
                        'problem_id': problem_slug,
                        'topics': ', '.join(topics_found)
                    })
                else:
                    print("No topics found in HTML")
                    results.append({
                        'problem_link': link,
                        'problem_id': problem_slug,
                        'topics': 'Not found'
                    })
            else:
                print(f"HTML request failed with status {response.status_code}")
                results.append({
                    'problem_link': link,
                    'problem_id': problem_slug,
                    'topics': f'Error: HTTP {response.status_code}'
                })
        
        except Exception as e:
            print(f"Error with HTML approach: {str(e)}")
            results.append({
                'problem_link': link,
                'problem_id': problem_slug,
                'topics': f'Error: {str(e)}'
            })
        
        # Save progress after every 10 links
        if (i + 1) % 10 == 0 or (i + 1) == total_links:
            print(f"Saving progress after processing {i+1} links...")
            pd.DataFrame(results).to_csv(output_file, index=False)
        
        # Add a delay to avoid rate limiting
        time.sleep(1)
        
    except KeyboardInterrupt:
        print("Script interrupted by user. Saving current progress...")
        break
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        if 'link' in locals():
            problem_slug = extract_problem_slug(link)
            results.append({
                'problem_link': link,
                'problem_id': problem_slug,
                'topics': f'Error: {str(e)}'
            })

# Save final results to CSV
pd.DataFrame(results).to_csv(output_file, index=False)
print(f"\nCompleted! Results saved to: {output_file}")