import os
import re

import pandas as pd

# from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

# from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

# from reportlab.platypus import PageBreak
from validate_email_address import validate_email

from target_phrases import target_phrases


# Function to extract sentences containing
# key phrases, emails, and phone numbers
def extract_sentences(username, input_csv, output_pdf, target_phrases):
    username = username.strip("@")  # Remove "@" symbol from username
    input_csv_path = f"Collection/{username}/{username}_messages.csv"
    output_pdf_path = f"Collection/{username}/{username}_keyphrase_report.pdf"
    if not os.path.exists(input_csv_path):
        print(f"CSV file not found: {input_csv_path}")
        return

    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv_path, encoding="utf-8")
    # Create a PDF document
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)

    story = []

    # Define paragraph styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]
    normal_style.leading = 14
    normal_style.alignment = 0  # Left alignment
    citation_style = ParagraphStyle(name="CitationStyle", parent=normal_style)
    citation_style.leading = 6  # Decrease font size to 6

    # Define subheading style after normal_style
    subheading_style = styles["Heading2"]

    # Add the title to the PDF
    title = Paragraph("Key Phrase Extraction Report", title_style)
    story.append(title)
    story.append(Spacer(1, 12))

    # Create a regex pattern for each target phrase
    target_patterns = [
        re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE)
        for phrase in target_phrases
    ]

    # Initialize variables for subheadings
    email_subheading_added = False
    phone_subheading_added = False
    other_subheading_added = False

    # Email pattern
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

    # Iterate through messages and extract sentences
    for index, row in df.iterrows():
        # Convert to string to handle non-string values
        message = str(row["Text"])
        url = row["Message URL"]

        # Remove URLs from the message text
        message = re.sub(r"http\S+", "", message)
        sentences = re.split(r"(?<=[.!?])\s+", message)
        for sentence in sentences:
            for pattern in target_patterns:
                if re.search(pattern, sentence):
                    # Check for subheadings and add them if not added yet
                    if not email_subheading_added:
                        story.append(
                            Paragraph(
                                "Potential Email Addresses", subheading_style
                            )
                        )
                        email_subheading_added = True

                    if not phone_subheading_added:
                        story.append(
                            Paragraph(
                                "Potential Phone Numbers", subheading_style
                            )
                        )
                        phone_subheading_added = True

                    if not other_subheading_added:
                        story.append(
                            Paragraph(
                                "Other Content of Interest", subheading_style
                            )
                        )
                        other_subheading_added = True

                    # Highlight target phrases
                    highlighted_sentence = re.sub(
                        pattern, r'<font color="red">\g<0></font>', sentence
                    )
                    story.append(Paragraph(highlighted_sentence, normal_style))

                    # Add URL end-note citation with size 6 font
                    citation = Paragraph(
                        "<font size='6'><b>Source:</b>"
                        f"<a href='{url}'>{url}</a></font>",
                        citation_style,
                    )

                    story.append(citation)

                    # Add a gap between extracted posts/URLs
                    story.append(Spacer(1, 12))

        # Find and highlight valid email addresses
        email_addresses = re.findall(email_pattern, message)
        for email in email_addresses:
            if validate_email(email):  # Check email validity

                # Check for the email subheading and add it if not added yet
                if not email_subheading_added:
                    story.append(
                        Paragraph(
                            "Potential Email Addresses", subheading_style
                        )
                    )
                    email_subheading_added = True
                email_pattern = re.compile(re.escape(email), re.IGNORECASE)
                highlighted_email = re.sub(
                    email_pattern, r'<font color="green">\g<0></font>', email
                )
                context_with_email = message.replace(email, highlighted_email)
                story.append(Paragraph(context_with_email, normal_style))

                # Add URL end-note citation with size 6 font and bold "Source:"
                email_url = (
                    "<font size='6'><b>Source:</b>"
                    f"<a href='{url}'>{url}</a></font>"
                )
                story.append(Paragraph(email_url, citation_style))

                # Add a gap between extracted email addresses
                story.append(Spacer(1, 12))

        # Find and highlight phone numbers
        # Match phone numbers with 7 to 15 digits
        phone_numbers = re.findall(r"\b\d{7,15}\b", message)
        for phone in phone_numbers:

            # Check for the phone subheading and add it if not added yet
            if not phone_subheading_added:
                story.append(
                    Paragraph(
                        "Potential Phone Numbers",
                        subheading_style
                    )
                )
                phone_subheading_added = True
            phone_pattern = re.compile(re.escape(phone), re.IGNORECASE)
            highlighted_phone = re.sub(
                phone_pattern, phone, r'<font color="blue">\g<0></font>'
            )
            context_with_phone = message.replace(phone, highlighted_phone)
            story.append(Paragraph(context_with_phone, normal_style))

            # Add URL end-note citation with size 6 font and bold "Source:"
            phone_url = (
                "<font size='6'><b>Source:</b>"
                f"<a href='{url}'>{url}</a></font>"
            )
            story.append(Paragraph(phone_url, citation_style))

            # Add a gap between extracted phone numbers
            story.append(Spacer(1, 12))

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
        target_username + "_keyphrase_report.pdf",
        target_phrases,
    )

# Ask if the user wants to return to the launcher
launcher = input("Do you want to return to the launcher? (y/n)")

if launcher == "y":
    print("Restarting...")

    exec(open("launcher.py").read())
