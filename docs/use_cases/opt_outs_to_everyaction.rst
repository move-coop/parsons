=======================
Opt-outs to EveryAction
=======================

As carriers tighten restrictions on peer-to-peer texting through 10DLC rules, it becomes more and more crucial for organizations to avoid texting people who have opted out of their communications. This is a challenge for organizations who pull outreach lists from EveryAction or VAN but run their actual texting program in another tool because their opt-outs are tracked in a different system from the one where they pull their lists. A number of commonly used texting tools have integrations with EveryAction and VAN but they don't always sync opt-out dispositions back into EveryAction/VAN.

The Movement Cooperative worked with a couple of different member organizations to create a script using Parsons that would opt-out phone numbers in EveryAction to prevent them from being pulled into future outreach lists. The script only updates existing records, it does not create new ones, so it requires you to provide a VAN ID and assumes that the people you want to opt out already exist in EveryAction.

The script requires the user to provide a table containing columns for phone number (must be named `phone`), committee ID (must be named `committeeid`), and vanid (must be named `vanid`).

Some questions to consider when you construct this table are:

- Which committees do you want to opt people out in?
- Multiple people can have the same phone number assigned to them in EveryAction. Do you want to opt out a phone regardless of who it's associated with, or do you want to attempt to identify the specific person who opted out in your texting tool?
- People can have multiple phone numbers associated with them in EveryAction. Do you want to opt out just the specific phone number that shows up in the texting tool data or all phones associated with a given person?

The code we used is available as a `sample script <https://github.com/move-coop/parsons/tree/master/useful_resources/sample_code/opt_outs_everyaction.py>`_ for you to view, re-use, or customize to fit your needs.
