import sys
from mail_processor.engine import EmailProcessor


def main():
    inbox_dir = sys.argv[1] if len(sys.argv) > 1 else "./inbox"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./output"
    rules_file = "rules.json"

    processor = EmailProcessor(
        src_dir=inbox_dir,
        dst_dir=output_dir,
        rules_path=rules_file
    )
    processor.process_all()


if __name__ == "__main__":
    main()
