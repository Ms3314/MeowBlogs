"""Decide-images node: inserts [[IMAGE_n]] placeholders and proposes prompts."""
from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import llm
from app.schemas.image import GlobalImagePlan
from app.schemas.state import State

# here we will make the subgraph where we add the placeholders with ids and then we will also make an ImageItem corresponding to that id
DECIDE_IMAGES_SYSTEM = """You are an expert technical editor.
Decide if images/diagrams are needed for THIS blog.

Rules:
- Max 3 images total.
- Each image must materially improve understanding (diagram/flow/table-like visual).
- Insert placeholders exactly: [[IMAGE_1]], [[IMAGE_2]], [[IMAGE_3]].
- If no images needed: md_with_placeholders must equal input and images=[].
- Avoid decorative images; prefer technical diagrams with short labels.
Return strictly GlobalImagePlan.
"""


# this is used to decide which image is suppose
def decide_images(state: State) -> dict:
    # this node plans to place the images in the right place
    planner = llm.with_structured_output(GlobalImagePlan)
    merged_md = state["merged_md"]
    plan = state["plan"]

    assert plan is not None

    # here is a question does a blog_kind matter for the question ???
    image_plan = planner.invoke([
        SystemMessage(content=DECIDE_IMAGES_SYSTEM),
        HumanMessage(
            content=(
                f"Blog kind {plan.blog_kind}"
                f"Topic: {state["topic"]}"
                "Insert placeholders + propose image prompts. \n\n"
                f"{merged_md}"
            )
        )
    ])

    return {
        "md_with_placeholders": image_plan.md_with_placeholders,
        "image_specs": [img.model_dump() for img in image_plan.images]
    }
