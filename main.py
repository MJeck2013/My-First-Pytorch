import streamlit as st

try:
    import math
    import ast
    import os
    import re
    import torch as t
    import time
    
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

    st.title(f"Chat with {ai_name}")
    user = st.chat_input(f"Talk to {ai_name}")

    if user:
        default = False
        Error = False
        ai_nums = ai()
        ai_intro = str(ai_nums).replace("1", "Hi!").replace("2", "Hello!").replace("3", "key1")
        name = ""

        if os.path.exists("name.py"):
            with open("name.py", "r") as file:
                name = file.read().strip()

        history = ""
        if os.path.exists("history.py"):
            with open("history.py", "r") as f:
                history = f.read()
    
        if ai_intro == "key1":
            ai_intro = f"Hello {name}!" if name else "Hello!"
    
        question = "?" in user
        ai_main = ""
    
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
        elif any(word in user_clean for word in ["what is", "divided by", "whats the answer to", "solve this equation", "can you solve this", "answer to"]):
            used_text = re.sub(r"[a-zA-Z]", "", user_clean.replace("plus", "+").replace("minus", "-").replace("subtract", "-").replace("times", "*").replace("power", "**").replace("divide", "/").replace("pi", "math.pi"))
            used_text = used_text.replace("\\", "").replace("\"", "").replace("|", "").replace(",", "").replace("!", "").replace("?", "")
            try:
                node = ast.parse(used_text.strip(), mode='eval')
                Answer = eval(compile(node, '<string>', 'eval'), {"__builtins__": None, "math": math}, {})
            except Exception:
                Error = True
                Answer = ""
            name_str = f"{name} i" if name else "I"
            options = {
                1: f"The answer to {used_text} is {Answer}.",
                2: f"{Answer}.",
                3: f"{name_str} think the answer is {Answer}."
            }
            ai_main = options.get(ai_nums, f"{name_str} think the answer is {Answer}.")
            default = True
        elif any(word in user_clean for word in ["im doing", "feeling", "day", "i am"]):
            name_str = f" {name}" if name else ""
            if any(word in user_clean for word in ["sad", "mad", "angry", "depressed", "anxiety"]):
                options = {
                    1: f"That must suck doesn't it{name_str}. I'm sorry :(",
                    2: f"I feel bad for you just know you got someone in your corner{name_str}.",
                    3: f"Its alright things'll get better{name_str}."
                }
                ai_main = options.get(ai_nums, f"Its alright things'll get better{name_str}.")
                default = True
            elif any(word in user_clean for word in ["happy", "excited", "energetic", "joy", "good", "well", "nice"]):
                options = {
                    1: f"That's great{name_str}!",
                    2: f"Great! I'm happy that you are doing so well today{name_str}!",
                    3: f"Let's go{name_str}! That's awesome!"
                }
                ai_main = options.get(ai_nums, f"Let's go{name_str}! That's awesome!")
                default = True
            elif "birthday" in user_clean and "my" in user_clean:
                if not name_str:
                    name_str = " user"
                options = {
                    1: f"Happy Birthday{name_str}!",
                    2: f"Happy birthday to you, happy birthday to you, Happy birthday to{name_str}, Happy birth day to you!",
                    3: f"Let's go{name_str}! Happy birthday!"
                }
                ai_main = options.get(ai_nums, f"Let's go{name_str}! Happy birthday!")
                default = True
            elif "died" in user_clean:
                ai_main = f"I am so sorry for your loss{name_str}."
                default = True

            if any(phrase in user_clean for phrase in ["how about you", "how are you", "you doing"]):
                ai_main = ai_main + " And I am doing well today, thank you for asking!"

        if any(word in user_clean for word in ["my name", "call me", "name is"]):
            match = re.search(r"(?:my name is|call me|my name|people call me)\s+([a-zA-Z]+)", user_clean.replace("!", "").replace(".", "").replace("?", ""), re.IGNORECASE)
            if match:
                name = match.group(1).capitalize()
                str_name = f" {name}"
            name_str = f" {name}" if name else ""
            ai_main = f"Nice to meet you{str_name}! How are you today?"
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

        if Error:
            ai_response = "Please try rephrasing your question."
        else:
            if default:
                if question or (name and (name in ai_main or name in ai_intro)):
                    ai_response = ai_main
                else:
                    ai_response = f"{name} {ai_main}" if name else ai_main
            else:
                ai_response = ai_intro

        if name:
            with open("name.py", "w") as file:
                file.write(name)
            name_label = f"{name}: "
        else:
            name_label = "User: "

        st.write(f"---Chatting-With-{ai_name}---")
        if history:
            st.text(history)

        st.write(f"{name_label}{user}")
        st.write_stream(stream_response(ai_name + ": " + ai_response))
        ai_exiting1 = f"{ai_name}: {ai_response}"
        ai_exiting2 = f"{name_label}{user}"
        history = f"{history}\n{ai_exiting2}\n{ai_exiting1}"
        with open("history.py", "w") as fil:
            fil.write(history)

except Exception as e:
    st.title("An Error occured.")
    st.write(e)
