from pathlib import Path

from app.schemas.rapla.schema_rapla_file import RaplaFile


def main() -> None:
    output_path = Path(__file__).with_name("rapla.xml")
    data = RaplaFile()
    data.save_to_file(str(output_path))
    print(f"Saved XML to: {output_path}")


if __name__ == "__main__":
    main()
