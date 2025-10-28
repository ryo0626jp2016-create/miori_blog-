import argparse
from src.generate_v2 import main

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--keyword", default="")
    args = p.parse_args()
    main(args.url, args.keyword)
