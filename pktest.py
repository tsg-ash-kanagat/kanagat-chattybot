import openai
import os
import streamlit as st

#################    ADDED THIS  ############################
#Need to add this to integrate with portkey url
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders, api_key
############################################################

# Setting page title and header
st.set_page_config(page_title="ChattyBot", page_icon='🖥️', menu_items=None)
st.markdown("<h1 style='text-align: center;'>Chatty Bot  🖥️</h1>", unsafe_allow_html=True)

# Access OpenAI API key and organization ID from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.organization = os.environ.get("OPENAI_ORGANIZATION")

#################    ADDED THIS  ############################
#add these options to your openai calls *PLEASE MAKE SURE YOUR ZSCALER IS TURNED OFF*
openai.base_url = "https://api.portkey.ai/v1/"
# openai.base_url = PORTKEY_GATEWAY_URL
openai.default_headers=createHeaders(
     provider="openai",
     api_key="PORTKEY_API_KEY"
)
############################################################
# Check if API key is set
if not openai.api_key:
    st.error("Error: OPENAI_API_KEY environment variable not set.")
    st.stop()  # Stop execution if API key is not found

# Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# Sidebar
st.sidebar.title("Sidebar")
model_name = st.sidebar.radio("Choose a model:", ("GPT-4o", "GPT-4o-mini"))
counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# Map model names to OpenAI model IDs
if model_name == "GPT-40-mini":
    model = "gpt-4o-mini"
else:
    model = "gpt-4o"

# Reset session state on clear button click
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

# Generate a response from the OpenAI API
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    completion = openai.chat.completions.create(
        model=model,
        messages=st.session_state['messages']
    )

    # CORRECTED way to access response content
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})

    total_tokens1 = completion.usage.total_tokens
    prompt_tokens1 = completion.usage.prompt_tokens
    completion_tokens1 = completion.usage.completion_tokens
    return response, total_tokens1, prompt_tokens1, completion_tokens1

# Containers for chat history and text input
response_container = st.container()
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)

        # Calculate cost based on the selected model
        if model_name == "GPT-4o":
            cost = total_tokens * 0.005 / 1000
        else:  # GPT-4o-mini
            cost = (prompt_tokens * 0.00015 + completion_tokens * 0.0006) / 1000

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

# Display chat history with custom styling
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            # User message
            st.markdown(
                f'<div style="background-color: #e9f5ff; padding: 10px; border-radius: 5px; margin-bottom: 5px; width: fit-content; float: right;">'
                f'{st.session_state["past"][i]}'
                f'</div>',
                unsafe_allow_html=True
            )

            # Bot message
            st.markdown(
                f'<div style="background-color: #f2f2f2; padding: 10px; border-radius: 5px; margin-bottom: 5px; width: fit-content;">'
                f'{st.session_state["generated"][i]}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.write(
                f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}"
            )
            counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

# Hide Streamlit footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)