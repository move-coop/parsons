# Contributing to Parsons

We're thrilled that you're thinking about contributing to Parsons! Welcome to our contributor community.

You can find a detailed version of this guide [on our website](https://www.parsonsproject.org/pub/contributing-guide/).

The best way to get involved is by joining our Slack. To join, email <engineering@movementcooperative.org>. In addition to all the great discussions that happen on our Slack, we also have virtual events including trainings, pairing sessions, social hangouts, discussions, and more. Every other Thursday afternoon we host 🎉 Parsons Parties 🎉 on Zoom where we work on contributions together.

You can contribute by:

* [submitting issues](https://www.parsonsproject.org/pub/contributing-guide#submitting-issues)
* [contributing code](https://www.parsonsproject.org/pub/contributing-guide/)
* [updating our documentation](https://www.parsonsproject.org/pub/updating-documentation/)
* [teaching and mentoring](https://www.parsonsproject.org/pub/contributing-guide#teaching-and-mentoring)
* [helping "triage" issues and review pull requests](https://www.parsonsproject.org/pub/contributing-guide#maintainer-tasks)

## Writing tests

Every code contribution should come with tests. Parsons has a single, canonical
testing standard — how to structure a connector's tests, how to mock external
services, and where to store test data — documented in
[docs/write_tests.rst](docs/write_tests.rst). Please follow it for new tests, and
migrate older tests toward it as you touch them.

We are incrementally migrating the existing suite onto this standard. If you touch
a connector's tests, see [test/MIGRATION.md](test/MIGRATION.md) for the per-connector
checklist and check off the one you converted.

If you're not sure how to get started, please ask for help! We're happy to chat and help you find the best way to get involved.
