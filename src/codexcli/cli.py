"""
Main CLI entry point for CodexCLI
"""
import os
import sys
from pathlib import Path
from typing import Optional
import click
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .agent import create_agent, CodexAgent
from .context import ConversationContext, ProjectContext
from .approval import ApprovalManager, ApprovalMode, parse_approval_mode
from .file_ops import FileOperations
from .shell import ShellExecutor
from .utils import print_info, print_success, print_error, print_warning, console


class CodexCLI:
    """Main CodexCLI application"""

    def __init__(
        self,
        provider: str = "openai",
        approval_mode: ApprovalMode = ApprovalMode.SUGGEST,
        project_root: Optional[Path] = None
    ):
        self.project_root = project_root or Path.cwd()
        self.approval_manager = ApprovalManager(approval_mode)
        self.context = ConversationContext()
        self.project_context = ProjectContext(self.project_root)
        self.file_ops = FileOperations(self.approval_manager, self.project_root)
        self.shell = ShellExecutor(self.approval_manager, self.project_root)

        try:
            self.agent = create_agent(provider=provider, context=self.context)
            print_success(f"Initialized with {provider} provider")
        except Exception as e:
            print_error(f"Failed to initialize agent: {e}")
            sys.exit(1)

    def run_interactive(self):
        """Run interactive mode"""
        from prompt_toolkit import prompt
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

        console.print(Panel.fit(
            "[bold cyan]CodexCLI - AI Coding Assistant[/bold cyan]\n"
            "Type your requests or questions. Type 'exit', 'quit', or press Ctrl+D to exit.\n"
            "Type 'help' for available commands.",
            border_style="cyan"
        ))

        # Show current mode
        self.approval_manager.show_mode_info()

        history_file = self.project_root / ".codex_history"
        history = FileHistory(str(history_file)) if history_file else None

        while True:
            try:
                user_input = prompt(
                    ">>> ",
                    history=history,
                    auto_suggest=AutoSuggestFromHistory(),
                    multiline=False
                )

                if not user_input.strip():
                    continue

                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    self._handle_exit()
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'clear':
                    self.context.clear()
                    print_success("Conversation history cleared")
                    continue
                elif user_input.lower() == 'mode':
                    self.approval_manager.show_mode_info()
                    continue
                elif user_input.lower().startswith('mode '):
                    mode_str = user_input[5:].strip()
                    try:
                        new_mode = parse_approval_mode(mode_str)
                        self.approval_manager.set_mode(new_mode)
                    except Exception as e:
                        print_error(f"Invalid mode: {e}")
                    continue
                elif user_input.lower() == 'tree':
                    tree = self.file_ops.get_file_tree()
                    console.print(tree)
                    continue

                # Process user request
                self._process_request(user_input)

            except (KeyboardInterrupt, EOFError):
                self._handle_exit()
                break
            except Exception as e:
                print_error(f"Error: {e}")

    def run_single(self, prompt: str):
        """Run a single command"""
        self._process_request(prompt)

    def _process_request(self, user_input: str):
        """Process a user request"""
        # Get project context
        additional_context = self.project_context.get_context_summary()

        # Ask agent
        response = self.agent.ask(user_input, additional_context)

        if not response:
            print_error("Failed to get response from agent")
            return

        # Display response
        console.print("\n[bold green]Assistant:[/bold green]")
        md = Markdown(response)
        console.print(md)
        console.print()

        # Parse and execute actions
        actions = self.agent.parse_actions(response)

        if actions:
            print_info(f"Found {len(actions)} action(s) to execute")
            self._execute_actions(actions)

    def _execute_actions(self, actions: list):
        """Execute parsed actions"""
        for i, action in enumerate(actions, 1):
            console.print(f"\n[bold yellow]Action {i}/{len(actions)}:[/bold yellow]")

            action_type = action['type']

            if action_type == 'create_file':
                filepath = action['filepath']
                content = action['content']
                self.file_ops.create_file(filepath, content)

            elif action_type == 'edit_file':
                filepath = action['filepath']
                content = action['content']
                self.file_ops.edit_file(filepath, content)

            elif action_type == 'shell_command':
                command = action['command']
                self.shell.execute(command)

            else:
                print_warning(f"Unknown action type: {action_type}")

    def _show_help(self):
        """Show help information"""
        help_text = """
# CodexCLI Help

## Interactive Commands

- **exit, quit, q** - Exit the program
- **help** - Show this help message
- **clear** - Clear conversation history
- **mode** - Show current approval mode
- **mode <mode>** - Set approval mode (suggest/auto/full)
- **tree** - Show project file tree

## Approval Modes

- **suggest** - Ask for approval on all operations (default)
- **auto** or **auto_edit** - Auto-approve file edits, ask for commands
- **full** or **full_auto** - Auto-approve all operations (use with caution!)

## Usage Examples

- "Create a Python file that calculates fibonacci numbers"
- "Read setup.py and tell me what dependencies are needed"
- "Add error handling to main.py"
- "Run the tests"
- "Show me the project structure"

## Tips

- The AI can read, create, and edit files
- It can execute shell commands with your approval
- Conversation history is maintained for context
- Use specific instructions for better results
"""
        console.print(Markdown(help_text))

    def _handle_exit(self):
        """Handle exit"""
        self.context.save_to_history()
        print_success("Goodbye!")


@click.group(invoke_without_command=True)
@click.option('--provider', type=click.Choice(['openai', 'anthropic']),
              default=None, help='LLM provider to use')
@click.option('--mode', type=click.Choice(['suggest', 'auto', 'full']),
              default='suggest', help='Approval mode')
@click.pass_context
def cli(ctx, provider, mode):
    """CodexCLI - AI-powered coding assistant"""
    # Load environment variables
    load_dotenv()

    # Get provider from env if not specified
    if provider is None:
        provider = os.getenv('DEFAULT_PROVIDER', 'openai')

    # Parse approval mode
    approval_mode = parse_approval_mode(mode)

    # Create CLI instance
    ctx.obj = CodexCLI(provider=provider, approval_mode=approval_mode)

    # If no subcommand, run interactive mode
    if ctx.invoked_subcommand is None:
        ctx.obj.run_interactive()


@cli.command()
@click.argument('prompt', nargs=-1, required=True)
@click.pass_obj
def ask(cli_obj, prompt):
    """Ask a single question or give a single command"""
    prompt_text = ' '.join(prompt)
    cli_obj.run_single(prompt_text)


@cli.command()
@click.pass_obj
def tree(cli_obj):
    """Show project file tree"""
    tree_output = cli_obj.file_ops.get_file_tree()
    console.print(tree_output)


@cli.command()
@click.pass_obj
def clear(cli_obj):
    """Clear conversation history"""
    cli_obj.context.clear()
    print_success("Conversation history cleared")


@cli.command()
@click.pass_obj
def info(cli_obj):
    """Show current session information"""
    console.print("\n[bold]Session Information[/bold]")
    console.print(f"Project: {cli_obj.project_root}")
    console.print(f"Provider: {cli_obj.agent.provider.__class__.__name__}")
    console.print(f"Model: {cli_obj.agent.provider.model}")
    console.print()
    cli_obj.approval_manager.show_mode_info()
    console.print()
    console.print(cli_obj.context.get_summary())


def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        print_info("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
