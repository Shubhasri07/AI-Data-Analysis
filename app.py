import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import re
from openai import OpenAI
client = OpenAI()
# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Schema-Agnostic AI Data Analyst",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Schema-Agnostic Natural Language Data Analyst")
st.write(
    "Upload a CSV, Excel, or JSON dataset and ask questions "
    "about your data using natural language."
)

# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "📂 Upload your dataset",
    type=["csv", "xlsx", "json"]
)

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def load_file(file):
    """Load CSV, Excel or JSON file."""
    
    filename = file.name.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(file)

    elif filename.endswith(".xlsx"):
        return pd.read_excel(file)

    elif filename.endswith(".json"):
        return pd.read_json(file)

    raise ValueError("Unsupported file format.")


def find_numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()


def find_categorical_columns(df):
    return df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()


def find_column_from_question(question, columns):
    """
    Try to identify a dataset column from the user's question.
    """

    question = question.lower()

    # Exact column name matching
    for column in columns:
        if column.lower() in question:
            return column

    # Match words from column names
    for column in columns:

        words = re.findall(r"\w+", column.lower())

        for word in words:
            if len(word) > 2 and word in question:
                return column

    return None


def show_basic_statistics(df):
    """Display basic dataset statistics."""

    st.subheader("📊 Basic Statistics")

    numeric_columns = find_numeric_columns(df)

    if not numeric_columns:
        st.info("No numeric columns available.")
        return

    st.dataframe(
        df[numeric_columns].describe().round(2),
        use_container_width=True
    )


def answer_question(question, df):
    """
    Simple natural-language analysis engine.
    """

    question = question.lower().strip()

    numeric_columns = find_numeric_columns(df)
    categorical_columns = find_categorical_columns(df)

    all_columns = df.columns.tolist()

    # -----------------------------------------------------
    # MISSING VALUES
    # -----------------------------------------------------

    if "missing" in question or "null" in question:

        missing = df.isnull().sum()
        total_missing = int(missing.sum())

        if total_missing == 0:
            st.success("✅ There are no missing values.")

        else:
            st.write(
                f"Total missing values: **{total_missing}**"
            )

            st.dataframe(
                missing[missing > 0]
            )

        return

    # -----------------------------------------------------
    # AVERAGE / MEAN
    # -----------------------------------------------------

    if "average" in question or "mean" in question:

        column = find_column_from_question(
            question,
            numeric_columns
        )

        if column:

            value = df[column].mean()

            st.success(
                f"📌 Average of **{column}**: "
                f"**{value:.2f}**"
            )

        else:

            if numeric_columns:

                st.write("### Average values")

                result = df[numeric_columns].mean()

                st.dataframe(
                    result.rename("Average").round(2)
                )

            else:

                st.warning(
                    "No numeric columns found."
                )

        return

    # -----------------------------------------------------
    # MAXIMUM / HIGHEST
    # -----------------------------------------------------

    if (
        "highest" in question
        or "maximum" in question
        or "max" in question
    ):

        column = find_column_from_question(
            question,
            numeric_columns
        )

        if column:

            value = df[column].max()

            st.success(
                f"📈 Highest value of **{column}**: "
                f"**{value}**"
            )

        else:

            st.write("### Highest values")

            result = df[numeric_columns].max()

            st.dataframe(
                result.rename("Highest")
            )

        return

    # -----------------------------------------------------
    # MINIMUM / LOWEST
    # -----------------------------------------------------

    if (
        "lowest" in question
        or "minimum" in question
        or "min" in question
    ):

        column = find_column_from_question(
            question,
            numeric_columns
        )

        if column:

            value = df[column].min()

            st.success(
                f"📉 Lowest value of **{column}**: "
                f"**{value}**"
            )

        else:

            st.write("### Lowest values")

            result = df[numeric_columns].min()

            st.dataframe(
                result.rename("Lowest")
            )

        return

    # -----------------------------------------------------
    # TOTAL / SUM
    # -----------------------------------------------------

    if (
        "total" in question
        or "sum" in question
        or "overall" in question
    ):

        column = find_column_from_question(
            question,
            numeric_columns
        )

        if column:

            value = df[column].sum()

            st.success(
                f"💰 Total of **{column}**: "
                f"**{value:,.2f}**"
            )

        else:

            st.write("### Total values")

            result = df[numeric_columns].sum()

            st.dataframe(
                result.rename("Total")
            )

        return

    # -----------------------------------------------------
    # COUNT
    # -----------------------------------------------------

    if "count" in question or "number of" in question:

        st.success(
            f"🔢 Total number of records: "
            f"**{len(df)}**"
        )

        return

    # -----------------------------------------------------
    # SHOW COLUMNS
    # -----------------------------------------------------

    if (
        "column" in question
        or "columns" in question
    ):

        st.write("### Dataset Columns")

        for column in all_columns:
            st.write(f"• {column}")

        return

    # -----------------------------------------------------
    # SHOW DATASET SIZE
    # -----------------------------------------------------

    if (
        "rows" in question
        or "records" in question
        or "dataset size" in question
    ):

        st.success(
            f"Dataset contains **{df.shape[0]} rows** "
            f"and **{df.shape[1]} columns**."
        )

        return

    # -----------------------------------------------------
    # TOP / BEST VALUE
    # -----------------------------------------------------

    if (
        "top" in question
        or "best" in question
    ):

        if numeric_columns:

            column = find_column_from_question(
                question,
                numeric_columns
            )

            if column is None:
                column = numeric_columns[0]

            result = df.nlargest(
                5,
                column
            )

            st.write(
                f"### Top 5 records by {column}"
            )

            st.dataframe(
                result,
                use_container_width=True
            )

        else:

            st.warning(
                "No numeric columns available."
            )

        return

    # -----------------------------------------------------
    # UNKNOWN QUESTION
    # -----------------------------------------------------

    st.info(
        "I couldn't understand that question yet.\n\n"
        "Try questions such as:\n"
        "- What is the average salary?\n"
        "- What is the highest sales?\n"
        "- What is the lowest price?\n"
        "- What is the total revenue?\n"
        "- How many records are there?\n"
        "- Are there any missing values?"
    )


# ---------------------------------------------------------
# MAIN APPLICATION
# ---------------------------------------------------------

if uploaded_file is not None:

    try:

        # -------------------------------------------------
        # LOAD DATA
        # -------------------------------------------------

        df = load_file(uploaded_file)

        st.success(
            f"✅ {uploaded_file.name} uploaded successfully!"
        )

        # -------------------------------------------------
        # DATASET PREVIEW
        # -------------------------------------------------

        st.subheader("📋 Dataset Preview")

        st.dataframe(
            df.head(100),
            use_container_width=True
        )

        # -------------------------------------------------
        # DATASET INFORMATION
        # -------------------------------------------------

        st.subheader("🔍 Dataset Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Rows",
                df.shape[0]
            )

        with col2:
            st.metric(
                "Columns",
                df.shape[1]
            )

        with col3:
            st.metric(
                "Missing Values",
                int(df.isnull().sum().sum())
            )

        # -------------------------------------------------
        # SCHEMA INFORMATION
        # -------------------------------------------------

        st.subheader("🧠 Detected Schema")

        schema = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Missing Values": df.isnull().sum().values,
            "Unique Values": [
                df[column].nunique()
                for column in df.columns
            ]
        })

        st.dataframe(
            schema,
            use_container_width=True
        )

        # -------------------------------------------------
        # NUMERIC ANALYSIS
        # -------------------------------------------------

        numeric_columns = find_numeric_columns(df)

        if numeric_columns:

            st.subheader("📈 Numeric Data Analysis")

            selected_column = st.selectbox(
                "Select a numeric column",
                numeric_columns
            )

            average = df[selected_column].mean()
            maximum = df[selected_column].max()
            minimum = df[selected_column].min()
            total = df[selected_column].sum()

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "Average",
                    round(average, 2)
                )

            with c2:
                st.metric(
                    "Maximum",
                    maximum
                )

            with c3:
                st.metric(
                    "Minimum",
                    minimum
                )

            with c4:
                st.metric(
                    "Total",
                    round(total, 2)
                )

            # -------------------------------------------------
            # HISTOGRAM
            # -------------------------------------------------

            st.subheader("📊 Data Distribution")

            fig, ax = plt.subplots()

            ax.hist(
                df[selected_column].dropna(),
                bins=10
            )

            ax.set_xlabel(
                selected_column
            )

            ax.set_ylabel(
                "Frequency"
            )

            ax.set_title(
                f"Distribution of {selected_column}"
            )

            st.pyplot(fig)

        else:

            st.info(
                "No numeric columns found."
            )

        # -------------------------------------------------
        # GROUPING
        # -------------------------------------------------

        categorical_columns = find_categorical_columns(df)

        if (
            categorical_columns
            and numeric_columns
        ):

            st.subheader(
                "📊 Grouped Data Analysis"
            )

            group_column = st.selectbox(
                "Select category column",
                categorical_columns
            )

            value_column = st.selectbox(
                "Select numeric column",
                numeric_columns
            )

            grouped_data = (
                df.groupby(group_column)[value_column]
                .mean()
                .sort_values(
                    ascending=False
                )
            )

            st.dataframe(
                grouped_data.rename(
                    "Average"
                ),
                use_container_width=True
            )

            st.bar_chart(
                grouped_data
            )

        # -------------------------------------------------
        # NATURAL LANGUAGE ANALYST
        # -------------------------------------------------

        st.subheader(
            "🤖 Ask Questions About Your Data"
        )

        st.write(
            "Ask your question in normal English."
        )

        question = st.text_input(
            "Example: What is the average salary?"
        )

        if question:

            answer_question(
                question,
                df
            )

        # -------------------------------------------------
        # BASIC STATISTICS
        # -------------------------------------------------

        with st.expander(
            "📊 View Statistical Summary"
        ):

            show_basic_statistics(df)

    except Exception as e:

        st.error(
            f"❌ Error while processing file: {e}"
        )

else:

    st.info(
        "👆 Please upload a CSV, Excel, or JSON file "
        "to begin analysis."
    )
