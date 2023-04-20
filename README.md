# 1Password Deduplicator
Deletes duplicate login items in 1Password.

It looks at the URL and username of login items. If two items have the same URL and username, it will delete one of the items. Login items with OTP or a longer password are kept and the other is deleted.

## Setup
```
# Install the 1Password CLI if you don't already have it
brew install --cask 1password/tap/1password-cli

# Download and setup
git clone git@github.com:Ben-Hampson/1Password-Deduplicator.git
cd 1Password-Deduplicator
pip install -r requirements.txt

# Run it
python -m 1password_deduplicator -d
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

## Credit
Originally created by [pauladams8](https://gist.github.com/pauladams8/1df2783103ee1594e7e82b3d9d182785). I've made it work with the latest version of `op`, added one or two features, and made it more readable.