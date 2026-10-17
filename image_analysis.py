import os
import json
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()

# Model and sizing configurations
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

# 1. Sub-Schema for strict composting metrics parameters
class CompostBlueprint(BaseModel):
    is_compostable: bool = Field(description="True if this item can go into a standard backyard or industrial compost bin.")
    material_type: str = Field(description="Must sort strictly into: 'Green (Nitrogen-rich)', 'Brown (Carbon-rich)', or 'Non-Compostable'.")
    expected_decomposition_timeline: str = Field(description="Estimated time to break down (e.g., '2-4 weeks', '6 months').")
    decomposition_acceleration_tips: list[str] = Field(description="Exact steps to speed up decay (e.g., chop into 1-inch pieces, adjust moisture, balance carbon ratio).")
    compost_bin_precautions: list[str] = Field(description="Warnings specific to bugs, odors, or structural damage (e.g., 'Avoid adding dairy to prevent pests', 'Turn pile weekly').")

# 2. Main structural analysis data model mapping fields
class WasteAnalysisSchema(BaseModel):
    identifiable_item: str = Field(description="The exact item name or material identified visually.")
    confidence_level: str = Field(description="Confidence ranking: High, Medium, or Low based on visual clarity.")
    category: str = Field(description="Must sort strictly into: Recyclable, Organic, Reusable, Hazardous, Electronic Waste, General Waste, or Uncertain.")
    disposal_suggestions: list[str] = Field(description="Actionable, practical steps to dispose or upcycle this exact item.")
    safety_precautions: list[str] = Field(description="Mandatory cleaning, washing, or toxic hazard handling safety rules.")
    check_local_rules_needed: bool = Field(description="True if municipal variations apply heavily.")
    technical_justification: str = Field(description="A concise explanation linking visible image textures to your decision.")
    compost_guide: CompostBlueprint = Field(description="Specific sub-analysis blueprints detailing organic breakdown structures.")

def show_image_analysis():
    st.title("🔍 AI Waste Analysis & Composting Blueprint")
    st.write(
        "Upload a picture of an item to learn how it "
        "might be sorted, disposed of, or composted responsibly."
    )

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of one waste item."
    )

    if uploaded_file is None:
        if "last_eco_analysis" in st.session_state:
            del st.session_state["last_eco_analysis"]
            
        st.info("👆 Upload an image to begin your analysis.")
        st.markdown("""
        ### Examples you can try
        - 🍌 Food scraps / Banana peels
        - 📦 Cardboard boxes (Brown material)
        - 🥤 Plastic bottles
        - ☕ Coffee grounds
        """)
        return

    if uploaded_file.size > MAX_IMAGE_SIZE:
        st.error("Please upload an image smaller than 10 MB.")
        return

    st.image(uploaded_file, caption="Your uploaded image", use_container_width=True)

    # Automatically flush out stale predictions upon receiving a fresh file change
    if "current_file_name" not in st.session_state or st.session_state["current_file_name"] != uploaded_file.name:
        st.session_state["current_file_name"] = uploaded_file.name
        if "last_eco_analysis" in st.session_state:
            del st.session_state["last_eco_analysis"]

    if st.button("🌱 Analyze Image & Composting Strategy", type="primary", use_container_width=True):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            st.error("API key missing. Add GEMINI_API_KEY to your .env file.")
            return

        client = genai.Client(api_key=api_key)

        system_instruction = """
        You are EcoScan, an environmental waste-analysis expert pipeline. 
        You analyze image bytes and provide absolute clarity on material types.
        You pay extra attention to organic processing steps, composting parameters, and breakdown dynamics.
        """

        try:
            with st.spinner("EcoScan is computing breakdown workflows... 🌿"):
                image_bytes = uploaded_file.getvalue()
                image_part = types.Part.from_bytes(data=image_bytes, mime_type=uploaded_file.type)

                response = client.models.generate_content(
                    model=MODEL,
                    contents=["Perform localized waste analysis and detail composting methods for this item.", image_part],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1,  
                        response_mime_type="application/json",
                        response_schema=WasteAnalysisSchema,
                    ),
                )

                if not response.text:
                    st.warning("No structural data returned. Please try again.")
                    return

                st.session_state["last_eco_analysis"] = json.loads(response.text)

        except Exception as exc:
            st.error("Analysis failed. Verify your network, API key configuration, and usage balance profiles.")
            print(f"API Error: {exc}")

    # Render results dynamically
    if st.session_state.get("last_eco_analysis"):
        data = st.session_state["last_eco_analysis"]
        st.divider()
        st.subheader("🌍 General Analysis Results")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Identified Object", value=data["identifiable_item"])
            st.metric(label="AI Confidence Level", value=data["confidence_level"])
        with col2:
            st.metric(label="Recommended Category", value=data["category"])
            st.metric(label="Local Rules Check Required?", value="Yes ⚠️" if data["check_local_rules_needed"] else "No ✅")

        st.markdown(f"**Technical Diagnosis:** {data['technical_justification']}")

        # ----------------------------------------------------
        # NEW COMPONENT DOCK: DEDICATED COMPOST BLUEPRINT VIEW
        # ----------------------------------------------------
        st.divider()
        st.subheader("♻️ Dedicated Composting Guide")
        comp = data["compost_guide"]

        if comp["is_compostable"]:
            st.success("✅ This item is verified as COMPOSTABLE!")
            
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                st.metric(label="Compost Classification Group", value=comp["material_type"])
            with c_col2:
                st.metric(label="Est. Decomposition Timeline", value=comp["expected_decomposition_timeline"])
                
            st.write("#### 🚀 Action Steps to Accelerate Decomposition:")
            for tip in comp["decomposition_acceleration_tips"]:
                st.write(f"- {tip}")
                
            st.write("#### ⚠️ Compost Bin Safety & Odour Management:")
            for caution in comp["compost_bin_precautions"]:
                st.write(f"- {caution}")
        else:
            st.error("❌ This item is classified as NON-COMPOSTABLE.")
            st.write(f"**Reason/Precaution:** {comp['compost_bin_precautions'][0] if comp['compost_bin_precautions'] else 'Do not mix this artificial/toxic item into backyard organic environments.'}")

        # General items block output
        st.divider()
        st.write("### 📋 Alternative Disposal & Cleaning Steps")
        for step in data["disposal_suggestions"]:
            st.write(f"- {step}")

        downloadable_text = json.dumps(data, indent=4)
        st.download_button(
            "📥 Download Advanced JSON Report",
            data=downloadable_text,
            file_name="ecoscan_compost_report.json",
            mime="application/json",
            use_container_width=True
        )

if __name__ == "__main__":
    show_image_analysis()
