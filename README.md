# BethesdaModKit

An opinionated toolkit for Bethesda modding, with project generation, build
rules and testing helpers for Skyrim and Fallout 4.

Use the [project template](docs/mod-authors/template/projects.md), or
[add tools to an existing mod](docs/mod-authors/tooling/building.md). See the
[documentation](docs/README.md) for individual rules and helpers.

## Create a project

Requires [Copier](https://copier.readthedocs.io/en/stable/), Git and
[XMake 3.1.1 or newer](https://github.com/xmake-io/xmake/releases/tag/v3.1.1).

```powershell
copier copy https://github.com/gabriel-andreescu/BethesdaModKit.git MyMod
```

[First build and project options](docs/mod-authors/template/projects.md)

## Update a project

Requires a clean Git working tree and the project's `.copier-answers.yml`.

```powershell
copier update
```

[Adding components and updating customized projects](docs/mod-authors/template/projects.md#adding-components-and-updating)

[Updating build tools and dependencies](docs/mod-authors/tooling/updating.md)

## Development

See [development setup and tests](docs/maintainers/development.md) and
[contribution guidelines](CONTRIBUTING.md).

## License

[MIT](LICENSE)
