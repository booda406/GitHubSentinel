from fastapi import APIRouter, HTTPException
import requests
from datetime import datetime
from pydantic import BaseModel
import aiohttp
import asyncio
import os

router = APIRouter()

# 簡單的內存存儲
subscriptions = set()

class Subscription(BaseModel):
    repo_url: str

@router.post("/subscribe")
async def subscribe(subscription: Subscription):
    subscriptions.add(subscription.repo_url)
    return {"message": f"Subscribed to {subscription.repo_url}"}

@router.post("/unsubscribe")
async def unsubscribe(subscription: Subscription):
    if subscription.repo_url in subscriptions:
        subscriptions.remove(subscription.repo_url)
        return {"message": f"Unsubscribed from {subscription.repo_url}"}
    raise HTTPException(status_code=404, detail="Subscription not found")

@router.get("/subscriptions")
async def get_subscriptions():
    return list(subscriptions)

async def fetch_repo_info(repo_url: str):
    try:
        # 獲取倉庫信息
        repo_response = requests.get(repo_url)
        repo_data = repo_response.json()

        # 獲取最新的提交
        commits_url = f"{repo_url}/commits"
        commits_response = requests.get(commits_url)
        commits_data = commits_response.json()

        # 獲取最新的版本標籤
        tags_url = f"{repo_url}/tags"
        tags_response = requests.get(tags_url)
        tags_data = tags_response.json()

        # 生成報告
        report = {
            "name": repo_data["name"],
            "description": repo_data["description"],
            "stars": repo_data["stargazers_count"],
            "forks": repo_data["forks_count"],
            "open_issues": repo_data["open_issues_count"],
            "latest_commit": {
                "message": commits_data[0]["commit"]["message"],
                "author": commits_data[0]["commit"]["author"]["name"],
                "date": commits_data[0]["commit"]["author"]["date"]
            },
            "latest_version": tags_data[0]["name"] if tags_data else "No tags found",
            "report_generated_at": datetime.now().isoformat()
        }

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/github-info")
async def get_github_info():
    try:
        subscriptions = await get_subscriptions()
        
        if not subscriptions:
            return {"message": "No subscriptions found"}

        async with aiohttp.ClientSession() as session:
            tasks = []
            for repo_url in subscriptions:
                # 從完整的 GitHub URL 中提取所有者和存儲庫名稱
                parts = repo_url.split('github.com/')
                if len(parts) == 2:
                    owner_repo = parts[1].strip('/')
                    api_url = f"https://api.github.com/repos/{owner_repo}"
                    tasks.append(fetch_repo_info_async(session, api_url))
                else:
                    tasks.append(asyncio.sleep(0))  # 添加一個空任務

            results = await asyncio.gather(*tasks)

        info = {repo_url: result for repo_url, result in zip(subscriptions, results) if result is not None}
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



async def fetch_repo_info_async(session, repo_url: str):
    try:
        async with session.get(repo_url) as repo_response:
            if repo_response.status != 200:
                error_body = await repo_response.text()
                return {"error": f"Failed to fetch repo data. Status: {repo_response.status}, Body: {error_body}"}
            repo_data = await repo_response.json()

        commits_url = f"{repo_url}/commits"
        async with session.get(commits_url) as commits_response:
            if commits_response.status != 200:
                return {"error": f"Failed to fetch commits data. Status: {commits_response.status}"}
            commits_data = await commits_response.json()

        tags_url = f"{repo_url}/tags"
        async with session.get(tags_url) as tags_response:
            if tags_response.status != 200:
                return {"error": f"Failed to fetch tags data. Status: {tags_response.status}"}
            tags_data = await tags_response.json()

        report = {
            "name": repo_data.get("name", "N/A"),
            "description": repo_data.get("description", "N/A"),
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "open_issues": repo_data.get("open_issues_count", 0),
            "latest_commit": {
                "message": commits_data[0]["commit"]["message"] if commits_data else "N/A",
                "author": commits_data[0]["commit"]["author"]["name"] if commits_data else "N/A",
                "date": commits_data[0]["commit"]["author"]["date"] if commits_data else "N/A"
            },
            "latest_version": tags_data[0]["name"] if tags_data else "No tags found",
            "report_generated_at": datetime.now().isoformat()
        }

        return report

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}



@router.post("/update/{repo_url:path}")
async def update_repo(repo_url: str):
    if repo_url not in subscriptions:
        raise HTTPException(status_code=404, detail="Repository not subscribed")
    return await fetch_repo_info(f"https://api.github.com/repos/{repo_url}")
