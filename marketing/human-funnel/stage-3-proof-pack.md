# Human Funnel Stage 3 Proof Pack

Issue: [#317](https://github.com/Scottcjn/rustchain-bounties/issues/317)

Reward: 55 RTC

Audience: skeptical non-developer users who want proof that RustChain can be tried with ordinary or older hardware before they invest more time.

## Stage 3 Goal

Stage 3 turns curiosity into repeatable evidence. The assets below are designed to help a first-time user say:

> Someone like me tried this, posted proof, and showed exactly what happened.

The proof pack uses three kinds of evidence:

1. Testimonial-style posts that sound specific and believable.
2. A five-minute setup guide with screenshot placeholders.
3. A comparison table that explains why old hardware still has a meaningful role.

## Testimonial-Style Post Templates

These are templates, not fake testimonials. Each should be filled with a real user's machine, proof link, and outcome before publishing.

### Template 1: The Skeptical First Run

```text
I did not expect this to work.

Machine: [model/year]
OS: [operating system]
RustChain step completed: [wallet/miner/setup/proof]
Proof: [link or screenshot]

I started with the machine I already had because I did not want to buy anything new just to test a blockchain project. The first win was simple: I got a public miner ID and a proof screenshot.

Still skeptical, but now I have something real to inspect.

CTA: Try one machine and post your first proof.
```

Best use:

- Reply to people who say old hardware is pointless.
- Pair with a terminal screenshot or setup panel image.

### Template 2: The Old Hardware Comeback

```text
This machine was sitting unused for [time period].

Machine: [model/year]
Why it was retired: [short reason]
What it did today: [started setup/ran miner/submitted proof]
Proof: [link]

It is not fast. It is not new. But it still works, and RustChain gave it a job that made sense: prove it can participate.

CTA: If you have an old computer in a drawer, try the five-minute mining guide.
```

Best use:

- Social post for vintage hardware owners.
- Hall-of-fame nomination captions.

### Template 3: The Non-Developer Proof

```text
I am not a blockchain developer.

I followed the beginner setup path, copied the proof checklist, and posted:

- Machine: [model]
- OS: [operating system]
- Wallet/miner id: [public id]
- Proof screenshot: [link]
- Confusing step: [one sentence]

That was enough to become part of the RustChain proof trail.

CTA: You do not need to understand everything before you test one machine.
```

Best use:

- Beginner onboarding.
- Reassurance for people intimidated by terminal output.

### Template 4: The Useful Feedback Post

```text
My first RustChain attempt was not perfect, but it helped.

Machine: [model/year]
Setup guide used: [guide link]
Where I got stuck: [step]
What fixed it: [fix or workaround]
Proof or log: [link]

This is why beginner proof matters. Even when the setup is messy, the feedback makes the next person's path easier.

CTA: If your first run fails, post the error. That is useful proof too.
```

Best use:

- Turning support friction into community evidence.
- Encouraging honest reports instead of polished-only wins.

### Template 5: The Invite That Worked

```text
I invited [person/handle] because they had an old [machine].

They tried RustChain and posted:

- Machine: [model]
- First proof: [link]
- Status: [roll-call/setup-started/mining/verified]

This is the part I like: the invite was not "buy this." It was "test the machine you already own."

CTA: Invite one person with old hardware and ask them to post proof.
```

Best use:

- Referral loop.
- Weekly hall-of-fame "Invite That Worked" category.

## Zero to Mining in 5 Minutes

This guide is intentionally short. It should get a skeptical user to the first proof artifact, not teach the entire protocol.

### Before You Start

You need:

- One computer you can run commands on.
- Internet access.
- A public wallet or miner ID.
- A place to save a screenshot.

Do not paste:

- Seed phrases.
- Private keys.
- Personal access tokens.
- Exchange logins.

### Minute 0-1: Pick the Machine

Choose the machine you want to test.

Good first choices:

- An old laptop that still boots.
- A desktop you no longer use daily.
- A mini PC or single-board computer.
- A vintage Mac or PowerPC machine if you already know how to run commands on it.

Write down:

```text
Machine:
Approximate year:
Operating system:
Why I am testing it:
```

Screenshot placeholder:

> [Screenshot 1: photo of the machine or system information screen]

### Minute 1-2: Create or Find Your Public Miner ID

Use the project setup guide to create or identify the public wallet/miner ID for your proof.

Proof checklist:

```text
Wallet/miner id:
Guide used:
Date:
```

Keep private recovery data off GitHub. Only publish the public ID.

Screenshot placeholder:

> [Screenshot 2: public miner ID or wallet screen with private data hidden]

### Minute 2-3: Open the Setup Guide

Open the beginner setup guide or the machine-specific guide for your hardware type.

Copy the first command or first setup action into your notes before running it.

Proof checklist:

```text
Setup guide link:
First command or step:
Expected result:
```

Screenshot placeholder:

> [Screenshot 3: setup guide section or command prompt before running]

### Minute 3-4: Start the Miner or Setup Check

Run the first setup command, miner start command, or validation check from the guide.

If it succeeds, capture the success line.

If it fails, capture the error. A clear error is still useful proof.

Proof checklist:

```text
Command or step completed:
Result: success / failed / unclear
Log line or error:
```

Screenshot placeholder:

> [Screenshot 4: terminal output showing success, failure, or next-step message]

### Minute 4-5: Post Your First Proof

Use this format in the bounty thread, setup thread, or proof collection page.

```text
## First RustChain Proof

Machine:
Approximate year:
Operating system:
Wallet/miner id:
Setup guide used:
Command or step completed:
Result:
Proof screenshot/log:
One thing that was easy:
One thing that was confusing:
```

Screenshot placeholder:

> [Screenshot 5: completed proof comment before submission]

CTA:

> Post the proof first. Improve the setup second. Keep mining if the machine works.

## Old Hardware vs Modern Hardware on RustChain

| Question | Old hardware | Modern hardware | RustChain framing |
| --- | --- | --- | --- |
| Is it fast? | Usually no. It may be limited by CPU, RAM, storage, or OS support. | Usually yes. It can run setup steps and mining tasks more easily. | Speed helps, but RustChain also values participation and visible proof. |
| Is it accessible? | Often already owned, borrowed, repaired, or found unused. | Often requires a new purchase or daily-use machine. | The lowest-friction start is the machine you already own. |
| Does it need special care? | Yes. Expect old batteries, disks, fans, and OS issues. | Less often, though drivers and security updates still matter. | Setup guides should collect feedback from both groups. |
| Why is it interesting? | It proves forgotten machines can still contribute. | It helps run smoother demos, tools, and infrastructure. | Both roles matter: old hardware tells the story, modern hardware supports the path. |
| Best proof artifact | Photo, machine story, miner ID, terminal screenshot, setup notes. | Clean logs, uptime proof, dashboard screenshots, repeatable guide output. | Publish proof that another beginner can understand. |
| Best first user | Collector, repair person, student, hobbyist, or anyone with a retired computer. | Developer, maintainer, guide writer, or user who wants a quick successful run. | Do not shame either path. The network needs both. |
| Common failure | Missing packages, unsupported OS, weak battery, unclear commands. | Overthinking the setup, skipping proof, treating the machine as invisible. | Every failure should become a clearer guide step. |
| Emotional value | High. The machine has a story. | Medium. The machine proves ease and reliability. | Pair old-machine stories with modern-machine repeatability. |

## Common Objections and Responses

### "My machine is too old."

Response:

> Maybe. The fastest way to know is to post a roll-call entry first. Even if mining does not work immediately, your machine details help the community improve the setup path.

### "I am not technical enough."

Response:

> You do not need to understand the whole chain to post first proof. Start with machine details, wallet/miner ID, setup guide used, and one screenshot.

### "This sounds like blockchain hype."

Response:

> Treat it as a test, not a belief system. Run one machine, post one proof, and decide after you see the result.

### "I do not want to buy hardware."

Response:

> Do not buy hardware for the first test. Use a machine you already own or can safely borrow.

### "What if setup fails?"

Response:

> A failed setup with a clear screenshot is still useful. It shows exactly where the guide needs to improve.

### "Will I make money?"

Response:

> Do not start with a payout expectation. Start with proof. Rewards depend on bounty rules, verification, and the public proof you submit.

### "Is it safe to post this?"

Response:

> Post only public machine information, public wallet/miner ID, screenshots with private data hidden, and setup logs. Never post seed phrases, private keys, tokens, or personal logins.

## Simple Repeatable Proof Format

Use this format for first proof, testimonial posts, micro-bounties, and hall-of-fame nominations.

```markdown
## RustChain Proof

**Status:** roll-call / setup-started / mining / verified
**Machine:**
**Approximate year:**
**Operating system:**
**Wallet/miner id:**
**Setup guide used:**
**Command or step completed:**
**Proof link or screenshot:**
**What worked:**
**What was confusing:**
**Next action:**
```

Quality bar:

- Specific machine details.
- Public wallet/miner ID.
- One screenshot, log, or proof link.
- One useful note for the next beginner.
- No private secrets.

## Proof Review Checklist

Reviewer should be able to answer:

- What machine was used?
- What public identity should receive credit?
- What action did the user complete?
- Is there visible proof?
- Is private information hidden?
- Is the next step clear?

Fast response template:

```text
Proof received.

Machine:
Status:
Next recommended action:

Thanks for including [specific useful detail]. Please hide or remove [private/sensitive item] if visible.
```

## Publication Notes

- Use real proof links before publishing testimonial-style posts.
- Do not imply guaranteed earnings.
- Keep screenshots readable and crop out private data.
- Highlight friction honestly; beginner confusion is useful evidence.
- Prefer "try one machine" over broad claims about replacing modern infrastructure.
