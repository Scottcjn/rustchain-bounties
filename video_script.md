# Video Tutorial: Install and Run the RustChain Miner

**Duration**: ~2 minutes 30 seconds
**Platform**: YouTube / BoTTube
**Preparation**:
- Have a terminal open with Rust installed (rustup)
- Clone the Elyan Labs RustChain repository: `git clone https://github.com/scottcjn/rustchain`

## Script

**[Intro - 0:00-0:15]**
"Hi everyone! In this quick tutorial, I'll show you how to install and run the RustChain miner. RustChain is a proof-of-work blockchain written in Rust, and running a miner is the best way to support the network. Let's dive in."

**[Step 1: Prerequisites - 0:15-0:30]**
"First, make sure you have Rust installed. If not, visit rustup.rs and follow the instructions. Also, ensure Git is installed. Open your terminal."

**[Step 2: Clone Repository - 0:30-0:45]**
"Clone the RustChain repo using: `git clone https://github.com/scottcjn/rustchain` and enter the directory: `cd rustchain`."

**[Step 3: Build the Project - 0:45-1:10]**
"Now build the project. Run `cargo build --release`. This may take a few minutes. RustChain compiles efficiently, so you should see a binary under `target/release/`. I'll speed up this part."

**[Step 4: Configure and Run - 1:10-1:50]**
"Once built, you'll find the `rustchain-miner` executable. Run it with `./target/release/rustchain-miner`. You'll see it connect to the network, sync the blockchain, and start mining. It will output its hashing rate and blocks found. For optimal performance, set the number of threads: `--threads 4`. Here's a quick demo."

**[Demo - 1:50-2:20]**
(Show terminal output: connecting, syncing, mining, and a block found. Narrate briefly.)
"As you can see, it's mining on testnet. You can check your progress on the RustChain explorer. Supporting the network has never been easier."

**[Outro - 2:20-2:30]**
"That's it! Thank you for watching. Don't forget to like and subscribe. Leave a comment with your RTC wallet to claim the bounty. Happy mining!"

---
**Post-production**: Add captions, link to Elyan Labs in description, and upload to YouTube/BoTTube. Submit link + wallet address in the GitHub issue.