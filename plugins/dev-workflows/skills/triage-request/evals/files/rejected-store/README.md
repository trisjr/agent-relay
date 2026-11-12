# linkcheck

A small CLI that finds broken links in a folder of Markdown files.

```text
linkcheck scan <dir>      # list broken links
linkcheck fix <dir>       # rewrite links that moved, when the new target is unambiguous
linkcheck report <dir>    # print a summary table of the last scan
```

Configuration lives in `linkcheck.toml` at the root of the scanned folder. Past decisions and lessons are kept in `docs/solutions/`.
