# Nexus Mods

BMK uploads release packages with the
[official Nexus action](https://github.com/Nexus-Mods/upload-action). Each
package selects an existing Nexus file to update:

```lua
target("MyMod", function()
    set_version("1.0.0")
    add_rules("@addon/bmk/skyrim.package", {
        targets = { "Native", "Papyrus" },
        nexus = {
            mod_id = "YOUR_UNIQUE_MOD_ID",
            file_id = "YOUR_FILE_ID",
            category = "main",
            primary = true,
        },
    })
    add_installfiles("assets/main/(**)")
end)
```

Create the mod page and upload each file once through Nexus. Copy its **Unique
Mod ID** and **File ID** from the Files tab's Advanced view or the file's edit
form. These are the API IDs, not the numbers in download URLs.

| Field          | Default      | Purpose                                                 |
| -------------- | ------------ | ------------------------------------------------------- |
| `mod_id`       | Required     | Unique Nexus mod ID, as a string.                       |
| `file_id`      | Required     | Existing Nexus file ID, as a string.                    |
| `category`     | Required     | `main`, `optional` or `miscellaneous`.                  |
| `primary`      | `false`      | Main download that also updates the mod page's version. |
| `display_name` | Package name | Name shown in Nexus's Files tab.                        |
| `description`  | Empty        | File description.                                       |

Each mod can have one primary Main package. Other packages retain their own
versions without changing the mod page's version. Packages without `nexus` still
appear in the GitHub release.

## Workflow

Add a `NEXUSMODS_API_KEY` repository secret using your
[personal Nexus API key](https://www.nexusmods.com/settings/api-keys), then pass
it to BMK's [build workflow](github-actions.md):

```yaml
with:
  publish-nexus: true
secrets:
  NEXUSMODS_API_KEY: ${{ secrets.NEXUSMODS_API_KEY }}
```

Tag releases upload the built ZIPs after the GitHub release succeeds. Previous
Nexus versions move to Old files. The workflow does not publish unpublished mod
pages.

## Changelogs and retries

Nexus receives the package's
[selected release notes](github-actions.md#target-changelogs) as plain entries,
preserving category labels and link destinations. Packages sharing a mod and
version share one changelog, with repeated entries removed.

Rerun failed jobs to resume publication. BMK skips file versions already present
on Nexus and posts only missing changelog entries. It does not replace uploaded
files with another ZIP under the same version. Upload and changelog failures
fail the workflow.

The official upload action is currently in beta.
