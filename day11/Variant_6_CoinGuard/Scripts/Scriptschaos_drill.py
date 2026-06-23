import random
import time
from datetime import datetime

class ChaosDrill:

    def __init__(self):
        self.safe_block = None

    def stop_matching_engine(self):
        print("[CHAOS] Matching Engine stopped")

    def simulate_51_attack(self):
        self.safe_block = random.randint(
            900000,
            930000
        )

        print(
            f"[CHAOS] 51% attack detected near block {self.safe_block}"
        )

    def corrupt_blockchain(self):
        print(
            "[CHAOS] Blockchain reorganization simulated"
        )

    def disable_deposits(self):
        print(
            "[CHAOS] Deposits disabled"
        )

    def disable_withdrawals(self):
        print(
            "[CHAOS] Withdrawals disabled"
        )

    def start_drill(self):

        print("=" * 50)
        print("CoinGuard Disaster Recovery Drill")
        print("=" * 50)

        print(
            f"Start time: {datetime.now()}"
        )

        self.disable_deposits()

        self.disable_withdrawals()

        time.sleep(1)

        self.stop_matching_engine()

        time.sleep(1)

        self.corrupt_blockchain()

        time.sleep(1)

        self.simulate_51_attack()

        print(
            f"[INFO] Rollback block: {self.safe_block}"
        )

        print(
            "[INFO] Execute Recovery_Runbook.md"
        )

        print(
            f"Finish time: {datetime.now()}"
        )

if __name__ == "__main__":

    drill = ChaosDrill()

    drill.start_drill()