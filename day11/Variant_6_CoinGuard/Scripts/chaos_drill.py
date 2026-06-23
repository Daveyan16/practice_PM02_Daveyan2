import random
import time
from datetime import datetime

class ChaosDrill:

    def __init__(self):
        self.safe_block = None

    def disable_deposits(self):
        print("[CHAOS] Deposits disabled")

    def disable_withdrawals(self):
        print("[CHAOS] Withdrawals disabled")

    def stop_matching_engine(self):
        print("[CHAOS] Matching Engine stopped")

    def simulate_blockchain_reorg(self):
        print("[CHAOS] Blockchain reorganization simulated")

    def simulate_51_attack(self):
        self.safe_block = random.randint(900000, 930000)

        print(
            f"[CHAOS] 51% attack detected near block {self.safe_block}"
        )

    def recovery_phase(self):
        print("[RECOVERY] Finding safe block...")
        time.sleep(1)

        print(
            f"[RECOVERY] Rollback to block {self.safe_block}"
        )

        time.sleep(1)

        print("[RECOVERY] Restoring blockchain snapshot...")
        time.sleep(1)

        print("[RECOVERY] Replaying WAL logs...")
        time.sleep(1)

        print("[RECOVERY] Validating balances...")
        time.sleep(1)

        print("[RECOVERY] Exchange restored")

    def run(self):

        print("=" * 60)
        print("CoinGuard Disaster Recovery Chaos Drill")
        print("=" * 60)

        print(
            f"Start Time: {datetime.now()}"
        )

        self.disable_deposits()
        time.sleep(1)

        self.disable_withdrawals()
        time.sleep(1)

        self.stop_matching_engine()
        time.sleep(1)

        self.simulate_blockchain_reorg()
        time.sleep(1)

        self.simulate_51_attack()
        time.sleep(1)

        self.recovery_phase()

        print(
            f"Finish Time: {datetime.now()}"
        )

        print("=" * 60)
        print("DR Drill Completed Successfully")
        print("=" * 60)

if __name__ == "__main__":
    drill = ChaosDrill()
    drill.run()