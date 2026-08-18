import streamlit as st
import os
import uuid
import base64
from datetime import datetime

from app.services.pdf_service import extract_text_from_pdf
from app.services.chunking_service import create_page_chunks
from app.services.vector_service import store_chunks, search_chunks
from app.services.llm_service import generate_answer


st.set_page_config(
    page_title="Semantic Context Retrieval Engine",
    page_icon="🐱",
    layout="wide"
)


hero_image_path = os.path.join(
    "assets",
    "cat_hero.png"
)

hero_image_base64 = ""

if os.path.exists(hero_image_path):

    with open(
        hero_image_path,
        "rb"
    ) as image_file:

        hero_image_base64 = base64.b64encode(
            image_file.read()
        ).decode()


st.markdown(
    f"""
<style>

/* =====================================================
   MAIN APP
===================================================== */

.stApp {{
    background-color: #0B0F17;
}}


/* =====================================================
   SIDEBAR
===================================================== */

[data-testid="stSidebar"] {{
    background-color: #0E1420;
    border-right: 1px solid #252D3D;
}}

[data-testid="stSidebar"] > div:first-child {{
    padding-top: 2rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
}}


/* =====================================================
   MAIN CONTAINER
===================================================== */

.main .block-container {{
    max-width: 1200px;
    padding-top: 0.5rem;
    padding-left: 3rem;
    padding-right: 3rem;
}}


/* =====================================================
   HERO SECTION
===================================================== */

.hero-section {{
    position: relative;

    /* CHANGED: 285px -> 360px */
    min-height: 360px;

    margin-top: 0.5rem;
    margin-bottom: 2rem;

    border-radius: 22px;

    overflow: hidden;

    border: 1px solid #7C1AD7;

    box-shadow:
        0 0 20px rgba(124, 26, 215, 0.35),
        0 0 45px rgba(124, 26, 215, 0.15);

    background:
        linear-gradient(
            90deg,
            rgba(8, 11, 18, 0.96) 0%,
            rgba(8, 11, 18, 0.78) 40%,
            rgba(8, 11, 18, 0.35) 75%,
            rgba(8, 11, 18, 0.45) 100%
        ),
        url("data:image/png;base64,{hero_image_base64}");

    background-size: cover;
    background-position: center;
}}


.hero-content {{
    position: relative;

    z-index: 2;

    /* CHANGED: more vertical spacing */
    padding: 65px 52px;

    max-width: 650px;
}}


.hero-welcome {{
    font-size: 22px;

    font-weight: 600;

    color: #F5F5F7;

    margin-bottom: 4px;
}}


.hero-title {{
    font-size: 42px;

    font-weight: 800;

    color: #FFFFFF;

    line-height: 1.15;

    margin-bottom: 18px;

    text-shadow:
        0 0 18px rgba(124, 26, 215, 0.25);
}}


.hero-title span {{
    color: #7C1AD7;

    text-shadow:
        0 0 15px rgba(124, 26, 215, 0.8);
}}


.hero-description {{
    font-size: 17px;

    line-height: 1.6;

    color: #E2E4EA;

    margin-bottom: 4px;
}}


.hero-highlight {{
    color: #A855F7;

    font-weight: 700;

    text-shadow:
        0 0 12px rgba(168, 85, 247, 0.65);
}}


/* =====================================================
   SECTION TITLES
===================================================== */

.section-title {{
    font-size: 20px;

    font-weight: 700;

    margin-bottom: 4px;
}}


.section-subtitle {{
    color: #A7ADBA;

    font-size: 14px;

    margin-bottom: 12px;
}}


/* =====================================================
   QUESTION INPUT
===================================================== */

div[data-testid="stTextInput"] input {{
    background-color: #121927;

    border: 1px solid #252D3D;

    border-radius: 10px;

    color: #F5F5F7;
}}


/* =====================================================
   BUTTON
===================================================== */

div.stButton > button {{
    background-color: #7C1AD7;

    color: white;

    border: none;

    border-radius: 9px;

    font-weight: 600;
}}


div.stButton > button:hover {{
    background-color: #9B4DFF;

    color: white;
}}


/* =====================================================
   RESPONSIVE HERO
===================================================== */

@media (max-width: 768px) {{

    .hero-section {{
        min-height: 300px;
    }}

    .hero-content {{
        padding: 40px 28px;
    }}

    .hero-title {{
        font-size: 32px;
    }}

    .hero-description {{
        font-size: 15px;
    }}

}}

</style>
""",
    unsafe_allow_html=True
)


if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "answer" not in st.session_state:
    st.session_state.answer = None

if "sources" not in st.session_state:
    st.session_state.sources = []

if "uploaded_file_id" not in st.session_state:
    st.session_state.uploaded_file_id = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "uploaded_file_signature" not in st.session_state:
    st.session_state.uploaded_file_signature = None

if "uploaded_page_count" not in st.session_state:
    st.session_state.uploaded_page_count = 0

if "uploaded_chunk_count" not in st.session_state:
    st.session_state.uploaded_chunk_count = 0


st.sidebar.markdown(
    "### 🐱 Semantic Context Retrieval Engine 🐾"
)

st.sidebar.caption(
    "Your personal AI assistant for document search"
)

st.sidebar.divider()


st.sidebar.markdown(
    "### 📄 Upload Document"
)

st.sidebar.caption(
    "Upload your PDF file to get started"
)


uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"],
    label_visibility="collapsed"
)


if uploaded_file is not None:

    current_signature = (
        f"{uploaded_file.name}:{uploaded_file.size}"
    )

    if (
        current_signature
        != st.session_state.uploaded_file_signature
    ):

        os.makedirs(
            "uploads",
            exist_ok=True
        )

        file_id = str(
            uuid.uuid4()
        )

        file_path = os.path.join(
            "uploads",
            f"{file_id}.pdf"
        )

        try:

            with open(
                file_path,
                "wb"
            ) as file:

                file.write(
                    uploaded_file.getbuffer()
                )


            with st.spinner(
                "Extracting text from your PDF..."
            ):

                pages = extract_text_from_pdf(
                    file_path
                )


            with st.spinner(
                "Creating document chunks..."
            ):

                chunks = create_page_chunks(
                    pages,
                    file_id
                )


            with st.spinner(
                "Creating embeddings and storing document..."
            ):

                store_chunks(
                    chunks
                )


            st.session_state.uploaded_file_id = file_id

            st.session_state.uploaded_filename = (
                uploaded_file.name
            )

            st.session_state.uploaded_file_signature = (
                current_signature
            )

            st.session_state.uploaded_page_count = (
                len(pages)
            )

            st.session_state.uploaded_chunk_count = (
                len(chunks)
            )

            st.session_state.answer = None

            st.session_state.sources = []


        except Exception as e:

            st.error(
                f"Document processing failed: {e}"
            )


if (
    st.session_state.uploaded_filename is not None
):

    st.sidebar.success(
        f"✓ {st.session_state.uploaded_filename}"
    )

    st.sidebar.caption(
        f"{st.session_state.uploaded_page_count} pages "
        f"• "
        f"{st.session_state.uploaded_chunk_count} chunks"
    )


st.sidebar.divider()


st.sidebar.markdown(
    "### 💬 Conversation History"
)


if (
    len(st.session_state.conversation_history)
    == 0
):

    st.sidebar.caption(
        "No questions yet."
    )

else:

    for item in st.session_state.conversation_history:

        with st.sidebar.expander(
            item["question"]
        ):

            st.write(
                item["answer"]
            )

            st.caption(
                item["time"]
            )


if (
    len(st.session_state.conversation_history)
    > 0
):

    if st.sidebar.button(
        "🗑 Clear History"
    ):

        st.session_state.conversation_history = []

        st.session_state.answer = None

        st.session_state.sources = []

        st.rerun()


st.markdown(
    """
<div class="hero-section">

<div class="hero-content">

<div class="hero-welcome">
Welcome to
</div>

<div class="hero-title">
Semantic Context Retrieval Engine <span>🐾</span>
</div>

<div class="hero-description">
Upload your documents and ask anything about them.
</div>

<div class="hero-description">
Let AI find the
<span class="hero-highlight">purr-fect</span>
answers for you!
</div>

</div>

</div>
""",
    unsafe_allow_html=True
)


st.markdown(
    """
<div class="section-title">
💬 Ask Something
</div>
""",
    unsafe_allow_html=True
)

st.markdown(
    """
<div class="section-subtitle">
Ask any question about your document
</div>
""",
    unsafe_allow_html=True
)


question_col, button_col = st.columns(
    [5, 1]
)


with question_col:

    question = st.text_input(
        "Question",
        placeholder="Type your question here...",
        label_visibility="collapsed"
    )


with button_col:

    ask_clicked = st.button(
        "🐾 Ask",
        use_container_width=True
    )


if ask_clicked:

    if (
        st.session_state.uploaded_file_id
        is None
    ):

        st.warning(
            "Please upload a PDF before asking a question."
        )


    elif not question.strip():

        st.warning(
            "Please enter a question."
        )


    else:

        try:


            with st.spinner(
                "Searching your document..."
            ):

                results = search_chunks(
                    question=question,
                    top_k=3,
                    file_id=st.session_state.uploaded_file_id
                )


            documents = results["documents"][0]

            metadatas = results["metadatas"][0]

            ids = results["ids"][0]


            context = ""

            for i in range(
                len(documents)
            ):

                context += (
                    f"[Chunk {i + 1}]\n"
                    f"{documents[i]}\n\n"
                )


            with st.spinner(
                "Generating answer..."
            ):

                answer = generate_answer(
                    question=question,
                    context=context
                )


            st.session_state.answer = answer


            retrieved_sources = []


            for i in range(
                len(metadatas)
            ):

                metadata = metadatas[i]

                source = {
                    "filename": (
                        st.session_state.uploaded_filename
                    ),
                    "file_id": metadata["file_id"],
                    "page_number": metadata["page_number"],
                    "chunk_id": ids[i],
                    "chunk_text": documents[i]
                }

                retrieved_sources.append(
                    source
                )


            st.session_state.sources = (
                retrieved_sources
            )


            current_time = datetime.now().strftime(
                "%H:%M"
            )


            history_item = {
                "question": question,
                "answer": answer,
                "time": current_time
            }


            st.session_state.conversation_history.append(
                history_item
            )


        except Exception as e:

            st.session_state.answer = None

            st.session_state.sources = []

            st.error(
                f"Search failed: {e}"
            )


st.markdown("")


st.markdown(
    """
<div class="section-title">
😺 Answer
</div>
""",
    unsafe_allow_html=True
)


with st.container(
    border=True
):

    if (
        st.session_state.answer
        is None
    ):

        st.caption(
            "Your answer will appear here after you ask a question."
        )

    else:

        st.markdown(
            st.session_state.answer
        )


st.markdown("")


st.markdown(
    """
<div class="section-title">
📚 Sources
</div>
""",
    unsafe_allow_html=True
)


if (
    len(st.session_state.sources)
    == 0
):

    st.caption(
        "Relevant document sources will appear here."
    )


else:

    source_columns = st.columns(
        len(st.session_state.sources)
    )


    for i in range(
        len(st.session_state.sources)
    ):

        source = st.session_state.sources[i]


        with source_columns[i]:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"📄 **{source['filename']}**"
                )

                st.caption(
                    f"Page {source['page_number']}"
                )

                st.caption(
                    f"Chunk: {source['chunk_id']}"
                )

                st.write(
                    source["chunk_text"][:180]
                    + "..."
                )