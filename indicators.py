import os
import re
import pandas as pd
# from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
# from reportlab.lib import colors
from target_phrases import target_phrase_sections
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import PageBreak


# Function to extract sentences containing key phrases
def extract_sentences(username, input_csv, output_pdf, target_phrase_sections):
    username = username.strip("@")  # Remove "@" symbol from username
    input_csv_path = f"Collection/{username}/{username}_messages.csv"
    output_pdf_path = (
        f"Collection/{username}/{username}__ideological_indicators_report.pdf"
    )
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
    normal_style.alignment = 0  # Left alignment
    citation_style = ParagraphStyle(name='CitationStyle', parent=normal_style)
    citation_style.leading = 6  # Decrease font size to 6

    # Add the title to the PDF
    title = Paragraph("Ideological Indicators Report", title_style)
    story = [title, Spacer(1, 12)]

    # Iterate through target phrase sections
    for section_title, target_phrases in target_phrase_sections:
        # Add sub-heading for the section
        section_heading = Paragraph(section_title, subheading_style)
        story.extend((section_heading, Spacer(1, 12)))
        # Create a regex pattern for each target phrase
        target_patterns = [
            re.compile(
                r'\b' + re.escape(phrase) + r'\b',
                re.IGNORECASE
            ) for phrase in target_phrases
        ]

        # Iterate through messages and extract sentences
        for index, row in df.iterrows():
            # Convert to string to handle non-string values
            message = str(row['Text'])
            url = row['Message URL']  # Get the source URL
            sentences = re.split(r'(?<=[.!?])\s+', message)

            for sentence in sentences:
                for pattern in target_patterns:
                    if re.search(pattern, sentence):

                        # Highlight target phrases
                        highlighted_sentence = re.sub(
                            pattern,
                            r'<font color="red">\g<0></font>',
                            sentence
                        )

                        story.extend(
                            Paragraph(highlighted_sentence, normal_style),
                            Spacer(1, 12)
                        )

                        # Add URL citation with size 6 font and bold "Source:"
                        citation = Paragraph(
                            "<font size='6'><b>Source:</b>"
                            f"<a href='{url}'>{url}</a></font>",
                            normal_style
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
        target_username + "_ideological_indicators_report.pdf",
        target_phrase_sections
        )

# Ask if the user wants to return to the launcher
launcher = input('Do you want to return to the launcher? (y/n)')

if launcher == 'y':
    print('Restarting...')

    exec(open("launcher.py").read())
