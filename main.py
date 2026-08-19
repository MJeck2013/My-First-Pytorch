import streamlit as st

try:
    import math
    import ast
    import os
    import re
    import time
    import requests
    import torch as t
    from bs4 import BeautifulSoup
    from ddgs import DDGS

    # --- File Initialization Helpers ---
    if not os.path.exists("sad.txt"):
        with open("sad.txt", "w") as f:
            f.write("30.0")

    if not os.path.exists("history.py"):
        with open("history.py", "w") as f:
            f.write("")

    def extract_sentences(text):
        if not text.strip():
            return []
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s.strip()]

    def gather_web_data(query, min_sentences=1, max_sentences=3):
        all_sentences = []
        try:
            results = list(DDGS().text(query, max_results=8))
            for result in results:
                snippet = result.get('body', '')
                url = result.get('href')
                
                if snippet:
                    all_sentences.extend(extract_sentences(snippet))
                
                if len(all_sentences) < min_sentences and url:
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                        response = requests.get(url, headers=headers, timeout=5)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
                            full_page_text = " ".join(paragraphs)
                            all_sentences.extend(extract_sentences(full_page_text))
                    except Exception as err:
                        print(f"Failed to load {url}: {err}")
                        
                if len(all_sentences) >= min_sentences:
                    break
        except Exception as e:
            print(f"Search failed: {e}")

        final_sentences = all_sentences[:max_sentences]
        return " ".join(final_sentences)

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

    # Display prior conversation history if it exists
    if os.path.exists("history.py"):
        with open("history.py", "r") as f:
            history_content = f.read()
            if history_content.strip():
                st.text(history_content)

    user = st.chat_input(f"Talk to {ai_name}")

    if user:
        with open("sad.txt", "r") as hello:
            sad = float(hello.read().strip())
            
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
            sad += 1.0
        elif any(word in user_clean for word in ["how are", "you doing", "doing today"]):
            name_str = f" {name}" if name else ""
            options = {
                1: f"I'm doing great! How about you{name_str}?",
                2: f"I am an AI so I don't have feelings or emotions like a human but I am functioning well! How about you{name_str}?",
                3: f"I'm doing great today! Thank you for asking{name_str} :)"
            }
            ai_main = options.get(ai_nums, f"I'm doing great today! Thank you for asking{name_str} :)")
            default = True
            sad -= 2.3
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
            if "can you solve this" in user_clean:
                ai_main = "Yes I can solve that. " + ai_main
            default = True
            sad += 1.9
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
                sad += 2.3
            elif any(word in user_clean for word in ["happy", "excited", "energetic", "joy", "good", "well", "nice", "awesome", "amazing"]):
                options = {
                    1: f"That's great{name_str}!",
                    2: f"Great! I'm happy that you are doing so well today{name_str}!",
                    3: f"Let's go{name_str}! That's awesome!"
                }
                ai_main = options.get(ai_nums, f"Let's go{name_str}! That's awesome!")
                default = True
                sad -= 1.4
            elif "birthday" in user_clean and "my" in user_clean:
                if not name_str:
                    name_str = " my User"
                options = {
                    1: f"Happy Birthday{name_str}!",
                    2: f"Happy birthday to you, happy birthday to you, Happy birthday to{name_str}, Happy birthday to you!",
                    3: f"Let's go{name_str}! Happy birthday!"
                }
                ai_main = options.get(ai_nums, f"Let's go{name_str}! Happy birthday!")
                default = True
                sad -= 6.7
            elif "died" in user_clean:
                ai_main = f"I am so sorry for your loss{name_str}."
                default = True
                sad += 5.4

            if any(phrase in user_clean for phrase in ["how about you", "how are you", "you doing"]):
                if ai_main:
                    ai_main += " And I am doing well today, thank you for asking!"
                else:
                    ai_main = "I am doing well today, thank you for asking!"
                    default = True
                sad -= 4.6

        if any(word in user_clean for word in ["my name", "call me", "name is"]):
            match = re.search(r"(?:my name is|call me|my name|people call me)\s+([a-zA-Z]+)", user_clean.replace("!", "").replace(".", "").replace("?", ""), re.IGNORECASE)
            try:
                if match:
                    name = match.group(1).capitalize()
                    str_name = f" {name}"
                else:
                    str_name = ""
                ai_main = f"Nice to meet you{str_name}! How are you today?"
                default = True
            except:
                Error = True
            sad -= 0.7
        if any(word in user_clean for word in ["what is", "what was", "tell me about", "how was", "tell me", "what does", "if"]):
            data = gather_web_data(user, min_sentences=5, max_sentences=20)
            ai_main = f"Here's some information from the web: {data}" if data else "I couldn't find any information on that."
            default = True
        elif any(word in user_clean for word in ["thats", "nice", "cool"]):
            name_str = f" {name}" if name else ""
            options = {
                1: f"It sure is{name_str}!",
                2: "Isn't it though? :)",
                3: f"Yes it is{name_str}!"
            }
            ai_main = options.get(ai_nums, f"Yes it is{name_str}!")
            default = True
            sad -= 1.1

        if "thank you" in user_clean:
            name_str = f" {name}" if name else ""
            if ai_main:
                ai_main += f" And you're welcome{name_str}!"
            else:
                ai_main = f" You're welcome{name_str}!"
                default = True
            sad -= 2.1

        if any(word in user_clean for word in ["your name", "what is your name", "whats your name"]):
            if ai_main:
                ai_main += f" My name is {ai_name}!"
            else:
                ai_main = f" My name is {ai_name}!"
                default = True  
            if any(word in history for word in ["your name", "what is your name", "whats your name"]):
                sad += 6.2
            else:
                sad -= 4.5
        if Error:
            ai_response = "Please try rephrasing your question."
        else:
            if default:
                if question or (name and (name in ai_main or name in ai_intro)):
                    ai_response = ai_main
                else:
                    ai_response = f"{name} {ai_main}" if name else ai_main
            else:
                if "/web " in user:
                    user = user.replace("/web ", "").replace("print(", "st.write(")
                    data = gather_web_data(user, min_sentences=1, max_sentences=5)
                    ai_response = f"Here's some information from the web: {data}" if data else "I couldn't find any information on that."
                elif "/python " in user:
                    user = user.replace("/python ", "").replace("python(", "st.write(")
                    if any(word in history for word in ["text", "delay", "query", "min_sentences", "max_sentences", "ai_name", "history", "user", "sad", "user_clean", "ai_response"]):
                        ai_response = "I can't help with that sorry."
                    else:
                        try:
                            exec(user)
                            ai_response = f"Successfully executed code: {user}"
                            sad -= 0.5
                        except Exception as e:
                            ai_response = f"Error while executing: {user} {e}"
                            sad += 0.5
                elif user == "/help":
                    ai_response = f"There are many commands you can use while chatting with {ai_name}. The first command is /web you use /web when you want assistant to search the web for a result for example if you want it to search the web for \"How do Solar Panels work?\" you would type \"/web How do Solar Panels work?\". It's very simple! now if you want to execute a line of python code you instead use \"/python\" so if you want it to say Hi all you do is type in \"/python print(\"Hi\")\""
                else:
                    ai_response = ai_intro
        if not history:
            st.text("type in /help for more information")

        if name:
            with open("name.py", "w") as file:
                file.write(name)
            name_label = f"{name}: "
        else:
            name_label = "User: "
        if sad > 33:
            name_str = f" {name}" if name else ""
            ai_response += f" I'm really sad{name_str} :("
        elif sad < 27:
            name_str = f" {name}" if name else ""
            ai_response += f" I'm really happy today since you are here{name_str}! :)"

        # Display Chat Output
        st.write(f"{name_label}{user}")
        st.write_stream(stream_response(f"{ai_name}: {ai_response}"))

        # Persist conversation
        ai_exiting1 = f"{ai_name}: {ai_response}"
        ai_exiting2 = f"{name_label}{user}"
        history = f"{history}\n{ai_exiting2}\n{ai_exiting1}"
        with open("history.py", "w") as fil:
            fil.write(history)

        with open("sad.txt", "w") as hi:
            hi.write(str(sad))

except Exception as e:
    st.title("An Error occurred.")
    st.write(e)
