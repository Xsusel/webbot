import asyncio
import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

from app.bot_engine import BotManager

async def test_bot_manager():
    print("Testing BotManager...")
    manager = BotManager()

    # 1. Load Tokens
    tokens = ["oauth:123", "oauth:456", "oauth:789"]
    manager.load_tokens(tokens)
    print(f"Loaded bots: {len(manager.bots)}")
    assert len(manager.bots) == 3

    # 2. Test Follow
    print("Testing Follow...")
    # This just mocks the API call log
    results = await manager.follow_target("target_user_id")
    # All should return 204 (mocked)
    assert all(r == 204 for r in results)
    print("Follow test passed.")

    # 3. Test Status
    status = manager.get_status()
    print("Status:", status)
    assert status["total_bots"] == 3

    print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_bot_manager())
