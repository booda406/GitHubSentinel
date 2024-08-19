import cmd
import sys
from cli.commands import cli as cli_commands
import click

class GitHubMonitorShell(cmd.Cmd):
    intro = "Welcome to the GitHub Monitor shell. Type help or ? to list commands.\n"
    prompt = "(github-monitor) "

    def do_exit(self, arg):
        """Exit the shell"""
        print("Goodbye!")
        return True

    def do_EOF(self, arg):
        """Exit on EOF (Ctrl+D)"""
        print("Goodbye!")
        return True

    def do_subscribe(self, arg):
        """Subscribe to a GitHub repository"""
        self.run_command(['subscribe'] + arg.split())

    def do_unsubscribe(self, arg):
        """Unsubscribe from a GitHub repository"""
        self.run_command(['unsubscribe'] + arg.split())

    def do_list_subscriptions(self, arg):
        """List all subscribed repositories"""
        self.run_command(['list-subscriptions'])

    def do_get_info(self, arg):
        """Get information for all subscribed repositories"""
        self.run_command(['get-info'])

    def do_update(self, arg):
        """Get latest information for a specific repository"""
        self.run_command(['update'] + arg.split())

    def run_command(self, args):
        try:
            sys.argv = [''] + args
            cli_commands.main(standalone_mode=False)
        except click.exceptions.Exit:
            pass
        except Exception as e:
            print(f"Error: {str(e)}")

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

def run_interactive_shell():
    GitHubMonitorShell().cmdloop()
