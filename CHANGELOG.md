# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.2.1] - 2025-11-04
### New Features
- [`75ef2a5`](https://github.com/HydroRoll-Team/conventional_role_play/commit/75ef2a5677eddc14917c738815982c60c197e43c) - add AutoParser class for automated content classification *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`4644d33`](https://github.com/HydroRoll-Team/conventional_role_play/commit/4644d33d0c23db46d706ec5667a759d6f92ebbf8) - add visualization tools for character relationship graphs *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*

### Refactors
- [`dcaf3a0`](https://github.com/HydroRoll-Team/conventional_role_play/commit/dcaf3a04f343f9f01191056fff9eb43f04d2b45f) - streamline THULACParser documentation and remove redundant comments *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*

### Chores
- [`c9b1331`](https://github.com/HydroRoll-Team/conventional_role_play/commit/c9b1331e2464356dc141923168339cbfa07aa09d) - **bump**: update version to 1.2.1 in Cargo.toml *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*


## [v1.2.0] - 2025-10-30
### New Features
- [`898db38`](https://github.com/HydroRoll-Team/conventional_role_play/commit/898db38f66f2b6b0047df75eaf3ced0d64cda664) - ➕ Add dependency json5 *(commit by [@pineoncellar](https://github.com/pineoncellar))*
- [`5f01c17`](https://github.com/HydroRoll-Team/conventional_role_play/commit/5f01c1710d4b6ae1e0ce9fba10f1528711a2f63f) - 🎨 More standardized log parse *(commit by [@pineoncellar](https://github.com/pineoncellar))*
- [`9f7e4b5`](https://github.com/HydroRoll-Team/conventional_role_play/commit/9f7e4b5d0a4aa6d9536a6eb1471a110d716e2566) - :art: refactor log parsing logic with simplified rules and priority-based matching *(commit by [@pineoncellar](https://github.com/pineoncellar))*
- [`a661b3a`](https://github.com/HydroRoll-Team/conventional_role_play/commit/a661b3ae3b5f6d41cd4d0b7d333285079d9905f9) - :art: update rules structure to use a dictionary for improved organization *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`08299b3`](https://github.com/HydroRoll-Team/conventional_role_play/commit/08299b37dfda86e56e4f2b442f68ccd2da7a82e3) - Enhance Processor, RuleExtractor, and Renderers with type hints and improved documentation *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`cbc653f`](https://github.com/HydroRoll-Team/conventional_role_play/commit/cbc653ffd0ea9abf4360623dc7a7651e1a49cc61) - Implement plugin system with combat tracker and dice analyzer *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*

### Bug Fixes
- [`3b0cd85`](https://github.com/HydroRoll-Team/conventional_role_play/commit/3b0cd85fd50ce159ce3bc219a9feb5d7b8650b0f) - :bug: using f.read() instead of json.load() *(commit by [@pineoncellar](https://github.com/pineoncellar))*
- [`9d08302`](https://github.com/HydroRoll-Team/conventional_role_play/commit/9d08302e61c029a8550778f1824e25933d5c59df) - Remove unnecessary links from the documentation table of contents *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*

### Refactors
- [`965771f`](https://github.com/HydroRoll-Team/conventional_role_play/commit/965771fb0d85ddb27dc6c5dd7df822d1fb318286) - clean up code formatting and add new PluginManager class *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`69a6c86`](https://github.com/HydroRoll-Team/conventional_role_play/commit/69a6c865c584a87693513e01cce5c2ab44ae92aa) - Refactor code structure for improved readability and maintainability *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*

### Chores
- [`421dd2a`](https://github.com/HydroRoll-Team/conventional_role_play/commit/421dd2a20c82339392359ff7302f09e469a0c27c) - 📝 Update example_log.log & example_rule.json *(commit by [@pineoncellar](https://github.com/pineoncellar))*
- [`be5c321`](https://github.com/HydroRoll-Team/conventional_role_play/commit/be5c32141aaee8b6e17e1b6ce9e659a77cb026be) - **deps**: update pyo3 requirement from 0.24.0 to 0.25.0 *(commit by [@dependabot[bot]](https://github.com/apps/dependabot))*
- [`65c3184`](https://github.com/HydroRoll-Team/conventional_role_play/commit/65c31844f6286aa85cce9d6b201d050424c1b687) - **docs**: update makefile and conf.py *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`8ccaab4`](https://github.com/HydroRoll-Team/conventional_role_play/commit/8ccaab4ff70f1e44e9594982f9baa78c4b1ee205) - **test**: Remove sensitive information *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`650403b`](https://github.com/HydroRoll-Team/conventional_role_play/commit/650403b82678ea3f542ab95c8a227345b9d8ece5) - Delete useless test dir *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`97c274a`](https://github.com/HydroRoll-Team/conventional_role_play/commit/97c274adc780748b986fa5347492616b321c2b13) - redactor `__version__` detector *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`eafadd7`](https://github.com/HydroRoll-Team/conventional_role_play/commit/eafadd7c059ceef979401e315d6cc2e0c9cbdded) - **deps**: update pyo3 requirement from 0.25.0 to 0.27.0 *(commit by [@dependabot[bot]](https://github.com/apps/dependabot))*
- [`be5fcf9`](https://github.com/HydroRoll-Team/conventional_role_play/commit/be5fcf92f834b5c4f1c6f8c433bb01b937c7f6e7) - **typo**: fix abbr typo *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`2cdb395`](https://github.com/HydroRoll-Team/conventional_role_play/commit/2cdb39569c1ba967e04ee604b7a9610055c0af77) - update version to 1.2.0 in Cargo.toml *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*


## [v0.2.3] - 2025-03-15
### New Features
- [`d7799f1`](https://github.com/HydroRoll-Team/conventional_role_play/commit/d7799f1ff7fca7525fd09c2e51f366be1d0886b5) - simple parser rules load and log processing *(commit by [@pineoncellar](https://github.com/pineoncellar))*
- [`ee15a8b`](https://github.com/HydroRoll-Team/conventional_role_play/commit/ee15a8b3174048f1c9f7f53a51d1e5b7a2410054) - :page_facing_up: Add sample rule and log files *(commit by [@pineoncellar](https://github.com/pineoncellar))*

### Bug Fixes
- [`5c5b871`](https://github.com/HydroRoll-Team/conventional_role_play/commit/5c5b8713e90642a767c67eb8da7c9a40e5ca6859) - update documentation URL in Cargo.toml *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*


## [v0.2.2] - 2025-03-14
### Chores
- [`6d3a6d8`](https://github.com/HydroRoll-Team/conventional_role_play/commit/6d3a6d851d88e572e2125932febfb9844064a7d1) - replace README.rst with README.md and update pyproject.toml to reference new README format *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`1ddf2a5`](https://github.com/HydroRoll-Team/conventional_role_play/commit/1ddf2a5202e065a5df18dfa58a88faa5784a3f8c) - bump version to 0.2.2 and update version retrieval method in __init__.py *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*


## [v0.2.1] - 2025-03-14
### Chores
- [`00e130b`](https://github.com/HydroRoll-Team/conventional_role_play/commit/00e130b06051a7d250d2a0a9b901d46cbd9eb756) - update CI workflow to use Python 3.9 and add interpreter finding option *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`fb5b1fb`](https://github.com/HydroRoll-Team/conventional_role_play/commit/fb5b1fbba51d68619d64f53e68164cc7a7741370) - update CI workflow to consistently use Python 3.9 and remove unnecessary interpreter arguments *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`a10578c`](https://github.com/HydroRoll-Team/conventional_role_play/commit/a10578cfd63151739b36f9cc5ba81a4c0eda05ec) - bump version to 0.2.1 in Cargo.toml and __init__.py *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*
- [`9b696f0`](https://github.com/HydroRoll-Team/conventional_role_play/commit/9b696f003a2b7da575ea086c6ddc0c579a13f46b) - rename project to conventionalrp and update metadata in Cargo.toml and pyproject.toml *(commit by [@HsiangNianian](https://github.com/HsiangNianian))*

[v0.2.1]: https://github.com/HydroRoll-Team/conventional_role_play/compare/v0.2.0...v0.2.1
[v0.2.2]: https://github.com/HydroRoll-Team/conventional_role_play/compare/v0.2.1...v0.2.2
[v0.2.3]: https://github.com/HydroRoll-Team/conventional_role_play/compare/v0.2.2...v0.2.3
[v1.2.0]: https://github.com/HydroRoll-Team/conventional_role_play/compare/v0.2.3...v1.2.0
[v1.2.1]: https://github.com/HydroRoll-Team/conventional_role_play/compare/v1.2.0...v1.2.1
