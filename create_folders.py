import os

if __name__ == "__main__":
    folders = ["in-sample", "out-sample"]
    for folder in folders:
        if not os.path.exists(f"stat/{folder}/ar"):
            os.makedirs(f"stat/{folder}/ar")

        if not os.path.exists(f"stat/{folder}/asset"):
            os.makedirs(f"stat/{folder}/asset")

        if not os.path.exists(f"stat/{folder}/no-stocks"):
            os.makedirs(f"stat/{folder}/no-stocks")

        if not os.path.exists(f"stat/{folder}/portfolio"):
            os.makedirs(f"stat/{folder}/portfolio")

        if not os.path.exists(f"stat/{folder}/sharpe"):
            os.makedirs(f"stat/{folder}/sharpe")
