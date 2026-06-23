import random

safe_block = random.randint(
    900000,
    930000
)

print(
    f"51 percent attack detected. Rollback to block {safe_block}"
)