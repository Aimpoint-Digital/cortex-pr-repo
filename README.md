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

### Step 4: Setup and Configure dbt Projects in Snowflake

#### Create a Workspace Connected to Your Git Repository

In this step, you'll create a workspace in Snowsight that is connected to your GitHub repository.

1. **Sign in to Snowsight**

2. **Navigate to Workspaces**
   - In the navigation menu, select **Projects » Workspaces**

3. **Create a New Workspace from Git**
   - Fork the following repo: `https://github.com/Snowflake-Labs/getting-started-with-dbt-on-snowflake/tree/main`
   - From the Workspaces list above the workspace files area, under **Create Workspace**, select **From Git repository**
   - For **Repository URL**, enter the URL of your GitHub repository; for example:
     ```
     https://github.com/my-github-account/getting-started-with-dbt-on-snowflake.git
     ```

4. **Configure Workspace Settings**
   - For **Workspace name**, enter `tasty_bytes_dbt` (or your preferred name)
   - Under **API integration**, select the name of the API integration that you created during setup (e.g., `TB_DBT_GIT_API_INTEGRATION`)

5. **Complete Authentication**
   - Select **Personal access token**
   - Under **Credentials secret**, select **Select database and schema**
   - Select the database from the list (e.g., `TASTY_BYTES_DBT_DB`)
   - Select the schema from the list (e.g., `INTEGRATIONS`) where you stored the API integration
   - Select **Select secret**, and then select your secret from the list (e.g., `tb_dbt_git_secret`)
   - Select **Create**

Snowflake will connect to your GitHub repository and open your new workspace. The `tasty_bytes_dbt_demo` folder contains the dbt project you'll work with.

#### Verify the profiles.yml File

Each dbt project folder in your Snowflake workspace must contain a `profiles.yml` file that specifies a target warehouse, database, schema, and role. The `type` must be set to `snowflake`. dbt requires an `account` and `user`, but these can be left with an empty or arbitrary string because the dbt project runs in Snowflake under the current account and user context.

#### Execute the dbt deps Command

The first command you must execute for any dbt project is `deps`, which updates the dependencies specified in your project's `packages.yml` file. Other commands will fail unless you have updated dependencies.

1. **Open the Output Tab**
   - Below the workspace editor, open the **Output** tab to see stdout after running dbt commands

2. **Select Project and Profile**
   - From the menu bar above the workspace editor, confirm that **tasty_bytes_dbt_demo** is selected as the Project
   - You can have any Profile selected (`dev` or `prod`)

3. **Run the deps Command**
   - From the command list, select **Deps**
   - Next to the execute button, select the down arrow
   - In the **dbt Deps** window, leave **Run with defaults** selected
   - Enter the name of the External Access Integration you created during setup (e.g., `dbt_ext_access`)
   - Select **Deps** to run the command

The Output tab will display SQL similar to:
```sql
execute dbt project from workspace "USER$"."PUBLIC"."tasty_bytes_dbt" 
project_root='tasty_bytes_dbt_demo' args='deps --target dev' 
external_access_integrations = (dbt_ext_access)
```

When the command finishes, you'll see stdout messages like:
```
14:47:19  Running with dbt=1.8.9
14:47:19  Updating lock file in file path: /tmp/dbt/package-lock.yml
14:47:19  Installing dbt-labs/dbt_utils
14:47:19  Installed from version 1.3.0
14:47:19  Up to date!
```

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
SELECT AI_COMPLETE(
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

## 👨‍💻 Stored Procedure

Modify the below stored procedure, including the above requirements:

```sql
CREATE OR REPLACE PROCEDURE TASTY_BYTES_DBT_DB.dev.generate_pr_description(
    PR_TITLE STRING,
    PR_COMMITS STRING,
    PR_DIFF STRING,
    FEATURE_BRANCH STRING
)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
HANDLER = 'main'
PACKAGES = ('snowflake-snowpark-python')
AS
$$
def main(session, pr_title, pr_commits, pr_diff, feature_branch):
    return "Hello world!"
$$;
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