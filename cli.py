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

if __name__ == '__main__':
    cli()