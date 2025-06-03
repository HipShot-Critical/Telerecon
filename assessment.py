import os
import re

import pandas as pd

# from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

# from reportlab.lib import colors
from target_phrases import (
    target_phrase_list1,
    target_phrase_list2,
    target_phrase_list3,
)


# Function to extract sentences containing key phrases
def extract_sentences(
    username,
    input_csv,
    output_pdf,
    target_phrase_list1,
    target_phrase_list2,
    target_phrase_list3
):
    username = username.strip("@")  # Remove "@" symbol from username

    input_csv_path = f"Collection/{username}/{username}_messages.csv"
    output_pdf_path = f"Collection/{username}/{username}_threat_assessment.pdf"

    if not os.path.exists(input_csv_path):
        print(f"CSV file not found: {input_csv_path}")
        return

    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv_path, encoding='utf-8')

    # Create a PDF document
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)

    # Define paragraph styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    subheading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    normal_style.leading = 14
    normal_style.alignment = 0
    citation_style = ParagraphStyle(name='CitationStyle', parent=normal_style)
    citation_style.leading = 6

    # Add the title to the PDF
    title = Paragraph("Target Threat Assessment", title_style)
    story = [title, Spacer(1, 12)]

    # Add subheading for possible indicators of capability
    subheading_capability = Paragraph(
        "Possible Indicators of Capability",
        subheading_style
    )
    story.extend([subheading_capability, Spacer(1, 12)])

    # Create a regex pattern for each target phrase with proximity search
    target_patterns_capability = [
        re.compile(
            r'\b(?:' + '|'.join(
                re.escape(phrase1) for phrase1 in target_phrase_list1
            ) + r')\b.{0,5}\b(?:' + '|'.join(
                re.escape(phrase2) for phrase2 in target_phrase_list2
            ) + r')\b', re.IGNORECASE
        )
    ]

    # Iterate through messages and extract sentences for capability
    for index, row in df.iterrows():
        # Convert to string to handle non-string values
        message = str(row['Text'])
        url = row['Message URL']  # Get the source URL
        sentences = re.split(r'(?<=[.!?])\s+', message)

        for sentence in sentences:
            for pattern in target_patterns_capability:
                if re.search(pattern, sentence):
                    # Highlight target phrases
                    highlighted_sentence = re.sub(
                        pattern, r'<font color="red">\g<0></font>',
                        sentence
                    )
                    story.extend(
                        Spacer(1, 6),
                        Paragraph(
                            highlighted_sentence,
                            normal_style
                        )
                    )
                    # Add URL citation with size 6 font and bold "Source:"
                    citation = Paragraph(
                        "<font size='6'><b>Source:</b>"
                        f"<a href='{url}'>{url}</a></font>",
                        citation_style
                    )
                    story.extend((citation, Spacer(1, 12)))

    # Add subheading for possible indicators of violent intent
    subheading_intent = Paragraph(
        "Possible Indicators of Violent Intent",
        subheading_style
    )
    story.extend(
        [
            PageBreak(),
            subheading_intent,
            Spacer(1, 12)
        ]
    )

    # Create regex pattern for each target phrase without proximity search
    target_patterns_intent = [
        re.compile(
            r'\b(?:' + '|'.join(
                re.escape(phrase) for phrase in target_phrase_list3
            ) + r')\b', re.IGNORECASE
        )
    ]

    # Iterate through messages and extract sentences for violent intent
    for index, row in df.iterrows():
        message = str(row['Text'])
        url = row['Message URL']
        sentences = re.split(r'(?<=[.!?])\s+', message)

        for sentence in sentences:
            for pattern in target_patterns_intent:
                if re.search(pattern, sentence):
                    # Highlight target phrases
                    highlighted_sentence = re.sub(
                        pattern,
                        r'<font color="red">\g<0></font>',
                        sentence
                    )
                    story.extend(
                        Spacer(1, 6),
                        Paragraph(
                            highlighted_sentence,
                            normal_style
                        )
                    )
                    # Add URL citation with size 6 font and bold "Source:"
                    citation = Paragraph(
                        "<font size='6'><b>Source:</b>"
                        f"<a href='{url}'>{url}</a></font>",
                        citation_style
                    )
                    story.extend((citation, Spacer(1, 12)))

    # Create the PDF
    doc.build(story)
    print(f"Key phrase extraction report saved to {output_pdf_path}")


if __name__ == "__main__":
    # Get the target username from the user
    target_username = input("Enter the target username (with @): ")

    # Run the extraction and PDF generation
    extract_sentences(
        target_username,
        "input.csv",
        target_username + "_threat_assessment.pdf",
        target_phrase_list1,
        target_phrase_list2,
        target_phrase_list3
    )

    # Ask if the user wants to return to the launcher
    launcher = input("Do you want to return to the launcher? (y/n)")
    if launcher == "y":
        print("Restarting...")
        exec(open("launcher.py").read())
