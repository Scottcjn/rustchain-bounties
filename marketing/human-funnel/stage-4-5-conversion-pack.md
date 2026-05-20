# Human Funnel Stage 4-5 Conversion Pack

Issue: [#318](https://github.com/Scottcjn/rustchain-bounties/issues/318)

Reward: 90 RTC
Audience: first-time users with old hardware who are curious but skeptical.

## Positioning

RustChain should feel like an invitation to use hardware people already own, not like a speculative coin pitch. The Stage 4 landing flow converts a reader from "this is interesting" to "I can try this today." Stage 5 keeps them engaged after the first action by giving them proof, status, referrals, and small ways to help.

Core promise:

> Your old machine can still do useful work. Start mining, prove it, and let the community see what it contributed.

Primary objections to answer before the click:

- "My computer is too old to matter."
- "I do not know how to mine."
- "I do not want to buy hardware."
- "I do not want a hype coin."
- "I need proof before I invite anyone else."

## Landing Page Copy

### Hero

Headline:

> Start Mining With the Computer You Already Own

Subheadline:

> RustChain rewards old machines for staying useful. Bring a spare laptop, desktop, mini PC, PowerPC box, or single-board computer back online and see whether it can earn RTC through proof-of-antiquity mining.

Primary CTA:

> Start Mining

Secondary CTA:

> See What Other Machines Are Running

Trust line:

> No VC pitch. No new rig required. Just your machine, a wallet, and a public proof trail.

Short supporting copy:

> RustChain is a community blockchain built around the idea that older hardware should not be treated as waste. The network gives vintage and low-power machines a real job: participate, report proof, and earn reputation through visible contribution.

### Three-Step CTA

Step 1: Pick your machine

> Use the machine you already have. Old laptop, retired desktop, forgotten mini PC, or vintage hardware all count. New hardware works too, but the point is to make existing hardware useful again.

Step 2: Create your miner identity

> Generate or connect a wallet so your work has a public destination. Your miner identity is how the community can verify what you ran and where rewards should go.

Step 3: Run, prove, and share

> Start the miner, capture your proof, and post the result. You can keep mining, submit a micro-bounty, or invite someone else with an old machine to try.

### Section: Why Old Hardware?

Headline:

> Because Useful Should Last Longer Than Supported

Copy:

> A computer does not become worthless because a vendor stopped selling it. RustChain turns that frustration into a simple action: run a miner, prove the machine is alive, and show that old hardware can still participate in a modern network.

Bullet copy:

- Keep a working machine out of the junk pile.
- Learn mining without buying a new rig.
- Earn RTC and reputation for visible participation.
- Help prove that a network can include unusual hardware.

### Section: What You Need

Headline:

> A Working Machine and About Five Minutes

Copy:

> You do not need a trading account, a hardware wallet, or a background in blockchain. Start with one machine and one wallet. If it runs, it can become part of your RustChain story.

Checklist:

- A computer you can install or run software on.
- Internet access.
- A terminal or basic command prompt.
- A RustChain wallet or miner ID.
- A screenshot or log snippet when the miner starts.

### Section: Proof Before Hype

Headline:

> Show the Work, Then Invite People

Copy:

> The first win is not a big payout. The first win is proof: your machine joined, produced a visible signal, and became part of a public ledger of contributors. That proof is what makes the invite believable.

Proof points to show on the page:

- Screenshot of a miner starting successfully.
- Example wallet or miner ID.
- Example "machine card" showing model, era, role, and status.
- Link to bounty submissions and hall-of-fame entries.

### Final CTA

Headline:

> Give One Old Machine a Job Today

Copy:

> Pick the machine. Run the miner. Post the proof. If it works, invite one person who has a retired laptop in a drawer.

Button:

> Start Mining

Secondary:

> View Beginner Bounties

## Start Mining Button Copy and Click Flow

### Button States

Default:

> Start Mining

Hover:

> Start With My Machine

Pressed:

> Preparing Setup

Loading:

> Checking Setup Options...

Success:

> Miner Setup Ready

Error:

> Show Manual Setup

### Click Flow

1. User clicks `Start Mining`.
2. Page opens a setup panel instead of sending the user away immediately.
3. Panel asks one simple question:

   > What kind of machine are you starting with?

4. Options:

   - Old laptop or desktop
   - Mini PC or single-board computer
   - Vintage Mac or PowerPC
   - I am not sure yet

5. After selection, show the matching setup card:

   - Recommended repo or setup guide link.
   - Minimum command or next action.
   - Wallet/miner ID field.
   - Screenshot placeholder: "Add your first proof screenshot here."

6. User clicks `Open Setup Guide`.
7. Page keeps a `Copy Proof Checklist` button visible:

   > Machine model, operating system, miner ID, start command, screenshot, one sentence about why this machine matters.

8. After guide click, show a retention prompt:

   > When your miner starts, come back and create your brag card.

### Empty and Fallback Copy

If the user does not know their machine type:

> No problem. Start with the general setup guide, then post your machine details in the bounty thread if you get stuck.

If setup links fail:

> The guided path is unavailable. Use the manual setup link and keep your miner ID ready.

If the user has no wallet yet:

> You can still read the setup guide. Create or request a wallet before submitting proof for rewards.

## Micro-Bounties for Non-Technical Users

Each micro-bounty should take less than 10 minutes and should create a visible proof artifact.

### Micro-Bounty 1: Old Machine Roll Call

Reward suggestion: 2 RTC

Task:

> Post a short "I have this machine" entry with model, approximate year, operating system, and one photo or screenshot.

Submission template:

```text
Machine:
Approximate year:
Operating system:
Why I want to run RustChain on it:
Wallet/miner id:
Proof image or screenshot:
```

Acceptance criteria:

- Includes machine model or best-effort description.
- Includes wallet/miner ID.
- Includes one image, screenshot, or terminal proof.
- Uses human language, not generic spam.

Why it works:

> It turns curiosity into a first public action before the user has to debug anything.

### Micro-Bounty 2: First Miner Proof

Reward suggestion: 5 RTC

Task:

> Start the miner or setup process and post the first successful terminal/log proof.

Submission template:

```text
Machine:
Setup guide used:
Command or step completed:
Wallet/miner id:
Proof screenshot/log:
One thing that was confusing:
```

Acceptance criteria:

- Shows a terminal line, log line, or setup screen.
- Includes wallet/miner ID.
- Names the setup guide used.
- Includes one sentence of feedback for improving the guide.

Why it works:

> It creates both conversion proof and usability feedback from a beginner.

### Micro-Bounty 3: Invite One Old Machine

Reward suggestion: 3 RTC

Task:

> Invite one person who owns an old machine and post the invite text plus their machine type if they reply.

Submission template:

```text
Who I invited:
Their machine:
Invite message:
Did they say yes, maybe, or no?
Wallet/miner id:
```

Acceptance criteria:

- Invite is personal and not mass-posted spam.
- Includes one specific machine or reason for inviting that person.
- Includes wallet/miner ID.
- Does not require the invited person to join before the bounty is valid.

Why it works:

> It moves Stage 5 retention into a small referral loop without pressuring users into promotion.

## Referral Mechanics Copy

### Invite Prompt

> Know someone with an old laptop, Mac mini, PowerPC machine, or retired desktop? Invite them to give it one useful job. If they post their first proof, both of you can appear on the weekly hall of fame.

### Share Card Copy

Default:

> I gave an old machine a new job on RustChain. If you have a retired computer, try mining with it and post your proof.

Short:

> Your old computer might still have work to do. Try RustChain.

Skeptic-friendly:

> I am testing whether old hardware can still contribute to a live blockchain. No new rig, no hype, just proof.

Vintage-hardware version:

> This machine was supposed to be obsolete. Now it has a miner ID.

### Referral Landing Copy

Headline:

> You Were Invited Because You Have a Machine Worth Testing

Copy:

> Someone thinks your old hardware can still do useful work. Start with one setup guide, post one proof, and decide after that whether you want to keep mining.

CTA:

> Test My Machine

### Referral Rules

- A referral counts when the invited user posts a machine roll call or first miner proof.
- The referrer must include their wallet/miner ID in the original invite proof.
- The invited user must include the referrer's GitHub handle or miner ID.
- Rewards should be capped per week to prevent spam.
- Repeated low-quality mass invites should be disqualified.

Suggested referral reward:

- 2 RTC for a verified machine roll call from an invited user.
- 5 RTC bonus if the invited user posts first miner proof within seven days.
- Weekly cap: 25 RTC per referrer unless manually approved.

## Brag Card Generator Spec

Purpose:

> Give each new miner a shareable proof card that makes their contribution easy to understand.

### Inputs

Required:

- Miner display name or GitHub handle.
- Wallet/miner ID.
- Machine name or model.
- Machine era or approximate year.
- Operating system.
- Proof status: `roll-call`, `setup-started`, `mining`, or `verified`.

Optional:

- CPU architecture.
- Photo or screenshot URL.
- First proof link.
- RTC earned.
- Referral handle.
- One-sentence machine story.

### Outputs

- PNG card for social sharing.
- Markdown snippet for GitHub issue comments.
- Plain-text alt copy for accessibility.
- JSON record for hall-of-fame ingestion.

### Template Fields

Card title:

> This Machine Still Works

Subtitle:

> Mining on RustChain

Fields:

- Miner
- Machine
- Era
- OS
- Status
- Proof link
- Wallet/miner ID, shortened to first 6 and last 6 characters

Footer:

> Every CPU has a voice.

### Rendering Approach

Recommended implementation:

- Static HTML template for browser rendering.
- CSS variables for status color and machine era accent.
- Server-side or CLI screenshot rendering with Playwright when automation is available.
- Fallback SVG template for environments without a browser renderer.
- Export sizes:
  - 1200 x 630 for social previews.
  - 1080 x 1080 for square posts.
  - 800 x 420 for GitHub-friendly embeds.

Status colors:

- `roll-call`: gray-blue, "machine registered"
- `setup-started`: amber, "setup started"
- `mining`: green, "miner running"
- `verified`: gold, "proof verified"

### Example Markdown Output

```markdown
## My RustChain Machine

- Miner: @example
- Machine: 2008 MacBook
- OS: Debian
- Status: mining
- Proof: <link>
- Wallet/miner id: eB51...pQV9

This machine was retired for years. Today it is mining on RustChain.
```

## Weekly Hall of Fame

Goal:

> Reward proof, persistence, and good invitations without turning the campaign into spam.

### Categories

- First Spark: best first machine roll call.
- Oldest Working Machine: most interesting vintage hardware proof.
- Best Proof: clearest screenshot, log, or setup explanation.
- Most Helpful Beginner Feedback: best note that improves the setup path.
- Invite That Worked: strongest personal referral proof.
- Persistence Award: miner that posts proof across multiple days.

### Prize Structure

Suggested weekly pool: 50 RTC

- First Spark: 8 RTC
- Oldest Working Machine: 8 RTC
- Best Proof: 8 RTC
- Most Helpful Beginner Feedback: 8 RTC
- Invite That Worked: 8 RTC
- Persistence Award: 8 RTC
- Editor's Note bonus: 2 RTC for a submission that tells a memorable story

### Rules

- One wallet/miner ID per submission.
- A user can win one category per week unless the pool is manually expanded.
- Screenshots must not expose private keys, seed phrases, or personal tokens.
- Referral wins require a real invited user submission or a clear reply from the invitee.
- Hall-of-fame entries should link to the original proof comment or PR.
- Judges can reject copied, AI-spam, or mass-invite content.
- Winners are posted every week with a short reason, not just a list of handles.

### Weekly Post Template

```markdown
# RustChain Old Machine Hall of Fame - Week of YYYY-MM-DD

This week, the community brought old hardware back online and posted proof.

## Winners

| Category | Winner | Machine | Proof | Prize |
| --- | --- | --- | --- | --- |
| First Spark | @user | 2012 ThinkPad | link | 8 RTC |
| Oldest Working Machine | @user | PowerPC Mac | link | 8 RTC |
| Best Proof | @user | Mini PC | link | 8 RTC |
| Beginner Feedback | @user | Old desktop | link | 8 RTC |
| Invite That Worked | @user | Referral proof | link | 8 RTC |
| Persistence Award | @user | Daily miner | link | 8 RTC |

## What We Learned

- One setup step that confused beginners:
- One hardware type that worked better than expected:
- One guide improvement to ship next:

## Next Week

Bring one machine, post one proof, and invite one person who has hardware sitting unused.
```

## Engineering Handoff Notes

Minimum viable implementation:

- Add landing page sections as static content first.
- Store setup-choice state in the URL query string, such as `?machine=vintage-mac`.
- Track CTA clicks with privacy-preserving event names:
  - `start_mining_click`
  - `machine_type_selected`
  - `setup_guide_opened`
  - `proof_checklist_copied`
  - `brag_card_started`
- Create a `brag-card.json` schema matching the inputs above.
- Render brag cards from the schema so issue comments, hall-of-fame pages, and share images use the same source.
- Keep wallet/miner ID validation light at first: required string, visible warning if shorter than expected, no private-key fields.

Suggested first screen order:

1. Hero with primary CTA.
2. Three-step CTA.
3. Machine type setup panel.
4. Proof checklist.
5. Brag card generator.
6. Micro-bounties.
7. Referral invite.
8. Weekly hall of fame.

Safety copy for all forms:

> Never paste a seed phrase, private key, exchange login, or personal access token. RustChain proof only needs public machine and miner information.

Success metric:

> A successful Stage 4-5 flow is not just a click. It is a posted proof artifact with a wallet/miner ID, machine description, and a next action.
