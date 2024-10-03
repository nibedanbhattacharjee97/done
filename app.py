import flet as ft
import pandas as pd
from PIL import Image
import os
from gtts import gTTS
from googletrans import Translator
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load the Excel file containing questions and answers
def load_excel_data(file_path):
    return pd.read_excel(file_path)

# Function to create and return a Flet page
def main(page: ft.Page):
    page.title = "Question Answer Translator"
    page.scroll = "auto"
    
    # Load Excel data
    excel_file = 'questions_answers.xlsx'  # Make sure this file is present in the same directory
    df = load_excel_data(excel_file)

    # Page Title
    page.add(ft.Text("Please Ask Your Question & Get Answer In Your Own Language", style="headlineMedium", color=ft.colors.TEAL))

    # Select a question from the drop-down
    question_list = list(df['question'])
    selected_question = ft.Dropdown(
        options=[ft.dropdown.Option(q) for q in question_list],
        label="Select a question",
        on_change=lambda e: update_answer(e.control.value)
    )

    # Containers for displaying question, answer, and image
    question_container = ft.Column()
    answer_container = ft.Column()
    image_container = ft.Container()

    # Function to update displayed question and answer
    def update_answer(selected_q):
        question_row = df[df['question'] == selected_q].iloc[0]

        # Display question and answer
        question_container.controls = [ft.Text(f"Question: {question_row['question']}")]
        answer_container.controls = [ft.Text(f"Answer: {question_row['answer']}")]

        # Display image if available
        if pd.notna(question_row['picpath']) and isinstance(question_row['picpath'], str) and os.path.exists(question_row['picpath']):
            try:
                img = Image.open(question_row['picpath'])
                img_io = ft.Image(src=question_row['picpath'], fit="contain")
                image_container.content = img_io
            except Exception as e:
                image_container.content = ft.Text(f"Error loading image: {e}")
        else:
            image_container.content = ft.Text("No image available.")

        page.update()

    # Language selection dropdown
    language_options = {"English": "en", "Hindi": "hi", "Bengali": "bn", "Tamil": "ta", "Telugu": "te", "Marathi": "mr"}
    selected_language = ft.Dropdown(
        options=[ft.dropdown.Option(lang) for lang in language_options.keys()],
        label="Choose language",
    )

    # Translator initialization
    translator = Translator()

    # Function to handle translation and TTS
    def translate_and_generate_audio():
        question_row = df[df['question'] == selected_question.value].iloc[0]

        # Translate question and answer
        if selected_language.value != "English":
            translated_question = translator.translate(question_row['question'], dest=language_options[selected_language.value]).text
            translated_answer = translator.translate(question_row['answer'], dest=language_options[selected_language.value]).text
        else:
            translated_question = question_row['question']
            translated_answer = question_row['answer']

        # Display translated question and answer
        question_container.controls = [ft.Text(f"Translated Question ({selected_language.value}): {translated_question}")]
        answer_container.controls = [ft.Text(f"Translated Answer ({selected_language.value}): {translated_answer}")]

        # Generate voice for the translated text
        text_to_speak = f"Question: {translated_question}. Answer: {translated_answer}"
        tts = gTTS(text=text_to_speak, lang=language_options[selected_language.value])
        audio_file_path = 'question_answer_audio.mp3'
        tts.save(audio_file_path)

        # Play audio file
        page.add(ft.Audio(src=audio_file_path, autoplay=True))

        page.update()

    # Translate button
    translate_button = ft.ElevatedButton("Translate and Speak", on_click=lambda _: translate_and_generate_audio())

    # WhatsApp contacts
    whatsapp_numbers = [
        {"number": "9147394695", "language": "English"},
        {"number": "9147394695", "language": "Hindi"},
        {"number": "9147394695", "language": "Bengali"},
        {"number": "7595063323", "language": "Tamil"},
        {"number": "6293415105", "language": "Telugu"}
    ]
    whatsapp_message = "Hi Anu! I Have a Query."

    # WhatsApp buttons
    whatsapp_buttons = []
    for contact in whatsapp_numbers:
        whatsapp_url = f"https://api.whatsapp.com/send?phone=91{contact['number']}&text={whatsapp_message}"
        whatsapp_buttons.append(ft.ElevatedButton(f"WhatsApp for {contact['language']}", on_click=lambda _: page.launch_url(whatsapp_url)))

    # Add all controls to the page
    page.add(
        selected_question,
        question_container,
        answer_container,
        image_container,
        selected_language,
        translate_button,
        ft.Column(whatsapp_buttons)
    )

# Run the Flet app
ft.app(target=main)
