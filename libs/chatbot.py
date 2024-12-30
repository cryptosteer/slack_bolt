import os
from .models import UserBotAgent, User, UserBotConversation
from .utils import debug
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")


class Chatbot:

    def __init__(self, slack_user_id, bot_agent_id, thread_ts):
        self.slack_user_id = slack_user_id
        self.bot_agent_id = bot_agent_id
        # try:
        self.user = User.get(User.slack_user_id == self.slack_user_id)
        print(self.user.id, 'self.user.id')
        self.user_bot_agent, created_user_bot_agent = UserBotAgent.get_or_create(
            user=self.user,
            bot_agent_id=self.bot_agent_id
        )
        print(self.user_bot_agent.id, 'self.user_bot_agent.id')
        self.user_bot_conversation, created_user_bot_conversation = UserBotConversation.get_or_create(
            user_bot_agent=self.user_bot_agent,
            thread_ts=thread_ts
        )
        print(self.user_bot_conversation.id, 'self.user_bot_conversation.id')
        print(created_user_bot_conversation, 'created_user_bot_conversation')
        # except:
        #     raise ValueError("User or Bot does not exist")
        self.summary = self.user_bot_conversation.summary
        self.buffer = self.user_bot_conversation.buffer
        self.memory = self._create_memory()

    def _create_memory(self):
        summary_prompt = PromptTemplate(input_variables=["summary", "new_lines"], template=self.user_bot_agent.bot_agent.summary_prompt)
        memory = ConversationSummaryBufferMemory(
            llm=ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=0.2,
                anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            ),
            max_token_limit=2000,
            memory_key="chat_history",
            return_messages=True,
            prompt=summary_prompt,
        )
        if self.summary:
            memory.chat_memory.add_ai_message(self.summary)
        if self.buffer:
            messages = eval(self.buffer)
            for msg in messages:
                if msg["type"] == "human":
                    memory.chat_memory.add_user_message(msg["content"])
                elif msg["type"] == "ai":
                    memory.chat_memory.add_ai_message(msg["content"])
        return memory
        
    def get_response(self, input_text):
        llm = ChatAnthropic(
            # model="claude-3-sonnet-20240229",
            model="claude-3-haiku-20240307",
            temperature=0.5,
            anthropic_api_key=ANTHROPIC_API_KEY,
        )
        
        prompt = PromptTemplate(
            input_variables=["chat_summary", "chat_history", "input"], template=self.user_bot_agent.bot_agent.prompt
        )

        memory_vars = self.memory.load_memory_variables({})
        chat_history = memory_vars["chat_history"]
        chat_summary = self.memory.predict_new_summary(chat_history, "")

        system_content = prompt.format(
            chat_summary=chat_summary,
            chat_history=chat_history,
            input=input_text,
        )

        messages = [SystemMessage(content=system_content), HumanMessage(content=input_text)]

        response = llm.invoke(messages)

        response_content = (
            response.content if isinstance(response, AIMessage) else str(response)
        )

        self.memory.save_context({"input": input_text}, {"output": response_content})

        updated_summary = self.memory.predict_new_summary(self.memory.chat_memory.messages, "")
        updated_buffer = str(
            [
                {
                    "type": "human" if isinstance(msg, HumanMessage) else "ai",
                    "content": msg.content,
                }
                for msg in self.memory.chat_memory.messages[-5:]
            ]
        )
        self.user_bot_conversation.summary = updated_summary
        self.user_bot_conversation.buffer = updated_buffer
        self.user_bot_conversation.save()
        
        return response_content
