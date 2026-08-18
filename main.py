import os
import torch as t
import time
import streamlit as st

def stream_response(text, delay=0.03):
    for word in text.split(" "):
        yield word + " "
        time.sleep(delay)

ai_name = "Assistant"

def ai():
    for i in range(30):
        inputs = t.tensor([1.5])
        target = t.tensor([2.0])
        weight = t.randn(1, requires_grad=True)
        
        ai_guess = inputs * weight
        loss = (ai_guess - target) ** 2
        loss.backward()
        
        with t.no_grad():
            learning_rate = 0.1
            weight.data -= learning_rate * weight.grad
        ai_num = int((ai_guess.round()).item())
        if ai_num in [1, 2, 3]:
            break
    return ai_num

while True:
    user = st.chat_input(f"Talk to {ai_name}: ")
    if user:
        default = False
        ai_nums = ai()
        
        ai_intro = str(ai_nums).replace("1", "Hi!").replace("2", "Hello!").replace("3", "key1")
        name = ""
        if os.path.exists("name.py"):
            with open("name.py", "r") as file:
                name = file.read().strip()
    
        if ai_intro == "key1":
            ai_intro = f"Hello {name}!" if name else "Hello!"
    
        question = "?" in user
        ai_main = ""
    
        # Check for prompt commands safely
        user_clean = user.lower().replace("'", "")
        
        if "what can you do" in user_clean:
            ai_main = "I can answer questions, inform you on things, and research stuff for you!"
            default = True
        elif any(word in user_clean for word in ["how are", "you doing", "doing today"]):
            name_str = f" {name}" if name else ""
            options = {
                1: f"I'm doing great! How about you{name_str}?",
                2: f"I am an AI so I don't have feelings or emotions like a human but I am functioning well! How about you{name_str}?",
                3: f"I'm doing great today! Thank you for asking{name_str} :)"
            }
            ai_main = options.get(ai_nums, f"I'm doing great today! Thank you for asking{name_str} :)")
            default = True
        elif any(word in user_clean for word in ["hello", "im", "bored"]):
            name_str = f" {name}" if name else ""
            options = {
                1: f"What can I do for you{name_str}?",
                2: f"What can I help you with today{name_str}?",
                3: f"How can I help{name_str}?"
            }
            ai_main = options.get(ai_nums, f"How can I help{name_str}?")
            default = True
        elif any(word in user_clean for word in ["thats", "nice", "cool"]):
            name_str = f" {name}" if name else ""
            options = {
                1: f"It sure is{name_str}!",
                2: f"Isn't it though{name_str}? :)",
                3: f"Yes it is{name_str}!"
            }
            ai_main = options.get(ai_nums, f"Yes it is{name_str}!")
            default = True
        if default:
            if question or (name and (name in ai_main or name in ai_intro)):
                ai_response = ai_main
            else:
                ai_response = f"{name} {ai_main}" if name else ai_main
        else:
            ai_response = ai_intro
        with st.chat_message("assistant"):
            st.write_stream(stream_response(ai_response))
