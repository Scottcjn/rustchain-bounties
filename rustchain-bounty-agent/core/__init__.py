"""
Main Agent Orchestrator - Coordinates all components
"""

import os
import time
from datetime import datetime

from scanner import BountyScanner
from evaluator import BountyEvaluator
from generator import CodeGenerator
from submitter import PRSubmitter


class BountyAgent:
    """Main autonomous bounty agent"""
    
    def __init__(self):
        print("🚀 Initializing RustChain Bounty Agent...")
        
        self.scanner = BountyScanner()
        self.evaluator = BountyEvaluator()
        self.generator = CodeGenerator()
        self.submitter = PRSubmitter()
        
        self.target_repos = [
            "Scottcjn/rustchain-bounties",
            "Scottcjn/Rustchain",
        ]
        
        print("✅ Agent initialized and ready!")
    
    def run_cycle(self):
        """Run one complete bounty hunting cycle"""
        print("\n" + "="*60)
        print(f"🔄 BOUNTY HUNTING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # Step 1: Scan for bounties
        print("\n📡 STEP 1: Scanning for bounties...")
        bounties = self.scanner.scan_multiple(self.target_repos)
        
        if not bounties:
            print("❌ No bounties found. Waiting for next cycle...")
            return
        
        self.scanner.print_summary()
        
        # Step 2: Evaluate bounties
        print("\n🧠 STEP 2: Evaluating bounties...")
        best_bounties = self.evaluator.select_best(bounties, top_n=3)
        self.evaluator.print_evaluation(best_bounties)
        
        # Step 3: Select top bounty
        top_bounty = best_bounties[0]['bounty']
        print(f"\n🎯 STEP 3: Selected bounty: {top_bounty.title[:50]}")
        
        # Step 4: Analyze and generate solution
        print("\n💻 STEP 4: Generating solution...")
        analysis = self.generator.analyze_bounty(
            top_bounty.title,
            top_bounty.body
        )
        
        if not analysis['success']:
            print(f"❌ Analysis failed: {analysis.get('error')}")
            return
        
        print("✅ Analysis complete")
        
        # Step 5: Fork and prepare
        print("\n🍴 STEP 5: Preparing repository...")
        repo_parts = top_bounty.url.split('/')
        if len(repo_parts) >= 5:
            repo_name = f"{repo_parts[3]}/{repo_parts[4]}"
        else:
            print("❌ Could not parse repository name")
            return
        
        fork_name = self.submitter.fork_repository(repo_name)
        if not fork_name:
            print("❌ Fork failed")
            return
        
        # Step 6: Create branch
        branch_name = f"bounty-{top_bounty.number}-{int(time.time())}"
        if not self.submitter.create_branch(fork_name, branch_name):
            print("❌ Branch creation failed")
            return
        
        print(f"\n✅ Ready to implement!")
        print(f"   Repository: {fork_name}")
        print(f"   Branch: {branch_name}")
        print(f"   Next: Implement solution and commit changes")
    
    def run(self, cycles: int = 1, interval_minutes: int = 60):
        """Run the agent for multiple cycles"""
        print(f"\n🤖 Starting Bounty Agent - {cycles} cycles")
        
        for i in range(cycles):
            self.run_cycle()
            
            if i < cycles - 1:
                print(f"\n⏳ Waiting {interval_minutes} minutes before next cycle...")
                time.sleep(interval_minutes * 60)
        
        print("\n✅ Agent run complete!")


if __name__ == "__main__":
    # Run the agent
    agent = BountyAgent()
    agent.run(cycles=1)
