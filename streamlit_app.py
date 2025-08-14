import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import io

st.set_page_config(page_title="Ploppo Pattern Explorer", layout="wide")
st.title("🎱 Ploppo Pattern Explorer")
st.write("Upload your dataset!")

# File upload
uploaded_file = st.file_uploader("Upload Lotto CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
    else:
        # Validate columns
        expected_columns = ["Num1", "Num2", "Num3", "Num4", "Num5", "Num6"]
        if not all(col in df.columns for col in expected_columns):
            st.error("Dataset must contain columns: Num1 to Num6")
        else:
            winning_columns = expected_columns

            # Hot Numbers
            st.header("🔥 Hot Number Frequency")
            all_numbers = df[winning_columns].values.flatten()
            counts = Counter(all_numbers)
            hot_df = pd.DataFrame(counts.items(), columns=["Number", "Frequency"]).sort_values(by="Frequency", ascending=False)

            fig1, ax1 = plt.subplots(figsize=(12, 5))
            sns.barplot(x="Number", y="Frequency", data=hot_df, palette="viridis", ax=ax1)
            ax1.set_title("Most Frequently Drawn Numbers")
            st.pyplot(fig1)

            st.subheader("Top 10 Numbers")
            st.dataframe(hot_df.head(10), use_container_width=True)

            # Odd/Even Split
            st.header("⚖️ Odd vs Even Patterns")
            def odd_even_split(row):
                odds = sum(1 for n in row if n % 2 != 0)
                evens = 6 - odds
                return f"{odds} Odd / {evens} Even"

            df["Odd_Even_Split"] = df[winning_columns].apply(odd_even_split, axis=1)
            split_counts = df["Odd_Even_Split"].value_counts().reset_index()
            split_counts.columns = ["Split", "Count"]
            fig2, ax2 = plt.subplots()
            ax2.pie(split_counts["Count"], labels=split_counts["Split"], autopct="%1.1f%%", startangle=90)
            ax2.set_title("Odd/Even Split Distribution")
            st.pyplot(fig2)

            # Range Buckets
            st.header("🔢 Number Range Patterns")
            def range_grouping(row):
                buckets = [0]*5
                for n in row:
                    if n <= 10:
                        buckets[0] += 1
                    elif n <= 20:
                        buckets[1] += 1
                    elif n <= 30:
                        buckets[2] += 1
                    elif n <= 40:
                        buckets[3] += 1
                    else:
                        buckets[4] += 1
                return str(buckets)

            df["Range_Pattern"] = df[winning_columns].apply(range_grouping, axis=1)
            st.dataframe(df["Range_Pattern"].value_counts().reset_index().rename(columns={"index": "Range Pattern", "Range_Pattern": "Count"}), use_container_width=True)

            # Repeats from previous draw
            st.header("🔁 Repeated Numbers from Previous Draw")
            repeats = []
            previous_set = set()
            for _, row in df.iterrows():
                current_set = set(row[winning_columns])
                repeated = current_set.intersection(previous_set)
                repeats.append(len(repeated))
                previous_set = current_set
            df['Repeated_From_Last_Draw'] = repeats
            st.bar_chart(df['Repeated_From_Last_Draw'].value_counts().sort_index())

            # Average Gap
            st.header("📏 Average Gap Between Numbers")
            def number_gaps(row):
                sorted_nums = sorted(row)
                gaps = [sorted_nums[i+1] - sorted_nums[i] for i in range(len(sorted_nums)-1)]
                return sum(gaps) / len(gaps)

            df['Avg_Gap'] = df[winning_columns].apply(number_gaps, axis=1)
            st.line_chart(df['Avg_Gap'])

            st.success("Analysis complete. Scroll through the results above!")


