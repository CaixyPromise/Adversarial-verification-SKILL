#!/usr/bin/env python3
"""Review CLI and explicit, verified Skill updates. Python 3.9+ standard library."""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
REPO = "CaixyPromise/Adversarial-verification-SKILL"
RAW = "https://raw.githubusercontent.com/" + REPO + "/"
MAIN_MANIFEST = RAW + "main/skill-version.json"
COMMITS = "https://api.github.com/repos/" + REPO + "/commits/main"
ARCHIVES = "https://codeload.github.com/" + REPO + "/tar.gz/"
HOSTS = {"raw.githubusercontent.com", "api.github.com", "codeload.github.com"}
TTL = 24 * 3600
MAX_DOWNLOAD = 16 * 1024 * 1024
MAX_EXPANDED = 30 * 1024 * 1024
SHA_PATTERN = re.compile(r"^[a-f0-9]{40}$")
VERSION_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def parse_version(value):
    if not isinstance(value, str) or not VERSION_PATTERN.fullmatch(value):
        raise ValueError("Expected a version formatted X.Y.Z")
    return tuple(int(x) for x in value.split("."))


def manifest(path=None):
    path = path or ROOT / "skill-version.json"
    if not path.exists():
        return {"version": "0.2.0"}  # Installed version before this CLI was added.
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or obj.get("repository") != REPO:
        raise ValueError("Unrecognized Skill version manifest")
    parse_version(obj.get("version"))
    return obj


def cache_root():
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache").expanduser() / "adversarial-verification"


def cache_file():
    return cache_root() / "update-check.json"


def load_cache():
    try:
        obj = json.loads(cache_file().read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except (OSError, ValueError):
        return {}


def write_cache(obj):
    folder = cache_root()
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=folder, prefix=".update-", delete=False) as f:
        json.dump(obj, f, separators=(",", ":"))
        name = Path(f.name)
    try:
        name.chmod(0o600)
        os.replace(name, cache_file())
    finally:
        name.unlink(missing_ok=True)


def fetch(url, limit=1024 * 1024, timeout=5):
    src = urllib.parse.urlsplit(url)
    if src.scheme != "https" or src.hostname not in HOSTS:
        raise ValueError("Untrusted update source")
    req = urllib.request.Request(url, headers={"User-Agent": "adversarial-verification-cli"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        dest = urllib.parse.urlsplit(response.geturl())
        if dest.scheme != "https" or dest.hostname not in HOSTS:
            raise ValueError("Untrusted update redirect")
        body = response.read(limit + 1)
    if len(body) > limit:
        raise ValueError("Remote update payload exceeds the size limit")
    return body


def fetch_json(url):
    obj = json.loads(fetch(url).decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("Unexpected GitHub JSON payload")
    return obj


def get_remote_version():
    obj = fetch_json(MAIN_MANIFEST)
    if obj.get("repository") != REPO:
        raise ValueError("Remote manifest identifies another repository")
    parse_version(obj.get("version"))
    return obj["version"]


def cache_remote(version, commit=None):
    state = {"checked_at": time.time(), "latest_version": version}
    if commit:
        state["latest_commit"] = commit
    write_cache(state)
    return state


def cached_notice():
    try:
        remote = load_cache().get("latest_version")
        if remote and parse_version(remote) > parse_version(manifest()["version"]):
            print("[av] Skill update " + remote + " available: run av update", file=sys.stderr)
    except (ValueError, OSError):
        pass


def background_worker():
    try:
        version = get_remote_version()
        cache_remote(version)
    except (OSError, ValueError, TimeoutError, urllib.error.URLError):
        # Record a bounded offline check, rather than retrying on every CLI call.
        state = load_cache()
        state["checked_at"] = time.time()
        try:
            write_cache(state)
        except OSError:
            pass
    finally:
        (cache_root() / ".update.lock").unlink(missing_ok=True)


def schedule_check():
    if os.environ.get("AV_DISABLE_UPDATE_CHECK", "").lower() in ("1", "true", "yes"):
        return
    try:
        checked = float(load_cache().get("checked_at", 0))
        if time.time() - checked < TTL:
            return
        folder = cache_root()
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        lock = folder / ".update.lock"
        if lock.exists() and time.time() - lock.stat().st_mtime > 40:
            lock.unlink(missing_ok=True)
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        try:
            subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "__worker"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, close_fds=True,
                start_new_session=(os.name != "nt"),
            )
        except OSError:
            lock.unlink(missing_ok=True)
    except (OSError, ValueError):
        pass  # Version checks must never block a report.


def check_update():
    remote = get_remote_version()
    state = cache_remote(remote)
    installed = manifest()["version"]
    print(json.dumps({
        "installed": installed, "latest": remote,
        "update_available": parse_version(remote) > parse_version(installed),
        "checked_at": state["checked_at"], "source": MAIN_MANIFEST
    }))
    return 0


def in_git_checkout(path):
    try:
        cmd = subprocess.run(["git", "-C", str(path), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
        if cmd.returncode:
            return False
        path.resolve().relative_to(Path(cmd.stdout.strip()).resolve())
        return True
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def extract_archive(blob, stage):
    """Extract only safe regular files from one trusted GitHub tar archive root."""
    prefix = None
    size = 0
    count = 0
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        for member in archive:
            count += 1
            if count > 500:
                raise ValueError("Archive contains too many entries")
            name = member.name
            if name.startswith("/") or "\\" in name:
                raise ValueError("Unsafe archive path")
            parts = PurePosixPath(name).parts
            if not parts or ".." in parts or ":" in parts[0]:
                raise ValueError("Unsafe archive path")
            if prefix is None:
                prefix = parts[0]
                if not prefix.startswith("Adversarial-verification-SKILL-"):
                    raise ValueError("Unexpected repository archive")
            if parts[0] != prefix:
                raise ValueError("Archive contains multiple root directories")
            if not (member.isfile() or member.isdir()):
                raise ValueError("Archive contains a link or special file")
            if len(parts) == 1:
                if not member.isdir():
                    raise ValueError("Unexpected file at archive root")
                continue
            dest = stage.joinpath(*parts[1:])
            if member.isdir():
                dest.mkdir(parents=True, exist_ok=True)
                continue
            size += member.size
            if member.size < 0 or size > MAX_EXPANDED:
                raise ValueError("Archive extraction exceeds the size limit")
            dest.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise ValueError("Unreadable archive entry")
            with source, dest.open("xb") as out:
                shutil.copyfileobj(source, out, length=64 * 1024)
            if dest.stat().st_size != member.size:
                raise ValueError("Truncated archive entry")
            # Preserve only normal executable bits, not archive-supplied special permissions.
            dest.chmod(0o755 if (member.mode & 0o111) else 0o644)
    for path in ("SKILL.md", "skill-version.json", "scripts/av.py",
                 "scripts/review_report.py", "templates/review-report.html"):
        if not (stage / path).is_file():
            raise ValueError("Missing required Skill file: " + path)
    return manifest(stage / "skill-version.json")["version"]


def update(yes=False, force=False):
    if not ROOT.is_dir() or ROOT.is_symlink():
        raise ValueError("The Skill directory is not a normal local directory")
    if in_git_checkout(ROOT):
        raise ValueError("Skill resides in a Git working tree; use git pull instead")
    previous = manifest()["version"]
    commit = fetch_json(COMMITS).get("sha")
    if not isinstance(commit, str) or not SHA_PATTERN.fullmatch(commit):
        raise ValueError("Invalid SHA returned by GitHub")
    pinned = fetch_json(RAW + commit + "/skill-version.json")
    if pinned.get("repository") != REPO:
        raise ValueError("The pinned update has an unexpected repository")
    latest = pinned.get("version")
    parse_version(latest)
    if parse_version(latest) < parse_version(previous):
        raise ValueError("Refusing to downgrade the Skill")
    if latest == previous and not force:
        print("Skill is already at the latest version: " + previous)
        return 0
    if not yes:
        if not sys.stdin.isatty():
            raise ValueError("Explicit noninteractive updates require --yes")
        answer = input("Update Skill " + previous + " -> " + latest + "? [y/N] ")
        if answer.strip().lower() not in ("y", "yes"):
            print("Update cancelled.")
            return 0
    downloaded = fetch(ARCHIVES + commit, limit=MAX_DOWNLOAD, timeout=20)
    stage = Path(tempfile.mkdtemp(prefix=".av-stage-", dir=ROOT.parent))
    backup = None
    try:
        actual = extract_archive(downloaded, stage)
        if actual != latest:
            raise ValueError("Pinned archive and version manifest do not match")
        backup = Path(tempfile.mkdtemp(prefix=".av-backup-", dir=ROOT.parent))
        backup.rmdir()
        os.replace(ROOT, backup)
        try:
            os.replace(stage, ROOT)
        except Exception:
            os.replace(backup, ROOT)
            backup = None
            raise
        try:
            cache_remote(latest, commit)
        except OSError:
            pass  # Installation succeeded even if the optional cache cannot be written.
        print("Updated " + previous + " -> " + latest)
        print("Previous Skill retained at: " + str(backup))
        print("Restart the coding agent to load the new Skill.")
        return 0
    finally:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)


def launcher_body(windows=False):
    """Return the platform launcher, preserving quoted paths with spaces."""
    script = str(ROOT / "scripts" / "av.py")
    if windows:
        # cmd.exe expands %% in batch files; doubling it preserves literal path values.
        executable = str(sys.executable).replace("%", "%%")
        script = script.replace("%", "%%")
        return ('@echo off\r\n'
                'REM Adversarial Verification launcher\r\n'
                '"' + executable + '" "' + script + '" %*\r\n'
                'exit /b %errorlevel%\r\n')
    import shlex
    return ("#!/bin/sh\n# Adversarial Verification launcher\nexec " +
            shlex.quote(sys.executable) + " " + shlex.quote(script) + ' "$@"\n')


def install_launcher(dest=None, windows=None):
    """Install a user-local av (POSIX) or av.cmd (Windows) launcher."""
    windows = (os.name == "nt") if windows is None else windows
    folder = Path(dest).expanduser() if dest else Path.home() / ".local" / "bin"
    folder.mkdir(parents=True, exist_ok=True)
    launcher = folder / ("av.cmd" if windows else "av")
    if launcher.is_symlink():
        raise ValueError("Refusing to overwrite a symbolic-link launcher: " + str(launcher))
    if launcher.exists():
        content = launcher.read_text(encoding="utf-8")
        if "Adversarial Verification launcher" not in content:
            raise ValueError("Refusing to replace another program at " + str(launcher))
    body = launcher_body(windows)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=folder,
                                     prefix=".av-", delete=False) as f:
        f.write(body)
        tmp = Path(f.name)
    try:
        os.replace(tmp, launcher)
    finally:
        tmp.unlink(missing_ok=True)
    if not windows:
        launcher.chmod(0o755)
    print("Installed " + str(launcher))
    print("Add the directory to PATH if necessary: " + str(folder))
    return 0


def run_report(options, project):
    import review_report
    old = sys.argv
    try:
        sys.argv = ["review_report.py", "--project", project, *options]
        return review_report.main()
    finally:
        sys.argv = old


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(prog="av", description="Review dossiers and Skill updates")
    parser.add_argument("--project", default=".", help="Project directory for reports")
    if "report" in argv:
        i = argv.index("report")
        opts = parser.parse_args(argv[:i])
        if not argv[i + 1:]:
            parser.error("report needs a subcommand (start, finding, fix, event, finish, render, show)")
        cached_notice()
        schedule_check()  # detached, bounded background work, never awaited
        return run_report(argv[i + 1:], opts.project)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("version")
    commands.add_parser("check-update")
    u = commands.add_parser("update")
    u.add_argument("--yes", action="store_true")
    u.add_argument("--force", action="store_true")
    ins = commands.add_parser("install-cli")
    ins.add_argument("--dest")
    commands.add_parser("__worker", help=argparse.SUPPRESS)
    opts = parser.parse_args(argv)
    if opts.action == "__worker":
        background_worker()
        return 0
    try:
        if opts.action == "version":
            print(manifest()["version"])
            return 0
        if opts.action == "check-update":
            return check_update()
        if opts.action == "update":
            return update(opts.yes, opts.force)
        if opts.action == "install-cli":
            return install_launcher(opts.dest)
    except (OSError, ValueError, TimeoutError, urllib.error.URLError, tarfile.TarError) as e:
        print("av: " + str(e), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
