import click
import requests
import json
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

@click.group()
def cli():
    """CLI for GitHub Repository Monitoring"""
    pass

@cli.command()
@click.argument('repo_url')
def subscribe(repo_url):
    """Subscribe to a GitHub repository"""
    response = requests.post(f"{BASE_URL}/subscribe", json={"repo_url": repo_url})
    click.echo(response.json()["message"])

@cli.command()
@click.argument('repo_url')
def unsubscribe(repo_url):
    """Unsubscribe from a GitHub repository"""
    response = requests.post(f"{BASE_URL}/unsubscribe", json={"repo_url": repo_url})
    if response.status_code == 200:
        click.echo(response.json()["message"])
    else:
        click.echo(f"Error: {response.json()['detail']}")

@cli.command()
def list_subscriptions():
    """List all subscribed repositories"""
    response = requests.get(f"{BASE_URL}/subscriptions")
    subscriptions = response.json()
    if subscriptions:
        click.echo("Subscribed repositories:")
        for repo in subscriptions:
            click.echo(f"- {repo}")
    else:
        click.echo("No subscriptions found.")

@cli.command()
def get_info():
    """Get information for all subscribed repositories"""
    response = requests.get(f"{BASE_URL}/github-info")
    if response.status_code == 200:
        try:
            info = response.json()
            if isinstance(info, dict) and "message" in info:
                click.echo(info["message"])
            else:
                for repo_url, repo_info in info.items():
                    click.echo(f"\nRepository: {repo_url}")
                    click.echo(json.dumps(repo_info, indent=2))
        except json.JSONDecodeError as e:
            click.echo(f"Error decoding JSON response: {str(e)}")
            click.echo(f"Raw response: {response.text}")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")



@cli.command()
@click.argument('repo_url')
def update(repo_url):
    """Get latest information for a specific repository"""
    response = requests.post(f"{BASE_URL}/update/{repo_url}")
    if response.status_code == 200:
        click.echo(json.dumps(response.json(), indent=2))
    else:
        click.echo(f"Error: {response.json()['detail']}")
