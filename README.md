# 🚀 Snowflake Cortex PR Description Generator Hackathon

Welcome to the most exciting hackathon challenge you'll tackle today! 🎉

## 🎯 The Challenge

Your mission, should you choose to accept it, is to build a **Snowflake stored procedure** that automatically generates intelligent PR descriptions by:

1. 📊 Executing SQL scripts from both the `main` branch and your feature branch
2. 🔍 Comparing sample results between the two
3. 🤖 Using Snowflake Cortex AI to generate a comprehensive, insightful PR description

The best part? **We've already done all the GitHub Actions heavy lifting for you!** All you need to focus on is the Snowflake magic. ✨

## 🌟 What's Already Built

Thanks to inspiration from [this excellent blog post](https://austinjhunt.medium.com/automating-pr-descriptions-with-github-actions-and-python-let-the-bots-do-the-talking-55b911369e67), we've got:

✅ GitHub Actions workflow that triggers on PR labels  
✅ Python script that connects to Snowflake via private key authentication  
✅ Automatic PR description updates on GitHub  
✅ Sample Tasty Bytes dbt project with real data  

All you need to do is create the brain of the operation: **the `generate_pr_description()` stored procedure**! 🧠

## 🛠️ Setup Instructions

### Step 1: Set Up Your Snowflake Environment

Run the setup SQL to create the Tasty Bytes demo data:

1. Navigate to `setup/tasty_bytes_setup.sql`
2. Select your warehouse from the context selector (we recommend creating `TASTY_BYTES_DBT_WH`)
3. Run all the uncommented SQL commands using `cmd + Shift + Enter` (Mac) or `Ctrl + Shift + Enter` (Windows)
4. Wait for the magic ✨ - you should see: `tasty_bytes_dbt_db setup is now complete`

This script:
- 🏢 Creates a warehouse, database, and schemas (RAW, DEV, PROD)
- 📝 Enables logging, tracing, and metrics for monitoring
- 📦 Creates and loads tables for the Tasty Bytes food truck business
- 🌐 Sets up external access integrations for dbt

### Step 2: Create a Snowflake Key Pair for Authentication

Generate a private key for secure authentication:

```bash
# Generate an unencrypted private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt

# Generate the public key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

**Note**: When copying the public key, remove the `-----BEGIN PUBLIC KEY-----` and `-----END PUBLIC KEY-----` lines.

### Step 3: Create a Service User

Create a service account:

```sql
USE ROLE ACCOUNTADMIN;

-- Create the service user
CREATE USER IF NOT EXISTS github_actions_user
    DEFAULT_ROLE = CICD
    DEFAULT_WAREHOUSE = TASTY_BYTES_DBT_WH
    RSA_PUBLIC_KEY = '<your_public_key>';

-- Grant necessary privileges
CREATE ROLE CICD;
GRANT ROLE CICD TO USER github_actions_user;
GRANT USAGE ON WAREHOUSE TASTY_BYTES_DBT_WH TO ROLE CICD;
GRANT USAGE ON DATABASE TASTY_BYTES_DBT_DB TO ROLE CICD;
GRANT USAGE ON SCHEMA TASTY_BYTES_DBT_DB.DEV TO ROLE CICD;
GRANT USAGE ON SCHEMA TASTY_BYTES_DBT_DB.PROD TO ROLE CICD;
```

### Step 4: Install and Configure dbt Core

This project requires dbt Core to run the Tasty Bytes demo. Follow these steps to install dbt:

#### Prerequisites

Before installing dbt, ensure you have:

- ✅ Python 3.8 or higher installed (`python3 --version`)
- ✅ pip installed (`pip3 --version`)
- ✅ Terminal/command prompt access
- ✅ Permissions to create directories and install packages

#### Create a Python Virtual Environment

Using a virtual environment is **highly recommended** to avoid dependency conflicts:

**macOS:**
```bash
# Navigate to your project directory
cd /path/to/cortex-pr-repo

# Create virtual environment
python3 -m venv env

# Activate virtual environment
source env/bin/activate

# Verify Python path
which python
```

**Windows:**
```bash
# Navigate to your project directory
cd \path\to\cortex-pr-repo

# Create virtual environment
py -m venv env

# Activate virtual environment
env\Scripts\activate

# Verify Python path
where python
```

#### Install dbt Core with Snowflake Adapter

Once your virtual environment is activated, install dbt:

```bash
# Install dbt-core and the Snowflake adapter
python -m pip install --upgrade pip
python -m pip install dbt-core dbt-snowflake
```

#### Verify Installation

Check that dbt is installed correctly:

```bash
dbt --version
```

You should see output showing dbt-core and the snowflake plugin:

```
installed version: 1.8.0
   latest version: 1.8.0

Plugins:
  - snowflake: 1.8.0
```

#### Configure dbt Profile

The project includes a `profiles.yml` file in the `tasty_bytes_dbt_demo` directory. You'll need to update it with your Snowflake credentials to enable dbt Core to communicate with Snowflake.

**Important**: The `profiles.yml` file is only needed for dbt Core. If you're using dbt Cloud, you can skip this configuration.

##### Authentication

dbt supports multiple authentication methods for Snowflake, for the sake of this hackathon, we will use password authentication

Update your `tasty_bytes_dbt_demo/profiles.yml`:

```yaml
tasty_bytes_dbt_demo:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: [your_account_id]  # e.g., abc123.us-east-1
      user: [your_username]
      password: [your_password]
      role: [your_role]           # e.g., your custom role
      database: TASTY_BYTES_DBT_DB
      warehouse: TASTY_BYTES_DBT_WH
      schema: DEV
      threads: 4
      client_session_keep_alive: False
```

##### Test Your Connection

After configuring your profile, test the connection:

```bash
cd tasty_bytes_dbt_demo
dbt debug
```

You should see a successful connection message. If you encounter errors, verify:
- Your credentials are correct
- The warehouse, database, and schema exist
- Your user has the necessary permissions


Then simply run `dbt_env` to activate your environment.

---

### Step 5: Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Description | Example |
|------------|-------------|---------|
| `SNOWFLAKE_ACCOUNT` | Your Snowflake account identifier | `abc12345.us-east-1` |
| `SNOWFLAKE_USER` | Your Snowflake username | `GITHUB_ACTIONS_USER` |
| `SNOWFLAKE_WAREHOUSE` | Warehouse to use | `TASTY_BYTES_DBT_WH` |
| `SNOWFLAKE_PK` | Your private key content | Paste the entire `rsa_key.p8` file content |

## 💡 Your Mission: Build the Stored Procedure

Now for the fun part! You need to create a stored procedure called `generate_pr_description()` that:

### Input Parameters

The procedure should accept four parameters:

```sql
CREATE OR REPLACE PROCEDURE generate_pr_description(
    PR_TITLE STRING,
    PR_COMMITS STRING,
    PR_DIFF STRING,
    FEATURE_BRANCH STRING
)
RETURNS STRING
LANGUAGE PYTHON
...
```

### Requirements

Your stored procedure must:

#### 1. 🔍 Identify Changed SQL Files

Parse the PR details to identify which SQL files have been modified in the feature branch.

**Hint**: You might need to use the `PARSE_JSON()` or string parsing functions. The `PR_DIFF` URL points to the GitHub diff, which you could fetch using Snowflake's external access capabilities.

#### 2. 🏃‍♀️ Execute SQL from Both Branches

For each changed SQL file:

- Execute the SQL from the `main` branch
- Execute the SQL from the feature branch
- Capture sample results from both (e.g., `SAMPLE(100 ROWS)`)

**Considerations**:
- How will you safely execute dynamic SQL?
- How will you handle different types of SQL statements (SELECT, CREATE, INSERT)?
- What schemas should you use for testing?

#### 3. 📊 Compare Results

Compare the sample results between `main` and feature branch:

- Identify schema changes (new/removed columns)
- Detect data differences
- Highlight significant variations

**Ideas**:
- Use Snowflake's built-in functions like `ARRAY_AGG()`, `OBJECT_CONSTRUCT()`, or `TO_JSON()`
- Consider statistical differences (row counts, distinct values, NULL percentages)
- Think about what information would be most valuable in a PR description

#### 4. 🤖 Generate PR Description with Cortex AI

Use **Snowflake Cortex LLM functions** to generate a comprehensive PR description:

```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    '<model_name>',
    '<your_prompt>'
)
```

Your prompt should include:
- PR title
- Commit messages
- Summary of SQL changes
- Comparison results
- Feature branch name

#### 5. 📤 Return the Description

Return a well-formatted string that includes:

- 📋 **Summary**: High-level overview of changes
- 🔧 **Technical Details**: What SQL files changed and how
- 📊 **Impact Analysis**: Results comparison between branches
- ✅ **Testing Notes**: What was validated
- 🎯 **Recommendations**: Any suggestions for reviewers

## 🧪 Testing Your Solution

To test your stored procedure locally:

```sql
-- Example test call
CALL generate_pr_description(
    'Add customer engagement scoring',
    'feat: add engagement score calculation\nUpdate customer_loyalty_metrics model',
    'https://github.com/your-repo/pull/123.diff',
    'feature/add-engagement-score'
);
```

## 📚 Helpful Resources

- [Snowflake AI_COMPLETE() Function](https://docs.snowflake.com/en/sql-reference/functions/ai_complete-prompt-object)
- [Snowflake PROMPT() Function](https://docs.snowflake.com/en/sql-reference/functions/prompt)
- [Snowflake Python Stored Procedures](https://docs.snowflake.com/en/sql-reference/stored-procedures-python)
- [Snowflake Python Stored Procedures (Examples)](https://docs.snowflake.com/en/developer-guide/stored-procedure/python/procedure-python-examples)

## 🤝 Tips for Success

1. **Start Simple**: Get a basic version working first, then iterate
2. **Use Logging**: Leverage Python's logging or Snowflake's query history
3. **Error Handling**: Wrap everything in try/except blocks
4. **Test Incrementally**: Test each component separately before combining
5. **Read the Docs**: Cortex AI prompts are an art - experiment with different formats
6. **Collaborate**: This is a hackathon - share ideas with your team!