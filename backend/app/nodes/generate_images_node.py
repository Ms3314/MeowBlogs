"""Generate-images node: renders each planned image and replaces placeholders."""
from pathlib import Path

from app.schemas.state import State
from app.services.openai_image import _openai_generate_image_bytes


def generate_and_place_images(state: State) -> dict:
    plan = state["plan"]
    assert plan is not None

    md = state.get("md_with_placeholders") or state["merged_md"]
    image_specs = state.get("image_specs", []) or []

    if image_specs is None:
        filename = plan.blog_title.lower().replace(" ", "_") + ".md"
        output_path = Path(filename)
        output_path.write_text(state['merged_md'], encoding="utf-8")

    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    for specs in image_specs:
        placeholder = specs["placeholder"]
        filename = Path(specs["filename"]).name
        out_path = images_dir / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if not out_path.exists():
            try:
                img_bytes = _openai_generate_image_bytes(
                    specs["prompt"],
                    size=specs.get("size", "1024x1024"),
                    quality=specs.get("quality", "low"),
                )
                out_path.write_bytes(img_bytes)
            except Exception as e:
                prompt_block = (
                    f"> **[IMAGE GENERATION FAILED]** {specs.get('caption','')}\n>\n"
                    f"> **Alt:** {specs.get('alt','')}\n>\n"
                    f"> **Prompt:** {specs.get('prompt','')}\n>\n"
                    f"> **Error:** {e}\n"
                )
                md = md.replace(placeholder, prompt_block)
                continue
        img_md = f"![{specs['alt']}](images/{filename})\n*{specs['caption']}*"
        md = md.replace(placeholder, img_md)

    filename = plan.blog_title.lower().replace(" ", "_") + ".md"
    output_path = Path(filename)
    output_path.write_text(md, encoding="utf-8")
    return {"final": md}
