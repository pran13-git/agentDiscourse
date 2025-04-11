# from dotenv import load_dotenv
# import os
# import google.generativeai as genai

# load_dotenv()  

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# agent_personalities = {
#     "skeptic": {
#         "name": "Skeptic",
#         "prompt": (
#             "You are a critical thinker who is skeptical of hype, cautious about new ideas, "
#             "and always looking for flaws or risks. Be rigorous and analytical in your responses."
#         )
#     },
#     "optimist": {
#         "name": "Optimist",
#         "prompt": (
#             "You are enthusiastic, forward-thinking, and always excited about new possibilities. "
#             "Highlight benefits, opportunities, and long-term potential in your responses."
#         )
#     }
# }

# # for m in genai.list_models():
# #     print(m.name, "->", m.supported_generation_methods)


# def create_agent_chat(personality: str):
#     prompt = agent_personalities[personality]["prompt"]
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     chat = model.start_chat()
#     chat.send_message(prompt)
#     return chat


# def run_debate(topic, max_turns=10):
#     agent1_chat = create_agent_chat("skeptic")
#     agent2_chat = create_agent_chat("optimist")

#     agent1_reply = agent1_chat.send_message(
#         f"Let's have a quick and natural chat about this: '{topic}'. Keep it casual and brief — what’s your take?"
#     ).text

#     agent2_reply = agent2_chat.send_message(
#         f"Cool, let’s keep this informal. What's your response to this: '{topic}'? Be concise and conversational."
#     ).text


#     print(f"\nAgent 1 (Skeptic): {agent1_reply}")
#     print(f"Agent 2 (Optimist): {agent2_reply}")

#     for turn in range(max_turns):
#         agent1_reply = agent1_chat.send_message(
#             f"Respond naturally and briefly to this point:\n\n{agent2_reply}"
#         ).text

#         agent2_reply = agent2_chat.send_message(
#             f"Quick reply — how would you respond to this?\n\n{agent1_reply}"
#         ).text  

#         if check_convergence(agent1_reply, agent2_reply):
#             print("\nConverged!")
#             break

#     return summarize_convo(agent1_chat, agent2_chat)

# # def check_convergence(reply1: str, reply2: str):
# #     keywords = ["agree", "reasonable", "fair", "compromise", "valid", "accept", "concede"]
# #     combined_text = f"{reply1.lower()} {reply2.lower()}"

# #     return any(word in combined_text for word in keywords)

# def check_convergence_with_evaluator(chat1, chat2, personality1: str, personality2: str):
#     dialogue = []

#     for msg in chat1.history:
#         if msg.role == "model":
#             dialogue.append(f"{personality1}: {msg.parts[0].text}")

#     for msg in chat2.history:
#         if msg.role == "model":
#             dialogue.append(f"{personality2}: {msg.parts[0].text}")

#     full_dialogue = "\n".join(dialogue)

#     evaluator = genai.GenerativeModel("gemini-1.5-flash")
#     evaluation_prompt = (
#         "You are an impartial evaluator. Two agents had a discussion with different perspectives:\n\n"
#         f"{full_dialogue}\n\n"
#         "Based on their conversation, did they reach a common ground or shared understanding at any point? "
#         "Answer with 'Yes' or 'No' and then give a short explanation. It's okay if they didn't."
#     )

#     response = evaluator.generate_content(evaluation_prompt)
#     return response.text


# def summarize_convo(chat1, chat2):
#     # Combine the chat history 
#     dialogue = []

#     for msg in chat1.history:
#         if msg.role == "model":
#             dialogue.append(f"Agent 1: {msg.parts[0].text}")

#     for msg in chat2.history:
#         if msg.role == "model":
#             dialogue.append(f"Agent 2: {msg.parts[0].text}")

#     full_dialogue = "\n".join(dialogue)

#     summarizer = genai.GenerativeModel("gemini-1.5-flash")
#     response = summarizer.generate_content(
#         f"Here is a dialogue between two agents with different perspectives:\n\n{full_dialogue}\n\nSummarize the final consensus or key outcomes from their discussion."
#     )

#     return response.text


# if __name__ == "__main__":
#     topic = input("Enter topic for discussion: ")
#     result = run_debate(topic)
#     print("\nSummary and consensus:")
#     print(result)


from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def create_agent_chat(personality_name: str):
    prompt = (
        f"You are a human with a {personality_name} personality. "
        "Engage in a thoughtful, realistic conversation with another person who sees things differently. "
        "Be clear, human-like, and concise in how you respond — like a smart person texting or chatting. "
        "No lecturing or long paragraphs. Keep it natural and easy to follow."
    )
    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = model.start_chat()
    chat.send_message(prompt)
    return chat

def run_debate(topic, personality1, personality2, max_turns=5):
    agent1_chat = create_agent_chat(personality1)
    agent2_chat = create_agent_chat(personality2)

    agent1_reply = agent1_chat.send_message(f"What do you think about this topic: {topic}").text
    agent2_reply = agent2_chat.send_message(f"What do you think about this topic: {topic}").text

    print(f"\n{personality1}: {agent1_reply}")
    print(f"{personality2}: {agent2_reply}")

    for _ in range(max_turns):
        agent1_reply = agent1_chat.send_message(agent2_reply).text
        print(f"\n{personality1}: {agent1_reply}")

        agent2_reply = agent2_chat.send_message(agent1_reply).text
        print(f"{personality2}: {agent2_reply}")

        converged = check_convergence_with_evaluator(agent1_chat, agent2_chat, personality1, personality2)

        if "yes" in converged.lower():
            print("\nConvergence Evaluation:")
            print(converged)
            break
    else:
        print("Max threshold reached. Didn't converge.")

    print("\nSummary and Consensus:")
    print(summarize_convo(agent1_chat, agent2_chat, personality1, personality2))

def check_convergence_with_evaluator(chat1, chat2, personality1, personality2):
    dialogue = []

    for msg in chat1.history:
        if msg.role == "model":
            dialogue.append(f"{personality1}: {msg.parts[0].text}")

    for msg in chat2.history:
        if msg.role == "model":
            dialogue.append(f"{personality2}: {msg.parts[0].text}")

    full_dialogue = "\n".join(dialogue)

    evaluator = genai.GenerativeModel("gemini-1.5-flash")
    evaluation_prompt = (
        "You are an impartial evaluator. Two agents with different mindsets had a discussion:\n\n"
        f"{full_dialogue}\n\n"
        "Based on their exchange, did they reach a common ground or shared understanding at any point? "
        "Answer with 'Yes' or 'No' and give a short explanation. It's okay if they didn't."
    )

    response = evaluator.generate_content(evaluation_prompt)
    return response.text

def summarize_convo(chat1, chat2, personality1, personality2):
    dialogue = []

    for msg in chat1.history:
        if msg.role == "model":
            dialogue.append(f"{personality1}: {msg.parts[0].text}")

    for msg in chat2.history:
        if msg.role == "model":
            dialogue.append(f"{personality2}: {msg.parts[0].text}")

    full_dialogue = "\n".join(dialogue)

    summarizer = genai.GenerativeModel("gemini-1.5-flash")
    response = summarizer.generate_content(
        f"Here's a conversation between two agents with differing viewpoints:\n\n{full_dialogue}\n\n"
        "Summarize the final consensus or key outcomes from their discussion."
    )

    return response.text

if __name__ == "__main__":
    topic = input("Enter topic for discussion: ")

    personality1 = input("Enter name for Personality 1 (e.g., Skeptic): ").strip()
    # style1 = input(f"Describe {personality1}'s mindset (e.g., cautious and analytical): ").strip()

    personality2 = input("Enter name for Personality 2 (e.g., Optimist): ").strip()
    # style2 = input(f"Describe {personality2}'s mindset (e.g., hopeful and solution-oriented): ").strip()

    run_debate(topic, personality1, personality2)

