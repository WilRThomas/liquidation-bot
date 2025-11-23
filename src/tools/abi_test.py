import sys
from pathlib import Path

# Add project src/ to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from sdk.abi_loader import load_abi


def main():
    print("ABI smoke test:")
    for name in ["erc20", "aave_pool", "aave_oracle"]:
        try:
            abi = load_abi(name)
            print(f"  {name}: loaded ({len(abi)} entries)")
        except Exception as e:
            print(f"  {name}: ERROR -> {e}")


if __name__ == "__main__":
    main()
