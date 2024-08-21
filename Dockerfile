# First stage: Fetch GitHub repositories
FROM python:3.10-slim AS fetch_stage

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY fetch_repos.py ./
COPY .env .env

# Run the script to fetch GitHub repositories
RUN ["python", "fetch_repos.py"]

# Second stage: Push repositories to Gitea
FROM python:3.10-slim AS push_stage

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY push_to_gitea.py ./
COPY --from=fetch_stage /app/all_repos.txt ./all_repos.txt
COPY .env .env

# Command to push repositories to Gitea
CMD ["python", "push_to_gitea.py"]
