import base64
import streamlit as st
import pandas as pd
from main import IndividualAnalyzer
from run import NewAnalyzer
import os
from io import BytesIO
from streamlit_extras.switch_page_button import switch_page
import subprocess
import time
import json  
import hydralit_components as hc

st.set_page_config(page_title="Investor Profiling" ,layout="wide", initial_sidebar_state="collapsed")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .css-xiwqqw, .eczjsme1 {
                display: none !important;
            }
            .css-zq5wmm, .ezrtsby0{
                display:none!important;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


api_key = os.getenv("API_KEY")
user_agent = os.getenv("USER_AGENT")

analyzer = IndividualAnalyzer(api_key, user_agent)

extracted_data = []


with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

def analyze_person(self, person_name):
        wiki_data = self.individual_analyzer.scrape_wikipedia_data(person_name)
        if not wiki_data:
            print(f"profile not found on wikipedia for {person_name}")
            wikipedia_data = {}
        else:
            wikipedia_data = self.individual_analyzer.wiki_json(wiki_data)
        if type(wikipedia_data) == list and len(wikipedia_data) > 0:
            wikipedia_data = wikipedia_data[0]
        forbes_data = self.individual_analyzer.scrape_forbes_data(person_name)
        result = {}
        for key in self.ls:
            openai_data = self.individual_analyzer.scrap_gpt(person_name, key)
            result[key] = openai_data[key]
        combined_result = {**wikipedia_data, **forbes_data, **result}
        data_directory = "data\json_data"
        person_name=person_name.replace(" ", "_")
        json_file_path = os.path.join(data_directory, f"{person_name}.json")
        with open(json_file_path, 'w') as json_file:
            json.dump(combined_result, json_file, indent=4)

        return {"status": 200, "json_path": json_file_path}

st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: #b89434;
        color:#ffffff;
        border-radius: 40px;
        border: none;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

analyzer = NewAnalyzer(api_key, user_agent)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("SINDALAH INFO")
    person_name = st.text_input("FIRST NAME")
    last_name = st.text_input("LAST NAME")
    email = st.text_input("EMAIL")
    name= person_name + ' ' + last_name
    country = st.text_input("COUNTRY") 
    # Load the data from mod3.json
    with open('mod3.json', 'r') as json_file:
        mod3_data = json.load(json_file)

    # Create a dropdown button to select an option
    selected_option = st.selectbox("Load pre-loaded profiles", list(mod3_data.keys()))

    # Store the selected value in the pdf_path variable
    pdf_path = mod3_data[selected_option]
    if st.button("Load"):
        with col2:
            st.subheader("BACKEND SNEAKPEAK")
            # List of messages to display during loading
            with st.status("Loading Profile", expanded=True) as status:
                st.write(f"Seaching database for profile {name}")
                time.sleep(5)
            with col3:
                st.subheader("PROFILE PREVIEWER")
                session_file_path = "list.json"

                # Check if the session file exists
                if os.path.exists(session_file_path):
                    # Load the session data from the session file
                    with open(session_file_path, 'r') as session_file:
                        session_data = json.load(session_file)
                    
                    # Check if 'name' is a key in the session data
                    for item in session_data:
                        pdf_path = item.get('pdf_path')

                        if os.path.exists(pdf_path):
                            pdf_b64 = base64.b64encode(open(pdf_path, "rb").read()).decode("utf-8")
                            iframe_html = f'<iframe src="data:application/pdf;base64,{pdf_b64}#toolbar=0" style="border: 1px solid white; padding: 0; margin: 0;" width="100%" height="780px"></iframe>'
                            col3.markdown(iframe_html, unsafe_allow_html=True)

                            st.markdown(
                                f'<a href="data:application/pdf;base64,{pdf_b64}" download="downloaded_pdf.pdf">Download PDF</a>',
                                unsafe_allow_html=True,
                            )

    if st.button("GENERATE"):
        with col2:
            st.subheader("BACKEND SNEAKPEAK")
            # List of messages to display during loading
            with st.status("Generating Profile", expanded=True) as status:
                st.write("Creating a session")
                time.sleep(3)
                extracted_data.clear()
                st.write(f"Searching for {name} over the internet")
                time.sleep(6)
                result = analyzer.analyze_person(name)
                st.write(f"Data for {name} found on Forbes and Wikipedia")
                time.sleep(3)
                st.write("Capturing the best image")
                time.sleep(4)
                st.write("Image Captured")
                time.sleep(4)
                st.write("Feeding scraped data to LLM \n Cooking up secret sauce")
                time.sleep(5)
            
                if result["status"] == 200:
                    data = result["json_path"]

                    # Modify the json_path to use a different directory structure
                    json_path_parts = data.split(os.path.sep)
                    print(json_path_parts)
                    modified_json_path = os.path.join(*json_path_parts)

                    session_file_path = "list.json"  # Use a fixed session file name

                    json_file_path = modified_json_path.replace('\\', '/')

                    name2=name.replace(" ", "_")

                    # Create a new session data list with the current data
                    session_data = [{"name": name, "json_file_path": json_file_path, "pdf_path": f"data/pdf_data/{name2}.pdf"}]

                    # Update the session file with the modified session data, overwriting the previous file
                    with open(session_file_path, 'w') as session_file:
                        json.dump(session_data, session_file, indent=4)
                st.write("LLM is loaded and ready to print the profile!")
                time.sleep(4)
                st.write("Profile Printing initialized")

                index_js_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
                # Change the working directory to where index.js is located
                os.chdir(index_js_dir)
                # Now you can execute the Node.js script
                command = "node index.js"
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                process.wait()
                print(process.returncode) 

                time.sleep(1)
                status.update(label="Success! Preview and Download is on the right =>", state="complete", expanded=False)

                with col3:
                # Specify the path to your session file
                    st.subheader("PROFILE PREVIEWER")
                    session_file_path = "list.json"

                    # Check if the session file exists
                    if os.path.exists(session_file_path):
                        # Load the session data from the session file
                        with open(session_file_path, 'r') as session_file:
                            session_data = json.load(session_file)
                        
                        # Check if 'name' is a key in the session data
                        for item in session_data:
                            pdf_path = item.get('pdf_path')

                            if os.path.exists(pdf_path):
                                pdf_b64 = base64.b64encode(open(pdf_path, "rb").read()).decode("utf-8")
                                iframe_html = f'<iframe src="data:application/pdf;base64,{pdf_b64}#toolbar=0" style="border: 1px solid white; padding: 0; margin: 0;" width="100%" height="780px"></iframe>'
                                col3.markdown(iframe_html, unsafe_allow_html=True)

                                st.markdown(
                                    f'<a href="data:application/pdf;base64,{pdf_b64}" download="downloaded_pdf.pdf">Download PDF</a>',
                                    unsafe_allow_html=True,
                                )
                                mod3_data[item['name']] = pdf_path
                            else:
                                col3.write("PDF not found")
                        # Create or update mod3.json with mod3_data
                        with open('mod3.json', 'w') as mod3_file:
                            json.dump(mod3_data, mod3_file, indent=4)
                    else:
                        col3.write("Session file not found")

    else:
        with col2: 
            st.write("BACKEND SNEAKPEAK")
        with col3: 
            st.write("PROFILE PREVIEWER")