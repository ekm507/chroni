"""
Click-based CLI commands for Chroni version control system.
"""

import click
import os
from core.tracker import Tracker
from core.scanner import Scanner
from core.restore import Restorer
from core.snapshot import SnapshotManager
from db.schema import init_database
from utils.paths import resolve_path

@click.group()
@click.pass_context
def cli(ctx):
    """Chroni - A lightweight local version control system."""
    # Initialize database on first run
    init_database()

    # Set up context
    ctx.ensure_object(dict)
    ctx.obj['tracker'] = Tracker()
    ctx.obj['scanner'] = Scanner()
    ctx.obj['restorer'] = Restorer()
    ctx.obj['snapshot_manager'] = SnapshotManager()

@cli.command()
@click.argument('path')
@click.pass_context
def track(ctx, path):
    """Start tracking file or folder."""
    abs_path = resolve_path(path)
    if not os.path.exists(abs_path):
        click.echo(f"Error: Path '{path}' does not exist.")
        return

    tracker = ctx.obj['tracker']
    if tracker.track_path(abs_path):
        click.echo(f"Now tracking: {path}")
    else:
        click.echo(f"Already tracking: {path}")

@cli.command()
@click.argument('path')
@click.pass_context
def untrack(ctx, path):
    """Stop tracking, but keep history."""
    abs_path = resolve_path(path)
    tracker = ctx.obj['tracker']
    if tracker.untrack_path(abs_path):
        click.echo(f"Stopped tracking: {path}")
    else:
        click.echo(f"Not currently tracking: {path}")

@cli.command()
@click.argument('path')
@click.pass_context
def forget(ctx, path):
    """Remove all history of path."""
    abs_path = resolve_path(path)
    tracker = ctx.obj['tracker']
    if tracker.forget_path(abs_path):
        click.echo(f"Removed all history for: {path}")
    else:
        click.echo(f"No history found for: {path}")

@cli.command()
@click.pass_context
def list(ctx):
    """List tracked files/folders."""
    tracker = ctx.obj['tracker']
    tracked_items = tracker.list_tracked()

    if not tracked_items:
        click.echo("No files or folders are currently being tracked.")
        return

    click.echo("Currently tracked items:")
    for item in tracked_items:
        click.echo(f"  {item}")

@cli.command()
@click.pass_context
def scan(ctx):
    """Scan for changes and store diffs."""
    scanner = ctx.obj['scanner']
    changes = scanner.scan_all()

    if not changes:
        click.echo("No changes detected.")
        return

    click.echo(f"Detected {len(changes)} changes:")
    for change in changes:
        click.echo(f"  {change}")

@cli.command()
@click.argument('path')
@click.option('--ver', type=int, required=True, help='Version number to restore')
@click.pass_context
def restore(ctx, path, ver):
    """Restore a file to specific version."""
    abs_path = resolve_path(path)
    restorer = ctx.obj['restorer']

    if restorer.restore_file(abs_path, ver):
        click.echo(f"Restored {path} to version {ver}")
    else:
        click.echo(f"Failed to restore {path} to version {ver}")

@cli.command('snapshot-create')
@click.argument('name')
@click.option('--note', help='Optional note for the snapshot')
@click.pass_context
def snapshot_create(ctx, name, note):
    """Create a named snapshot of the current state."""
    snapshot_manager = ctx.obj['snapshot_manager']

    if snapshot_manager.create_snapshot(name, note):
        click.echo(f"Created snapshot: {name}")
    else:
        click.echo(f"Failed to create snapshot: {name}")

@cli.command('snapshot-list')
@click.pass_context
def snapshot_list(ctx):
    """List all snapshots."""
    snapshot_manager = ctx.obj['snapshot_manager']
    snapshots = snapshot_manager.list_snapshots()

    if not snapshots:
        click.echo("No snapshots found.")
        return

    click.echo("Snapshots:")
    for snapshot in snapshots:
        note_text = f" - {snapshot['note']}" if snapshot['note'] else ""
        click.echo(f"  {snapshot['name']} ({snapshot['timestamp']}){note_text}")

@cli.command('snapshot-restore')
@click.argument('name')
@click.pass_context
def snapshot_restore(ctx, name):
    """Restore all files to a snapshot state."""
    snapshot_manager = ctx.obj['snapshot_manager']

    if snapshot_manager.restore_snapshot(name):
        click.echo(f"Restored to snapshot: {name}")
    else:
        click.echo(f"Failed to restore snapshot: {name}")

@cli.command('history')
@click.argument('path')
@click.option('--limit', type=int, help='Limit number of versions to show')
@click.pass_context
def history(ctx, path, limit):
    """Show full history of a file."""
    from core.history import HistoryViewer

    abs_path = resolve_path(path)
    history_viewer = HistoryViewer()

    versions = history_viewer.get_file_history(abs_path, limit)

    if not versions:
        click.echo(f"No history found for: {path}")
        return

    click.echo(f"History for: {path}")
    click.echo("=" * 50)

    for version in versions:
        click.echo(f"Version {version['version']} - {version['formatted_timestamp']}")
        if version['diff']:
            click.echo("  Changes:")
            for line in version['diff'].split('\n')[:5]:  # Show first 5 lines of diff
                if line.strip():
                    click.echo(f"    {line}")
            if len(version['diff'].split('\n')) > 5:
                click.echo("    ...")
        click.echo()

@cli.command('show')
@click.argument('path')
@click.option('--ver', type=int, help='Show specific version (default: latest)')
@click.pass_context
def show(ctx, path, ver):
    """Show latest version or specific version of a file."""
    from core.history import HistoryViewer

    abs_path = resolve_path(path)
    history_viewer = HistoryViewer()

    if ver:
        version_info = history_viewer.get_file_version_info(abs_path, ver)
        if not version_info:
            click.echo(f"Version {ver} not found for: {path}")
            return

        click.echo(f"File: {path} (Version {ver})")
        click.echo(f"Date: {version_info['formatted_timestamp']}")
        click.echo("=" * 50)
        click.echo(version_info['content'])
    else:
        # Show latest version
        latest = history_viewer.get_latest_version_info(abs_path)
        if not latest:
            click.echo(f"No versions found for: {path}")
            return

        click.echo(f"File: {path} (Latest - Version {latest['version']})")
        click.echo(f"Date: {latest['formatted_timestamp']}")
        click.echo("=" * 50)
        click.echo(latest['content'])

@cli.command('restore-date')
@click.argument('path')
@click.argument('date')
@click.pass_context
def restore_date(ctx, path, date):
    """Restore a file to the version closest to a specific date."""
    from core.history import HistoryViewer

    abs_path = resolve_path(path)
    history_viewer = HistoryViewer()
    restorer = ctx.obj['restorer']

    version = history_viewer.find_version_by_date(abs_path, date)

    if not version:
        click.echo(f"No version found for date '{date}' for file: {path}")
        return

    if restorer.restore_file(abs_path, version['version']):
        click.echo(f"Restored {path} to version {version['version']} from {version['formatted_timestamp']}")
    else:
        click.echo(f"Failed to restore {path}")

@cli.command('watch')
@click.pass_context
def watch(ctx):
    """Watch tracked paths for changes and auto-scan."""
    from core import watcher
    watcher.start_watching()
    pass

if __name__ == '__main__':
    cli()
