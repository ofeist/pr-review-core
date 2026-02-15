# Changelog

All notable changes to this project are documented in this file.

This project follows Keep a Changelog style and Semantic Versioning with compatibility constraints documented in `ops/versioning-policy.md`.

## [0.2.0](https://github.com/ofeist/pr-review-core/compare/v0.1.0...v0.2.0) (2026-02-15)


### Features

* **adapter:** add phase-4.1 slice-1 openai-compat skeleton with env … ([e630ecc](https://github.com/ofeist/pr-review-core/commit/e630ecc3d9b179b143cc05493e66f21bac5c8dd7))
* **adapter:** add phase-4.1 slice-1 openai-compat skeleton with env validation tests ([ba1ad45](https://github.com/ofeist/pr-review-core/commit/ba1ad45cb15d7d55ea2276a02deb6117eede5bdd))
* **examples:** add Bitbucket PR review helper script for branch and PR-ID workflows ([f2e9e6e](https://github.com/ofeist/pr-review-core/commit/f2e9e6e23568bd9954c80a1cc328727f49c74b56))
* **packaging:** complete phase-4 slice-2 src layout migration and le… ([1bfbdd3](https://github.com/ofeist/pr-review-core/commit/1bfbdd353b19b2ac65c3a7d5264cd0b83400e1e7))
* **packaging:** complete phase-4 slice-2 src layout migration and legacy test relocation ([0d1e3a3](https://github.com/ofeist/pr-review-core/commit/0d1e3a35d6f1c289e2e7ccc4ce0cceb04c1fda7a))
* **packaging:** complete phase-4 slice-3 dependency extras and insta… ([f15811f](https://github.com/ofeist/pr-review-core/commit/f15811f3475c83172098e1d560317b9572be93e6))
* **packaging:** complete phase-4 slice-3 dependency extras and install matrix ([181f1c8](https://github.com/ofeist/pr-review-core/commit/181f1c8056db8db4406da0f539f47ec6168c7855))
* **phase-4.1:** harden openai-compat runtime errors and redact secrets ([3cacbc7](https://github.com/ofeist/pr-review-core/commit/3cacbc7467713e850068a2021c4729300e4b65e8))
* **phase-4.1:** harden openai-compat runtime errors and redact secrets ([d8e29d0](https://github.com/ofeist/pr-review-core/commit/d8e29d04b6576c138b0c058f0d267b327b5baf99))
* **phase-4.1:** wire openai-compat into registry and CLI selection ([c661105](https://github.com/ofeist/pr-review-core/commit/c6611059e5ec83b7c9cff1ae38c450f9bdedd08d))
* **phase-4.1:** wire openai-compat into registry and CLI selection ([4356d74](https://github.com/ofeist/pr-review-core/commit/4356d74cdc9241124c4ab64629f5b9684d453d75))
* **phase-4.2:** add ollama adapter skeleton with strict env validation ([50175d2](https://github.com/ofeist/pr-review-core/commit/50175d2466443c22e5797f0feebe82aa56f3bcb9))
* **phase-4.2:** add ollama adapter skeleton with strict env validation ([5ee07c7](https://github.com/ofeist/pr-review-core/commit/5ee07c719b55def070f7e3be7ba80f40be323f70))
* **phase-4.2:** add opt-in ollama fallback for empty openai-compat r… ([a5dea9c](https://github.com/ofeist/pr-review-core/commit/a5dea9ccbef19ad5fd69bd929949abadb76056b8))
* **phase-4.2:** add opt-in ollama fallback for empty openai-compat responses ([0bcce83](https://github.com/ofeist/pr-review-core/commit/0bcce8358cda662181be5c1504cbe26af71f2fd4))
* **phase-4.2:** harden ollama fallback runtime errors and redaction ([976c900](https://github.com/ofeist/pr-review-core/commit/976c9008fc100be3510d03da610952bb70c15ecd))
* **phase-4.2:** harden ollama fallback runtime errors and redaction ([f3fab29](https://github.com/ofeist/pr-review-core/commit/f3fab2954c76858921789afe17a7e78ff5336874))
* **phase-4.2:** register ollama adapter in pipeline and CLI selectio… ([62671d4](https://github.com/ofeist/pr-review-core/commit/62671d44b613edf016f1a78ffbb92699dc758442))
* **phase-4.2:** register ollama adapter in pipeline and CLI selection tests ([af9cf8a](https://github.com/ofeist/pr-review-core/commit/af9cf8a4d2d1f39d16a6c8cf6bc4e50a9ae661d6))
* **release:** add release-please PR automation skeleton for versioni… ([9b2a4f4](https://github.com/ofeist/pr-review-core/commit/9b2a4f49c3da5afc899a7b2eb297ecd1c030c3cd))
* **release:** add release-please PR automation skeleton for versioning slice-1 ([f091063](https://github.com/ofeist/pr-review-core/commit/f091063c92b91e0d4f6ecf3561a3046960abbb02))
* **release:** add tag-driven GitHub Release asset publishing with sm… ([d33b5ac](https://github.com/ofeist/pr-review-core/commit/d33b5ac0c3b65cf579f80bf05efaa846116fe2c5))
* **release:** add tag-driven GitHub Release asset publishing with smoke gate ([7282a35](https://github.com/ofeist/pr-review-core/commit/7282a35e97e246f3d0b970831d7f54536cdd4c43))
* **release:** enforce PR release labels and contract-sensitive versi… ([789ffc4](https://github.com/ofeist/pr-review-core/commit/789ffc4801a148c756b7bf4b4bdcc256afe3db5c))
* **release:** enforce PR release labels and contract-sensitive versioning policy ([a06d090](https://github.com/ofeist/pr-review-core/commit/a06d0907fd3630bd7e25e71bdc70af011bf163e7))


### Bug Fixes

* **intent:** avoid truncated PR title by falling back to body when ti… ([27d2b4a](https://github.com/ofeist/pr-review-core/commit/27d2b4a48e87da77e64b638edf7a839c8251a5a0))
* **intent:** avoid truncated PR title by falling back to body when title ends with ellipsis ([5773d70](https://github.com/ofeist/pr-review-core/commit/5773d7036aeb4470a5bcb3deeb58c6dbeb072faa))
* **intent:** handle leading-ellipsis truncated titles and improve fallback behavior ([21ffba7](https://github.com/ofeist/pr-review-core/commit/21ffba7aa77a4ac533052a46ce8c1bf87f82a182))
* **intent:** ignore truncated body when title is truncated and return safe fallback ([fcb6826](https://github.com/ofeist/pr-review-core/commit/fcb68264c5ae202da84893cacee8963a2cbdd2a4))
* **intent:** ignore truncated body when title is truncated and return… ([5dea255](https://github.com/ofeist/pr-review-core/commit/5dea255cddae63578eb57a25465922153b5fbf62))
* **noise-filter:** suppress generic advisory/praise findings from openai output ([07ddc6f](https://github.com/ofeist/pr-review-core/commit/07ddc6f50737a5aa8df3ea7e9bfaf45e10cc0fa8))


### Documentation

* add timeout env vars for openai-compat and ollama across guides ([9bf718a](https://github.com/ofeist/pr-review-core/commit/9bf718ad2aa5a8a4756eef965215d12ef2b3fafa))
* archive phase-4.1 docs under ops/done and refresh references ([7b01ba5](https://github.com/ofeist/pr-review-core/commit/7b01ba58dffcb1ea049d19fb61db7665d82fb4ae))
* centralize adapter env vars in canonical matrix and deduplicate guides ([82b4e82](https://github.com/ofeist/pr-review-core/commit/82b4e82fcea6010c1b0a05bf2a1a893c98fdd96b))
* **consumer:** complete phase-4 slice-6 integration quickstart for G… ([4e57688](https://github.com/ofeist/pr-review-core/commit/4e57688b76fd9daf64849eaf426e66011606be13))
* **consumer:** complete phase-4 slice-6 integration quickstart for GitHub and Bitbucket ([2d3e575](https://github.com/ofeist/pr-review-core/commit/2d3e57500b9171ba342fd264b17509640c5b8f51))
* **ops:** add versioning automation thin-slices and strategy placeholders ([61f0894](https://github.com/ofeist/pr-review-core/commit/61f089443ce5d3304cae2a9c422dc04dc9ae5d50))
* **ops:** move completed phase-4 docs into ops/done and update references ([5678c1b](https://github.com/ofeist/pr-review-core/commit/5678c1b2b19a331528021f266aac512eab239c9c))
* **packaging:** add latest-version wheel build/install flow with isolated venvs ([e0679f0](https://github.com/ofeist/pr-review-core/commit/e0679f07f0cc303d8be30fc693eaf7cc4bae2460))
* **phase-4.1:** add exit validation and close openai-compat track ([038efd9](https://github.com/ofeist/pr-review-core/commit/038efd9900c343ed0eedb1840f9362c23f8d4e74))
* **phase-4.1:** add exit validation and close openai-compat track ([ff891f9](https://github.com/ofeist/pr-review-core/commit/ff891f9524524ff41aa46a009ffecbb813ad6ac3))
* **phase-4.1:** add openai-compat setup and usage guidance ([7c5cf05](https://github.com/ofeist/pr-review-core/commit/7c5cf050a0fa94c4908c073b60bbada95dffd509))
* **phase-4.1:** add openai-compat setup and usage guidance ([0477526](https://github.com/ofeist/pr-review-core/commit/0477526f78bded88e2c9aaf1d9e5f87328f4be69))
* **phase-4.2:** add exit validation, archive thin-slices, and hand o… ([849e51c](https://github.com/ofeist/pr-review-core/commit/849e51c699990e89cc94d360f8bd4b1d4286e324))
* **phase-4.2:** add exit validation, archive thin-slices, and hand off to phase-5 ([2ca0494](https://github.com/ofeist/pr-review-core/commit/2ca0494f51e0ec5de91e98507283d88b2b0befc2))
* **phase-4.2:** document openai-compat fallback and ollama adapter u… ([5734429](https://github.com/ofeist/pr-review-core/commit/57344292bad6f262315a87103adcf44a06d917cf))
* **phase-4.2:** document openai-compat fallback and ollama adapter usage ([8cbff86](https://github.com/ofeist/pr-review-core/commit/8cbff86b36678fcfb32c81de4dbe766171e3809f))
* **phase-4.2:** lock fallback/ollama adapter guardrails and close sl… ([79cf863](https://github.com/ofeist/pr-review-core/commit/79cf8639dbb302f2c4587109ef4dd778d1f30a2f))
* **phase-4.2:** lock fallback/ollama adapter guardrails and close slice-0 ([8b21236](https://github.com/ofeist/pr-review-core/commit/8b21236ed71a21ac3238a4510e6f52abfb304a85))
* **plan:** add phase-4.2 thin slices for openai-compat fallback and ollama adapter ([dcb6cf1](https://github.com/ofeist/pr-review-core/commit/dcb6cf1f889cac3ad10abeac1f6535cdd53771e6))
* **planning:** add openai-compatible adapter thin-slice implementation plan ([9b16f59](https://github.com/ofeist/pr-review-core/commit/9b16f59fbbbcbc17b4c5c2ab654669f25bfbf538))
* **planning:** introduce phase-agnostic next-thin-slices queue and align roadmap references ([9efa894](https://github.com/ofeist/pr-review-core/commit/9efa89425d697492ef4031aa11b1f6fd32b5ac53))
* **release:** add release label how-to for GitHub UI and gh CLI ([70cc1be](https://github.com/ofeist/pr-review-core/commit/70cc1be168c2c0bc04fbd341e8d648c10eb7e39f))
* **release:** complete phase-4 slice-5 versioning policy and release checklist ([436058a](https://github.com/ofeist/pr-review-core/commit/436058a939d2894de4901118614a61fc1909179c))
* **release:** complete phase-4 slice-5 versioning policy and release… ([ad5c356](https://github.com/ofeist/pr-review-core/commit/ad5c356683e1ae383e7d0a89c53fb70853227ffb))
* **testing:** add git diff stdin usage to package-testing guide and README pointer ([8dcf1ec](https://github.com/ofeist/pr-review-core/commit/8dcf1ecbc25610db8b9721d63cf8a3e805213768))
* **testing:** add package validation guide for pip build/install smoke checks ([a71f54e](https://github.com/ofeist/pr-review-core/commit/a71f54e7d9f29f55f0ae0d42223e951fce44d2c9))
* **validation:** complete phase-4 slice-8 exit checklist and handoff notes ([211c7cc](https://github.com/ofeist/pr-review-core/commit/211c7cc5eca44677a6e83732b6ec7f39c2aacd10))
* **validation:** complete phase-4 slice-8 exit checklist and handoff… ([6319747](https://github.com/ofeist/pr-review-core/commit/6319747232a7360fceb97830031faf4740670cda))
* **versioning:** complete slice-0 human-in-loop policy baseline ([a859282](https://github.com/ofeist/pr-review-core/commit/a859282282bca779444cbd71dab867bbb5596462))
* **versioning:** complete slice-0 human-in-loop policy baseline ([ebcffdd](https://github.com/ofeist/pr-review-core/commit/ebcffddd23e5b1bac45909505ce093f169d4c141))

## [Unreleased]
### Added
- _No entries yet._

## [0.1.0] - 2026-02-12
### Added
- Diff foundation (`core/diff`) with parsing/filtering CLI.
- Review core (`core/review`) with deterministic prompting, adapter abstraction, output normalization, noise filtering, chunking, and fallback behavior.
- GitHub MVP workflow for AI review comment upsert.
- Packaging baseline with `pyproject.toml`, `src/` layout, optional `openai` extra, and package smoke workflow.
