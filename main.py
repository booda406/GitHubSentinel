import click
from cli.commands import cli as cli_commands
from cli.interactive import run_interactive_shell
import uvicorn
from api.main import app

@click.group()
def cli():
    pass

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind the server to')
@click.option('--port', default=8000, help='Port to bind the server to')
def run_server(host, port):
    """Run the FastAPI server"""
    uvicorn.run(app, host=host, port=port)

@cli.command()
def interactive():
    """Start interactive shell"""
    run_interactive_shell()

@cli.command()
def help():
    """Show help for all commands"""
    ctx = click.get_current_context()
    click.echo(ctx.parent.get_help())
    click.echo("\nGitHub commands:")
    click.echo(cli_commands.get_help(ctx))

cli.add_command(cli_commands, name="github")

if __name__ == '__main__':
    cli()
