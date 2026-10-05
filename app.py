import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

st.set_page_config(
    page_title="AI Data Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Data Analysis")
st.write("Upload a CSV, Excel, or JSON dataset and analyze it easily.")

uploaded_file = st.file_uploader(
    "Upload your dataset",
    type=["csv", "xlsx", "json"]
)

if uploaded_file is not None:

    try:
        file_name = uploaded_file.name.lower()

        # Read uploaded file
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

        elif file_name.endswith(".json"):
            df = pd.read_json(uploaded_file)

        else:
            st.error("Unsupported file format.")
            st.stop()

        st.success("File uploaded successfully!")

        # Dataset information
        st.subheader("📋 Dataset Preview")
        st.dataframe(df)

        st.subheader("🔍 Dataset Information")
        col1, col2 = st.columns(2)

        with col1:
            st.write("Number of rows:", df.shape[0])

        with col2:
            st.write("Number of columns:", df.shape[1])

        # Automatic column detection
        st.subheader("📌 Columns")
        st.write(list(df.columns))

        # Missing values
        st.subheader("⚠️ Missing Values")

        missing = df.isnull().sum()

        if missing.sum() == 0:
            st.success("No missing values found.")
        else:
            st.dataframe(missing[missing > 0])

            if st.button("Handle Missing Values"):
                numeric_columns = df.select_dtypes(
                    include="number"
                ).columns

                for column in numeric_columns:
                    df[column] = df[column].fillna(df[column].mean())

                categorical_columns = df.select_dtypes(
                    exclude="number"
                ).columns

                for column in categorical_columns:
                    if df[column].isnull().any():
                        df[column] = df[column].fillna(
                            df[column].mode()[0]
                        )

                st.success("Missing values handled successfully!")
                st.dataframe(df)

        # Numeric analysis
        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:

            st.subheader("📈 Numeric Data Analysis")

            selected_column = st.selectbox(
                "Select a numeric column",
                numeric_columns
            )

            average = df[selected_column].mean()
            highest = df[selected_column].max()
            lowest = df[selected_column].min()

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Average", round(average, 2))

            with c2:
                st.metric("Highest", highest)

            with c3:
                st.metric("Lowest", lowest)

            # Chart
            st.subheader("📊 Chart")

            fig, ax = plt.subplots()

            ax.hist(
                df[selected_column].dropna(),
                bins=10
            )

            ax.set_xlabel(selected_column)
            ax.set_ylabel("Frequency")
            ax.set_title("Data Distribution")

            st.pyplot(fig)

        else:
            st.info("No numeric columns found.")

        # Grouping
        categorical_columns = df.select_dtypes(
            exclude="number"
        ).columns.tolist()

        if categorical_columns and numeric_columns:

            st.subheader("📊 Data Grouping")

            group_column = st.selectbox(
                "Select a column for grouping",
                categorical_columns
            )

            value_column = st.selectbox(
                "Select a numeric column",
                numeric_columns
            )

            grouped_data = df.groupby(
                group_column
            )[value_column].mean()

            st.dataframe(grouped_data)

            st.bar_chart(grouped_data)

        # Simple AI-style Q&A
        st.subheader("🤖 Ask About Your Data")

        question = st.text_input(
            "Example: What is the average?"
        )

        if question:

            question_lower = question.lower()

            if "average" in question_lower or "mean" in question_lower:
                if numeric_columns:
                    for column in numeric_columns:
                        st.write(
                            f"Average of {column}: "
                            f"{df[column].mean():.2f}"
                        )
                else:
                    st.write("No numeric columns available.")

            elif "highest" in question_lower or "maximum" in question_lower:
                if numeric_columns:
                    for column in numeric_columns:
                        st.write(
                            f"Highest {column}: "
                            f"{df[column].max()}"
                        )

            elif "lowest" in question_lower or "minimum" in question_lower:
                if numeric_columns:
                    for column in numeric_columns:
                        st.write(
                            f"Lowest {column}: "
                            f"{df[column].min()}"
                        )

            elif "missing" in question_lower:
                st.write(
                    "Missing values:",
                    int(df.isnull().sum().sum())
                )

            else:
                st.info(
                    "Try asking about average, highest, "
                    "lowest, or missing values."
                )

    except Exception as e:
        st.error(f"Error while processing file: {e}")

else:
    st.info("Please upload a CSV, Excel, or JSON file.")
