# 1Password Deduplicator
Deletes duplicate login items in 1Password. 

Based on the script originally made by [pauladams8](https://gist.github.com/pauladams8/1df2783103ee1594e7e82b3d9d182785).

Items are considered dupes if all the folowing are true:
* the domain of the URLs match (1Pass does not look at the whole URL when suggesting a password, only the domain)
* the usernames match.

Determining which to keep is based on the following rules (in order):
* If only one item has a one-time-password, it is preferred.
* If there is a modified date for both items, then the item with the most recently modified date is preferred (old versions of 1Pass did not record this)
* The item with a longer password is preferred.

## Setup
```
# Install the 1Password CLI if you don't already have it
brew install --cask 1password/tap/1password-cli

# Download and setup
git clone git@github.com:Ben-Hampson/1Password-Deduplicator.git
cd 1Password-Deduplicator
pip install -r requirements.txt

# Run it
python -m 1password_deduplicator --dry-run
```

## Options
```
--ignore-favorites - Ignores favourited login items.
--archive          - Archives items instead of deleting them.
--dry-run          - Tells you which items it would delete but doesn't delete them.
-y                 - Doesn't prompt before deleting / archiving.
--tag <tag>        - Only looks for duplicates with the given tag. (untested)
--vault <vault>    - Only looks for duplicates in the given vault. (untested)
```
