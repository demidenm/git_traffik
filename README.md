# git traffik

**Situation**: GitHub [Insights → Traffic data](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-traffic-to-a-repository) only offers 14 days of visit/clone data.  
**Task**: A workflow is needed to access the repository every 10-14 days to pull the data and store it, retaining and expanding visitor/clone history.  
**Action**: `git_traffic` is a simple workflow that can be integrated directly within a repository, run in a separate repository to track another repo, or run locally.  
**Result**: Historical data >14 days in .csv format and visualized automatically for any repo.

## How Does it Work?

### 1. Running it via a cloned `git_traffik` repo.

[.github/workflows/repo.yaml](.github/workflows/repo.yaml):  
Includes fields for repository name [`REPO`], repository owner [`OWNER`], and the API key, [personal token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).  
The token provides read/write/pull/push access to the repository [`MY_ACCESS_TOKEN`]. The token is stored as a [SECRET KEY](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) for security.

To run, clone this repository and update the `.github/workflows/repo.yaml` file with your information, then monitor the actions.  
![repo info location](./images/repo_info.png)

You can, at any time, manually trigger the workflow.  
![Workflow actions example](./images/git_actions.png)

You can also modify the [cron schedule](https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html).  
![cron schedule](./images/cron_schedule.png)

When a workflow is completed, it will indicate this with a green checkmark. You can review the steps within it for specific details. Set up some manual and automated (timed) tests to ensure everything is working.  
![Workflow complete example](./images/workflow_completion.png)

The results will then be populated in the `./git_traffik/output` folder for the given repo in .csv and .png formats.  
![results output example](./images/results_example.png)

You can download and/or view the compiled data in the .csv file or as an image:  
![Example PyReliMRI Traffic Data Plot](./git_traffik/output/PyReliMRI_traffic-data.png)

**Note:**

1. For the code to work, the token should have repository privileges.
2. For the code to run, ensure the repo where actions are being performed (e.g., `git_traffik`) has Settings → Actions → General → Workflow Permissions set to _Read and write permissions_.

### 2. Running it within your package/software repo

To run `git_traffik` within your package repo, copy the `git_traffik` folder to the root directory and place the `.github/workflows/repo.yaml` file in your `.github/workflows` folder. As with #1, update the repo details in the .yaml file and insert the two secret keys with your personal token.  
![repo info location](./images/repo_info.png)  
![git token info](./images/git_token.png)

**Note:**

1. For the code to work, the token should have repository privileges.
2. For the code to run, ensure the repo where actions are being performed (e.g., `<repo_name>`) has Settings → Actions → General → Workflow Permissions set to _Read and write permissions_.

### 3. Running it locally on your machine

To run it locally, you will only need the [./git_traffik/repo_check_traffic.py](./git_traffik/repo_check_traffic.py) script. Since it is running locally, you can avoid secret keys, but you will still need a [personal token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) with repo permissions. Update the owner, repo, and token information with your own:  
![local run updates](./images/git-traffik_local.png)

Then, either run the Python script to generate the data or write a bash script to call the Python code. If your machine is on most days of the week, you can set a schedule using [crontab](https://phoenixnap.com/kb/cron-job-mac) to run it on a set schedule. Test to ensure it works.

## More Specific Details of the Code

[.github/workflows/repo.yaml](.github/workflows/repo.yaml):

This YAML file defines a GitHub Actions workflow named "Repo Data & Figures" that performs the following tasks:

- **Schedule/Trigger**: Runs on the 1st, 11th, and 21st of every month at midnight (UTC) & can be triggered manually. It uses [cron syntax](https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html).
- **Job**: `update-data` runs on Ubuntu and includes these steps:
  - **Checkout Code**: Retrieves the repository code within `git_traffik`.
  - **Setup Python**: Configures Python 3.9.
  - **Install Dependencies**: Installs dependencies in [./git_traffik/repo_check_traffic.py](./git_traffik/repo_check_traffic.py), such as `requests`, `pandas`, `matplotlib`, and `seaborn`.
  - **Run Script**: Gathers data and generates figures:
    - **Setup**: Configures owner, repo name, and personal access token based on the [repo.yaml](.github/workflows/repo.yaml) file.
    - **Data Retrieval**: Fetches views and clones data from the GitHub API. Converts data to DataFrames and merges clones/views data. Keeps only unique dates and excludes dates when both clones/views are 0. Ensures unique timestamps and fills missing values.
    - **CSV Handling**: Updates the existing .csv file if present; otherwise, creates a new .csv file with the traffic data.
    - **Plotting**: Generates plots for views and clones over time in a two-panel figure.
    - **Saving**: Saves the plots as .csv and PNG files.
  - **List Files**: Displays the contents generated in the output directory.
  - **Upload Output Files**: Uploads output files from the output directory as artifacts (saved as a .zip for each workflow).
  - **Configure Git**: Configures Git using a generic username and email.
  - **Check Git Status**: Checks the repository for changes (if hashes are identical, no changes).
  - **Add Files**: Stages output files for commit to the [./output/](./output/) directory.
  - **Commit Files**: Commits files with a message if any changes exist.

This workflow ensures that data and figures are updated regularly and consistently in the repository.

## Example Using [PyReliMRI](https://github.com/demidenm/PyReliMRI) Package

I created a small package that I wanted to observe the fluctuations in usage. It helps me determine whether people are using it and if I should consider maintaining and expanding it. Unfortunately, I discovered very quickly that the first 4-5 months of data were lost. I needed something more consistent.

### Essentials to Update in [repo.yaml](.github/workflows/repo.yaml)

These are called as variables into the .py code for use with the API:

- **OWNER**: Update the GitHub repository owner to your name or whoever has access and has granted you repo privileges.
- **REPO**: Update the repository name (in my case, it is `PyReliMRI`).
- **MY_ACCESS_TOKEN**: This is the token to access the data, and it needs to be private. In the `repo_trafficplots` repo, go to Settings → Secrets & Variables → Actions and create a [New Repository Secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) with your Personal Token. You can create one for yourself by following these [instructions](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).

Once this is set up, the Actions are triggered via the event trigger (cron details). You can review all runs and the associated logs. When the figures are created, they are updated in [./git_traffik/output/](./git_traffik/output/). The figure below is compiled based on the [running data](./git_traffik/output/PyReliMRI_git-trafficdata.csv).
