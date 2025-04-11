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

    transcript = []

    agent1_reply = agent1_chat.send_message(f"What do you think about this topic: {topic}").text
    transcript.append({"speaker": "agent1", "text": agent1_reply})

    agent2_reply = agent2_chat.send_message(f"What do you think about this topic: {topic}").text
    transcript.append({"speaker": "agent2", "text": agent2_reply})

    for _ in range(max_turns):
        agent1_reply = agent1_chat.send_message(agent2_reply).text
        transcript.append({"speaker": "agent1", "text": agent1_reply})

        agent2_reply = agent2_chat.send_message(agent1_reply).text
        transcript.append({"speaker": "agent2", "text": agent2_reply})

        converged = check_convergence_with_evaluator(agent1_chat, agent2_chat, personality1, personality2)
        if "yes" in converged.lower():
            break
    else:
        converged = "No, they did not converge. Max turns reached."

    summary = summarize_convo(agent1_chat, agent2_chat, personality1, personality2)

    return {
        "transcript": transcript,
        "evaluation": converged,
        "summary": summary
    }


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