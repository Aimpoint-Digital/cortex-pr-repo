import os
import json
import snowflake.connector
from github import Github
from github import Auth
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# Set up GitHub credentials
auth = Auth.Token(os.getenv('GITHUB_TOKEN'))
gh = Github(auth=auth)

# Get PR details from event payload
repo_name = os.getenv('GITHUB_REPOSITORY')
event_path = os.getenv('GITHUB_EVENT_PATH')

with open(event_path, 'r') as f:
    event_data = json.load(f)

pr_number = event_data['pull_request']['number']

repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# Gather the PR data (diff, title, commits, feature branch)
pr_title = pr.title
pr_commits = "\n".join([commit.commit.message for commit in pr.get_commits()])
pr_diff = pr.diff_url
feature_branch = pr.head.ref

# Set up Snowflake credentials
snowflake_account = os.getenv('SNOWFLAKE_ACCOUNT')
snowflake_user = os.getenv('SNOWFLAKE_USER')
snowflake_role = os.getenv('SNOWFLAKE_ROLE')
snowflake_warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
private_key_path = os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH')

# Read and load the private key
with open(private_key_path, 'rb') as key_file:
    private_key_data = key_file.read()

p_key = serialization.load_pem_private_key(
    private_key_data,
    password=None,
    backend=default_backend()
)

# Convert private key to DER format
pkb = p_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

ctx = snowflake.connector.connect(
    user=snowflake_user,
    account=snowflake_account,
    private_key=pkb,
    role=snowflake_role,
    database="TASTY_BYTES_DBT_DB",
    schema="DEV",
    warehouse=snowflake_warehouse
)

# Call the stored procedure to generate PR description
cursor = ctx.cursor()
try:
    print("Calling generate_pr_description stored procedure...")
    cursor.execute(
        "CALL generate_pr_description(?, ?, ?, ?)",
        (pr_title, pr_commits, pr_diff, feature_branch)
    )
    
    # Fetch the result
    result = cursor.fetchone()
    generated_description = result[0] if result else ""
    
    print("Generated description received from Snowflake")
    
except Exception as e:
    print(f"Error calling stored procedure: {e}")
    raise
finally:
    cursor.close()
    ctx.close()

# Update the PR description on GitHub
pr.edit(body=generated_description)

print(f"Updated PR #{pr_number} with generated description.")