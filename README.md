# LeetCode Topic Tag Scraper

A Python tool to extract topic tags for LeetCode problems. This script takes a list of LeetCode problem URLs and automatically extracts the topic tags associated with each problem (e.g., "Array", "String", "Dynamic Programming", etc.).

## Why is this useful?

When studying for coding interviews, it's helpful to know which data structures and algorithms are being tested by each LeetCode problem. This tool automatically extracts those tags to help you focus your study efforts on specific topics.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ascender1729/leetcode_scraper.git
cd leetcode_scraper
```

2. Create a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install requests beautifulsoup4 pandas
```

## How to Use

### Step 1: Get Company-Specific LeetCode Problems

You can obtain company-specific LeetCode problem lists from these repositories:
- [LeetCode-Questions-CompanyWise](https://github.com/krishnadey30/LeetCode-Questions-CompanyWise)
- [leetcode-company-wise-problems](https://github.com/liquidslr/leetcode-company-wise-problems)

To get the links:
1. Clone one of these repositories:
   ```bash
   git clone https://github.com/krishnadey30/LeetCode-Questions-CompanyWise.git
   # OR
   git clone https://github.com/liquidslr/leetcode-company-wise-problems.git
   ```

2. Find the CSV file for your desired company (e.g., Google, Amazon, Microsoft)

3. Extract all the LeetCode problem links from the CSV file

### Step 2: Create Input File

1. Create a text file called `links.txt` in the project directory
2. Paste all the LeetCode problem links you extracted, one link per line, for example:
```
https://leetcode.com/problems/two-sum/
https://leetcode.com/problems/add-two-numbers/
https://leetcode.com/problems/longest-substring-without-repeating-characters/
```

### Step 3: Run the Script

```bash
python scraper.py
```

The script will:
1. Process each link in the `links.txt` file
2. Extract the topic tags for each problem
3. Save the results to `output/leetcode_topics.csv`

## Output

The output CSV file will have three columns:
- `problem_link`: The full URL of the problem
- `problem_id`: The problem ID/slug (e.g., "two-sum")
- `topics`: Comma-separated list of topic tags for the problem

Example output:
```
problem_link,problem_id,topics
https://leetcode.com/problems/two-sum/,two-sum,"Array, Hash Table"
https://leetcode.com/problems/add-two-numbers/,add-two-numbers,"Linked List, Math, Recursion"
```

## Troubleshooting

### Rate Limiting
If you're processing a large number of problems, you might encounter rate limiting from LeetCode. If this happens:
- Try increasing the delay between requests by modifying the `time.sleep()` value
- Run the script in smaller batches

### Module Not Found Errors
If you see "ModuleNotFoundError", make sure you've installed all required dependencies:
```bash
pip install requests beautifulsoup4 pandas
```

### Connection Errors
If you're getting connection errors, it might be due to network issues or LeetCode blocking the requests. Try:
- Checking your internet connection
- Waiting for a few minutes before trying again
- Using a VPN if necessary

## Example Workflow

Here's a complete example of how you might use this tool:

```bash
# Clone the repository
git clone https://github.com/ascender1729/leetcode_scraper.git
cd leetcode_scraper

# Set up the environment
python -m venv venv
venv\Scripts\activate
pip install requests beautifulsoup4 pandas

# Get company-specific problem lists
git clone https://github.com/krishnadey30/LeetCode-Questions-CompanyWise.git
# Now open the CSV for your target company and copy the links

# Create links.txt with your LeetCode problem URLs
# (each URL on a new line)

# Run the scraper
python scraper.py

# Results will be in output/leetcode_topics.csv
```

## How It Works

The script uses two approaches to extract topic tags:

1. **GraphQL API**: First attempts to use LeetCode's GraphQL API to fetch topic tags directly
2. **HTML Parsing**: If the API approach fails, it scrapes the HTML content of the problem page

The script saves progress every 10 problems, so if it's interrupted, you won't lose all your data.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request to the [repository](https://github.com/ascender1729/leetcode_scraper).