# Guide for managing branches

All work is to be available to all workstations via GitHub.

(Important) branches can be remote-only, but ideally not local-only.

## `master`

The name says it all.

## `feature-name` / `characteristic-name` / `mark-name` branches

These are branches where a particular feature is developed. They should be
deleted after merging. Descriptive/marking names, ideally non-repeating, names
should be used.

## `origin/docsrun` branch

This is a branch for writing documents, as it is easier to write them directly
in GitHub. It is periodically merged into origin/master. It should only contain
documentation changes.

## Archive (reference) branches

They are kept for reference reasons.

They currently are (roughly in reverse-chronological order):

- architecture-flat
- with-button-bar
- with-lexer
- with-resize
- with-status
- with-zoom

In the case of `with-*` branches, the name says it what they are about.

`architecture-flat` is the first architecture that I used in the very first
rough mock-up prototype. 
