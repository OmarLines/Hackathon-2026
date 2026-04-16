import os
import sys

# Ensure the app can be imported
sys.path.insert(0, os.path.abspath(os.curdir))

from app.dummy_data import referrers_data, referees_data


def generate_dummy_data_reference():
    with open("docs/dummy_data_reference.md", "w") as f:
        f.write("# Dummy Data Reference\n\n")
        f.write(
            "This document is automatically generated from the pre-loaded dummy data used for development.\n\n"
        )

        f.write("## Referrers\n\n")
        for email, data in referrers_data.items():
            f.write(f"- **Name:** {data['name']}\n")
            f.write(f"  - **Email:** `{email}`\n")
            f.write("  - **Password:** `password`\n")
            f.write(f"  - **Referrals:** {', '.join(data['referrals'])}\n\n")

        f.write("## Referrals (Referees)\n\n")
        for ref, data in referees_data.items():
            f.write(f"### Reference: {ref}\n")
            f.write(f"- **Child Name:** {data['child_name']}\n")
            f.write(f"- **Postcode:** {data['postcode']}\n")
            f.write(f"- **Status:** {data['status']}\n")
            f.write(f"- **Created At:** {data['created_at']}\n")
            f.write("- **Answers:**\n")
            for key, val in data["answers"].items():
                f.write(f"  - **{key}:** {val}\n")
            f.write("\n")

    print("Generated docs/dummy_data_reference.md")


if __name__ == "__main__":
    generate_dummy_data_reference()
