"""Merge node: concatenates worker sections into a single markdown doc."""
from pathlib import Path

from app.schemas.state import State


def merge_content(state: State) -> dict:  # brings all the work together and stiches
    plan = state["plan"]
    if plan is None:
        raise ValueError("Reducer called without plan.")

    ordered_sections = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered_sections).strip()  # need to understand what this does lol

    final_md = f"# {plan.blog_title} \n\n {body}\n"

    # filename = plan.blog_title.lower().replace(" " , "_") + ".md"
    # output_path = Path(filename)
    # output_path.write_text(final_md , encoding="utf-8")
    return {"merged_md": final_md}
