import subprocess
import tldextract
import argparse

import shlex
import json


def run_command(cmd):
    try:
        return subprocess.run(
            shlex.split(cmd), check=True, capture_output=True, text=True
        ).stdout
    except subprocess.CalledProcessError as e:
        # print(e)
        raise


def domain_parts(item: dict):
    """Get top level domain."""
    if not "domain_parts" in item:
        item["domain_parts"] = [tldextract.extract(url["href"]) for url in item["urls"]]
    return item["domain_parts"]


def domains(item):
    s = set()
    for d in domain_parts(item):
        if d.subdomain == "www":
            d = (d.domain, d.suffix)
        s.add(".".join(p for p in d if p))
    return s


def root_domains(item) -> set:
    """Return a set of domain names linked to the item."""
    return set(
        ".".join(p for p in (d.domain, d.suffix) if p) for d in domain_parts(item)
    )


def username(item):
    return item.get("additional_information", None)


def password(item):
    cmd = f"op read op://{item['vault']['name']}/{item['id']}/password"
    try:
        return run_command(cmd)
    except subprocess.CalledProcessError:
        print(f"Exception while getting password for {item['title']}")


def otp(item):
    cmd = f"op item get {item['id']} --otp"
    try:
        result = int(run_command(cmd).strip("\n"))
    except subprocess.CalledProcessError:
        return None
    return result


def details(item):
    if not "details" in item:
        item["details"] = json.loads(
            run_command(
                f'op get item {item["id"]} --fields "username,password,one-time password"'
            )
        )
    return item["details"]


def delete(item):
    """Delete / archive the item in 1Password."""
    if dry_run:
        print(
            f'To delete duplicate item {item["title"]}, username {username(item)}, with password {password(item)} in vault {item["vault"]["name"]} for site{"s" if len(domains(item)) > 1 else ""} {", ".join(domains(item))}, run again without the dry run flag.'
        )
        item["trashed"] = "Y"
        return None
    if prompt:
        confirm = input(
            f'Are you sure you want to delete duplicate item {item["title"]}, username {username(item)}, password {password(item)} in vault {item["vault"]["name"]} for site{"s" if len(domains(item)) > 1 else ""} {", ".join(domains(item))}? (Y/n): '
        )
        if confirm.upper() != "Y":
            return None
    if archive:
        verb = "Archived"
        run_command(f'op item delete {item["id"]} --archive')
    else:
        run_command(f'op item delete {item["id"]}')
        verb = "Deleted"
    print(
        f'{verb} duplicate item {item["title"]}, username {username(item)} for site{"s" if len(domains(item)) > 1 else ""} {", ".join(domains(item))}'
    )
    item["trashed"] = "Y"


def run(items: list):
    uniq = {}

    for new_item in items:
        if "trashed" in new_item:
            continue

        if not "urls" in new_item:
            continue

        if ignore_favorites and new_item.get("favorite", False):
            continue

        for domain_name in root_domains(new_item):
            try:
                # Get item from 'uniq' if it already exists.
                existing_item = uniq[(domain_name, username(new_item))]
            except KeyError:
                # Not in 'uniq'. Add to 'uniq'.
                uniq[(domain_name, username(new_item))] = new_item
                continue

            # If it's already marked as trashed, continue.
            if existing_item.get("trashed", None) == "Y":
                continue

            if domains(new_item) != domains(existing_item) and password(
                new_item
            ) != password(existing_item):
                continue

            # Keep the account with OTP or a longer password
            if (otp(new_item) and not otp(existing_item)) or (
                len(password(new_item)) > len(password(existing_item))
            ):
                uniq[(domain_name, username(existing_item))] = new_item
                delete(existing_item)
            else:
                delete(new_item)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove duplicate logins from your 1Password vault"
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Output the items to be removed without actually removing them",
    )
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Don't prompt for delete confirmation"
    )
    parser.add_argument(
        "--vault",
        metavar="[vault id]",
        help="Only search for duplicates in the specified vault",
    )
    parser.add_argument(
        "--tag",
        metavar="[tag id]",
        action="append",
        help="Only search for duplicates with the specified tags",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Archive duplicates instead of deleting them",
    )
    parser.add_argument(
        "--ignore-favorites",
        action="store_true",
        help="Ignore favorites",
    )

    args = parser.parse_args()
    dry_run = args.dry_run
    prompt = not args.yes
    archive = args.archive
    ignore_favorites = args.ignore_favorites

    cmd = "op item list --categories Login --format=json"
    if args.vault:
        cmd += f" --vault {args.vault}"
    if args.tag:
        cmd += f' --tags {",".join(args.tag)}'
    items = json.loads(run_command(cmd))

    run(items)
    print("Finished.")
