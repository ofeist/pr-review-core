# Changelog

All notable changes to this project are documented in this file.

This project follows Keep a Changelog style and Semantic Versioning with compatibility constraints documented in `ops/versioning-policy.md`.

## [2.0.0](https://github.com/ofeist/pr-review-core/compare/v1.0.2...v2.0.0) (2026-04-21)


### ⚠ BREAKING CHANGES

* **adapter:** visible <think>...</think> reasoning blocks are stripped from normalized review output before markdown section extraction.

### Features

* **adapter:** add env-configurable max output tokens ([f8c5e6f](https://github.com/ofeist/pr-review-core/commit/f8c5e6fcb8e6dbc6c63a094b18bd7626a1606dfd))
* **adapter:** add env-configurable max output tokens ([785b9f4](https://github.com/ofeist/pr-review-core/commit/785b9f4a3a689b2ae23606277288cd20faa6bc1d))
* **adapter:** add phase-4.1 slice-1 openai-compat skeleton with env … ([e630ecc](https://github.com/ofeist/pr-review-core/commit/e630ecc3d9b179b143cc05493e66f21bac5c8dd7))
* **adapter:** add phase-4.1 slice-1 openai-compat skeleton with env validation tests ([ba1ad45](https://github.com/ofeist/pr-review-core/commit/ba1ad45cb15d7d55ea2276a02deb6117eede5bdd))
* **adapter:** add reasoning disable controls ([03b36fe](https://github.com/ofeist/pr-review-core/commit/03b36fe7d5036b4a8feb4e92ef920cf30cfe699c))
* **adapter:** add reasoning disable controls ([489ed9d](https://github.com/ofeist/pr-review-core/commit/489ed9de0a1fa74eddbde928429d40233ab372a9))
* **adapter:** mark reasoning sanitizer as contract-sensitive ([cdd0e4a](https://github.com/ofeist/pr-review-core/commit/cdd0e4a2017f6d30d98279a23f01499308facbf5))
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
* **release:** add tag-version-changelog consistency guards for slice-4 ([6cd9de1](https://github.com/ofeist/pr-review-core/commit/6cd9de1b92c532ad22146507e33796edd85d3e91))
* **release:** add tag-version-changelog consistency guards for slice-4 ([9d239cb](https://github.com/ofeist/pr-review-core/commit/9d239cb2df737a92fd113ccaeb74fa003c9f2541))
* **release:** enforce PR release labels and contract-sensitive versi… ([789ffc4](https://github.com/ofeist/pr-review-core/commit/789ffc4801a148c756b7bf4b4bdcc256afe3db5c))
* **release:** enforce PR release labels and contract-sensitive versioning policy ([a06d090](https://github.com/ofeist/pr-review-core/commit/a06d0907fd3630bd7e25e71bdc70af011bf163e7))
* **review:** add agentic demo output mode ([14ce428](https://github.com/ofeist/pr-review-core/commit/14ce428ace9512cce90463173b8bf9f0e79764f5))


### Bug Fixes

* **diff:** tolerate invalid UTF-8 bytes in diff input ([658e0a6](https://github.com/ofeist/pr-review-core/commit/658e0a6fa6926c1fa3805edc494cb74b7e219850))
* **diff:** tolerate invalid UTF-8 bytes in diff input ([1f24f54](https://github.com/ofeist/pr-review-core/commit/1f24f5457f9b4f7bc73a8f90762d55633be05927))
* **intent:** avoid truncated PR title by falling back to body when ti… ([27d2b4a](https://github.com/ofeist/pr-review-core/commit/27d2b4a48e87da77e64b638edf7a839c8251a5a0))
* **intent:** avoid truncated PR title by falling back to body when title ends with ellipsis ([5773d70](https://github.com/ofeist/pr-review-core/commit/5773d7036aeb4470a5bcb3deeb58c6dbeb072faa))
* **intent:** handle leading-ellipsis truncated titles and improve fallback behavior ([21ffba7](https://github.com/ofeist/pr-review-core/commit/21ffba7aa77a4ac533052a46ce8c1bf87f82a182))
* **intent:** ignore truncated body when title is truncated and return safe fallback ([fcb6826](https://github.com/ofeist/pr-review-core/commit/fcb68264c5ae202da84893cacee8963a2cbdd2a4))
* **intent:** ignore truncated body when title is truncated and return… ([5dea255](https://github.com/ofeist/pr-review-core/commit/5dea255cddae63578eb57a25465922153b5fbf62))
* **noise-filter:** suppress generic advisory/praise findings from openai output ([07ddc6f](https://github.com/ofeist/pr-review-core/commit/07ddc6f50737a5aa8df3ea7e9bfaf45e10cc0fa8))
* **release:** trigger 0.2.1 patch release ([f353c31](https://github.com/ofeist/pr-review-core/commit/f353c314a14c6df638b5dee1b5dd77303ec2a9c9))
* **release:** trigger 0.2.1 patch release ([61a20bf](https://github.com/ofeist/pr-review-core/commit/61a20bf0da98c8685f5128e500263cda88072fa0))


### Documentation

* add timeout env vars for openai-compat and ollama across guides ([9bf718a](https://github.com/ofeist/pr-review-core/commit/9bf718ad2aa5a8a4756eef965215d12ef2b3fafa))
* **agentic:** add post-merge worktree reset notes ([d4d2a26](https://github.com/ofeist/pr-review-core/commit/d4d2a26d278942af77119165525d3fe2b35df04f))
* **agentic:** add task for agentic demo review slice ([4ab55e1](https://github.com/ofeist/pr-review-core/commit/4ab55e1e80e140e7f50dfe5ebb28500b388b9299))
* **agentic:** add task for noise filter regression fix ([df6381f](https://github.com/ofeist/pr-review-core/commit/df6381f362ceb582ef7a5e22b54b6e706f13a919))
* **agentic:** add workflow scaffolding and templates ([ac2cdb6](https://github.com/ofeist/pr-review-core/commit/ac2cdb6466bed872285a8a0f6e04eea77873cedd))
* **agentic:** clarify finding decisions for showcase slices ([0a6ae41](https://github.com/ofeist/pr-review-core/commit/0a6ae416b43dd97523622dd9dbdd732f60ee087d))
* **agentic:** clarify workdir setup and planning scope ([6475f15](https://github.com/ofeist/pr-review-core/commit/6475f1532994f0fd9b786e3a5b276e60ef921c30))
* **agentic:** link release policy from workflow ([ed3f3bf](https://github.com/ofeist/pr-review-core/commit/ed3f3bfd46736396a5092c1d388969ccb08cbd00))
* archive phase-4.1 docs under ops/done and refresh references ([7b01ba5](https://github.com/ofeist/pr-review-core/commit/7b01ba58dffcb1ea049d19fb61db7665d82fb4ae))
* centralize adapter env vars in canonical matrix and deduplicate guides ([82b4e82](https://github.com/ofeist/pr-review-core/commit/82b4e82fcea6010c1b0a05bf2a1a893c98fdd96b))
* **consumer:** add Jenkins and Bitbucket Data Center integration example ([8db683f](https://github.com/ofeist/pr-review-core/commit/8db683f05647854ee55eb6653f1ea243b38a6d6e))
* **consumer:** add Jenkins Bitbucket review wrapper with intent metadata ([514fde1](https://github.com/ofeist/pr-review-core/commit/514fde1ea40174d71013629664d9e330056a4016))
* **consumer:** complete phase-4 slice-6 integration quickstart for G… ([4e57688](https://github.com/ofeist/pr-review-core/commit/4e57688b76fd9daf64849eaf426e66011606be13))
* **consumer:** complete phase-4 slice-6 integration quickstart for GitHub and Bitbucket ([2d3e575](https://github.com/ofeist/pr-review-core/commit/2d3e57500b9171ba342fd264b17509640c5b8f51))
* **examples:** harden Bitbucket Jenkins review scripts ([ecf0743](https://github.com/ofeist/pr-review-core/commit/ecf07430b3841cf08ea59a9a082e725404d2dc6f))
* **ops:** add versioning automation thin-slices and strategy placeholders ([61f0894](https://github.com/ofeist/pr-review-core/commit/61f089443ce5d3304cae2a9c422dc04dc9ae5d50))
* **ops:** align reasoning plan release label ([ce7e1c9](https://github.com/ofeist/pr-review-core/commit/ce7e1c95ac695ca35e537e435ce2e041ebbecb19))
* **ops:** include normalizer tests in reasoning plan ([3b60d5d](https://github.com/ofeist/pr-review-core/commit/3b60d5d916386738e315455213a3c2f1fcd69403))
* **ops:** move completed phase-4 docs into ops/done and update references ([5678c1b](https://github.com/ofeist/pr-review-core/commit/5678c1b2b19a331528021f266aac512eab239c9c))
* **ops:** plan env-configurable max output tokens ([c574746](https://github.com/ofeist/pr-review-core/commit/c5747463a9f8ed46991a3fc50a468d3e7b645f69))
* **ops:** plan reasoning disable controls ([d4a529d](https://github.com/ofeist/pr-review-core/commit/d4a529d830fb27a20097bc1a54346fe71a6d07b8))
* **ops:** refine reasoning disable plan ([b876564](https://github.com/ofeist/pr-review-core/commit/b876564d7ad1e6c460b7cd520264a86c6101fd42))
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
* **readme:** update consumer install and pin examples to v0.3.0 ([65c3441](https://github.com/ofeist/pr-review-core/commit/65c344198bd0d8a13f877dc4c90a38cd5d1c9cf3))
* **release:** add release label how-to for GitHub UI and gh CLI ([70cc1be](https://github.com/ofeist/pr-review-core/commit/70cc1be168c2c0bc04fbd341e8d648c10eb7e39f))
* **release:** complete phase-4 slice-5 versioning policy and release checklist ([436058a](https://github.com/ofeist/pr-review-core/commit/436058a939d2894de4901118614a61fc1909179c))
* **release:** complete phase-4 slice-5 versioning policy and release… ([ad5c356](https://github.com/ofeist/pr-review-core/commit/ad5c356683e1ae383e7d0a89c53fb70853227ffb))
* **review:** record agentic demo compatibility note ([39857be](https://github.com/ofeist/pr-review-core/commit/39857be9c2ffbaffc57b03424f7de1234346be0f))
* **testing:** add git diff stdin usage to package-testing guide and README pointer ([8dcf1ec](https://github.com/ofeist/pr-review-core/commit/8dcf1ecbc25610db8b9721d63cf8a3e805213768))
* **testing:** add package validation guide for pip build/install smoke checks ([a71f54e](https://github.com/ofeist/pr-review-core/commit/a71f54e7d9f29f55f0ae0d42223e951fce44d2c9))
* **validation:** complete phase-4 slice-8 exit checklist and handoff notes ([211c7cc](https://github.com/ofeist/pr-review-core/commit/211c7cc5eca44677a6e83732b6ec7f39c2aacd10))
* **validation:** complete phase-4 slice-8 exit checklist and handoff… ([6319747](https://github.com/ofeist/pr-review-core/commit/6319747232a7360fceb97830031faf4740670cda))
* **versioning:** complete slice-0 human-in-loop policy baseline ([a859282](https://github.com/ofeist/pr-review-core/commit/a859282282bca779444cbd71dab867bbb5596462))
* **versioning:** complete slice-0 human-in-loop policy baseline ([ebcffdd](https://github.com/ofeist/pr-review-core/commit/ebcffddd23e5b1bac45909505ce093f169d4c141))
* **versioning:** complete slice-5 consumer pinning and upgrade guidance ([7c45e12](https://github.com/ofeist/pr-review-core/commit/7c45e128a5a1bc00524de39131dc6e79c5526a9f))
* **versioning:** complete slice-5 consumer pinning and upgrade guidance ([6f1a820](https://github.com/ofeist/pr-review-core/commit/6f1a820a6796393c6697e63a5fd3257b34d901cd))
* **versioning:** complete slice-6 exit validation and close automati… ([81a9eeb](https://github.com/ofeist/pr-review-core/commit/81a9eeb2d3372ae763da3f76f06ce0cf86f41727))
* **versioning:** complete slice-6 exit validation and close automation track ([4c8f2e7](https://github.com/ofeist/pr-review-core/commit/4c8f2e709cc5e9bcdadd5f32304cd232c7eca64a))

## [1.0.2](https://github.com/ofeist/pr-review-core/compare/v1.0.1...v1.0.2) (2026-04-21)


### Documentation

* **agentic:** add task for noise filter regression fix ([df6381f](https://github.com/ofeist/pr-review-core/commit/df6381f362ceb582ef7a5e22b54b6e706f13a919))

## [1.0.1](https://github.com/ofeist/pr-review-core/compare/v1.0.0...v1.0.1) (2026-04-20)


### Documentation

* **examples:** harden Bitbucket Jenkins review scripts ([ecf0743](https://github.com/ofeist/pr-review-core/commit/ecf07430b3841cf08ea59a9a082e725404d2dc6f))

## [1.0.0](https://github.com/ofeist/pr-review-core/compare/v0.5.0...v1.0.0) (2026-04-20)


### ⚠ BREAKING CHANGES

* **adapter:** visible <think>...</think> reasoning blocks are stripped from normalized review output before markdown section extraction.

### Features

* **adapter:** add reasoning disable controls ([03b36fe](https://github.com/ofeist/pr-review-core/commit/03b36fe7d5036b4a8feb4e92ef920cf30cfe699c))
* **adapter:** add reasoning disable controls ([489ed9d](https://github.com/ofeist/pr-review-core/commit/489ed9de0a1fa74eddbde928429d40233ab372a9))
* **adapter:** mark reasoning sanitizer as contract-sensitive ([cdd0e4a](https://github.com/ofeist/pr-review-core/commit/cdd0e4a2017f6d30d98279a23f01499308facbf5))


### Documentation

* **consumer:** add Jenkins Bitbucket review wrapper with intent metadata ([514fde1](https://github.com/ofeist/pr-review-core/commit/514fde1ea40174d71013629664d9e330056a4016))
* **ops:** align reasoning plan release label ([ce7e1c9](https://github.com/ofeist/pr-review-core/commit/ce7e1c95ac695ca35e537e435ce2e041ebbecb19))
* **ops:** include normalizer tests in reasoning plan ([3b60d5d](https://github.com/ofeist/pr-review-core/commit/3b60d5d916386738e315455213a3c2f1fcd69403))
* **ops:** plan reasoning disable controls ([d4a529d](https://github.com/ofeist/pr-review-core/commit/d4a529d830fb27a20097bc1a54346fe71a6d07b8))
* **ops:** refine reasoning disable plan ([b876564](https://github.com/ofeist/pr-review-core/commit/b876564d7ad1e6c460b7cd520264a86c6101fd42))

## [Unreleased]

### Features

* **adapter:** add opt-in reasoning/thinking suppression controls for OpenAI-compatible and Ollama adapters.

### Compatibility

* Migration note: visible `<think>...</think>` reasoning blocks are stripped from normalized review output before markdown section extraction.

## [0.5.0](https://github.com/ofeist/pr-review-core/compare/v0.4.0...v0.5.0) (2026-04-17)


### Features

* **adapter:** add env-configurable max output tokens ([f8c5e6f](https://github.com/ofeist/pr-review-core/commit/f8c5e6fcb8e6dbc6c63a094b18bd7626a1606dfd))
* **adapter:** add env-configurable max output tokens ([785b9f4](https://github.com/ofeist/pr-review-core/commit/785b9f4a3a689b2ae23606277288cd20faa6bc1d))


### Documentation

* **ops:** plan env-configurable max output tokens ([c574746](https://github.com/ofeist/pr-review-core/commit/c5747463a9f8ed46991a3fc50a468d3e7b645f69))

## [0.4.0](https://github.com/ofeist/pr-review-core/compare/v0.3.1...v0.4.0) (2026-04-17)


### Features

* **review:** add agentic demo output mode ([14ce428](https://github.com/ofeist/pr-review-core/commit/14ce428ace9512cce90463173b8bf9f0e79764f5))


### Bug Fixes

* **diff:** tolerate invalid UTF-8 bytes in diff input ([658e0a6](https://github.com/ofeist/pr-review-core/commit/658e0a6fa6926c1fa3805edc494cb74b7e219850))
* **diff:** tolerate invalid UTF-8 bytes in diff input ([1f24f54](https://github.com/ofeist/pr-review-core/commit/1f24f5457f9b4f7bc73a8f90762d55633be05927))


### Documentation

* **agentic:** add post-merge worktree reset notes ([d4d2a26](https://github.com/ofeist/pr-review-core/commit/d4d2a26d278942af77119165525d3fe2b35df04f))
* **agentic:** add task for agentic demo review slice ([4ab55e1](https://github.com/ofeist/pr-review-core/commit/4ab55e1e80e140e7f50dfe5ebb28500b388b9299))
* **agentic:** add workflow scaffolding and templates ([ac2cdb6](https://github.com/ofeist/pr-review-core/commit/ac2cdb6466bed872285a8a0f6e04eea77873cedd))
* **agentic:** clarify finding decisions for showcase slices ([0a6ae41](https://github.com/ofeist/pr-review-core/commit/0a6ae416b43dd97523622dd9dbdd732f60ee087d))
* **agentic:** clarify workdir setup and planning scope ([6475f15](https://github.com/ofeist/pr-review-core/commit/6475f1532994f0fd9b786e3a5b276e60ef921c30))
* **agentic:** link release policy from workflow ([ed3f3bf](https://github.com/ofeist/pr-review-core/commit/ed3f3bfd46736396a5092c1d388969ccb08cbd00))
* **consumer:** add Jenkins and Bitbucket Data Center integration example ([8db683f](https://github.com/ofeist/pr-review-core/commit/8db683f05647854ee55eb6653f1ea243b38a6d6e))
* **review:** record agentic demo compatibility note ([39857be](https://github.com/ofeist/pr-review-core/commit/39857be9c2ffbaffc57b03424f7de1234346be0f))

## [0.3.1](https://github.com/ofeist/pr-review-core/compare/v0.3.0...v0.3.1) (2026-03-09)


### Documentation

* **readme:** update consumer install and pin examples to v0.3.0 ([65c3441](https://github.com/ofeist/pr-review-core/commit/65c344198bd0d8a13f877dc4c90a38cd5d1c9cf3))

## [0.3.0](https://github.com/ofeist/pr-review-core/compare/v0.2.0...v0.3.0) (2026-02-15)


### Features

* **release:** add tag-version-changelog consistency guards for slice-4 ([6cd9de1](https://github.com/ofeist/pr-review-core/commit/6cd9de1b92c532ad22146507e33796edd85d3e91))
* **release:** add tag-version-changelog consistency guards for slice-4 ([9d239cb](https://github.com/ofeist/pr-review-core/commit/9d239cb2df737a92fd113ccaeb74fa003c9f2541))


### Bug Fixes

* **release:** trigger 0.2.1 patch release ([f353c31](https://github.com/ofeist/pr-review-core/commit/f353c314a14c6df638b5dee1b5dd77303ec2a9c9))
* **release:** trigger 0.2.1 patch release ([61a20bf](https://github.com/ofeist/pr-review-core/commit/61a20bf0da98c8685f5128e500263cda88072fa0))


### Documentation

* **versioning:** complete slice-5 consumer pinning and upgrade guidance ([7c45e12](https://github.com/ofeist/pr-review-core/commit/7c45e128a5a1bc00524de39131dc6e79c5526a9f))
* **versioning:** complete slice-5 consumer pinning and upgrade guidance ([6f1a820](https://github.com/ofeist/pr-review-core/commit/6f1a820a6796393c6697e63a5fd3257b34d901cd))
* **versioning:** complete slice-6 exit validation and close automati… ([81a9eeb](https://github.com/ofeist/pr-review-core/commit/81a9eeb2d3372ae763da3f76f06ce0cf86f41727))
* **versioning:** complete slice-6 exit validation and close automation track ([4c8f2e7](https://github.com/ofeist/pr-review-core/commit/4c8f2e709cc5e9bcdadd5f32304cd232c7eca64a))

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
- Add `--agentic-demo` mode to `core.review.cli` for deterministic staged showcase output (`Plan`, `Review`, `QA`, `Final Recommendation`).

### Fixed
- Keep high-signal hardcoded-secret and commented-out configuration findings in filtered review output while avoiding false evidence matches from generic phrases such as `new line`.

### Migration
- No migration required for existing consumers. Default CLI behavior and canonical review output remain unchanged unless `--agentic-demo` is explicitly used.

## [0.1.0] - 2026-02-12
### Added
- Diff foundation (`core/diff`) with parsing/filtering CLI.
- Review core (`core/review`) with deterministic prompting, adapter abstraction, output normalization, noise filtering, chunking, and fallback behavior.
- GitHub MVP workflow for AI review comment upsert.
- Packaging baseline with `pyproject.toml`, `src/` layout, optional `openai` extra, and package smoke workflow.
